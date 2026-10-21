import { execFileSync } from 'node:child_process'
import { createHmac, randomBytes } from 'node:crypto'
import { fileURLToPath } from 'node:url'
import { expect, test, type Browser, type Page } from '@playwright/test'

/**
 * Phase 1 journeys through Nginx (https://localhost) against the real compose stack: real CAPTCHA
 * proof-of-work, real console SMS (read from the API log), real TOTP codes computed from the secret
 * the page shows. Run after `make up` + migrate:  npx playwright test --project=chromium p1-identity
 */

const REPO = fileURLToPath(new URL('../..', import.meta.url))

function compose(...args: string[]): string {
  return execFileSync('docker', ['compose', ...args], { cwd: REPO, encoding: 'utf8', maxBuffer: 20_000_000 })
}

/** Dev stack only: forget rate-limit counters so repeated local runs are not throttled (5 registrations/hour/IP). */
function resetRateLimits(): void {
  compose(
    'exec', '-T', 'redis', 'sh', '-c',
    `redis-cli -a "$REDIS_PASSWORD" --no-auth-warning EVAL "for _,k in ipairs(redis.call('keys','cg:rl:*')) do redis.call('del',k) end for _,k in ipairs(redis.call('keys','cg:lf:*')) do redis.call('del',k) end return 1" 0`,
  )
}

function lastSmsCode(): string {
  const logs = compose('logs', '--no-color', '--tail', '400', 'api')
  const hits = [...logs.matchAll(/\[sms:console\] to=\S+ :: .*?(\d{6})/g)]
  if (hits.length === 0) throw new Error('no console SMS found in the API log')
  return hits[hits.length - 1]![1]!
}

function base32Decode(input: string): Buffer {
  const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567'
  let bits = ''
  for (const ch of input.replace(/=+$/, '')) bits += alphabet.indexOf(ch).toString(2).padStart(5, '0')
  const bytes: number[] = []
  for (let i = 0; i + 8 <= bits.length; i += 8) bytes.push(Number.parseInt(bits.slice(i, i + 8), 2))
  return Buffer.from(bytes)
}

function totp(secret: string, offsetSteps = 0): string {
  const counter = Math.floor(Date.now() / 1000 / 30) + offsetSteps
  const msg = Buffer.alloc(8)
  msg.writeBigUInt64BE(BigInt(counter))
  const hmac = createHmac('sha1', base32Decode(secret)).update(msg).digest()
  const offset = hmac[hmac.length - 1]! & 0xf
  const code = (hmac.readUInt32BE(offset) & 0x7fffffff) % 1_000_000
  return code.toString().padStart(6, '0')
}

const rand = (n = 6) => randomBytes(n).toString('hex')
const STRONG = `river-lantern-${rand(4)}-orchard`

async function registerFarmer(page: Page): Promise<string> {
  const phone = `017${Math.floor(Math.random() * 1e8).toString().padStart(8, '0')}`
  await page.goto('/register')
  await page.getByLabel('আপনার নাম').fill('রহিমা বেগম')
  await page.getByLabel('মোবাইল নম্বর').fill(phone)
  await page.getByLabel('পাসওয়ার্ড', { exact: true }).fill(STRONG)
  await page.getByRole('checkbox').first().check()
  const submit = page.getByRole('button', { name: 'নিবন্ধন করুন' })
  await expect(submit).toBeEnabled({ timeout: 20_000 }) // proof-of-work finished
  await submit.click()
  await expect(page).toHaveURL(/\/verify$/)
  await page.waitForTimeout(800)
  await page.getByLabel('৬ সংখ্যার কোড').fill(lastSmsCode())
  await page.getByRole('button', { name: 'যাচাই করুন' }).click()
  await expect(page).toHaveURL(/\/home$/)
  return phone
}

async function newPage(browser: Browser): Promise<Page> {
  const context = await browser.newContext({ ignoreHTTPSErrors: true })
  return context.newPage()
}

test.beforeEach(() => resetRateLimits())

test.describe('farmer', () => {
  test('registers with a real OTP, stays signed in across reload, and is kept out of the admin area', async ({ page }) => {
    await registerFarmer(page)
    await expect(page.getByRole('heading', { level: 1 })).toContainText('কৃষক')
    await page.reload()
    await expect(page).toHaveURL(/\/home$/)

    await page.goto('/admin')
    await expect(page.getByRole('heading', { level: 1 })).toContainText('পাওয়া যায়নি')
    const api = await page.request.get('/api/v1/admin/users')
    expect(api.status()).toBe(404)

    await page.goto('/review')
    await expect(page.getByRole('heading', { level: 1 })).toContainText('অনুমতি')
  })

  test('the admin bundle is never requested by a farmer', async ({ page }) => {
    const requested: string[] = []
    page.on('request', (r) => requested.push(r.url()))
    await registerFarmer(page)
    await page.goto('/admin')
    await page.waitForLoadState('networkidle')
    expect(requested.filter((u) => /AdminHome/.test(u))).toEqual([])
  })

  test('sign out everywhere ends the other browser session too', async ({ page, browser }) => {
    const phone = await registerFarmer(page)
    const other = await newPage(browser)
    await other.goto('/login')
    await other.getByLabel('ফোন নম্বর বা ইমেইল').fill(phone)
    await other.getByLabel('পাসওয়ার্ড', { exact: true }).fill(STRONG)
    await other.getByRole('button', { name: 'প্রবেশ করুন' }).click()
    await expect(other).toHaveURL(/\/home$/)

    await page.goto('/account/sessions')
    await page.getByRole('button', { name: 'সব ডিভাইস থেকে বের হন' }).click()
    await expect(page).toHaveURL(/\/$|\/login/)

    await other.goto('/home')
    await expect(other).toHaveURL(/\/login\?return_to=/)
    await other.context().close()
  })

  test('wrong password shows one uniform message', async ({ page }) => {
    await page.goto('/login')
    await page.getByLabel('ফোন নম্বর বা ইমেইল').fill(`017${Math.floor(Math.random() * 1e8).toString().padStart(8, '0')}`)
    await page.getByLabel('পাসওয়ার্ড', { exact: true }).fill('definitely-wrong-1')
    await page.getByRole('button', { name: 'প্রবেশ করুন' }).click()
    await expect(page.getByRole('alert')).toContainText('ঠিক নয়')
  })
})

test.describe('demo', () => {
  test('one click opens a demo role with the DEMO ribbon', async ({ page }) => {
    await page.goto('/demo')
    const reviewer = page.getByRole('button', { name: 'পর্যালোচক হিসেবে দেখুন' })
    await expect(reviewer).toBeEnabled({ timeout: 20_000 })
    await reviewer.click()
    await expect(page).toHaveURL(/\/review$/)
    await expect(page.getByText('ডেমো ডেটা')).toBeVisible()
  })
})

test.describe('staff', () => {
  test('forced two-factor setup, recovery codes, then the admin area (and its separate bundle)', async ({ page }) => {
    const email = `e2e-admin-${rand(3)}@example.org`
    const password = `Correct-Horse-${rand(6)}!`
    const out = compose('exec', '-T', '-e', `CG_ADMIN_PASSWORD=${password}`, 'api', 'python', 'scripts/create_admin.py', '--email', email, '--name', 'E2E Admin')
    expect(out).toContain('created ADMIN')

    const requested: string[] = []
    page.on('request', (r) => requested.push(r.url()))
    await page.goto('/staff')
    await page.getByLabel('ফোন নম্বর বা ইমেইল').fill(email)
    await page.getByLabel('পাসওয়ার্ড', { exact: true }).fill(password)
    await page.getByRole('button', { name: 'প্রবেশ করুন' }).click()
    await expect(page).toHaveURL(/\/setup-2fa$/)

    const secret = (await page.getByTestId('totp-secret').innerText()).trim()
    await page.getByLabel('অ্যাপের কোড দিয়ে নিশ্চিত করুন').fill(totp(secret))
    await page.getByRole('button', { name: 'নিশ্চিত করুন' }).click()
    await expect(page.getByText(/^[a-z0-9]{5}-[a-z0-9]{5}$/).first()).toBeVisible()
    await expect(page.locator('li', { hasText: /^[a-z0-9]{5}-[a-z0-9]{5}$/ })).toHaveCount(10)
    await page.getByRole('button', { name: 'আমি কোডগুলো রেখেছি' }).click()
    await expect(page).toHaveURL(/\/admin$/)
    await expect(page.getByRole('heading', { level: 1 })).toContainText('প্রশাসক')
    expect(requested.some((u) => /AdminHome/.test(u))).toBe(true)

    // the console API now answers; after sign-out the admin area is unreachable
    expect((await page.request.get('/api/v1/admin/users')).status()).toBe(200)
    await page.getByRole('button', { name: 'বের হন' }).click()
    await page.goto('/admin')
    await expect(page).toHaveURL(/\/login\?return_to=/)
  })
})

test.describe('small screens', () => {
  test('a very long Bangla name does not overflow a 360 px screen', async ({ browser }) => {
    const context = await browser.newContext({ ignoreHTTPSErrors: true, viewport: { width: 360, height: 640 } })
    const page = await context.newPage()
    await page.goto('/register')
    await page.getByLabel('আপনার নাম').fill('মোহাম্মদআবদুল্লাহআলমামুনআলমাহমুদচৌধুরীসিদ্দিকীরহমানখন্দকার'.repeat(2))
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth)
    expect(overflow).toBeLessThanOrEqual(0)
    await context.close()
  })
})
