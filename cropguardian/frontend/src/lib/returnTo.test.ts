import { describe, expect, it } from 'vitest'
import { safeReturnTo } from './returnTo'

// Same corpus as backend/tests/unit/test_pure_security.py (open-redirect cases)
const BAD = [
  '//evil.com',
  'https://evil.com',
  '/\\evil.com',
  'javascript:alert(1)',
  'evil.com',
  '',
  '/%2f%2fevil.com',
  '/%5cevil.com',
  '/%252f%252fevil.com',
  '/a\nb',
  `/a${'x'.repeat(600)}`,
  '/\t/evil.com',
  'mailto:a@b.c',
  '///evil.com',
  'data:text/html,x',
  '/%0d%0aSet-Cookie:x=1',
]
const GOOD = ['/', '/scans/12', '/alerts?filter=open&page=2', '/a/b#frag']

describe('safeReturnTo (open redirect defence)', () => {
  it.each(BAD)('rejects %j', (value) => {
    expect(safeReturnTo(value)).toBe('/')
    expect(safeReturnTo(value, '/home')).toBe('/home')
  })
  it.each(GOOD)('keeps %j', (value) => {
    expect(safeReturnTo(value)).toBe(value)
  })
  it('handles null, undefined and malformed percent-encoding', () => {
    expect(safeReturnTo(null, '/x')).toBe('/x')
    expect(safeReturnTo(undefined, '/x')).toBe('/x')
    expect(safeReturnTo('/%E0%A4%A', '/x')).toBe('/%E0%A4%A') // not decodable: still a plain path
  })
})
