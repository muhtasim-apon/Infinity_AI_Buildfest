import { TrendingDown, TrendingUp } from 'lucide-react'
import type { HTMLAttributes, ReactNode } from 'react'
import { cn } from '../../lib/cn'

/** Cards sit on --bg: radius 14, 1 px border, shadow xs (spec 15.13.2). */
export function Card({
  className,
  interactive = false,
  ...rest
}: HTMLAttributes<HTMLDivElement> & { interactive?: boolean }) {
  return (
    <div
      className={cn(
        'rounded-lg border border-border bg-surface p-4 shadow-xs sm:p-6',
        interactive &&
          'transition-[transform,box-shadow,border-color] duration-base ease-standard motion-ok:hover:-translate-y-0.5 hover:border-primary hover:shadow-md',
        className,
      )}
      {...rest}
    />
  )
}

export function CardTitle({ className, children, ...rest }: HTMLAttributes<HTMLHeadingElement>) {
  return (
    <h3 className={cn('text-lg font-semibold', className)} {...rest}>
      {children}
    </h3>
  )
}

export function CardDescription({ className, ...rest }: HTMLAttributes<HTMLParagraphElement>) {
  return <p className={cn('mt-1 text-sm text-muted', className)} {...rest} />
}

/** Tiny inline trend line. Decorative: the numbers carry the meaning, so it is aria-hidden. */
function Sparkline({ values }: { values: number[] }) {
  if (values.length < 2 || values.some((v) => !Number.isFinite(v))) return null
  const min = Math.min(...values)
  const span = Math.max(...values) - min || 1
  const points = values
    .map((v, i) => `${(i / (values.length - 1)) * 100},${24 - ((v - min) / span) * 22 - 1}`)
    .join(' ')
  return (
    <svg
      viewBox="0 0 100 24"
      className="h-6 w-24 text-primary"
      aria-hidden="true"
      focusable="false"
    >
      <polyline fill="none" stroke="currentColor" strokeWidth="2" points={points} />
    </svg>
  )
}

export interface StatCardProps {
  label: string
  /** Already formatted for the locale (use lib/format); never a raw float. */
  value: ReactNode
  /** Signed change text, e.g. "+12". The sign picks the arrow; text is always shown. */
  delta?: string
  /** Optional trend values for the sparkline. */
  trend?: number[]
  /** A "Not yet measured" style note instead of a number (spec 0.2.6). */
  note?: string
  className?: string
}

export function StatCard({ label, value, delta, trend, note, className }: StatCardProps) {
  const negative = delta?.trim().startsWith('-') || delta?.trim().startsWith('−')
  return (
    <Card className={className}>
      <p className="text-sm text-muted">{label}</p>
      <div className="mt-1 flex items-end justify-between gap-3">
        <p className="text-3xl font-semibold tabular-nums">{value}</p>
        {trend ? <Sparkline values={trend} /> : null}
      </div>
      {delta ? (
        <p
          className={cn(
            'mt-1 inline-flex items-center gap-1 text-sm',
            negative ? 'text-danger' : 'text-success',
          )}
        >
          {negative ? (
            <TrendingDown className="h-4 w-4" aria-hidden="true" />
          ) : (
            <TrendingUp className="h-4 w-4" aria-hidden="true" />
          )}
          {delta}
        </p>
      ) : null}
      {note ? <p className="mt-1 text-sm text-muted">{note}</p> : null}
    </Card>
  )
}
