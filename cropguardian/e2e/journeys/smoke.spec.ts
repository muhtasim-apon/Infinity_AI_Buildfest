import { expect, test } from '@playwright/test'

// Phase 0 smoke through Nginx: page loads, Bangla heading renders, no console errors and no
// requests to external origins (self-hosted fonts, strict CSP).
test('placeholder loads through nginx with no console errors or external requests', async ({
  page,
  baseURL,
}) => {
  const errors: string[] = []
  const external: string[] = []
  const origin = new URL(baseURL ?? 'https://localhost').origin
  page.on('console', (m) => m.type() === 'error' && errors.push(m.text()))
  page.on('request', (r) => {
    const u = new URL(r.url())
    if (u.protocol.startsWith('http') && u.origin !== origin) external.push(r.url())
  })
  const response = await page.goto('/')
  expect(response?.status()).toBe(200)
  await expect(page.getByRole('heading', { level: 1 })).toContainText('ফসল রক্ষী')
  const headers = response?.headers() ?? {}
  expect(headers['content-security-policy']).toContain("default-src 'self'")
  expect(headers['x-frame-options']).toBe('DENY')
  expect(errors).toEqual([])
  expect(external).toEqual([])
})
