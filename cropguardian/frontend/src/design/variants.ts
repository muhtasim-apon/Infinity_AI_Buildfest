/**
 * Reusable Framer Motion variants (spec 15.2 catalogue). Nothing animates outside this list, and
 * every number comes from motion.ts. `reducedVariants` turns any variant set into the reduced-motion
 * version: opacity only, at most 120 ms, no transforms.
 */

import type { Transition, Variants } from 'framer-motion'
import { duration, ease, reducedMotionTransition, spring, stagger } from './motion'

const standard: Transition = { duration: duration.base, ease: ease.standard }

/** Cards, list rows, sections: fade + 10 px rise, 200 ms. */
export const fadeRise: Variants = {
  hidden: { opacity: 0, y: 10 },
  show: { opacity: 1, y: 0, transition: standard },
}

/** Page content: fade + 8 px rise, 240 ms (the shell stays static). */
export const pageEnter: Variants = {
  hidden: { opacity: 0, y: 8 },
  show: { opacity: 1, y: 0, transition: { duration: duration.page, ease: ease.standard } },
}

/** Farmer app scan -> result: horizontal slide of 16 px. */
export const slideX: Variants = {
  hidden: { opacity: 0, x: 16 },
  show: { opacity: 1, x: 0, transition: { duration: duration.page, ease: ease.standard } },
}

/** Dialog panel: scale 0.96 -> 1 + fade; the overlay fade is plain opacity. */
export const dialogPanel: Variants = {
  hidden: { opacity: 0, scale: 0.96 },
  show: { opacity: 1, scale: 1, transition: standard },
}

/** Bottom sheet (mobile): slides up with the soft spring. */
export const sheetBottom: Variants = {
  hidden: { opacity: 0, y: 48 },
  show: { opacity: 1, y: 0, transition: spring.soft },
}

/** Side sheet: slides in from the edge. */
export const sheetSide: Variants = {
  hidden: { opacity: 0, x: -24 },
  show: { opacity: 1, x: 0, transition: spring.soft },
}

/** Toast: rises from the bottom and fades. */
export const toastSlide: Variants = {
  hidden: { opacity: 0, y: 16 },
  show: { opacity: 1, y: 0, transition: standard },
}

/** Staggered lists: at most `stagger.maxAnimated` rows animate, 35 ms apart. */
export const listContainer: Variants = {
  hidden: {},
  show: { transition: { staggerChildren: stagger.list } },
}

/** Count badge bump (outbox): scale 0.6 -> 1 with the soft spring. */
export const badgeBump: Variants = {
  hidden: { scale: 0.6 },
  show: { scale: 1, transition: spring.soft },
}

/** Form error: the field shakes 4 px twice (150 ms). */
export const fieldShake: Variants = {
  idle: { x: 0 },
  shake: { x: [0, -4, 4, -4, 4, 0], transition: { duration: duration.shake, ease: ease.standard } },
}

const TRANSFORM_KEYS = new Set([
  'x',
  'y',
  'scale',
  'rotate',
  'rotateX',
  'rotateY',
  'skewX',
  'skewY',
])

/** Keep only opacity in every state and swap the transition for the reduced-motion fade. */
export function reducedVariants(variants: Variants): Variants {
  const out: Variants = {}
  for (const [name, state] of Object.entries(variants)) {
    if (typeof state !== 'object' || state === null) {
      out[name] = state
      continue
    }
    const kept: Record<string, unknown> = {}
    for (const [key, value] of Object.entries(state)) {
      if (key === 'transition') continue
      if (TRANSFORM_KEYS.has(key)) continue
      kept[key] = value
    }
    out[name] = { ...kept, transition: reducedMotionTransition }
  }
  return out
}
