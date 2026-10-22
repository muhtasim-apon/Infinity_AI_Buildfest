import { expect, test as base } from '@playwright/test'

/**
 * Shared fixtures for the layout / accessibility / visual specs.
 *
 * - `cspViolations`: every Content-Security-Policy violation the page reports. The production CSP is
 *   served by Nginx, so any inline script/style, blocked font or injected <style> shows up here
 *   (DECISIONS D-022, D-025). A spec that touches a page should end with
 *   `expect(cspViolations).toEqual([])`.
 * - `slow3g` project: Chromium DevTools "Slow 3G" (400 kbps both ways, 2 s round trip) via CDP.
 */
export const test = base.extend<{ cspViolations: string[] }>({
  cspViolations: async ({ page }, use) => {
    const violations: string[] = []
    await page.exposeFunction('__reportCsp', (detail: string) => violations.push(detail))
    await page.addInitScript(() => {
      document.addEventListener('securitypolicyviolation', (event) => {
        const report = (window as unknown as { __reportCsp: (d: string) => void }).__reportCsp
        report(`${event.violatedDirective} blocked ${event.blockedURI || 'inline'}`)
      })
    })
    await use(violations)
  },
  page: async ({ page, context }, use, testInfo) => {
    if (testInfo.project.name === 'slow3g') {
      const cdp = await context.newCDPSession(page)
      await cdp.send('Network.enable')
      await cdp.send('Network.emulateNetworkConditions', {
        offline: false,
        latency: 2000,
        downloadThroughput: (400 * 1024) / 8,
        uploadThroughput: (400 * 1024) / 8,
      })
    }
    await use(page)
  },
})

export { expect }
