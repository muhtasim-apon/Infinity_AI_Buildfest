import { useReducedMotion, type Variants } from 'framer-motion'
import { useEffect, useState } from 'react'
import { useUiPrefs } from '../lib/uiPrefs'
import { reducedVariants } from './variants'

interface NetworkInformationLike {
  saveData?: boolean
}
interface BatteryLike {
  level: number
  charging: boolean
  addEventListener: (type: string, fn: () => void) => void
  removeEventListener: (type: string, fn: () => void) => void
}
type NavigatorWithHints = Navigator & {
  connection?: NetworkInformationLike
  getBattery?: () => Promise<BatteryLike>
}

/** Below this battery level (and not charging) looping animations stop (spec 15.2). */
export const LOW_BATTERY_LEVEL = 0.2

export function dataSaverOn(nav: NavigatorWithHints = navigator): boolean {
  return nav.connection?.saveData === true
}

/** True while the battery is low and not charging; false where the Battery API does not exist. */
export function useLowBattery(): boolean {
  const [low, setLow] = useState(false)
  useEffect(() => {
    const nav = navigator as NavigatorWithHints
    if (typeof nav.getBattery !== 'function') return
    let alive = true
    let battery: BatteryLike | undefined
    const update = () => {
      if (battery && alive) setLow(!battery.charging && battery.level < LOW_BATTERY_LEVEL)
    }
    nav
      .getBattery()
      .then((b) => {
        battery = b
        update()
        b.addEventListener('levelchange', update)
        b.addEventListener('chargingchange', update)
      })
      .catch(() => undefined) // Battery API refused (permissions policy): treat as unknown
    return () => {
      alive = false
      battery?.removeEventListener('levelchange', update)
      battery?.removeEventListener('chargingchange', update)
    }
  }, [])
  return low
}

export interface MotionPolicy {
  /** No transforms, scale, shimmer, sweeps, pulses or count-ups: opacity fades of <= 120 ms only. */
  reduced: boolean
  /** Looping animations (breathing ring, pulses, shimmer) may run. */
  loopsAllowed: boolean
  /** Pick the variant set for the current policy. */
  pick: (variants: Variants) => Variants
}

/**
 * One answer to "may this animate?": OS preference, the in-app setting, data saver and low battery.
 * Reduced motion is OS or in-app; data saver and low battery only stop the looping animations.
 */
export function useMotionPolicy(): MotionPolicy {
  const os = useReducedMotion() === true
  const [prefs] = useUiPrefs()
  const lowBattery = useLowBattery()
  const reduced = os || prefs.reducedMotion
  const loopsAllowed = !reduced && !dataSaverOn() && !lowBattery
  return { reduced, loopsAllowed, pick: (v) => (reduced ? reducedVariants(v) : v) }
}
