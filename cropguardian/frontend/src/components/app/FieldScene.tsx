import { cn } from '../../lib/cn'

/**
 * Brand scene for heroes and the farmer header: sky, sun, hills, paddy rows and a scarecrow
 * (কাকতাড়ুয়া). Token colours only (CSP + theme safe), decorative (aria-hidden), scales by `slice`
 * so it always fills its container like a photo would.
 */
export function FieldScene({
  className,
  scarecrow = true,
}: {
  className?: string
  scarecrow?: boolean
}) {
  const rows = [
    { y: 250, h: 46, step: 26, cls: 'stroke-success', w: 3 },
    { y: 285, h: 58, step: 30, cls: 'stroke-primary', w: 4 },
    { y: 330, h: 72, step: 34, cls: 'stroke-success', w: 5 },
    { y: 380, h: 88, step: 40, cls: 'stroke-primary', w: 6 },
  ]
  return (
    <svg
      viewBox="0 0 800 420"
      preserveAspectRatio="xMidYMid slice"
      className={cn('h-full w-full', className)}
      aria-hidden="true"
      focusable="false"
    >
      <rect width="800" height="420" className="fill-sky-bg" />
      <rect y="150" width="800" height="270" className="fill-accent-bg" opacity="0.7" />
      <circle cx="520" cy="70" r="56" className="fill-accent" opacity="0.25" />
      <circle cx="520" cy="70" r="34" className="fill-accent" />
      <path d="M0 230 Q160 150 340 205 T700 190 T800 200 V420 H0Z" className="fill-primary-soft" />
      <path d="M0 260 Q220 205 460 250 T800 240 V420 H0Z" className="fill-success" opacity="0.55" />
      <rect y="300" width="800" height="120" className="fill-primary" opacity="0.85" />
      {rows.map((r) =>
        Array.from({ length: Math.ceil(820 / r.step) }, (_, i) => {
          const x = i * r.step + (r.y % 2 ? 6 : 0)
          return (
            <g
              key={`${r.y}-${i}`}
              className={r.cls}
              strokeWidth={r.w}
              strokeLinecap="round"
              fill="none"
            >
              <path d={`M${x} ${r.y} q2 ${-r.h * 0.6} ${-6} ${-r.h}`} />
              <path d={`M${x} ${r.y} q${-10} ${-r.h * 0.45} ${-18} ${-r.h * 0.7}`} />
              <path d={`M${x} ${r.y} q${10} ${-r.h * 0.45} ${16} ${-r.h * 0.75}`} />
            </g>
          )
        }),
      )}
      {scarecrow ? (
        <g transform="translate(345 26) scale(0.68)">
          <rect x="46" y="40" width="8" height="200" rx="3" className="fill-accent" />
          <rect x="-4" y="78" width="108" height="8" rx="3" className="fill-accent" />
          <path d="M18 74 L82 74 L74 150 L26 150 Z" className="fill-danger" />
          <path d="M26 150 L74 150 L78 178 L22 178 Z" className="fill-sky" />
          <circle cx="50" cy="56" r="20" className="fill-accent-bg" />
          <path d="M18 42 L50 8 L82 42 Z" className="fill-warning" />
          <ellipse cx="50" cy="42" rx="40" ry="7" className="fill-accent" />
          <circle cx="43" cy="56" r="2.6" className="fill-text" />
          <circle cx="57" cy="56" r="2.6" className="fill-text" />
          <path d="M42 65 Q50 70 58 65" className="stroke-text" strokeWidth="2" fill="none" />
          <path
            d="M-4 82 l-10 10 M104 82 l10 10"
            className="stroke-accent"
            strokeWidth="4"
            strokeLinecap="round"
          />
        </g>
      ) : null}
    </svg>
  )
}

/** Scarecrow mark used for the logo and favicon. */
export function ScarecrowMark({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 64 64"
      className={cn('h-8 w-8', className)}
      aria-hidden="true"
      focusable="false"
    >
      <rect width="64" height="64" rx="16" className="fill-primary" />
      <rect x="30" y="26" width="4" height="30" rx="2" className="fill-accent" />
      <rect x="12" y="34" width="40" height="4" rx="2" className="fill-accent" />
      <path d="M22 36 L42 36 L39 50 L25 50 Z" className="fill-primary-on" />
      <circle cx="32" cy="26" r="8" className="fill-accent-bg" />
      <path d="M18 22 L32 8 L46 22 Z" className="fill-accent" />
      <ellipse cx="32" cy="22" rx="17" ry="3" className="fill-accent" />
    </svg>
  )
}
