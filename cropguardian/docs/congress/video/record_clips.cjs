// Record real screen clips of the LIVE app at phone size (390x844) with Playwright.
// Usage: node record_clips.cjs <out_dir> <photos_dir> [only=name,name]
// Every clip uses the real hosted app and real scans (demo tenant, labelled SIMULATED in the UI).
const path = require('path')
const fs = require('fs')
const { chromium } = require(path.resolve(__dirname, '../../../e2e/node_modules/@playwright/test'))

const BASE = process.env.APP_BASE || 'https://infinityaibuildfest-prototype-five.vercel.app'
const out = path.resolve(process.argv[2])
const photos = path.resolve(process.argv[3])
const only = (process.argv[4] || '').replace('only=', '').split(',').filter(Boolean)

async function demoLogin(page, role) {
  for (let attempt = 1; ; attempt++) {
    try { return await demoLoginOnce(page, role) } catch (e) { if (attempt >= 4) throw e; await page.waitForTimeout(1500) }
  }
}

async function demoLoginOnce(page, role) {
  await page.goto(BASE + '/demo')
  const status = await page.evaluate(async (role) => {
    const hex = async (s) => Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(s)))).map((b) => b.toString(16).padStart(2, '0')).join('')
    const csrf = (await (await fetch('/api/v1/auth/csrf', { credentials: 'include' })).json()).csrf_token
    const ch = await (await fetch('/api/v1/captcha/challenge', { credentials: 'include' })).json()
    let n = 0
    for (; n <= ch.maxnumber; n++) if ((await hex(ch.salt + n)) === ch.challenge) break
    const captcha = btoa(JSON.stringify({ challenge: ch.challenge, salt: ch.salt, signature: ch.signature, issued_at: ch.issued_at, expires_at: ch.expires_at, number: n, algorithm: ch.algorithm }))
    await new Promise((r) => setTimeout(r, 2300))
    const r = await fetch('/api/v1/demo/session', { method: 'POST', credentials: 'include', headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': csrf }, body: JSON.stringify({ role, captcha }) })
    return r.status === 201 ? 201 : r.status + ' ' + (await r.text()).slice(0, 200)
  }, role)
  if (status !== 201) throw new Error('demo login failed: ' + status)
}

async function smoothScroll(page, px, ms = 2500) {
  const steps = 40
  for (let i = 0; i < steps; i++) {
    await page.mouse.wheel(0, px / steps)
    await page.waitForTimeout(ms / steps)
  }
}

async function scanFlow(page, photo, meta) {
  await page.goto(BASE + '/app')
  await page.waitForTimeout(1800)
  await page.getByRole('link', { name: /ছবি তুলুন/ }).first().click()
  await page.waitForTimeout(1200)
  await page.locator('input[type=file]').nth(1).setInputFiles(photo)
  await page.waitForTimeout(1600)
  await page.getByRole('button', { name: 'রোগ পরীক্ষা করুন' }).click()
  await page.waitForURL(/\/app\/scan\/[0-9a-f-]{36}/, { timeout: 90000 })
  if (meta) meta.resultAt = (Date.now() - meta.t0) / 1000
  await page.waitForTimeout(2200)
  await smoothScroll(page, 900, 4000)
  await page.waitForTimeout(1500)
  await smoothScroll(page, 900, 4000)
  await page.waitForTimeout(1500)
}

const CLIPS = {
  scan: { role: 'DEMO_FARMER', run: (p, m) => scanFlow(p, path.join(photos, process.env.SCAN_PHOTO || 'blb_3.jpg'), m) },
  notsure: { role: 'DEMO_FARMER', run: (p, m) => scanFlow(p, path.join(photos, 'blurred.jpg'), m) },
  review: {
    role: 'DEMO_REVIEWER',
    run: async (p) => {
      await p.goto(BASE + '/review')
      await p.waitForTimeout(3500)
      await smoothScroll(p, 700, 4000)
      await p.waitForTimeout(2500)
      await smoothScroll(p, 700, 3000)
      await p.waitForTimeout(2000)
    },
  },
  trust: {
    role: null,
    run: async (p) => {
      await p.goto(BASE + '/trust')
      await p.waitForTimeout(3500)
      await smoothScroll(p, 1400, 6000)
      await p.waitForTimeout(1500)
      await smoothScroll(p, 1400, 6000)
      await p.waitForTimeout(1500)
    },
  },
}

;(async () => {
  fs.mkdirSync(out, { recursive: true })
  const browser = await chromium.launch()
  for (const [name, clip] of Object.entries(CLIPS)) {
    if (only.length && !only.includes(name)) continue
    // log in without recording, then reuse the cookies in a recorded context
    const auth = await browser.newContext({ viewport: { width: 390, height: 844 }, locale: 'bn-BD', colorScheme: 'light' })
    const ap = await auth.newPage()
    if (clip.role) await demoLogin(ap, clip.role)
    const state = await auth.storageState()
    await auth.close()
    const ctx = await browser.newContext({
      viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, locale: 'bn-BD', colorScheme: 'light',
      storageState: state, recordVideo: { dir: out, size: { width: 780, height: 1688 } },
    })
    const meta = { t0: Date.now() }
    const page = await ctx.newPage()
    try {
      await clip.run(page, meta)
      console.log(name, 'ok', page.url().replace(BASE, ''))
    } catch (e) {
      console.log(name, 'FAILED', e.message.split('\n')[0])
    }
    const v = page.video()
    await ctx.close()
    fs.renameSync(await v.path(), path.join(out, `${name}.webm`))
    fs.writeFileSync(path.join(out, `${name}.json`), JSON.stringify({ resultAt: meta.resultAt ?? null }))
  }
  await browser.close()
})().catch((e) => { console.error(e); process.exit(1) })
