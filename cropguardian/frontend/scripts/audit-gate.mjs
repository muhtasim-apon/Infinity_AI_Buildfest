// npm audit gate (spec 19.6 step 7): FAIL on any high/critical advisory that is not on the allow-list.
// The allow-list is explicit, justified and expires - an expired entry fails the gate again.
// Runtime (shipped) dependencies are checked separately and must always be clean.
import { execFileSync } from 'node:child_process'

const TODAY = new Date().toISOString().slice(0, 10)

/** advisory id -> why it is accepted and until when. Review at each phase gate. */
const ALLOWED = {
  'GHSA-vfj7-8cjw-p6xm': {
    why: 'braces ReDoS via tailwindcss 3 build-time glob expansion of our own content globs; braces is already at its latest release; the fix needs Tailwind 4 (spec pins Tailwind 3). Not shipped, no attacker-controlled input.',
    until: '2026-11-30',
  },
  'GHSA-rj75-hqrm-r3gf': {
    why: 'postcss-selector-parser quadratic parsing in the Tailwind 3 build chain; build-time only, our own CSS.',
    until: '2026-11-30',
  },
}

function audit(args) {
  try {
    return JSON.parse(
      execFileSync('npm', ['audit', '--json', ...args], {
        encoding: 'utf8',
        shell: process.platform === 'win32',
      }),
    )
  } catch (e) {
    // npm audit exits non-zero when vulnerabilities exist but still prints JSON
    return JSON.parse(e.stdout)
  }
}

const runtime = audit(['--omit=dev'])
const runtimeTotal = Object.values(runtime.metadata.vulnerabilities).reduce((a, b) => a + b, 0)
if (runtimeTotal > 0) {
  console.error(`FAIL: ${runtimeTotal} vulnerabilities in shipped (runtime) dependencies`)
  process.exit(1)
}

const full = audit([])
const problems = []
const seen = new Set()
for (const [name, v] of Object.entries(full.vulnerabilities)) {
  if (!['high', 'critical'].includes(v.severity) && !v.via.some((y) => typeof y === 'object'))
    continue
  for (const via of v.via) {
    if (typeof via !== 'object') continue
    const id = via.url.split('/').pop()
    if (seen.has(id)) continue
    seen.add(id)
    if (!['high', 'critical'].includes(via.severity)) continue
    const allow = ALLOWED[id]
    if (!allow) problems.push(`${via.severity.toUpperCase()} ${id} in ${name}: ${via.title}`)
    else if (allow.until < TODAY)
      problems.push(`allow-list entry for ${id} EXPIRED on ${allow.until}`)
  }
}
if (problems.length > 0) {
  console.error('FAIL: unaccepted high/critical advisories:\n - ' + problems.join('\n - '))
  process.exit(1)
}
const accepted = [...seen].filter((id) => ALLOWED[id])
console.log(
  `audit gate OK: runtime clean; ${accepted.length} dev-only advisory(ies) accepted: ${accepted.join(', ')}`,
)
