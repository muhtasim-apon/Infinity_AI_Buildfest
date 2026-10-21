/**
 * Open-redirect defence (spec 16.6): `return_to` is only ever followed if it is a plain in-app path.
 * Mirrors backend/app/core/redirects.py; both are tested against the same corpus.
 */

const MAX_LENGTH = 512
// eslint-disable-next-line no-control-regex
const CONTROL = /[\u0000-\u001f\u007f]/

function isPlainPath(path: string): boolean {
  if (!path.startsWith('/') || path.startsWith('//') || path.includes('\\') || CONTROL.test(path)) {
    return false
  }
  return !/^[a-z][a-z0-9+.-]*:/i.test(path)
}

function safeDecode(value: string): string {
  try {
    return decodeURIComponent(value)
  } catch {
    return value
  }
}

export function safeReturnTo(value: string | null | undefined, fallback = '/'): string {
  if (!value || value.length > MAX_LENGTH) return fallback
  const once = safeDecode(value)
  const twice = safeDecode(once)
  return [value, once, twice].every(isPlainPath) ? value : fallback
}
