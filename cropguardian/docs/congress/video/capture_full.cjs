// Tall full-page captures of LIVE app screens, split into: fixed header, scrollable content, fixed
// bottom bar. The film scrolls the content between the fixed bars like a real phone.
// Usage: node capture_full.cjs <ui_dir>   (reads meta.json written by capture_ui.cjs)
const path = require('path')
const fs = require('fs')
const { chromium } = require(path.resolve(__dirname, '../../../e2e/node_modules/@playwright/test'))

const BASE = process.env.APP_BASE || 'https://infinityaibuildfest-prototype-five.vercel.app'
const dir = path.resolve(process.argv[2])
const meta = JSON.parse(fs.readFileSync(path.join(dir, 'meta.json'), 'utf8'))

async function demoLogin(page) {
  for (let a = 1; a <= 4; a++) {
    try {
      return await demoLoginOnce(page)
    } catch (e) {
      if (a === 4) throw e
      await page.waitForTimeout(2000)
    }
  }
}

async function demoLoginOnce(page) {
  await page.goto(BASE + '/demo')
  const st = await page.evaluate(async () => {
    const hex = async (s) => Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(s)))).map((b) => b.toString(16).padStart(2, '0')).join('')
    const csrf = (await (await fetch('/api/v1/auth/csrf', { credentials: 'include' })).json()).csrf_token
    const ch = await (await fetch('/api/v1/captcha/challenge', { credentials: 'include' })).json()
    let n = 0
    for (; n <= ch.maxnumber; n++) if ((await hex(ch.salt + n)) === ch.challenge) break
    const captcha = btoa(JSON.stringify({ challenge: ch.challenge, salt: ch.salt, signature: ch.signature, issued_at: ch.issued_at, expires_at: ch.expires_at, number: n, algorithm: ch.algorithm }))
    await new Promise((r) => setTimeout(r, 2300))
    return (await fetch('/api/v1/demo/session', { method: 'POST', credentials: 'include', headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': csrf }, body: JSON.stringify({ role: 'DEMO_FARMER', captcha }) })).status
  })
  if (st !== 201) throw new Error('login ' + st)
}

// The demo farmer is a shared demo account, so the scans capture_ui.cjs created are in its history.
async function grab(page, url, name) {
  await page.goto(url)
  await page.waitForTimeout(3500)
  await page.evaluate(() => window.scrollTo(0, 0))
  await page.waitForTimeout(600)
  // fixed parts
  const header = page.locator('div.sticky').first()
  const nav = page.locator('nav').last()
  const hb = await header.boundingBox().catch(() => null)
  const nb = await nav.boundingBox().catch(() => null)
  if (hb) await page.screenshot({ path: path.join(dir, `${name}_header.png`), clip: { x: 0, y: 0, width: 390, height: hb.y + hb.height } })
  if (nb) await page.screenshot({ path: path.join(dir, `${name}_nav.png`), clip: { x: 0, y: nb.y - 8, width: 390, height: 844 - nb.y + 8 }, omitBackground: true })
  // content without the fixed bars
  // CSSOM styles (the app's CSP blocks injected <style> tags, by design)
  await page.evaluate(() => {
    document.querySelectorAll('div.sticky').forEach((e) => (e.style.visibility = 'hidden'))
    document.querySelectorAll('nav').forEach((e) => {
      if (getComputedStyle(e).position === 'fixed') e.style.display = 'none'
    })
  })
  await page.waitForTimeout(300)
  await page.screenshot({ path: path.join(dir, `${name}_full.png`), fullPage: true })
  const h = await page.evaluate(() => document.documentElement.scrollHeight)
  console.log(name, 'header', hb && Math.round(hb.y + hb.height), 'nav', nb && Math.round(nb.y), 'height', h)
  return { header: hb ? hb.y + hb.height : 0, navTop: nb ? nb.y : 844, height: h }
}

;(async () => {
  const b = await chromium.launch()
  const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 3, locale: 'bn-BD', colorScheme: 'light' })
  const p = await ctx.newPage()
  await demoLogin(p)
  const info = {}
  info.home = await grab(p, BASE + '/app', 'home')
  info.capture = await grab(p, BASE + '/app/scan', 'capture')
  info.diag = await grab(p, meta.diagUrl, 'diag')
  info.unsure = await grab(p, meta.unsureUrl, 'unsure')
  info.history = await grab(p, BASE + '/app/history', 'history')
  fs.writeFileSync(path.join(dir, 'full.json'), JSON.stringify(info, null, 2))
  await b.close()
})().catch((e) => { console.error(e); process.exit(1) })
