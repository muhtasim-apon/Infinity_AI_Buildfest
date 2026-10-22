/**
 * Zod startup configuration. Import this FIRST (src/main.tsx does).
 *
 * Zod 4 probes `Function('')` once to decide whether it may compile schemas with eval. Under our
 * strict CSP (`script-src 'self'`, no unsafe-eval, spec 16.3) that probe fails, which is harmless to
 * Zod but makes the browser report a Content-Security-Policy violation (and a console error) on every
 * page load. `jitless` tells Zod never to try: it uses its interpreter path, which is plenty fast for
 * our small form schemas. The a11y/CSP E2E gate caught this (DECISIONS D-027).
 */
import { z } from 'zod'

z.config({ jitless: true })
