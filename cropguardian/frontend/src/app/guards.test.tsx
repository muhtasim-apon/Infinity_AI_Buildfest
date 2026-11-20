import { screen, waitFor } from '@testing-library/react'
import { http, HttpResponse } from 'msw'
import { describe, expect, it, vi } from 'vitest'
import { server, signedIn } from '../../tests/msw'
import { bnText, renderApp } from '../../tests/render'

const adminChunkLoaded = vi.hoisted(() => ({ count: 0 }))
vi.mock('./pages/AdminHome', () => {
  adminChunkLoaded.count += 1
  return { default: () => <h1>admin-chunk</h1> }
})

function as(role: string, next = 'home') {
  server.use(http.get('*/api/v1/auth/state', () => HttpResponse.json(signedIn(role, next))))
}
const where = () => screen.getByTestId('location').textContent

describe('route guards (spec 15.4)', () => {
  it('sends an anonymous visitor to /login with a return_to', async () => {
    renderApp('/home')
    await waitFor(() => expect(where()).toContain('/login?return_to='))
    expect(decodeURIComponent(where() ?? '')).toContain('return_to=/home')
    expect(await screen.findByRole('heading', { level: 1 })).toHaveTextContent(
      bnText('auth.login.title'),
    )
  })

  it('lets a farmer into the farmer app (/home redirects to /app)', async () => {
    as('FARMER')
    renderApp('/home')
    await waitFor(() => expect(where()).toBe('/app'), { timeout: 5000 })
    expect(
      await screen.findByText(bnText('farmerHome.hero.title'), {}, { timeout: 5000 }),
    ).toBeInTheDocument()
  })

  it('wrong role: reviewer area for a farmer is 403', async () => {
    as('FARMER')
    renderApp('/review')
    expect(await screen.findByText(bnText('errors.forbiddenTitle'))).toBeInTheDocument()
  })

  it('admin area for a non-admin looks like a missing page (404), and its chunk is never loaded', async () => {
    as('FARMER')
    renderApp('/admin')
    expect(await screen.findByText(bnText('errors.notFoundTitle'))).toBeInTheDocument()
    expect(adminChunkLoaded.count).toBe(0)
  })

  it('an admin gets the admin chunk', async () => {
    as('ADMIN')
    renderApp('/admin')
    expect(await screen.findByText('admin-chunk')).toBeInTheDocument()
    expect(adminChunkLoaded.count).toBe(1)
  })

  it('staff with 2FA pending are held at the 2FA screens', async () => {
    as('REVIEWER', 'totp')
    renderApp('/review')
    await waitFor(() => expect(where()).toBe('/login/totp'))
    expect(await screen.findByRole('heading', { level: 1 })).toHaveTextContent(
      bnText('auth.totp.title'),
    )
  })

  it('staff who must enrol 2FA are sent to setup', async () => {
    as('ADMIN', 'setup_totp')
    server.use(
      http.post('*/api/v1/auth/totp/setup', () =>
        HttpResponse.json({ secret: 'ABCDEF234567', otpauth_uri: 'otpauth://x' }),
      ),
    )
    renderApp('/admin')
    await waitFor(() => expect(where()).toBe('/setup-2fa'))
    expect(await screen.findByTestId('totp-secret')).toHaveTextContent('ABCDEF234567')
  })

  it('a signed-in user opening /login is sent to their home', async () => {
    as('REVIEWER')
    renderApp('/login')
    await waitFor(() => expect(where()).toBe('/review'), { timeout: 5000 })
  })

  it('shows the DEMO ribbon for demo roles only', async () => {
    as('DEMO_FARMER')
    const { unmount } = renderApp('/home')
    expect(await screen.findByText(bnText('demo.ribbon'))).toBeInTheDocument()
    unmount()
    as('FARMER')
    renderApp('/app')
    await screen.findByText(bnText('farmerHome.hero.title'), {}, { timeout: 5000 })
    expect(screen.queryByText(bnText('demo.ribbon'))).not.toBeInTheDocument()
  })

  it('unknown paths show the 404 page', async () => {
    renderApp('/no/such/page')
    expect(await screen.findByText(bnText('errors.notFoundTitle'))).toBeInTheDocument()
  })

  it('shows a retry option when the API is still waking up', async () => {
    server.use(http.get('*/api/v1/auth/state', () => new HttpResponse(null, { status: 503 })))
    renderApp('/home')
    expect(
      await screen.findByText(bnText('errors.waking'), {}, { timeout: 15000 }),
    ).toBeInTheDocument()
  }, 20000)
})
