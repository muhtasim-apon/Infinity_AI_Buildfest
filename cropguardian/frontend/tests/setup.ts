import '@testing-library/jest-dom/vitest'
import { cleanup } from '@testing-library/react'
import { afterAll, afterEach, beforeAll, expect } from 'vitest'
import * as axeMatchers from 'vitest-axe/matchers'
import { resetApiStateForTests } from '../src/lib/api'
import { server } from './msw'

expect.extend(axeMatchers)

// jsdom has neither matchMedia nor the <dialog> methods; the app feature-detects them (old browsers),
// tests install minimal behaviour-compatible versions so components run the same code path as real browsers.
if (typeof window !== 'undefined') {
  if (!window.matchMedia) {
    window.matchMedia = ((query: string) => ({
      matches: false,
      media: query,
      onchange: null,
      addEventListener: () => undefined,
      removeEventListener: () => undefined,
      addListener: () => undefined,
      removeListener: () => undefined,
      dispatchEvent: () => false,
    })) as typeof window.matchMedia
  }
  // Radix (slider, popper) and Framer (whileInView) observe layout; jsdom has no layout engine.
  const globals = window as unknown as Record<string, unknown>
  if (!globals.ResizeObserver) {
    globals.ResizeObserver = class {
      observe() {}
      unobserve() {}
      disconnect() {}
    }
  }
  if (!globals.IntersectionObserver) {
    globals.IntersectionObserver = class {
      readonly root = null
      readonly rootMargin = ''
      readonly thresholds = []
      observe() {}
      unobserve() {}
      disconnect() {}
      takeRecords() {
        return []
      }
    }
  }
  const elementProto = window.HTMLElement.prototype
  if (!elementProto.hasPointerCapture) elementProto.hasPointerCapture = () => false
  if (!elementProto.setPointerCapture) elementProto.setPointerCapture = () => undefined
  if (!elementProto.releasePointerCapture) elementProto.releasePointerCapture = () => undefined
  if (!elementProto.scrollIntoView) elementProto.scrollIntoView = () => undefined
  const proto = window.HTMLDialogElement?.prototype
  if (proto && typeof proto.showModal !== 'function') {
    proto.showModal = function showModal(this: HTMLDialogElement) {
      this.setAttribute('open', '')
    }
    proto.close = function close(this: HTMLDialogElement) {
      if (!this.hasAttribute('open')) return
      this.removeAttribute('open')
      this.dispatchEvent(new Event('close'))
    }
  }
}

// Any request a test did not expect is an error, so a missing handler never passes silently.
beforeAll(() => server.listen({ onUnhandledRequest: 'error' }))
afterEach(() => {
  cleanup()
  server.resetHandlers()
  resetApiStateForTests()
})
afterAll(() => server.close())
