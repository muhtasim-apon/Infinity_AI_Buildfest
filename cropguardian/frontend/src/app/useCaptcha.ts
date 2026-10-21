import { useCallback, useEffect, useRef, useState } from 'react'
import { fetchAndSolve } from '../lib/captcha'

export type CaptchaStatus = 'idle' | 'solving' | 'ready' | 'failed'

interface Outcome {
  round: number
  status: 'ready' | 'failed'
}

/** Solves one proof-of-work challenge in the background; `consume()` hands out the token once. */
export function useCaptcha(enabled: boolean) {
  const token = useRef<string | null>(null)
  const [round, setRound] = useState(0)
  const [outcome, setOutcome] = useState<Outcome | null>(null)

  useEffect(() => {
    if (!enabled) return
    const controller = new AbortController()
    token.current = null
    fetchAndSolve(controller.signal)
      .then((payload) => {
        if (controller.signal.aborted) return
        token.current = payload
        setOutcome({ round, status: 'ready' })
      })
      .catch(() => {
        if (!controller.signal.aborted) setOutcome({ round, status: 'failed' })
      })
    return () => controller.abort()
  }, [enabled, round])

  // "solving" is derived: a result only counts for the round that produced it
  let status: CaptchaStatus = 'idle'
  if (enabled) status = outcome?.round === round ? outcome.status : 'solving'

  const consume = useCallback((): string | null => {
    const value = token.current
    token.current = null
    if (value) setRound((n) => n + 1) // a challenge works once: fetch the next one
    return value
  }, [])
  const retry = useCallback(() => setRound((n) => n + 1), [])
  return { status, consume, retry }
}
