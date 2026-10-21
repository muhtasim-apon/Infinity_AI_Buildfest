import '@testing-library/jest-dom/vitest'
import { cleanup } from '@testing-library/react'
import { afterAll, afterEach, beforeAll, expect } from 'vitest'
import * as axeMatchers from 'vitest-axe/matchers'
import { resetApiStateForTests } from '../src/lib/api'
import { server } from './msw'

expect.extend(axeMatchers)

// Any request a test did not expect is an error, so a missing handler never passes silently.
beforeAll(() => server.listen({ onUnhandledRequest: 'error' }))
afterEach(() => {
  cleanup()
  server.resetHandlers()
  resetApiStateForTests()
})
afterAll(() => server.close())
