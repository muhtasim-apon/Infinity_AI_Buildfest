import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { delay, http, HttpResponse } from 'msw'
import { axe } from 'vitest-axe'
import { describe, expect, it } from 'vitest'
import { CONSENTS, problem, server, signedIn } from '../../../tests/msw'
import { bnText, renderApp } from '../../../tests/render'

const where = () => screen.getByTestId('location').textContent

/** auth/state answers "anonymous" until `signIn()` is called (as the real server would). */
function statefulAuth() {
  let current: Record<string, unknown> = { authenticated: false, csrf_token: 'c0' }
  server.use(http.get('*/api/v1/auth/state', () => HttpResponse.json(current)))
  return {
    signIn: (role: string, next = 'home') => {
      current = signedIn(role, next)
    },
  }
}

const reply = (role: string, next = 'home') => ({
  next,
  csrf_token: 'c1',
  user: { id: 'u1', role, display_name: 'Rahima', locale: 'bn', tenant: 'real' },
})

describe('login page', () => {
  it('signs a farmer in and lands on the farmer home (keep-signed-in unchecked by default)', async () => {
    const auth = statefulAuth()
    let body: Record<string, unknown> = {}
    server.use(
      http.post('*/api/v1/auth/login', async ({ request }) => {
        body = (await request.json()) as Record<string, unknown>
        auth.signIn('FARMER')
        return HttpResponse.json(reply('FARMER'))
      }),
    )
    const user = userEvent.setup()
    renderApp('/login')
    await user.type(await screen.findByLabelText(bnText('auth.login.identifier')), '01712345678')
    await user.type(screen.getByLabelText(bnText('auth.login.password')), 'river-lantern-47')
    await user.click(screen.getByRole('button', { name: bnText('auth.login.submit') }))
    await waitFor(() => expect(where()).toBe('/home'))
    expect(body).toEqual({
      identifier: '01712345678',
      password: 'river-lantern-47',
      keep_signed_in: false,
    })
  })

  it('honours a safe return_to and ignores an unsafe one', async () => {
    const auth = statefulAuth()
    server.use(
      http.post('*/api/v1/auth/login', () => {
        auth.signIn('FARMER')
        return HttpResponse.json(reply('FARMER'))
      }),
    )
    const user = userEvent.setup()
    const { unmount } = renderApp('/login?return_to=%2Faccount%2Fsessions')
    await user.type(await screen.findByLabelText(bnText('auth.login.identifier')), 'a')
    await user.type(screen.getByLabelText(bnText('auth.login.password')), 'b')
    await user.click(screen.getByRole('button', { name: bnText('auth.login.submit') }))
    await waitFor(() => expect(where()).toBe('/account/sessions'))
    unmount()

    const auth2 = statefulAuth()
    server.use(
      http.post('*/api/v1/auth/login', () => {
        auth2.signIn('FARMER')
        return HttpResponse.json(reply('FARMER'))
      }),
    )
    renderApp('/login?return_to=https%3A%2F%2Fevil.example')
    await user.type(await screen.findByLabelText(bnText('auth.login.identifier')), 'a')
    await user.type(screen.getByLabelText(bnText('auth.login.password')), 'b')
    await user.click(screen.getByRole('button', { name: bnText('auth.login.submit') }))
    await waitFor(() => expect(where()).toBe('/home'))
  })

  it('shows one uniform message for wrong credentials and keeps the user on the page', async () => {
    statefulAuth()
    server.use(http.post('*/api/v1/auth/login', () => problem(401, 'invalid_credentials')))
    const user = userEvent.setup()
    renderApp('/login')
    await user.type(await screen.findByLabelText(bnText('auth.login.identifier')), 'someone')
    await user.type(screen.getByLabelText(bnText('auth.login.password')), 'wrong')
    await user.click(screen.getByRole('button', { name: bnText('auth.login.submit') }))
    expect(await screen.findByRole('alert')).toHaveTextContent(bnText('errors.invalidCredentials'))
    expect(screen.getByRole('alert')).toHaveTextContent('req-123')
    expect(where()).toBe('/login')
  })

  it('validates empty fields without calling the server', async () => {
    statefulAuth()
    let called = false
    server.use(
      http.post(
        '*/api/v1/auth/login',
        () => ((called = true), problem(401, 'invalid_credentials')),
      ),
    )
    const user = userEvent.setup()
    renderApp('/login')
    await user.click(await screen.findByRole('button', { name: bnText('auth.login.submit') }))
    expect((await screen.findAllByText(bnText('errors.validation'))).length).toBeGreaterThan(0)
    expect(called).toBe(false)
  })

  it('shows the rate-limit wait and the lockout messages', async () => {
    statefulAuth()
    let n = 0
    server.use(
      http.post('*/api/v1/auth/login', () =>
        ++n === 1
          ? problem(429, 'rate_limited', {}, { 'Retry-After': '42' })
          : problem(429, 'account_locked', {}, { 'Retry-After': '900' }),
      ),
    )
    const user = userEvent.setup()
    renderApp('/login')
    await user.type(await screen.findByLabelText(bnText('auth.login.identifier')), 'a')
    await user.type(screen.getByLabelText(bnText('auth.login.password')), 'b')
    await user.click(screen.getByRole('button', { name: bnText('auth.login.submit') }))
    expect(await screen.findByRole('alert')).toHaveTextContent('42')
    await user.click(screen.getByRole('button', { name: bnText('auth.login.submit') }))
    await waitFor(() =>
      expect(screen.getByRole('alert')).toHaveTextContent(bnText('errors.locked')),
    )
  })

  it('starts the proof-of-work check when the server asks for CAPTCHA, then sends the payload', async () => {
    statefulAuth()
    const payloads: unknown[] = []
    server.use(
      http.post('*/api/v1/auth/login', async ({ request }) => {
        const b = (await request.json()) as { captcha?: string }
        payloads.push(b.captcha)
        return b.captcha ? problem(401, 'invalid_credentials') : problem(400, 'captcha_required')
      }),
    )
    const user = userEvent.setup()
    renderApp('/login')
    await user.type(await screen.findByLabelText(bnText('auth.login.identifier')), 'a')
    await user.type(screen.getByLabelText(bnText('auth.login.password')), 'b')
    await user.click(screen.getByRole('button', { name: bnText('auth.login.submit') }))
    await screen.findByText(bnText('errors.captchaRequired'))
    await waitFor(
      () => expect(screen.getByRole('button', { name: bnText('auth.login.submit') })).toBeEnabled(),
      { timeout: 5000 },
    )
    await user.click(screen.getByRole('button', { name: bnText('auth.login.submit') }))
    await waitFor(() => expect(payloads).toHaveLength(2))
    expect(payloads[0]).toBeUndefined()
    expect(JSON.parse(atob(String(payloads[1]))).number).toBe(7)
  })

  it('has no accessibility violations and a working password toggle', async () => {
    statefulAuth()
    const user = userEvent.setup()
    const { container } = renderApp('/login')
    const password = await screen.findByLabelText(bnText('auth.login.password'))
    expect(password).toHaveAttribute('type', 'password')
    await user.click(screen.getByRole('button', { name: bnText('auth.login.showPassword') }))
    expect(password).toHaveAttribute('type', 'text')
    expect(await axe(container)).toHaveNoViolations()
  })

  it('staff login asks for an email-style identifier and offers no demo link', async () => {
    statefulAuth()
    renderApp('/staff')
    expect(await screen.findByRole('heading', { level: 1 })).toHaveTextContent(
      bnText('auth.staff.title'),
    )
    expect(screen.queryByText(bnText('auth.login.tryDemo'))).not.toBeInTheDocument()
  })

  it('routes staff straight to 2FA after the password step', async () => {
    const auth = statefulAuth()
    server.use(
      http.post('*/api/v1/auth/login', () => {
        auth.signIn('ADMIN', 'totp')
        return HttpResponse.json(reply('ADMIN', 'totp'))
      }),
    )
    const user = userEvent.setup()
    renderApp('/staff')
    await user.type(
      await screen.findByLabelText(bnText('auth.login.identifier')),
      'admin@example.org',
    )
    await user.type(screen.getByLabelText(bnText('auth.login.password')), 'a-long-passphrase-1')
    await user.click(screen.getByRole('button', { name: bnText('auth.login.submit') }))
    await waitFor(() => expect(where()).toBe('/login/totp'))
  })
})

describe('registration and OTP', () => {
  it('shows the versioned consent texts, blocks submit without the required consent, then goes to /verify', async () => {
    statefulAuth()
    let body: Record<string, unknown> = {}
    server.use(
      http.post('*/api/v1/auth/register/farmer', async ({ request }) => {
        body = (await request.json()) as Record<string, unknown>
        return HttpResponse.json({ status: 'otp_sent' }, { status: 202 })
      }),
    )
    const user = userEvent.setup()
    const { container } = renderApp('/register')
    await screen.findByText(bnText('auth.register.title'))
    expect((await screen.findAllByText('সেবার জন্য প্রয়োজনীয় তথ্য')).length).toBeGreaterThan(0)
    expect(screen.getByText('মডেল উন্নত করতে ছবি ব্যবহার')).toBeInTheDocument()
    expect(await axe(container)).toHaveNoViolations()

    await user.type(screen.getByLabelText(bnText('auth.register.name')), 'রহিমা বেগম')
    await user.type(screen.getByLabelText(bnText('auth.register.phone')), '01712345678')
    await user.type(
      screen.getByLabelText(bnText('auth.register.password')),
      'river-lantern-orchard-47',
    )
    const submit = screen.getByRole('button', { name: bnText('auth.register.submit') })
    await waitFor(() => expect(submit).toBeEnabled(), { timeout: 5000 })
    await user.click(submit)
    expect((await screen.findAllByText(bnText('errors.validation'))).length).toBeGreaterThan(0)
    expect(body).toEqual({})

    await user.click(screen.getAllByRole('checkbox')[0] as HTMLElement) // required consent
    await waitFor(() => expect(submit).toBeEnabled(), { timeout: 5000 })
    await user.click(submit)
    await waitFor(() => expect(where()).toBe('/verify'))
    expect(body).toMatchObject({
      phone: '01712345678',
      accept_service: true,
      training_use: false,
      push_alerts: false,
      website: '',
    })
    expect(typeof body.captcha).toBe('string')
    expect(where()).not.toContain('01712345678') // the phone number never goes into the URL
  })

  it('hides the honeypot from people and assistive technology', async () => {
    statefulAuth()
    renderApp('/register')
    await screen.findByText(bnText('auth.register.title'))
    const trap = screen.getByText(bnText('auth.captcha.honeypot')).closest('div')
    expect(trap).toHaveAttribute('aria-hidden', 'true')
    expect(trap?.querySelector('input')).toHaveAttribute('tabindex', '-1')
  })

  it('never shows an unnamed consent checkbox while the wording loads (axe `label`, found by E2E)', async () => {
    statefulAuth()
    server.use(
      http.get('*/api/v1/consents/texts', async () => {
        await delay(400)
        return HttpResponse.json(CONSENTS)
      }),
    )
    const { container } = renderApp('/register')
    await screen.findByText(bnText('auth.register.title'))
    // loading window: no checkbox exists, a status says so, submit is locked, and the page is clean
    expect(screen.queryAllByRole('checkbox')).toHaveLength(0)
    expect(screen.getByRole('button', { name: bnText('auth.register.submit') })).toBeDisabled()
    expect(await axe(container)).toHaveNoViolations()
    // once loaded, every checkbox carries its consent text as its accessible name
    const boxes = await screen.findAllByRole('checkbox')
    expect(boxes.length).toBeGreaterThan(0)
    for (const box of boxes) expect(box).toHaveAccessibleName()
    expect(await axe(container)).toHaveNoViolations()
  })

  it('fails closed when the consent wording cannot be loaded: message shown, submit stays locked', async () => {
    statefulAuth()
    server.use(http.get('*/api/v1/consents/texts', () => problem(503, 'unavailable')))
    renderApp('/register')
    await screen.findByText(bnText('auth.register.title'))
    expect(await screen.findByText(bnText('errors.unavailable'))).toBeInTheDocument()
    expect(screen.queryAllByRole('checkbox')).toHaveLength(0)
    // even after the CAPTCHA is solved, a consent the farmer cannot read must not be submittable
    await screen.findByText(bnText('auth.captcha.label'), undefined, { timeout: 5000 })
    expect(screen.getByRole('button', { name: bnText('auth.register.submit') })).toBeDisabled()
  }, 20_000) // waits for a real proof-of-work solve

  it('shows the weak-password message from the server', async () => {
    statefulAuth()
    server.use(
      http.post('*/api/v1/auth/register/farmer', () =>
        problem(422, 'password_weak', { reason: 'common' }),
      ),
    )
    const user = userEvent.setup()
    renderApp('/register')
    await screen.findByText(bnText('auth.register.title'))
    await user.type(screen.getByLabelText(bnText('auth.register.name')), 'রহিমা')
    await user.type(screen.getByLabelText(bnText('auth.register.phone')), '01712345678')
    await user.type(screen.getByLabelText(bnText('auth.register.password')), 'password123')
    await user.click((await screen.findAllByRole('checkbox'))[0] as HTMLElement)
    const submit = screen.getByRole('button', { name: bnText('auth.register.submit') })
    await waitFor(() => expect(submit).toBeEnabled(), { timeout: 5000 })
    await user.click(submit)
    expect(await screen.findByRole('alert')).toHaveTextContent(bnText('errors.passwordCommon'))
  })

  it('verifies the 6-digit code, signs in and keeps resend disabled for 60 s', async () => {
    const auth = statefulAuth()
    let body: Record<string, unknown> = {}
    server.use(
      http.post('*/api/v1/auth/otp/verify', async ({ request }) => {
        body = (await request.json()) as Record<string, unknown>
        auth.signIn('FARMER')
        return HttpResponse.json(reply('FARMER'))
      }),
    )
    const user = userEvent.setup()
    renderApp({ pathname: '/verify', state: { phone: '01712345678' } })
    const resend = await screen.findByRole('button', { name: /৬০|60/ })
    expect(resend).toBeDisabled()
    await user.type(screen.getByLabelText(bnText('auth.otp.code')), '12ab')
    await user.click(screen.getByRole('button', { name: bnText('auth.otp.submit') }))
    expect((await screen.findAllByText(bnText('errors.validation'))).length).toBeGreaterThan(0)
    const code = screen.getByLabelText(bnText('auth.otp.code'))
    await user.clear(code)
    await user.type(code, '123456')
    await user.click(screen.getByRole('button', { name: bnText('auth.otp.submit') }))
    await waitFor(() => expect(where()).toBe('/home'))
    expect(body).toEqual({ phone: '01712345678', code: '123456', keep_signed_in: true })
  })

  it('shows "code not correct" for a wrong OTP', async () => {
    statefulAuth()
    server.use(http.post('*/api/v1/auth/otp/verify', () => problem(400, 'otp_invalid')))
    const user = userEvent.setup()
    renderApp({ pathname: '/verify', state: { phone: '01712345678' } })
    await user.type(await screen.findByLabelText(bnText('auth.otp.code')), '000000')
    await user.click(screen.getByRole('button', { name: bnText('auth.otp.submit') }))
    expect(await screen.findByRole('alert')).toHaveTextContent(bnText('auth.otp.wrong'))
  })
})

describe('password recovery and invitations', () => {
  it('forgot-password always shows the same generic confirmation', async () => {
    statefulAuth()
    server.use(
      http.post('*/api/v1/auth/password/forgot', () =>
        HttpResponse.json({ status: 'accepted' }, { status: 202 }),
      ),
    )
    const user = userEvent.setup()
    renderApp('/forgot-password')
    await user.type(
      await screen.findByLabelText(bnText('auth.login.identifier')),
      'nobody@example.org',
    )
    await user.click(screen.getByRole('button', { name: bnText('auth.forgot.submit') }))
    expect(await screen.findByRole('status')).toHaveTextContent(bnText('auth.forgot.sentGeneric'))
  })

  it('reset-password reads the emailed token once, removes it from the URL, and shows success', async () => {
    statefulAuth()
    let body: Record<string, unknown> = {}
    server.use(
      http.post('*/api/v1/auth/password/reset', async ({ request }) => {
        body = (await request.json()) as Record<string, unknown>
        return new HttpResponse(null, { status: 204 })
      }),
    )
    const user = userEvent.setup()
    renderApp('/reset-password?token=abcdefghijklmnop')
    await waitFor(() => expect(where()).toBe('/reset-password'))
    await user.type(
      await screen.findByLabelText(bnText('auth.reset.newPassword')),
      'violet-harbor-lantern-91',
    )
    await user.click(screen.getByRole('button', { name: bnText('auth.reset.submit') }))
    expect(await screen.findByText(bnText('auth.reset.done'))).toBeInTheDocument()
    expect(body).toEqual({ new_password: 'violet-harbor-lantern-91', token: 'abcdefghijklmnop' })
  })

  it('reset with a bad link shows the invalid-link message', async () => {
    statefulAuth()
    server.use(http.post('*/api/v1/auth/password/reset', () => problem(400, 'reset_invalid')))
    const user = userEvent.setup()
    renderApp('/reset-password?token=abcdefghijklmnop')
    await user.type(
      await screen.findByLabelText(bnText('auth.reset.newPassword')),
      'violet-harbor-lantern-91',
    )
    await user.click(screen.getByRole('button', { name: bnText('auth.reset.submit') }))
    expect(await screen.findByRole('alert')).toHaveTextContent(bnText('auth.reset.invalidLink'))
  })

  it('accepting an invitation sends the token from the link and moves on to staff sign-in', async () => {
    statefulAuth()
    let body: Record<string, unknown> = {}
    server.use(
      http.post('*/api/v1/auth/register/staff', async ({ request }) => {
        body = (await request.json()) as Record<string, unknown>
        return HttpResponse.json({ status: 'created' }, { status: 201 })
      }),
    )
    const user = userEvent.setup()
    renderApp('/accept-invite?token=0123456789abcdefghij')
    await waitFor(() => expect(where()).toBe('/accept-invite'))
    await user.type(await screen.findByLabelText(bnText('auth.register.name')), 'নাদিয়া')
    await user.type(
      screen.getByLabelText(bnText('auth.register.password')),
      'a-long-passphrase-123',
    )
    await user.click(screen.getByRole('button', { name: bnText('auth.staff.submit') }))
    await waitFor(() => expect(where()).toBe('/staff'))
    expect(body).toMatchObject({ token: '0123456789abcdefghij', locale: 'bn' })
  })
})

describe('two-factor screens', () => {
  it('login TOTP accepts a code, then an alternative recovery code', async () => {
    const auth = statefulAuth()
    auth.signIn('ADMIN', 'totp')
    const bodies: Record<string, unknown>[] = []
    server.use(
      http.post('*/api/v1/auth/login/totp', async ({ request }) => {
        const b = (await request.json()) as Record<string, unknown>
        bodies.push(b)
        if (!b.recovery) return problem(400, 'totp_invalid')
        auth.signIn('ADMIN')
        return HttpResponse.json(reply('ADMIN'))
      }),
    )
    const user = userEvent.setup()
    renderApp('/login/totp')
    await user.type(await screen.findByLabelText(bnText('auth.totp.code')), '123456')
    await user.click(screen.getByRole('button', { name: bnText('auth.totp.submit') }))
    expect(await screen.findByRole('alert')).toHaveTextContent(bnText('auth.otp.wrong'))
    await user.click(screen.getByRole('button', { name: bnText('auth.totp.useRecovery') }))
    const field = screen.getByLabelText(bnText('auth.totp.recoveryCode'))
    await user.clear(field)
    await user.type(field, 'abcde-fghij')
    await user.click(screen.getByRole('button', { name: bnText('auth.totp.submit') }))
    await waitFor(() => expect(where()).toBe('/admin'))
    expect(bodies).toEqual([
      { code: '123456', recovery: false },
      { code: 'abcde-fghij', recovery: true },
    ])
  })

  it('setup shows the secret once, then the recovery codes with a warning', async () => {
    const auth = statefulAuth()
    auth.signIn('REVIEWER', 'setup_totp')
    server.use(
      http.post('*/api/v1/auth/totp/setup', () =>
        HttpResponse.json({ secret: 'JBSWY3DPEHPK3PXP', otpauth_uri: 'otpauth://totp/x' }),
      ),
      http.post('*/api/v1/auth/totp/confirm', () => {
        auth.signIn('REVIEWER')
        return HttpResponse.json({
          ...reply('REVIEWER'),
          recovery_codes: ['aaaaa-bbbbb', 'ccccc-ddddd'],
        })
      }),
    )
    const user = userEvent.setup()
    const { container } = renderApp('/setup-2fa')
    expect(await screen.findByTestId('totp-secret')).toHaveTextContent('JBSWY3DPEHPK3PXP')
    expect(await axe(container)).toHaveNoViolations()
    await user.type(screen.getByLabelText(bnText('auth.totp.setupConfirm')), '123456')
    await user.click(screen.getByRole('button', { name: bnText('auth.totp.submit') }))
    expect(await screen.findByText('aaaaa-bbbbb')).toBeInTheDocument()
    expect(screen.getByRole('alert')).toHaveTextContent(bnText('auth.totp.recoveryWarn'))
    await user.click(screen.getByRole('button', { name: bnText('auth.totp.recoveryDone') }))
    await waitFor(() => expect(where()).toBe('/review'))
  })
})

describe('demo picker and sessions', () => {
  it('opens a demo session for the chosen role after the proof-of-work check', async () => {
    const auth = statefulAuth()
    let body: Record<string, unknown> = {}
    server.use(
      http.post('*/api/v1/demo/session', async ({ request }) => {
        body = (await request.json()) as Record<string, unknown>
        auth.signIn('DEMO_REVIEWER')
        return HttpResponse.json(reply('DEMO_REVIEWER'), { status: 201 })
      }),
    )
    const user = userEvent.setup()
    const { container } = renderApp('/demo')
    const button = await screen.findByRole('button', { name: bnText('demoPicker.reviewer') })
    await waitFor(() => expect(button).toBeEnabled(), { timeout: 5000 })
    expect(await axe(container)).toHaveNoViolations()
    await user.click(button)
    await waitFor(() => expect(where()).toBe('/review'))
    expect(body.role).toBe('DEMO_REVIEWER')
    expect(typeof body.captcha).toBe('string')
  })

  it('the devices page lists sessions and can sign one out', async () => {
    const auth = statefulAuth()
    auth.signIn('FARMER')
    let revoked = ''
    const sessions = [
      {
        id: 's1',
        created_at: '2026-10-19T10:00:00Z',
        last_seen_at: '2026-10-19T11:00:00Z',
        device: 'Chrome',
        current: true,
      },
      {
        id: 's2',
        created_at: '2026-10-18T10:00:00Z',
        last_seen_at: '2026-10-18T11:00:00Z',
        device: 'Firefox on Android',
        current: false,
      },
    ]
    server.use(
      http.get('*/api/v1/me/sessions', () => HttpResponse.json({ sessions })),
      http.delete('*/api/v1/me/sessions/:id', ({ params }) => {
        revoked = String(params.id)
        sessions.pop()
        return new HttpResponse(null, { status: 204 })
      }),
    )
    const user = userEvent.setup()
    renderApp('/account/sessions')
    expect(await screen.findByText(bnText('auth.sessions.current'))).toBeInTheDocument()
    await user.click(await screen.findByRole('button', { name: bnText('auth.sessions.revoke') }))
    await waitFor(() => expect(revoked).toBe('s2'))
    await waitFor(() => expect(screen.queryByText('Firefox on Android')).not.toBeInTheDocument())
  })

  it('a 401 from an authenticated call sends the user to /login with the page to come back to', async () => {
    const auth = statefulAuth()
    auth.signIn('FARMER')
    server.use(http.get('*/api/v1/me/sessions', () => problem(401, 'authentication_required')))
    renderApp('/account/sessions')
    await waitFor(() => expect(where()).toContain('/login?return_to='))
    expect(decodeURIComponent(where() ?? '')).toContain('return_to=/account/sessions')
  })
})
