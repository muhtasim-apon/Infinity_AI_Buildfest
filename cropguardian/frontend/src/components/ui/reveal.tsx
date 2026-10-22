import { motion, type Variants } from 'framer-motion'
import type { ElementType, ReactNode } from 'react'
import { useMotionPolicy } from '../../design/useMotion'
import { fadeRise } from '../../design/variants'

const TAGS = new Map<string, unknown>([
  ['div', motion.div],
  ['section', motion.section],
  ['li', motion.li],
  ['article', motion.article],
  ['p', motion.p],
])

/**
 * Enter animation wrapper. Under reduced motion the variants collapse to an opacity-only fade of
 * at most 120 ms (useMotionPolicy), so content is never hidden or delayed by motion.
 */
export function Reveal({
  children,
  variants = fadeRise,
  className,
  as = 'div',
  onView = false,
}: {
  children: ReactNode
  variants?: Variants
  className?: string
  as?: 'div' | 'section' | 'li' | 'article' | 'p'
  /** Animate once when 20% visible (landing sections) instead of on mount. */
  onView?: boolean
}) {
  const { pick } = useMotionPolicy()
  const Tag = (TAGS.get(as) ?? motion.div) as ElementType
  const v = pick(variants)
  return onView ? (
    <Tag
      className={className}
      variants={v}
      initial="hidden"
      whileInView="show"
      viewport={{ once: true, amount: 0.2 }}
    >
      {children}
    </Tag>
  ) : (
    <Tag className={className} variants={v} initial="hidden" animate="show">
      {children}
    </Tag>
  )
}
