// Bundle budget gate (spec 15.9): run after `vite build`. Exit 1 when any budget is exceeded.
import { readdirSync, readFileSync, statSync } from 'node:fs'
import { resolve } from 'node:path'
import { evaluate } from './lib/budgets.mjs'

const dist = resolve(process.cwd(), 'dist')
let manifest
try {
  manifest = JSON.parse(readFileSync(resolve(dist, '.vite', 'manifest.json'), 'utf8'))
} catch {
  console.error('budgets FAILED: dist/.vite/manifest.json missing (run `npm run build` first)')
  process.exit(1)
}

const assets = resolve(dist, 'assets')
const bengaliFontFiles = readdirSync(assets)
  .filter((f) => /bengali.*\.woff2$/i.test(f))
  .map((f) => ({ file: f, bytes: statSync(resolve(assets, f)).size }))

const { rows, problems } = evaluate({
  manifest,
  readFile: (file) => readFileSync(resolve(dist, file)),
  bengaliFontFiles,
})

const width = Math.max(...rows.map((r) => r.name.length), 10)
for (const r of rows) {
  console.log(
    `${r.ok ? 'ok  ' : 'FAIL'} ${r.name.padEnd(width)}  ${String(r.kb).padStart(7)} KB / ${r.limit} KB  (${r.kind})`,
  )
}
if (problems.length > 0) {
  console.error('\nbudgets FAILED:\n - ' + problems.join('\n - '))
  process.exit(1)
}
console.log('\nbudgets OK')
