import { describe, expect, it } from 'vitest'
import { makeChallenge } from '../../tests/msw'
import { solveChallenge } from './captcha'

describe('proof-of-work solver', () => {
  it('finds the number and returns the base64 payload the server verifies', async () => {
    const ch = makeChallenge(23)
    const payload = JSON.parse(atob(await solveChallenge(ch)))
    expect(payload).toMatchObject({
      number: 23,
      salt: ch.salt,
      challenge: ch.challenge,
      signature: ch.signature,
      issued_at: ch.issued_at,
      expires_at: ch.expires_at,
    })
  })

  it('gives up cleanly when the challenge cannot be solved', async () => {
    const ch = { ...makeChallenge(7), maxnumber: 3 }
    await expect(solveChallenge(ch)).rejects.toThrow('captcha-unsolvable')
  })

  it('stops when aborted', async () => {
    const controller = new AbortController()
    controller.abort()
    await expect(solveChallenge(makeChallenge(40), controller.signal)).rejects.toMatchObject({
      name: 'AbortError',
    })
  })
})
