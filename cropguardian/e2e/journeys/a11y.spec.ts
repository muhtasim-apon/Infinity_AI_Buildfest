import AxeBuilder from '@axe-core/playwright'
import { expect, test } from '../fixtures'
import { LOCALES, PUBLIC_SCREENS, THEMES } from '../screens'

/**
 * Accessibility gate (spec 15.8, 19.6 step 16): axe on every built public screen, in both themes and
 * both languages, at the project's width (360 / 768 / 1366). Zero serious or critical violations and
 * zero CSP violations. Contrast is checked here in a real browser, which jsdom cannot do.
 */
for (const screen of PUBLIC_SCREENS) {
  for (const theme of THEMES) {
    for (const locale of LOCALES) {
      test(`axe: ${screen.id} (${theme}, ${locale}) @e2e`, async ({ page, cspViolations }) => {
        await page.emulateMedia({
          colorScheme: theme,
          reducedMotion: 'reduce',
        })
        await page.goto(screen.path)
        if (locale === 'en') await page.getByRole('button', { name: 'EN', exact: true }).click()
        await expect(page.locator('main')).toBeVisible()
        await expect(page.locator('html')).toHaveAttribute('lang', locale)
        // CSP is judged on what the PAGE did, before axe runs: axe-core itself uses eval inside the page,
        // which the strict CSP (correctly) reports, so a violation after analyze() would be the tool's.
        expect(cspViolations).toEqual([])

        const results = await new AxeBuilder({ page })
          .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
          .analyze()
        const serious = results.violations
          .filter((v) => v.impact === 'serious' || v.impact === 'critical')
          .map(
            (v) =>
              `${v.id} (${v.impact}): ${v.nodes.length} node(s), e.g. ${v.nodes[0]?.target.join(' ')}`,
          )
        expect(serious).toEqual([])
      })
    }
  }
}
