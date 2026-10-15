// Playwright E2E — user journeys (docs/product/user-journeys.md) in BOTH locales at phone size.
// Run: npx playwright test tests/e2e   (needs the app running; BASE_URL env)
import { expect, test } from "@playwright/test";

const BASE = process.env.BASE_URL ?? "http://localhost:5173";

for (const locale of ["bn", "en"] as const) {
  test.describe(`journeys (${locale})`, () => {
    test.use({ viewport: { width: 360, height: 740 }, locale: locale === "bn" ? "bn-BD" : "en-US" });

    test("J7: one-click demo user lands on /app with synthetic banner", async ({ page }) => {
      await page.goto(`${BASE}/demo-user`);
      await expect(page).toHaveURL(/\/app/);
      await expect(page.getByTestId("synthetic-banner")).toBeVisible();
    });

    test.fixme("J1: scan fixture leaf → result with top-3 and cited advice", async () => {});
    test.fixme("J2: non-leaf photo → 'not sure' message, no disease shown as answer", async () => {});
    test.fixme("J3: offline → item queued → online → auto-sent", async () => {});
    test.fixme("Cold start: API delayed 60 s → waking message, then result", async () => {});
    test.fixme("Deep link /audit loads directly (SPA rewrite)", async () => {});
    test.fixme("J4: agronomist confirms a review case", async () => {});
    test.fixme("J5: approve alert draft", async () => {});
  });
}
