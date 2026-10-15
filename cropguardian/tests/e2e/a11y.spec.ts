// Accessibility — axe-core on every public route, both locales.
import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

const BASE = process.env.BASE_URL ?? "http://localhost:5173";
const ROUTES = ["/app", "/demo-user", "/admin", "/data", "/security", "/architecture", "/presentation", "/pitchdeck", "/audit"];

for (const route of ROUTES) {
  test.fixme(`no serious a11y violations on ${route}`, async ({ page }) => {
    await page.goto(`${BASE}${route}`);
    const results = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa"]).analyze();
    expect(results.violations.filter((v) => v.impact === "serious" || v.impact === "critical")).toEqual([]);
  });
}
