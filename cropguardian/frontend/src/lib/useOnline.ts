import { useEffect, useState } from 'react'

/**
 * Live `navigator.onLine`. The browser only knows "has a network interface", not "can reach our
 * server", so this drives gentle UI (a banner, queued photos) and never blocks an action: every
 * request still handles its own failure (spec 15.9 fetch wrapper).
 */
export function useOnline(): boolean {
  const [online, setOnline] = useState(() =>
    typeof navigator === 'undefined' ? true : navigator.onLine,
  )
  useEffect(() => {
    const on = () => setOnline(true)
    const off = () => setOnline(false)
    window.addEventListener('online', on)
    window.addEventListener('offline', off)
    return () => {
      window.removeEventListener('online', on)
      window.removeEventListener('offline', off)
    }
  }, [])
  return online
}

/** `Date.now()` that re-renders every `everyMs` (a countdown that does not need second precision). */
export function useNow(everyMs: number): number {
  const [now, setNow] = useState(() => Date.now())
  useEffect(() => {
    const id = window.setInterval(() => setNow(Date.now()), everyMs)
    return () => window.clearInterval(id)
  }, [everyMs])
  return now
}
