/**
 * Motion system (spec 15.2). The ONLY place durations and easings are defined; an ESLint rule
 * forbids numeric animation durations elsewhere. Durations are in seconds (Framer Motion units).
 * Framer Motion itself is added in Phase 2 when components land; these tokens are library-free.
 */

export const duration = { fast: 0.12, base: 0.2, slow: 0.32, page: 0.24 } as const

export const ease = {
  standard: [0.2, 0, 0, 1],
  emphasized: [0.3, 0, 0, 1],
  exit: [0.4, 0, 1, 1],
} as const

export const spring = { soft: { type: 'spring', stiffness: 260, damping: 26 } } as const

export const stagger = { list: 0.035, maxAnimated: 8 } as const

/** Reduced motion: opacity fades of at most 120 ms, no transforms (spec 15.2). */
export const reducedMotionTransition = { duration: duration.fast, ease: ease.standard } as const

export function listDelay(index: number): number {
  if (!Number.isInteger(index) || index < 0)
    throw new RangeError('index must be a non-negative integer')
  return Math.min(index, stagger.maxAnimated) * stagger.list
}

/** Motion never delays content by more than this (spec 15.2). */
export const MAX_CONTENT_DELAY = 0.3
