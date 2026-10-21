import { createHash } from 'node:crypto'
import { http, HttpResponse } from 'msw'
import { setupServer } from 'msw/node'

/** A solvable proof-of-work challenge with a tiny search space, issued 10 s ago (min wait already passed). */
export function makeChallenge(number = 7) {
  const salt = 'cafebabe'
  const issued = Math.floor(Date.now() / 1000) - 10
  return {
    algorithm: 'SHA-256',
    challenge: createHash('sha256').update(`${salt}${number}`).digest('hex'),
    salt,
    signature: 'sig',
    maxnumber: 50,
    issued_at: issued,
    expires_at: issued + 300,
  }
}

export const CONSENTS = {
  version: 'consent-v1',
  consents: [
    {
      purpose: 'service',
      required: true,
      default_granted: false,
      title: { bn: 'সেবার জন্য প্রয়োজনীয় তথ্য', en: 'Information needed for the service' },
      body: { bn: 'ছবি ও এলাকার তথ্য ব্যবহার করা হবে।', en: 'Photos and area are used.' },
    },
    {
      purpose: 'training_use',
      required: false,
      default_granted: false,
      title: { bn: 'মডেল উন্নত করতে ছবি ব্যবহার', en: 'Using photos to improve the model' },
      body: { bn: 'এটি ঐচ্ছিক।', en: 'This is optional.' },
    },
  ],
}

export const anonymousState = { authenticated: false, csrf_token: 'csrf-anon' }

export function signedIn(role: string, next = 'home', name = 'Rahima') {
  return {
    authenticated: true,
    next,
    role,
    tenant: role.startsWith('DEMO_') ? 'demo' : 'real',
    display_name: name,
    locale: 'bn',
    step_up: false,
    csrf_token: 'csrf-session',
  }
}

export const defaultHandlers = [
  http.get('*/api/v1/auth/csrf', () => HttpResponse.json({ csrf_token: 'csrf-1' })),
  http.get('*/api/v1/auth/state', () => HttpResponse.json(anonymousState)),
  http.get('*/api/v1/captcha/challenge', () => HttpResponse.json(makeChallenge())),
  http.get('*/api/v1/consents/texts', () => HttpResponse.json(CONSENTS)),
]

export const server = setupServer(...defaultHandlers)

export function problem(
  status: number,
  code: string,
  extra: Record<string, unknown> = {},
  headers = {},
) {
  return HttpResponse.json(
    {
      type: `https://cropguardian.invalid/problems/${code}`,
      title: 'x',
      status,
      code,
      request_id: 'req-123',
      ...extra,
    },
    { status, headers: { 'Content-Type': 'application/problem+json', ...headers } },
  )
}
