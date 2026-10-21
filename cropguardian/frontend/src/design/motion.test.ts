import { describe, expect, it } from 'vitest'
import { MAX_CONTENT_DELAY, duration, listDelay, reducedMotionTransition, stagger } from './motion'

describe('motion tokens (spec 15.2)', () => {
  it('has the specified durations', () => {
    expect(duration).toEqual({ fast: 0.12, base: 0.2, slow: 0.32, page: 0.24 })
  })

  it('list stagger caps at 8 animated items and never delays content past 300 ms', () => {
    expect(listDelay(0)).toBe(0)
    expect(listDelay(100)).toBeCloseTo(stagger.maxAnimated * stagger.list)
    expect(listDelay(100)).toBeLessThanOrEqual(MAX_CONTENT_DELAY)
  })

  it('rejects invalid indexes', () => {
    expect(() => listDelay(-1)).toThrow(RangeError)
    expect(() => listDelay(1.5)).toThrow(RangeError)
    expect(() => listDelay(Number.NaN)).toThrow(RangeError)
  })

  it('reduced motion is a <=120 ms opacity-only transition', () => {
    expect(reducedMotionTransition.duration).toBeLessThanOrEqual(0.12)
  })
})
