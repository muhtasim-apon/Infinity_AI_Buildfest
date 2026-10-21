/**
 * Proof-of-work CAPTCHA solver (ALTCHA style, spec 16.15). Runs in the page with WebCrypto; no third
 * party, no tracking. It slows scripted abuse; it is not a test of being human.
 */

import { api } from './api'

export interface CaptchaChallenge {
  algorithm: string
  challenge: string
  salt: string
  signature: string
  maxnumber: number
  issued_at: number
  expires_at: number
}

async function sha256Hex(text: string): Promise<string> {
  const digest = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(text))
  return Array.from(new Uint8Array(digest), (b) => b.toString(16).padStart(2, '0')).join('')
}

/** Find the number whose hash matches, then return the base64 payload the server expects. */
export async function solveChallenge(ch: CaptchaChallenge, signal?: AbortSignal): Promise<string> {
  for (let n = 0; n <= ch.maxnumber; n += 1) {
    if (signal?.aborted) throw new DOMException('aborted', 'AbortError')
    if ((await sha256Hex(`${ch.salt}${n}`)) === ch.challenge) {
      const payload = {
        challenge: ch.challenge,
        salt: ch.salt,
        signature: ch.signature,
        issued_at: ch.issued_at,
        expires_at: ch.expires_at,
        number: n,
      }
      return btoa(JSON.stringify(payload))
    }
    // yield now and then so the UI stays responsive
    if (n % 500 === 0) await new Promise((resolve) => setTimeout(resolve, 0))
  }
  throw new Error('captcha-unsolvable')
}

export async function fetchAndSolve(signal?: AbortSignal): Promise<string> {
  const challenge = await api.get<CaptchaChallenge>('/api/v1/captcha/challenge', {
    signal,
    quiet401: true,
  })
  // The server requires >= 2 s between issue and submit; solving usually takes less, so wait out the rest.
  const solved = await solveChallenge(challenge, signal)
  const wait = challenge.issued_at + 2 - Date.now() / 1000
  if (wait > 0) await new Promise((resolve) => setTimeout(resolve, Math.ceil(wait * 1000)))
  return solved
}
