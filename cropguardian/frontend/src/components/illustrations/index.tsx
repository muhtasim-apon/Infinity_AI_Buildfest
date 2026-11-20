import { motion } from 'framer-motion'
import type { ReactNode } from 'react'
import { duration, ease } from '../../design/motion'
import { useMotionPolicy } from '../../design/useMotion'
import { cn } from '../../lib/cn'

/**
 * Team-drawn illustration set (spec 15.5.2: icons and pictures carry meaning, text supports them; no
 * copyrighted photos). Flat shapes in the brand tones, coloured only through theme utilities
 * (`fill-primary`, `fill-accent`...) so every scene follows light/dark mode and the contrast tokens.
 * Decorative by default (`aria-hidden`): the surrounding text carries the meaning.
 *
 * The signature device is the camera VIEWFINDER BRACKET: the four corner marks of the scan frame.
 * It is the product's one action (point at a leaf), so it recurs on the hero, empty states and loaders.
 */

interface IllustrationProps {
  className?: string
  /** Set only when the picture carries information that the text next to it does not. */
  title?: string
}

function Frame({ className, title, children }: IllustrationProps & { children: ReactNode }) {
  return (
    <svg
      viewBox="0 0 160 160"
      fill="none"
      className={cn('h-auto w-full', className)}
      role={title ? 'img' : undefined}
      aria-hidden={title ? undefined : true}
      aria-label={title}
      focusable="false"
    >
      {children}
    </svg>
  )
}

/** One leaf, symmetric, 108 px tall; reused by several scenes. */
const LEAF = 'M80 22C108 46 118 84 80 130C42 84 52 46 80 22Z'
const VEINS = 'M80 58L64 46M80 58L96 46M80 78L60 64M80 78L100 64M80 98L64 86M80 98L96 86'

function Leaf({ transform, tone = 'fill-primary' }: { transform?: string; tone?: string }) {
  return (
    <g transform={transform}>
      <path d={LEAF} className={tone} />
      <path
        d="M80 34V124"
        className="stroke-primary-on"
        strokeWidth="3"
        strokeLinecap="round"
        opacity="0.55"
      />
      <path
        d={VEINS}
        className="stroke-primary-on"
        strokeWidth="2.5"
        strokeLinecap="round"
        opacity="0.4"
      />
    </g>
  )
}

/** Hero scene: a leaf inside the camera viewfinder, with the disease spots the scan finds. */
export function LeafScan(props: IllustrationProps) {
  return (
    <Frame {...props}>
      <circle cx="80" cy="80" r="72" className="fill-primary-soft" />
      <Leaf />
      <circle cx="70" cy="72" r="5.5" className="fill-accent" />
      <circle cx="93" cy="98" r="4.5" className="fill-accent" />
      <circle cx="86" cy="62" r="3" className="fill-accent" opacity="0.8" />
      <path
        d="M22 44V22H44M116 22H138V44M22 116V138H44M116 138H138V116"
        className="stroke-accent"
        strokeWidth="6"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </Frame>
  )
}

/** Alerts: a phone showing a warning, with signal arcs. */
export function PhoneAlert(props: IllustrationProps) {
  return (
    <Frame {...props}>
      <circle cx="80" cy="80" r="72" className="fill-warning-bg" />
      <rect
        x="46"
        y="18"
        width="68"
        height="124"
        rx="14"
        className="fill-surface stroke-border"
        strokeWidth="3"
      />
      <rect x="70" y="24" width="20" height="4" rx="2" className="fill-border" />
      <rect x="54" y="36" width="52" height="88" rx="8" className="fill-warning-bg" />
      <path d="M80 54L98 88H62Z" className="fill-warning" strokeLinejoin="round" />
      <path d="M80 66V77" className="stroke-surface" strokeWidth="4" strokeLinecap="round" />
      <circle cx="80" cy="83" r="2.4" className="fill-surface" />
      <rect x="62" y="98" width="36" height="5" rx="2.5" className="fill-border" />
      <rect x="68" y="108" width="24" height="5" rx="2.5" className="fill-border" />
      <path
        d="M30 62C24 74 24 88 30 100M130 62C136 74 136 88 130 100"
        className="stroke-warning"
        strokeWidth="4"
        strokeLinecap="round"
        opacity="0.55"
      />
      <path
        d="M20 54C10 72 10 90 20 108M140 54C150 72 150 90 140 108"
        className="stroke-warning"
        strokeWidth="3"
        strokeLinecap="round"
        opacity="0.3"
      />
    </Frame>
  )
}

function Stalk({ x, y, s = 1, tone }: { x: number; y: number; s?: number; tone: string }) {
  return (
    <g transform={`translate(${x} ${y}) scale(${s})`}>
      <path d="M0 0C-3 -14 -8 -26 -13 -34C-3 -30 3 -18 0 0Z" className={tone} />
      <path d="M0 0C3 -16 9 -28 15 -36C5 -30 -2 -16 0 0Z" className={tone} />
      <path d="M0 0C-1 -18 1 -30 2 -42C6 -30 4 -16 0 0Z" className={tone} />
    </g>
  )
}

/** Field: sun over rows of rice. */
export function PaddyField(props: IllustrationProps) {
  const near = [18, 46, 74, 102, 130]
  const far = [32, 60, 88, 116, 144]
  return (
    <Frame {...props}>
      <rect x="4" y="12" width="152" height="136" rx="24" className="fill-sky-bg" />
      <circle cx="118" cy="48" r="26" className="fill-accent" opacity="0.22" />
      <circle cx="118" cy="48" r="16" className="fill-accent" />
      <path
        d="M4 104C40 92 84 112 156 98V124C156 138 146 148 132 148H28C14 148 4 138 4 124Z"
        className="fill-primary-soft"
      />
      {far.map((x) => (
        <Stalk key={`f${x}`} x={x} y={118} s={0.78} tone="fill-success" />
      ))}
      {near.map((x) => (
        <Stalk key={`n${x}`} x={x} y={140} tone="fill-primary" />
      ))}
    </Frame>
  )
}

/** Protection: a shield with a leaf. */
export function ShieldLeaf(props: IllustrationProps) {
  return (
    <Frame {...props}>
      <circle cx="80" cy="80" r="72" className="fill-primary-soft" />
      <path
        d="M80 16L128 33V78C128 108 108 130 80 144C52 130 32 108 32 78V33Z"
        className="fill-primary"
      />
      <path
        d="M80 28L118 41V78C118 101 103 119 80 131C57 119 42 101 42 78V41Z"
        className="stroke-primary-on"
        strokeWidth="2"
        opacity="0.35"
      />
      <Leaf transform="translate(40 38) scale(0.5)" tone="fill-primary-on" />
      <circle cx="122" cy="30" r="6" className="fill-accent" />
    </Frame>
  )
}

/** Empty lists: a leaf under a magnifying glass. */
export function MagnifierLeaf(props: IllustrationProps) {
  return (
    <Frame {...props}>
      <circle cx="80" cy="80" r="72" className="fill-surface-2" />
      <Leaf transform="translate(-14 4) scale(0.92)" />
      <circle
        cx="104"
        cy="92"
        r="28"
        className="fill-sky-bg stroke-sky"
        strokeWidth="7"
        opacity="0.96"
      />
      <path d="M124 113L142 132" className="stroke-sky" strokeWidth="10" strokeLinecap="round" />
      <path
        d="M92 82C95 76 102 74 108 76"
        className="stroke-sky"
        strokeWidth="3"
        strokeLinecap="round"
        opacity="0.5"
      />
    </Frame>
  )
}

/** Server error: a drooping leaf. */
export function WiltedLeaf(props: IllustrationProps) {
  return (
    <Frame {...props}>
      <circle cx="80" cy="80" r="72" className="fill-danger-bg" />
      <path
        d="M62 134V84C62 62 84 54 104 62"
        className="stroke-primary"
        strokeWidth="7"
        strokeLinecap="round"
      />
      <path d="M104 62C128 58 140 86 122 104C108 98 98 82 104 62Z" className="fill-accent" />
      <path
        d="M62 112C48 110 38 98 40 84C54 86 62 96 62 112Z"
        className="fill-primary"
        opacity="0.75"
      />
      <ellipse cx="62" cy="136" rx="30" ry="6" className="fill-border" />
      <path d="M118 124l-5 11a5.5 5.5 0 1 0 10 0Z" className="fill-sky" opacity="0.85" />
    </Frame>
  )
}

/** Not found: a leaf and a question mark. */
export function LostLeaf(props: IllustrationProps) {
  return (
    <Frame {...props}>
      <circle cx="80" cy="80" r="72" className="fill-surface-2" />
      <Leaf transform="translate(-10 14) rotate(-18 80 80)" />
      <circle cx="112" cy="50" r="22" className="fill-accent-bg stroke-accent" strokeWidth="4" />
      <path
        d="M103 45C103 36 121 36 121 45C121 52 112 52 112 60"
        className="stroke-accent"
        strokeWidth="5"
        strokeLinecap="round"
      />
      <circle cx="112" cy="68" r="3.2" className="fill-accent" />
    </Frame>
  )
}

/** Offline: a cloud with a slash. */
export function OfflineLeaf(props: IllustrationProps) {
  return (
    <Frame {...props}>
      <circle cx="80" cy="80" r="72" className="fill-sky-bg" />
      <path
        d="M50 112H112C128 112 138 98 132 84C127 72 112 70 104 77C99 59 78 52 64 62C50 56 34 68 38 84C24 88 26 112 50 112Z"
        className="fill-surface stroke-sky"
        strokeWidth="5"
        strokeLinejoin="round"
      />
      <path d="M42 36L124 130" className="stroke-danger" strokeWidth="7" strokeLinecap="round" />
      <path
        d="M45 33L127 127"
        className="stroke-surface"
        strokeWidth="2"
        strokeLinecap="round"
        opacity="0.6"
      />
    </Frame>
  )
}

/** Forbidden: a padlock. */
export function LockLeaf(props: IllustrationProps) {
  return (
    <Frame {...props}>
      <circle cx="80" cy="80" r="72" className="fill-surface-2" />
      <path
        d="M60 78V62C60 38 100 38 100 62V78"
        className="stroke-primary"
        strokeWidth="9"
        strokeLinecap="round"
      />
      <rect x="46" y="76" width="68" height="54" rx="12" className="fill-primary" />
      <circle cx="80" cy="100" r="7" className="fill-primary-on" />
      <rect x="77" y="104" width="6" height="14" rx="3" className="fill-primary-on" />
      <circle cx="118" cy="40" r="6" className="fill-accent" />
    </Frame>
  )
}

export const ILLUSTRATION_NAMES = [
  'leafScan',
  'phoneAlert',
  'paddyField',
  'shieldLeaf',
  'magnifierLeaf',
  'wiltedLeaf',
  'lostLeaf',
  'offlineLeaf',
  'lockLeaf',
] as const

export type IllustrationName = (typeof ILLUSTRATION_NAMES)[number]

/** Render by name. A switch (not a lookup table) keeps every scene a statically known component. */
export function Illustration({ name, ...rest }: IllustrationProps & { name: IllustrationName }) {
  switch (name) {
    case 'leafScan':
      return <LeafScan {...rest} />
    case 'phoneAlert':
      return <PhoneAlert {...rest} />
    case 'paddyField':
      return <PaddyField {...rest} />
    case 'shieldLeaf':
      return <ShieldLeaf {...rest} />
    case 'magnifierLeaf':
      return <MagnifierLeaf {...rest} />
    case 'wiltedLeaf':
      return <WiltedLeaf {...rest} />
    case 'lostLeaf':
      return <LostLeaf {...rest} />
    case 'offlineLeaf':
      return <OfflineLeaf {...rest} />
    default:
      return <LockLeaf {...rest} />
  }
}

const CORNERS = [
  'left-0 top-0 border-l-[3px] border-t-[3px] rounded-tl-md',
  'right-0 top-0 border-r-[3px] border-t-[3px] rounded-tr-md',
  'bottom-0 left-0 border-b-[3px] border-l-[3px] rounded-bl-md',
  'bottom-0 right-0 border-b-[3px] border-r-[3px] rounded-br-md',
] as const

/**
 * The viewfinder brackets as a frame around any content. The marks ease in from slightly outside
 * (200 ms, spec 15.2 "camera viewfinder"); under reduced motion they simply appear.
 */
export function BracketFrame({
  children,
  className,
  size = 'md',
}: {
  children: ReactNode
  className?: string
  size?: 'sm' | 'md'
}) {
  const { reduced } = useMotionPolicy()
  const dim = size === 'sm' ? 'h-4 w-4' : 'h-6 w-6'
  return (
    <div className={cn('relative', className)}>
      {children}
      {CORNERS.map((corner) => (
        <motion.span
          key={corner}
          aria-hidden="true"
          className={cn('pointer-events-none absolute border-accent', dim, corner)}
          initial={reduced ? false : { opacity: 0, scale: 1.25 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: duration.base, ease: ease.standard }}
        />
      ))}
    </div>
  )
}

/** The brand mark (the favicon): paddy-green tile, white leaf, gold sun. */
export function LogoMark({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 64 64"
      className={cn('h-8 w-8', className)}
      aria-hidden="true"
      focusable="false"
    >
      <rect width="64" height="64" rx="14" className="fill-primary" />
      <path
        d="M32 11c-9.5 8.2-15 16.6-15 26 0 8.4 6.4 15 15 15s15-6.6 15-15c0-9.4-5.5-17.8-15-26z"
        className="fill-primary-on"
      />
      <path
        d="M32 24v27M32 36l-7.5-6.5M32 43l7.5-6.5"
        className="stroke-primary"
        strokeWidth="3"
        strokeLinecap="round"
        fill="none"
      />
      <circle cx="48" cy="16" r="5.5" className="fill-accent" />
    </svg>
  )
}
