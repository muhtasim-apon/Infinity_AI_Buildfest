// Render the v2 film frame by frame on the GPU (deterministic: every frame is computed for its exact
// time, so quality never depends on real-time speed). Usage:
//   node render_v2.cjs <build_dir> <ui_dir> frames [fps=30] [from=0] [to=180]   -> <build>/frames/f_000000.jpg
//   node render_v2.cjs <build_dir> <ui_dir> stills 5,20,45                   -> <build>/still_<t>.png
const path = require('path')
const fs = require('fs')
const http = require('http')
const { chromium } = require(path.resolve(__dirname, '../../../e2e/node_modules/@playwright/test'))

const [build, uiDir, mode, arg, ...rest] = process.argv.slice(2)
const ROOT = path.resolve(__dirname, '../../..') // cropguardian/
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.png': 'image/png', '.jpg': 'image/jpeg', '.woff2': 'font/woff2' }

function serve() {
  const server = http.createServer((req, res) => {
    const url = decodeURIComponent(req.url.split('?')[0])
    const file = url.startsWith('/ui/') ? path.join(path.resolve(uiDir), url.slice(4)) : path.join(ROOT, url)
    if (!file.startsWith(ROOT) && !file.startsWith(path.resolve(uiDir))) return res.writeHead(403).end()
    fs.readFile(file, (err, data) => {
      if (err) return res.writeHead(404).end()
      res.writeHead(200, { 'Content-Type': TYPES[path.extname(file)] || 'application/octet-stream' })
      res.end(data)
    })
  })
  return new Promise((r) => server.listen(0, '127.0.0.1', () => r(server)))
}

;(async () => {
  const out = path.resolve(build)
  fs.mkdirSync(out, { recursive: true })
  const timeline = JSON.parse(fs.readFileSync(path.join(out, 'timeline.json'), 'utf8'))
  const server = await serve()
  const base = `http://127.0.0.1:${server.address().port}`
  const browser = await chromium.launch({ channel: 'chrome', args: ['--use-angle=d3d11', '--enable-gpu', '--ignore-gpu-blocklist', '--disable-gpu-watchdog'] })
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 })
  const errors = []
  page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()) })
  page.on('pageerror', (e) => errors.push('pageerror: ' + e.message))
  page.on('response', (r) => { if (r.status() >= 400) errors.push(r.status() + ' ' + r.url()) })
  await page.addInitScript((tl) => { window.__TIMELINE = tl }, timeline)
  await page.goto(base + '/docs/congress/video/film/index.html')
  await page.waitForFunction(() => window.__ready === true, null, { timeout: 180000 }).catch(() => {})
  if (errors.length) console.log('errors:', errors.slice(0, 6).join('\n'))
  const stage = page.locator('#stage')
  if (mode === 'stills') {
    for (const t of arg.split(',').map(Number)) {
      await page.evaluate((t) => window.__frame(t), t)
      await stage.screenshot({ path: path.join(out, `still_${t}.png`) })
      console.log('still', t)
    }
  } else {
    const fps = Number(arg || 30), from = Number(rest[0] || 0), to = Number(rest[1] || 180)
    const dir = path.join(out, 'frames')
    fs.mkdirSync(dir, { recursive: true })
    const t0 = Date.now()
    for (let f = Math.round(from * fps); f < Math.round(to * fps); f++) {
      const file = path.join(dir, `f_${String(f).padStart(6, '0')}.jpg`)
      if (fs.existsSync(file)) continue // resumable
      await page.evaluate((t) => window.__frame(t), f / fps)
      await stage.screenshot({ path: file, type: 'jpeg', quality: 93 })
      if (f % 150 === 0) console.log(`frame ${f} (${(f / fps).toFixed(1)}s) ${((Date.now() - t0) / 1000).toFixed(0)}s elapsed`)
    }
  }
  if (errors.length) console.log('errors:', errors.slice(0, 6).join('\n'))
  await browser.close()
  server.close()
})().catch((e) => { console.error(e); process.exit(1) })
