import react from '@vitejs/plugin-react'
import { defineConfig } from 'vitest/config'

// No inline scripts/styles are emitted (strict CSP, spec 16.3): assets are never inlined and CSS is
// always extracted to files; the modulepreload polyfill is an inline script, so it is disabled.
export default defineConfig({
  plugins: [react()],
  build: {
    target: 'es2022',
    cssCodeSplit: true,
    assetsInlineLimit: 0,
    sourcemap: false,
    // dist/.vite/manifest.json lets scripts/check-budgets.mjs see the real chunk graph (budgets, 3D isolation)
    manifest: true,
    modulePreload: { polyfill: false },
  },
  server: { port: 5173, strictPort: true, proxy: { '/api': 'http://localhost:8000' } },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./tests/setup.ts'],
    include: ['src/**/*.test.{ts,tsx}', 'tests/**/*.test.{ts,tsx}'],
  },
})
