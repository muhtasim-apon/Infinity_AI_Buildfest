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
  // Port 5180, not 5173: other Vite projects on the same machine usually hold 5173 (DECISIONS D-029).
  // /api goes to the running compose stack (nginx on https://localhost, self-signed so secure:false),
  // not to an unpublished :8000. The Origin header is rewritten so the API's CSRF origin check, which
  // trusts only APP_BASE_URL, accepts dev requests. Override with VITE_API_PROXY.
  server: {
    port: 5180,
    strictPort: true,
    proxy: {
      '/api': {
        target: process.env.VITE_API_PROXY ?? 'https://localhost',
        secure: false,
        changeOrigin: true,
        headers: { Origin: process.env.VITE_API_PROXY ?? 'https://localhost' },
      },
    },
  },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./tests/setup.ts'],
    include: ['src/**/*.test.{ts,tsx}', 'tests/**/*.test.{ts,tsx}'],
  },
})
