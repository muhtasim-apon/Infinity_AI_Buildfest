import { renderHook } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { resetPrefsForTests, setPrefs } from '../lib/uiPrefs'
import { LOW_BATTERY_LEVEL, dataSaverOn, useMotionPolicy } from './useMotion'
import { duration, reducedMotionTransition } from './motion'
import * as variants from './variants'
import { reducedVariants } from './variants'

const TRANSFORMS = ['x', 'y', 'scale', 'rotate', 'rotateX', 'rotateY']

describe('variants (spec 15.2 catalogue)', () => {
  it('every entrance variant starts invisible and ends fully visible', () => {
    for (const v of [
      variants.fadeRise,
      variants.pageEnter,
      variants.slideX,
      variants.dialogPanel,
      variants.sheetBottom,
      variants.sheetSide,
      variants.toastSlide,
    ]) {
      expect(v.hidden).toMatchObject({ opacity: 0 })
      expect(v.show).toMatchObject({ opacity: 1 })
    }
  })

  it('uses the spec offsets: cards rise 10 px, pages 8 px, farmer slide 16 px, dialog scales from 0.96', () => {
    expect(variants.fadeRise.hidden).toMatchObject({ y: 10 })
    expect(variants.pageEnter.hidden).toMatchObject({ y: 8 })
    expect(variants.slideX.hidden).toMatchObject({ x: 16 })
    expect(variants.dialogPanel.hidden).toMatchObject({ scale: 0.96 })
  })

  it('the field shake lasts the shake token (150 ms) and moves 4 px each way', () => {
    const shake = variants.fieldShake.shake as { x: number[]; transition: { duration: number } }
    expect(shake.transition.duration).toBe(duration.shake)
    expect(Math.max(...shake.x.map(Math.abs))).toBe(4)
  })
})

describe('reducedVariants', () => {
  it('keeps opacity, drops every transform, and uses the <=120 ms fade', () => {
    for (const v of Object.values(variants).filter((x) => typeof x === 'object')) {
      const reduced = reducedVariants(v as never)
      for (const state of Object.values(reduced)) {
        const s = state as Record<string, unknown>
        for (const key of TRANSFORMS) expect(s).not.toHaveProperty(key)
        expect(s.transition).toBe(reducedMotionTransition)
      }
    }
    expect(reducedVariants(variants.fadeRise).show).toMatchObject({ opacity: 1 })
    expect(reducedMotionTransition.duration).toBeLessThanOrEqual(0.12)
  })

  it('passes non-object variant values through untouched', () => {
    expect(reducedVariants({ a: 'label' as never }).a).toBe('label')
  })
})

describe('useMotionPolicy', () => {
  beforeEach(() => {
    window.localStorage.clear()
    resetPrefsForTests()
  })
  afterEach(() => vi.restoreAllMocks())

  it('allows motion and loops by default', () => {
    const { result } = renderHook(() => useMotionPolicy())
    expect(result.current.reduced).toBe(false)
    expect(result.current.loopsAllowed).toBe(true)
    expect(result.current.pick(variants.fadeRise)).toBe(variants.fadeRise)
  })

  it('the in-app setting disables transforms and loops', () => {
    setPrefs({ reducedMotion: true })
    const { result } = renderHook(() => useMotionPolicy())
    expect(result.current.reduced).toBe(true)
    expect(result.current.loopsAllowed).toBe(false)
    expect(result.current.pick(variants.fadeRise).hidden).not.toHaveProperty('y')
  })

  it('data saver stops loops but keeps one-shot motion', () => {
    Object.defineProperty(navigator, 'connection', {
      value: { saveData: true },
      configurable: true,
    })
    const { result } = renderHook(() => useMotionPolicy())
    expect(dataSaverOn()).toBe(true)
    expect(result.current.reduced).toBe(false)
    expect(result.current.loopsAllowed).toBe(false)
    Object.defineProperty(navigator, 'connection', { value: undefined, configurable: true })
  })

  it('low battery stops loops; a refused Battery API is treated as unknown', async () => {
    expect(LOW_BATTERY_LEVEL).toBe(0.2)
    const battery = {
      level: 0.1,
      charging: false,
      addEventListener: () => undefined,
      removeEventListener: () => undefined,
    }
    Object.defineProperty(navigator, 'getBattery', {
      value: () => Promise.resolve(battery),
      configurable: true,
    })
    const low = renderHook(() => useMotionPolicy())
    await vi.waitFor(() => expect(low.result.current.loopsAllowed).toBe(false))

    Object.defineProperty(navigator, 'getBattery', {
      value: () => Promise.reject(new Error('blocked')),
      configurable: true,
    })
    const refused = renderHook(() => useMotionPolicy())
    await Promise.resolve()
    expect(refused.result.current.loopsAllowed).toBe(true)
    Object.defineProperty(navigator, 'getBattery', { value: undefined, configurable: true })
  })
})
