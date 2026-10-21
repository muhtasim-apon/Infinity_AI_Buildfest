import { http, HttpResponse } from 'msw'
import { describe, expect, it, vi } from 'vitest'
import { problem, server } from '../../tests/msw'
import { api, ApiError, onUnauthenticated } from './api'

describe('api wrapper', () => {
  it('sends the CSRF header on unsafe requests only, with cookies included', async () => {
    const seen: Record<string, string | null> = {}
    server.use(
      http.get('*/api/v1/ping', ({ request }) => {
        seen.getCsrf = request.headers.get('x-csrf-token')
        return HttpResponse.json({ ok: true })
      }),
      http.post('*/api/v1/ping', ({ request }) => {
        seen.postCsrf = request.headers.get('x-csrf-token')
        seen.contentType = request.headers.get('content-type')
        return HttpResponse.json({ ok: true })
      }),
    )
    await api.get('/api/v1/ping')
    await api.post('/api/v1/ping', { a: 1 })
    expect(seen.getCsrf).toBeNull()
    expect(seen.postCsrf).toBe('csrf-1')
    expect(seen.contentType).toContain('application/json')
  })

  it('follows a rotated CSRF token returned in a response body', async () => {
    let second: string | null = null
    server.use(
      http.post('*/api/v1/first', () => HttpResponse.json({ csrf_token: 'rotated' })),
      http.post('*/api/v1/second', ({ request }) => {
        second = request.headers.get('x-csrf-token')
        return new HttpResponse(null, { status: 204 })
      }),
    )
    await api.post('/api/v1/first')
    await expect(api.post('/api/v1/second')).resolves.toBeUndefined()
    expect(second).toBe('rotated')
  })

  it('refetches the token and retries once when the server says csrf_failed', async () => {
    let calls = 0
    server.use(
      http.post('*/api/v1/guarded', () => {
        calls += 1
        return calls === 1 ? problem(403, 'csrf_failed') : HttpResponse.json({ done: true })
      }),
    )
    await expect(api.post('/api/v1/guarded', {})).resolves.toEqual({ done: true })
    expect(calls).toBe(2)
  })

  it('does not retry csrf_failed forever', async () => {
    let calls = 0
    server.use(
      http.post('*/api/v1/guarded', () => {
        calls += 1
        return problem(403, 'csrf_failed')
      }),
    )
    await expect(api.post('/api/v1/guarded', {})).rejects.toMatchObject({ code: 'csrf_failed' })
    expect(calls).toBe(2)
  })

  it('maps problem+json to ApiError (code, Retry-After, request id, extras)', async () => {
    server.use(
      http.get('*/api/v1/limited', () =>
        problem(429, 'rate_limited', { retry_after: 12 }, { 'Retry-After': '12' }),
      ),
      http.get('*/api/v1/weak', () => problem(422, 'password_weak', { reason: 'common' })),
    )
    const limited = await api.get('/api/v1/limited').catch((e: unknown) => e)
    expect(limited).toBeInstanceOf(ApiError)
    expect(limited).toMatchObject({
      status: 429,
      code: 'rate_limited',
      retryAfter: 12,
      requestId: 'req-123',
    })
    const weak = (await api.get('/api/v1/weak').catch((e: unknown) => e)) as ApiError
    expect(weak.extra.reason).toBe('common')
    expect(weak.extra).not.toHaveProperty('request_id')
  })

  it('treats 503 and network failures as "server waking up"', async () => {
    server.use(
      http.get('*/api/v1/cold', () => problem(503, 'service_unavailable')),
      http.get('*/api/v1/down', () => HttpResponse.error()),
      http.get(
        '*/api/v1/html',
        () => new HttpResponse('<html>bad gateway</html>', { status: 502 }),
      ),
    )
    await expect(api.get('/api/v1/cold')).rejects.toMatchObject({ isUnavailable: true })
    await expect(api.get('/api/v1/down')).rejects.toMatchObject({
      status: 0,
      code: 'network',
      isUnavailable: true,
    })
    await expect(api.get('/api/v1/html')).rejects.toMatchObject({
      status: 502,
      code: 'http_502',
      isUnavailable: true,
    })
  })

  it('notifies listeners on 401 unless the call is marked quiet', async () => {
    server.use(http.get('*/api/v1/secret', () => problem(401, 'authentication_required')))
    const listener = vi.fn()
    const off = onUnauthenticated(listener)
    await expect(api.get('/api/v1/secret')).rejects.toMatchObject({ status: 401 })
    expect(listener).toHaveBeenCalledTimes(1)
    await expect(api.get('/api/v1/secret', { quiet401: true })).rejects.toMatchObject({
      status: 401,
    })
    expect(listener).toHaveBeenCalledTimes(1)
    off()
    await expect(api.get('/api/v1/secret')).rejects.toMatchObject({ status: 401 })
    expect(listener).toHaveBeenCalledTimes(1)
  })

  it('aborts when the caller cancels', async () => {
    server.use(http.get('*/api/v1/slow', async () => new Promise<Response>(() => undefined)))
    const controller = new AbortController()
    const pending = api.get('/api/v1/slow', { signal: controller.signal })
    controller.abort()
    await expect(pending).rejects.toMatchObject({ code: 'network' })
  })
})
