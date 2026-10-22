import { describe, expect, it } from 'vitest'
import './zodConfig'
import { z } from 'zod'

describe('zod under a strict CSP', () => {
  it('parses without ever touching eval or the Function constructor', () => {
    const Original = globalThis.Function
    let attempts = 0
    globalThis.Function = new Proxy(Original, {
      construct(target, args) {
        attempts += 1
        return Reflect.construct(target, args)
      },
      apply(target, thisArg, args) {
        attempts += 1
        return Reflect.apply(target, thisArg, args)
      },
    })
    try {
      const schema = z.object({
        phone: z.string().min(3),
        n: z.number().int(),
        tags: z.array(z.string()),
      })
      expect(schema.parse({ phone: '+8801712345678', n: 3, tags: ['a'] }).n).toBe(3)
    } finally {
      globalThis.Function = Original
    }
    expect(attempts).toBe(0) // any attempt is a CSP violation report in the browser
  })

  it('still rejects invalid input (jitless is only the execution strategy, not the rules)', () => {
    const schema = z.object({ n: z.number().int().min(1) })
    expect(schema.safeParse({ n: 0 }).success).toBe(false)
    expect(schema.safeParse({ n: 'x' }).success).toBe(false)
    expect(schema.safeParse(null).success).toBe(false)
    expect(schema.safeParse({}).success).toBe(false)
  })
})
