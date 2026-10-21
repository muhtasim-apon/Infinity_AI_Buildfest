import { defineConfig, devices } from '@playwright/test'

// Phase 0 smoke through Nginx (https://localhost) once `make up` is running; devices per spec 15.14.
export default defineConfig({
  testDir: './journeys',
  retries: 0,
  use: {
    baseURL: process.env.E2E_BASE_URL ?? 'https://localhost',
    ignoreHTTPSErrors: true, // dev certs (mkcert or self-signed)
    trace: 'retain-on-failure',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } },
    { name: 'android', use: { ...devices['Pixel 5'] } },
  ],
})
