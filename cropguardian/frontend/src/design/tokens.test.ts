import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'
import { banglaScale, darkTheme, diseaseColours, lightTheme, risk, typeScale } from './tokens'

const css = readFileSync(resolve(__dirname, 'tokens.css'), 'utf8')
const kebab = (s: string) => s.replace(/[A-Z]|\d+/g, (m) => '-' + m.toLowerCase())

function block(startMarker: string): string {
  const start = css.indexOf(startMarker)
  if (start < 0) throw new Error(`marker not found: ${startMarker}`)
  return css.slice(start, css.indexOf('}', start))
}

describe('tokens.css mirrors tokens.ts (no drift)', () => {
  const lightBlock = block(":root,\n:root[data-theme='light']")
  const darkAttrBlock = block(":root[data-theme='dark']")

  it('every light token matches', () => {
    for (const [key, hex] of Object.entries(lightTheme)) {
      expect(lightBlock.toLowerCase()).toContain(`--${kebab(key)}: ${hex.toLowerCase()};`)
    }
  })

  it('every dark token matches (explicit dark theme)', () => {
    for (const [key, hex] of Object.entries(darkTheme)) {
      expect(darkAttrBlock.toLowerCase()).toContain(`--${kebab(key)}: ${hex.toLowerCase()};`)
    }
  })

  it('disease and risk palettes match', () => {
    diseaseColours.forEach((hex, i) =>
      expect(lightBlock.toLowerCase()).toContain(`--disease-${i + 1}: ${hex.toLowerCase()};`),
    )
    for (const [k, hex] of Object.entries(risk)) {
      expect(lightBlock.toLowerCase()).toContain(`--risk-${k}: ${hex.toLowerCase()};`)
    }
  })

  it('Bangla scale is +2 px and x1.15 line-height at every step', () => {
    expect(banglaScale).toHaveLength(typeScale.length)
    typeScale.forEach(([size, line], i) => {
      expect(banglaScale[i]![0]).toBe(size + 2)
      expect(banglaScale[i]![1]).toBe(Math.round(line * 1.15))
    })
  })

  it('has no external URLs or inline-unsafe constructs (strict CSP)', () => {
    expect(css).not.toMatch(/https?:\/\//)
    expect(css).not.toMatch(/@import/)
  })
})
