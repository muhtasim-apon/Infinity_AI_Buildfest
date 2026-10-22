// Bundle budgets (spec 15.9, gate P2): pure logic over the Vite manifest so it is unit-tested.
// Sizes are gzip KB. "Initial" is the entry chunk plus everything it statically imports; every
// dynamic-import chunk (route, admin, landing 3D) is judged separately with its own static imports.
import { gzipSync } from 'node:zlib'

export const BUDGET_KB = {
  initial: 170, // farmer app initial JS
  route: 120, // each lazy route chunk
  staff: 250, // staff console (admin / review) chunk
  hero3d: 220, // landing 3D hero, lazy
  bengaliFonts: 120, // Bangla subset fonts, total woff2 KB
}

const HERO_3D = /sentinel|hero|three|r3f|fiber/i
const STAFF = /admin|review|staff/i
// A marker only the three.js renderer contains: it must never be reachable from the initial graph.
const THREE_MARKER = 'WebGLRenderer'

/** Gzip size of a Buffer in KB (level 9: what a CDN with brotli/gzip would at best deliver). */
export function gzipKb(buffer) {
  return gzipSync(buffer, { level: 9 }).length / 1024
}

function closure(manifest, startKey, skip = new Set()) {
  const files = new Map()
  const seen = new Set()
  const visit = (key) => {
    if (seen.has(key)) return
    seen.add(key)
    const chunk = manifest[key]
    if (!chunk) return
    if (!skip.has(chunk.file) && chunk.file.endsWith('.js')) files.set(chunk.file, key)
    for (const dep of chunk.imports ?? []) visit(dep)
  }
  visit(startKey)
  return files
}

/**
 * @param {{ manifest: Record<string, any>, readFile: (f: string) => Buffer, bengaliFontFiles: {file: string, bytes: number}[] }} input
 * @returns {{ rows: {name: string, kind: string, kb: number, limit: number, ok: boolean}[], problems: string[] }}
 */
export function evaluate({ manifest, readFile, bengaliFontFiles }) {
  const rows = []
  const problems = []
  const row = (name, kind, kb, limit) => {
    const ok = kb <= limit
    rows.push({ name, kind, kb: Math.round(kb * 10) / 10, limit, ok })
    if (!ok) {
      // fonts are woff2 (already compressed): report plain KB, not gzip KB
      const unit = kind === 'bengaliFonts' ? 'KB' : 'KB gzip'
      problems.push(`${name}: ${kb.toFixed(1)} ${unit} exceeds the ${limit} KB ${kind} budget`)
    }
  }

  const entries = Object.keys(manifest).filter((k) => manifest[k].isEntry)
  if (entries.length === 0)
    return { rows, problems: ['manifest has no entry chunk (build with manifest: true)'] }

  const initial = new Map()
  for (const key of entries)
    for (const [file, owner] of closure(manifest, key)) initial.set(file, owner)
  const initialKb = [...initial.keys()].reduce((sum, f) => sum + gzipKb(readFile(f)), 0)
  row('initial JS (entry + static imports)', 'initial', initialKb, BUDGET_KB.initial)

  for (const [file, owner] of initial) {
    if (HERO_3D.test(owner) || readFile(file).includes(THREE_MARKER)) {
      problems.push(`${file}: 3D code is reachable from the initial graph (must be a lazy chunk)`)
    }
  }

  const initialFiles = new Set(initial.keys())
  for (const key of Object.keys(manifest)) {
    const chunk = manifest[key]
    if (!chunk.isDynamicEntry) continue
    const files = closure(manifest, key, initialFiles)
    const kb = [...files.keys()].reduce((sum, f) => sum + gzipKb(readFile(f)), 0)
    const label = chunk.src ?? key
    if (HERO_3D.test(label)) row(label, 'hero3d', kb, BUDGET_KB.hero3d)
    else if (STAFF.test(label)) row(label, 'staff', kb, BUDGET_KB.staff)
    else row(label, 'route', kb, BUDGET_KB.route)
  }

  const fontKb = bengaliFontFiles.reduce((sum, f) => sum + f.bytes, 0) / 1024
  row(
    `Bangla fonts (${bengaliFontFiles.length} woff2 files)`,
    'bengaliFonts',
    fontKb,
    BUDGET_KB.bengaliFonts,
  )
  return { rows, problems }
}
