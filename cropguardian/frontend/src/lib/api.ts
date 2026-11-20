/**
 * The only way the app talks to the API (spec 15.4, 16.6).
 * - same-origin, cookies included, never a token readable from script or kept in web storage
 * - CSRF double-submit header on every unsafe request (fetched lazily, retried once if rejected)
 * - 15 s timeout, problem+json parsed into ApiError, no response body is ever logged
 * - 401 notifies the app (-> /login?return_to=...), 429 carries Retry-After, 503/network = "waking"
 */

export const API_TIMEOUT_MS = 15_000
const SAFE_METHODS = new Set(['GET', 'HEAD', 'OPTIONS'])

export interface FieldError {
  loc: string[]
  msg: string
}

export class ApiError extends Error {
  readonly status: number
  readonly code: string
  readonly retryAfter: number | undefined
  readonly requestId: string | undefined
  readonly fields: FieldError[]
  readonly extra: Record<string, unknown>

  constructor(
    status: number,
    code: string,
    init: {
      retryAfter?: number
      requestId?: string
      fields?: FieldError[]
      extra?: Record<string, unknown>
    } = {},
  ) {
    super(code)
    this.name = 'ApiError'
    this.status = status
    this.code = code
    this.retryAfter = init.retryAfter
    this.requestId = init.requestId
    this.fields = init.fields ?? []
    this.extra = init.extra ?? {}
  }

  /** The server could not be reached or is still starting (Render free tier cold start). */
  get isUnavailable(): boolean {
    return this.status === 0 || this.status === 502 || this.status === 503 || this.status === 504
  }
}

type Listener = () => void
const unauthenticatedListeners = new Set<Listener>()

/** Subscribe to "the session is gone" (HTTP 401 on an authenticated call). Returns unsubscribe. */
export function onUnauthenticated(listener: Listener): () => void {
  unauthenticatedListeners.add(listener)
  return () => unauthenticatedListeners.delete(listener)
}

let csrfToken = ''

export function setCsrfToken(token: string): void {
  csrfToken = token
}

export function resetApiStateForTests(): void {
  csrfToken = ''
  unauthenticatedListeners.clear()
}

interface RequestOptions {
  body?: unknown
  /** Calls that are allowed to 401 without signing the user out (login, state probe...). */
  quiet401?: boolean
  signal?: AbortSignal
  /** Extra request headers (e.g. Idempotency-Key). Never credentials: cookies carry the session. */
  headers?: Record<string, string>
  /** Per-call timeout; photo uploads + model calls need longer than the default. */
  timeoutMs?: number
}

async function ensureCsrf(): Promise<void> {
  if (csrfToken) return
  const data = await request<{ csrf_token: string }>('GET', '/api/v1/auth/csrf', { quiet401: true })
  csrfToken = data.csrf_token
}

function parseRetryAfter(value: string | null): number | undefined {
  if (!value) return undefined
  const seconds = Number.parseInt(value, 10)
  return Number.isFinite(seconds) && seconds >= 0 ? seconds : undefined
}

const RESERVED = new Set(['type', 'title', 'status', 'code', 'request_id', 'errors'])

async function parseError(response: Response): Promise<ApiError> {
  let body: Record<string, unknown> = {}
  try {
    body = (await response.json()) as Record<string, unknown>
  } catch {
    // non-JSON error body (proxy page): fall through to a generic code
  }
  const code = typeof body.code === 'string' ? body.code : `http_${response.status}`
  const rawFields = Array.isArray(body.errors) ? (body.errors as FieldError[]) : []
  const extra = Object.fromEntries(Object.entries(body).filter(([key]) => !RESERVED.has(key)))
  const request_id = body.request_id
  return new ApiError(response.status, code, {
    retryAfter: parseRetryAfter(response.headers.get('Retry-After')),
    requestId: typeof request_id === 'string' ? request_id : undefined,
    fields: rawFields,
    extra,
  })
}

async function request<T>(
  method: string,
  path: string,
  options: RequestOptions = {},
  retried = false,
): Promise<T> {
  const unsafe = !SAFE_METHODS.has(method)
  if (unsafe) await ensureCsrf()

  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), options.timeoutMs ?? API_TIMEOUT_MS)
  options.signal?.addEventListener('abort', () => controller.abort(), { once: true })

  const isForm = typeof FormData !== 'undefined' && options.body instanceof FormData
  const headers: Record<string, string> = { ...options.headers, Accept: 'application/json' }
  // multipart: the browser sets Content-Type with the boundary itself
  if (options.body !== undefined && !isForm) headers['Content-Type'] = 'application/json'
  if (unsafe && csrfToken) headers['X-CSRF-Token'] = csrfToken

  let response: Response
  try {
    response = await fetch(new URL(path, window.location.origin), {
      method,
      headers,
      credentials: 'include',
      signal: controller.signal,
      body:
        options.body === undefined
          ? undefined
          : isForm
            ? (options.body as FormData)
            : JSON.stringify(options.body),
    })
  } catch {
    throw new ApiError(0, 'network')
  } finally {
    clearTimeout(timer)
  }

  if (response.ok) {
    if (response.status === 204) return undefined as T
    const data = (await response.json()) as T
    const token = (data as { csrf_token?: unknown } | null)?.csrf_token
    if (typeof token === 'string') csrfToken = token
    return data
  }

  const error = await parseError(response)
  if (error.status === 403 && error.code === 'csrf_failed' && unsafe && !retried) {
    csrfToken = '' // token rotated server-side (login/logout): fetch a fresh one and retry once
    return request<T>(method, path, options, true)
  }
  if (error.status === 401 && !options.quiet401) {
    for (const listener of unauthenticatedListeners) listener()
  }
  throw error
}

export const api = {
  get: <T>(path: string, options?: RequestOptions) => request<T>('GET', path, options),
  post: <T>(path: string, body?: unknown, options?: RequestOptions) =>
    request<T>('POST', path, { ...options, body }),
  put: <T>(path: string, body?: unknown, options?: RequestOptions) =>
    request<T>('PUT', path, { ...options, body }),
  patch: <T>(path: string, body?: unknown, options?: RequestOptions) =>
    request<T>('PATCH', path, { ...options, body }),
  delete: <T>(path: string, options?: RequestOptions) => request<T>('DELETE', path, options),
}
