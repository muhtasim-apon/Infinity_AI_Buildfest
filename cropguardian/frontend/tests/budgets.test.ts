// @vitest-environment node
import { randomBytes } from 'node:crypto'
import { describe, expect, it } from 'vitest'
import { BUDGET_KB, evaluate } from '../scripts/lib/budgets.mjs'

/** Random bytes do not compress, so N bytes ~ N gzip bytes: sizes in the tests are real gzip sizes. */
const kb = (n: number) => randomBytes(Math.round(n * 1024))

type Chunk = {
  file: string
  isEntry?: boolean
  isDynamicEntry?: boolean
  imports?: string[]
  src?: string
}

function run(
  manifest: Record<string, Chunk>,
  files: Record<string, Buffer>,
  bengaliFontFiles: { file: string; bytes: number }[] = [],
) {
  return evaluate({
    manifest,
    readFile: (f: string) => files[f] ?? Buffer.alloc(0),
    bengaliFontFiles,
  })
}

describe('bundle budgets (spec 15.9)', () => {
  it('uses the spec numbers', () => {
    expect(BUDGET_KB).toEqual({
      initial: 170,
      route: 120,
      staff: 250,
      hero3d: 220,
      bengaliFonts: 120,
    })
  })

  it('passes when everything is under budget', () => {
    const out = run(
      {
        'index.html': { file: 'a.js', isEntry: true, imports: [] },
        'src/pages/Scan.tsx': { file: 'scan.js', isDynamicEntry: true, src: 'src/pages/Scan.tsx' },
      },
      { 'a.js': kb(100), 'scan.js': kb(60) },
    )
    expect(out.problems).toEqual([])
    expect(out.rows.every((r) => r.ok)).toBe(true)
  })

  it('fails when the farmer initial JS is over 170 KB gzip', () => {
    const out = run({ 'index.html': { file: 'a.js', isEntry: true } }, { 'a.js': kb(175) })
    expect(out.problems.join()).toMatch(/initial JS.*exceeds the 170 KB initial budget/)
  })

  it('counts the entry plus everything it statically imports', () => {
    const out = run(
      {
        'index.html': { file: 'a.js', isEntry: true, imports: ['shared.js'] },
        'shared.js': { file: 'shared.js', imports: [] },
      },
      { 'a.js': kb(100), 'shared.js': kb(90) },
    )
    expect(out.problems.join()).toMatch(/initial/)
  })

  it('judges a lazy route chunk on its own, without double counting shared initial code', () => {
    const manifest = {
      'index.html': { file: 'a.js', isEntry: true, imports: ['shared.js'] },
      'shared.js': { file: 'shared.js' },
      'src/pages/History.tsx': {
        file: 'h.js',
        isDynamicEntry: true,
        imports: ['shared.js'],
        src: 'src/pages/History.tsx',
      },
    }
    const ok = run(manifest, { 'a.js': kb(40), 'shared.js': kb(90), 'h.js': kb(100) })
    expect(ok.problems).toEqual([]) // 100 KB route; the 90 KB shared chunk is NOT counted again
    const bad = run(manifest, { 'a.js': kb(40), 'shared.js': kb(20), 'h.js': kb(125) })
    expect(bad.problems.join()).toMatch(/History.*exceeds the 120 KB route budget/)
  })

  it('gives the landing 3D chunk its own 220 KB budget', () => {
    const hero = {
      'index.html': { file: 'a.js', isEntry: true },
      'src/landing/SentinelField.tsx': {
        file: 'hero.js',
        isDynamicEntry: true,
        src: 'src/landing/SentinelField.tsx',
      },
    }
    expect(run(hero, { 'a.js': kb(50), 'hero.js': kb(200) }).problems).toEqual([])
    expect(run(hero, { 'a.js': kb(50), 'hero.js': kb(230) }).problems.join()).toMatch(
      /hero3d budget/,
    )
  })

  it('gives staff chunks the 250 KB staff budget', () => {
    const admin = {
      'index.html': { file: 'a.js', isEntry: true },
      'src/app/pages/AdminHome.tsx': {
        file: 'adm.js',
        isDynamicEntry: true,
        src: 'src/app/pages/AdminHome.tsx',
      },
    }
    expect(run(admin, { 'a.js': kb(50), 'adm.js': kb(200) }).problems).toEqual([])
    expect(run(admin, { 'a.js': kb(50), 'adm.js': kb(260) }).problems.join()).toMatch(
      /staff budget/,
    )
  })

  it('fails when 3D code is reachable from the initial graph (by name)', () => {
    const out = run(
      {
        'index.html': { file: 'a.js', isEntry: true, imports: ['src/landing/hero.ts'] },
        'src/landing/hero.ts': { file: 'hero.js' },
      },
      { 'a.js': kb(10), 'hero.js': kb(10) },
    )
    expect(out.problems.join()).toMatch(/3D code is reachable from the initial graph/)
  })

  it('fails when the three.js renderer is bundled into the initial chunk (by content)', () => {
    const out = run(
      { 'index.html': { file: 'a.js', isEntry: true } },
      { 'a.js': Buffer.from('/* x */ new WebGLRenderer({}) ') },
    )
    expect(out.problems.join()).toMatch(/3D code is reachable/)
  })

  it('fails when the Bangla fonts exceed 120 KB and reports plain KB for fonts', () => {
    const out = run({ 'index.html': { file: 'a.js', isEntry: true } }, { 'a.js': kb(10) }, [
      { file: 'a.woff2', bytes: 100 * 1024 },
      { file: 'b.woff2', bytes: 40 * 1024 },
    ])
    const msg = out.problems.join()
    expect(msg).toMatch(/Bangla fonts \(2 woff2 files\).*exceeds the 120 KB/)
    expect(msg).not.toMatch(/KB gzip exceeds the 120 KB bengaliFonts/)
  })

  it('refuses to pass without a manifest entry (build without manifest: true)', () => {
    const out = run({}, {})
    expect(out.problems.join()).toMatch(/no entry chunk/)
  })

  it('tolerates a missing dependency in the manifest instead of crashing', () => {
    const out = run(
      { 'index.html': { file: 'a.js', isEntry: true, imports: ['ghost.js'] } },
      { 'a.js': kb(10) },
    )
    expect(out.problems).toEqual([])
  })
})
