import { motion, type Variants } from 'framer-motion'
import type { ElementType, ReactNode } from 'react'
import { useMotionPolicy } from '../../design/useMotion'
import { fadeRise, listContainer } from '../../design/variants'

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

/**
 * A group whose direct `StaggerItem` children enter one after another (35 ms apart, at most 8
 * animated, spec 15.2 "Lists / tables"). Reduced motion keeps the order but drops the movement.
 */
export function Stagger({ children, className }: { children: ReactNode; className?: string }) {
  const { pick } = useMotionPolicy()
  return (
    <motion.div
      className={className}
      variants={pick(listContainer)}
      initial="hidden"
      animate="show"
    >
      {children}
    </motion.div>
  )
}

export function StaggerItem({
  children,
  className,
  as = 'div',
}: {
  children: ReactNode
  className?: string
  as?: 'div' | 'section' | 'li' | 'article'
}) {
  const { pick } = useMotionPolicy()
  const Tag = (TAGS.get(as) ?? motion.div) as ElementType
  return (
    <Tag className={className} variants={pick(fadeRise)}>
      {children}
    </Tag>
  )
}
