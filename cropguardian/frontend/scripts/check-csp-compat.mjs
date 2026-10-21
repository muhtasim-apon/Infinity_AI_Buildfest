// CSP-compatibility test (spec 20 Phase 0): dist/index.html must contain no inline scripts, inline
// event handlers, inline styles or style attributes, and no external origins.
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

const file = resolve(process.cwd(), 'dist', 'index.html')
const html = readFileSync(file, 'utf8')
const problems = []

for (const m of html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/gi)) {
  const attrs = m[1] ?? ''
  const body = (m[2] ?? '').trim()
  if (body.length > 0) problems.push('inline <script> body')
  if (!/\bsrc=/.test(attrs)) problems.push('<script> without src')
}
if (/<style\b/i.test(html)) problems.push('inline <style> element')
if (/\sstyle\s*=/i.test(html)) problems.push('inline style= attribute')
if (/\son[a-z]+\s*=/i.test(html)) problems.push('inline event handler attribute')
if (/(src|href)\s*=\s*["']https?:\/\//i.test(html)) problems.push('external origin in src/href')

if (problems.length > 0) {
  console.error('CSP compatibility FAILED:\n - ' + [...new Set(problems)].join('\n - '))
  process.exit(1)
}
console.log('CSP compatibility OK: no inline scripts/styles, no external origins')
