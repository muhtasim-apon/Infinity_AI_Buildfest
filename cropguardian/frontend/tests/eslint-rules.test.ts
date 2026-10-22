// @vitest-environment node
// The lint rules ARE the gate for "no hex colours / numeric durations outside src/design" (spec 19.8),
// so they get their own tests: a rule that silently stops matching would pass the gate while the
// design system rots.
import { ESLint } from 'eslint'
import { beforeAll, describe, expect, it } from 'vitest'

const eslint = new ESLint({ overrideConfigFile: 'eslint.config.js' })

async function messages(code: string, filePath: string): Promise<string[]> {
  const [result] = await eslint.lintText(code, { filePath })
  if (!result) throw new Error('ESLint returned no result (file ignored?)')
  return result.messages.map((m) => m.message)
}

describe('design-system lint rules', () => {
  // The first lintText loads the whole flat config and every plugin (about 3 s warm, much more on a
  // cold cache or a loaded machine), so it must not be charged to whichever test happens to run first.
  beforeAll(async () => {
    await eslint.lintText('export {}', { filePath: 'src/components/warmup.ts' })
  }, 120_000)

  it('rejects a hex colour in app code', async () => {
    const out = await messages("export const c = '#16a34a'\n", 'src/components/x.ts')
    expect(out.some((m) => m.includes('Hex colours live in src/design'))).toBe(true)
  })

  it('rejects hex colours of every legal length (3, 6, 8 digits)', async () => {
    for (const hex of ['#abc', '#aabbcc', '#aabbccdd']) {
      const out = await messages(`export const c = '${hex}'\n`, 'src/components/x.ts')
      expect(out.some((m) => m.includes('Hex colours'))).toBe(true)
    }
  })

  it('does not flag in-page anchors or ordinary words', async () => {
    const out = await messages(
      "export const a = ['#main-content', '#address', 'colour']\n",
      'src/components/x.ts',
    )
    expect(out.filter((m) => m.includes('Hex colours'))).toEqual([])
  })

  it('rejects numeric animation durations and delays outside motion.ts', async () => {
    const out = await messages(
      'export const t = { duration: 0.3, delay: 1, staggerChildren: 0.05 }\n',
      'src/components/x.ts',
    )
    expect(out.filter((m) => m.includes('Animation durations')).length).toBe(3)
  })

  it('allows durations that come from the motion tokens', async () => {
    const out = await messages(
      "import { duration } from '../design/motion'\nexport const t = { duration: duration.base }\n",
      'src/components/x.ts',
    )
    expect(out.filter((m) => m.includes('Animation durations'))).toEqual([])
  })

  it('allows both inside src/design (the single source of truth)', async () => {
    const out = await messages(
      "export const c = '#16a34a'\nexport const t = { duration: 0.3 }\n",
      'src/design/x.ts',
    )
    expect(out.filter((m) => m.includes('live in src/design'))).toEqual([])
  })

  it('still forbids XSS sinks everywhere, including src/design', async () => {
    for (const file of ['src/components/x.ts', 'src/design/x.ts']) {
      const out = await messages('document.body.innerHTML = "x"\n', file)
      expect(out.some((m) => m.includes('XSS sink forbidden'))).toBe(true)
    }
  })
})
