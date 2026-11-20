// Record storyboard.html in real time (1920x1080) with Playwright. Usage:
//   node render.cjs <build_dir> [clips_dir]
// Writes <build_dir>/storyboard.webm and <build_dir>/offset.txt (seconds to trim before the timeline starts).
const path = require('path')
const fs = require('fs')
const { chromium } = require(path.resolve(__dirname, '../../../e2e/node_modules/@playwright/test'))

;(async () => {
  const build = path.resolve(process.argv[2])
  const clipsDir = process.argv[3] ? path.resolve(process.argv[3]) : null
  const timeline = JSON.parse(fs.readFileSync(path.join(build, 'timeline.json'), 'utf8'))
  const clips = {}
  if (clipsDir) {
    for (const name of ['scan', 'result', 'notsure', 'review', 'trust']) {
      const f = path.join(clipsDir, `${name}.webm`)
      if (fs.existsSync(f)) clips[name] = 'file:///' + f.replace(/\\/g, '/')
    }
  }
  const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required', '--allow-file-access-from-files'] })
  const ctx = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    deviceScaleFactor: 1,
    recordVideo: { dir: build, size: { width: 1920, height: 1080 } },
  })
  const t0 = Date.now()
  await ctx.addInitScript(([tl, cl]) => { window.__TIMELINE = tl; window.__CLIPS = cl }, [timeline, clips])
  const page = await ctx.newPage()
  page.on('console', (m) => { if (m.type() === 'error') console.log('page error:', m.text()) })
  await page.goto('file:///' + path.join(__dirname, 'storyboard.html').replace(/\\/g, '/'))
  await page.waitForTimeout(1500) // fonts + first paint
  const startAt = Date.now()
  await page.evaluate(() => window.__start())
  await page.waitForFunction(() => window.__done === true, null, { timeout: (timeline.total + 30) * 1000, polling: 500 })
  const video = page.video()
  await ctx.close()
  await browser.close()
  const src = await video.path()
  fs.renameSync(src, path.join(build, 'storyboard.webm'))
  fs.writeFileSync(path.join(build, 'offset.txt'), String((startAt - t0) / 1000))
  console.log('recorded; clips:', Object.keys(clips).join(',') || 'none', 'offset', (startAt - t0) / 1000)
})().catch((e) => { console.error(e); process.exit(1) })
