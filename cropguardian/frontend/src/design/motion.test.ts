import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'
import {
  MAX_CONTENT_DELAY,
  TOAST_DISMISS_MS,
  duration,
  ease,
  listDelay,
  reducedMotionTransition,
  stagger,
} from './motion'

describe('motion tokens (spec 15.2)', () => {
  it('has the specified durations', () => {
    expect(duration).toEqual({
      press: 0.08,
      fast: 0.12,
      shake: 0.15,
      base: 0.2,
      slow: 0.32,
      page: 0.24,
      reveal: 0.4,
      draw: 0.6,
    })
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

  it('tokens.css mirrors the duration and easing tokens (no drift)', () => {
    const css = readFileSync(resolve(__dirname, 'tokens.css'), 'utf8')
    for (const [name, seconds] of Object.entries(duration)) {
      expect(css).toContain(`--duration-${name}: ${Math.round(seconds * 1000)}ms;`)
    }
    const bez = (e: readonly number[]) => `cubic-bezier(${e.join(', ')})`
    expect(css).toContain(`--ease-standard: ${bez(ease.standard)};`)
    expect(css).toContain(`--ease-emphasized: ${bez(ease.emphasized)};`)
    expect(css).toContain(`--ease-exit: ${bez(ease.exit)};`)
  })

  it('toasts auto-dismiss after 5 seconds', () => {
    expect(TOAST_DISMISS_MS).toBe(5000)
  })
})
