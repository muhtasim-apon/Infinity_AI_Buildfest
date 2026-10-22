import { defineConfig, devices } from '@playwright/test'

// Journeys through Nginx (https://localhost) once `make up` is running; devices per spec 15.14.
// Phase 2 adds the layout matrix (360 / 768 / 1366 wide) and a Slow-3G profile. The width projects
// only run the specs that are about layout, so the heavy identity journeys are not tripled.
const LAYOUT_SPECS = /(a11y|layout|shells|visual|gallery)\.spec\.ts$/

export default defineConfig({
  testDir: './journeys',
  retries: 0,
  // snapshots live next to the specs, one folder per project, so baselines never collide
  snapshotPathTemplate: '{testDir}/__screenshots__/{projectName}/{testFilePath}/{arg}{ext}',
  use: {
    baseURL: process.env.E2E_BASE_URL ?? 'https://localhost',
    ignoreHTTPSErrors: true, // dev certs (mkcert or self-signed)
    trace: 'retain-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
      testIgnore: LAYOUT_SPECS,
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
      testIgnore: LAYOUT_SPECS,
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
      testIgnore: LAYOUT_SPECS,
    },
    {
      name: 'android',
      use: { ...devices['Pixel 5'] },
      testIgnore: LAYOUT_SPECS,
    },
    // 360x740: the low-end Android target (spec 15.14), touch, mobile UA
    {
      name: 'w360',
      use: { ...devices['Pixel 5'], viewport: { width: 360, height: 740 } },
      testMatch: LAYOUT_SPECS,
    },
    {
      name: 'w768',
      use: {
        ...devices['Desktop Chrome'],
        viewport: { width: 768, height: 1024 },
        hasTouch: true,
      },
      testMatch: LAYOUT_SPECS,
    },
    // 1366x768: the common laptop (spec 20 Phase 2 manual check)
    {
      name: 'w1366',
      use: {
        ...devices['Desktop Chrome'],
        viewport: { width: 1366, height: 768 },
      },
      testMatch: LAYOUT_SPECS,
    },
    // Slow 3G for the farmer flows F1-F3 (spec 15.14); throttling is applied in fixtures.ts
    {
      name: 'slow3g',
      use: { ...devices['Pixel 5'] },
      grep: /@slow3g/,
    },
  ],
})
