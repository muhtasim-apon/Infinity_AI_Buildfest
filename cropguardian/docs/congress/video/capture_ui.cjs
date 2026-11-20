// Capture REAL screenshots (and one screen recording) of the LIVE app for the v2 pitch video.
// Usage: node capture_ui.cjs <out_dir> <photos_dir>
// Real hosted app, real scans on the demo tenant (the UI labels them SIMULATED / DEMO DATA).
const path = require('path')
const fs = require('fs')
const { chromium } = require(path.resolve(__dirname, '../../../e2e/node_modules/@playwright/test'))

const BASE = process.env.APP_BASE || 'https://infinityaibuildfest-prototype-five.vercel.app'
const out = path.resolve(process.argv[2])
const photos = path.resolve(process.argv[3])
const DIAG = process.env.DIAG_PHOTO || 'brownspot_3.jpg'
const UNSURE = process.env.UNSURE_PHOTO || 'blurred.jpg'

async function demoLogin(page) {
  for (let attempt = 1; attempt <= 4; attempt++) {
    await page.goto(BASE + '/demo')
    const status = await page.evaluate(async () => {
      const hex = async (s) => Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(s)))).map((b) => b.toString(16).padStart(2, '0')).join('')
      const csrf = (await (await fetch('/api/v1/auth/csrf', { credentials: 'include' })).json()).csrf_token
      const ch = await (await fetch('/api/v1/captcha/challenge', { credentials: 'include' })).json()
      let n = 0
      for (; n <= ch.maxnumber; n++) if ((await hex(ch.salt + n)) === ch.challenge) break
      const captcha = btoa(JSON.stringify({ challenge: ch.challenge, salt: ch.salt, signature: ch.signature, issued_at: ch.issued_at, expires_at: ch.expires_at, number: n, algorithm: ch.algorithm }))
      await new Promise((r) => setTimeout(r, 2300))
      const r = await fetch('/api/v1/demo/session', { method: 'POST', credentials: 'include', headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': csrf }, body: JSON.stringify({ role: 'DEMO_FARMER', captcha }) })
      return r.status
    })
    if (status === 201) return
    await page.waitForTimeout(1500)
  }
  throw new Error('demo login failed')
}

const shot = (page, name) => page.screenshot({ path: path.join(out, name + '.png') })

async function scan(page, photo, prefix, meta, want) {
  await page.goto(BASE + '/app')
  await page.waitForTimeout(2500)
  await page.getByRole('link', { name: /ছবি তুলুন/ }).first().click()
  await page.waitForTimeout(1500)
  await shot(page, prefix + '_1_capture')
  await page.locator('input[type=file]').nth(1).setInputFiles(photo)
  await page.waitForTimeout(1800)
  await shot(page, prefix + '_2_selected')
  await page.getByRole('button', { name: 'রোগ পরীক্ষা করুন' }).click()
  await page.waitForTimeout(1200)
  await shot(page, prefix + '_3_analyzing')
  await page.waitForURL(/\/app\/scan\/[0-9a-f-]{36}/, { timeout: 120000 })
  if (meta) meta.resultAt = (Date.now() - meta.t0) / 1000
  const id = page.url().split('/').pop()
  const status = await page.evaluate(async (id) => (await (await fetch('/api/v1/scans/' + id, { credentials: 'include' })).json()).status, id)
  if (want && status !== want) return { url: page.url(), status }
  await page.waitForTimeout(2500)
  await shot(page, prefix + '_4_result')
  for (let i = 1; i <= 4; i++) {
    await page.mouse.wheel(0, 700)
    await page.waitForTimeout(900)
    await shot(page, `${prefix}_5_result_s${i}`)
  }
  return { url: page.url(), status }
}

/** The model's answer varies run to run: repeat the real flow until it gives the outcome to show. */
async function scanUntil(page, photo, prefix, want, meta) {
  for (let i = 1; i <= 4; i++) {
    if (meta) meta.t0 = Date.now()
    const r = await scan(page, photo, prefix, meta, want)
    console.log(prefix, 'attempt', i, r.status)
    if (r.status === want) return r.url
  }
  throw new Error(prefix + ': never got ' + want)
}

;(async () => {
  fs.mkdirSync(out, { recursive: true })
  const browser = await chromium.launch()
  const auth = await browser.newContext({ viewport: { width: 390, height: 844 }, locale: 'bn-BD', colorScheme: 'light' })
  const ap = await auth.newPage()
  await demoLogin(ap)
  const state = await auth.storageState()
  await auth.close()

  // stills
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 3, locale: 'bn-BD', colorScheme: 'light', storageState: state })
  const p = await ctx.newPage()
  await p.goto(BASE + '/app')
  await p.waitForTimeout(5000)
  await shot(p, 'home')
  const diagUrl = await scanUntil(p, path.join(photos, DIAG), 'diag', 'diagnosed')
  const unsureUrl = await scanUntil(p, path.join(photos, UNSURE), 'unsure', 'not_sure')
  await p.goto(BASE + '/app/history')
  await p.waitForTimeout(3000)
  await shot(p, 'history')
  await ctx.close()

  // one real-time screen recording of the full scan flow (for the holographic panels)
  const rec = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, locale: 'bn-BD', colorScheme: 'light', storageState: state, recordVideo: { dir: out, size: { width: 780, height: 1688 } } })
  const rp = await rec.newPage()
  const meta = { t0: Date.now() }
  // record attempts until one shows a real diagnosis; keep only that recording
  let v = null
  const recStart = meta.t0
  for (let i = 1; i <= 4; i++) {
    meta.attemptAt = (Date.now() - recStart) / 1000 // seconds into the recording where this attempt starts
    meta.t0 = recStart
    const r = await scan(rp, path.join(photos, DIAG), 'rec', meta, 'diagnosed')
    console.log('rec attempt', i, r.status)
    if (r.status === 'diagnosed') break
  }
  v = rp.video()
  await rec.close()
  fs.renameSync(await v.path(), path.join(out, 'scanflow.webm'))
  fs.writeFileSync(path.join(out, 'meta.json'), JSON.stringify({ diagUrl, unsureUrl, attemptAt: meta.attemptAt, resultAt: meta.resultAt }, null, 2))
  await browser.close()
  console.log('captured', diagUrl.replace(BASE, ''), unsureUrl.replace(BASE, ''), 'resultAt', meta.resultAt)
})().catch((e) => { console.error(e); process.exit(1) })
