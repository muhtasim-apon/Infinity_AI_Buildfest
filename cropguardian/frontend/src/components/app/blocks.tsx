import type { LucideIcon } from 'lucide-react'
import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'
import { cn } from '../../lib/cn'
import { Card } from '../ui/card'

/** Section title row: a real `h2` and an optional trailing action. */
export function SectionHeader({
  title,
  action,
  className,
}: {
  title: string
  action?: ReactNode
  className?: string
}) {
  return (
    <div className={cn('flex min-h-[44px] items-center justify-between gap-3', className)}>
      <h2 className="text-lg font-semibold">{title}</h2>
      {action}
    </div>
  )
}

/**
 * A quick-action tile: icon in a soft circle above a short label, one tap to a built screen. The icon
 * is decoration; the label is the name (spec 15.5.2).
 */
export function QuickTile({
  to,
  icon: Icon,
  label,
  className,
}: {
  to: string
  icon: LucideIcon
  label: string
  className?: string
}) {
  return (
    <Link to={to} className={cn('block rounded-lg', className)}>
      <Card
        interactive
        className="flex min-h-[104px] flex-col items-center justify-center gap-2 p-3 text-center sm:p-3"
      >
        <span className="flex h-12 w-12 items-center justify-center rounded-full bg-primary-soft text-primary">
          <Icon className="h-6 w-6" aria-hidden="true" />
        </span>
        <span className="font-medium">{label}</span>
      </Card>
    </Link>
  )
}

/** A compact "nothing here yet" card for a section of a page (the full-page version is EmptyState). */
export function InlineEmpty({
  illustration,
  title,
  hint,
}: {
  illustration: ReactNode
  title: string
  hint: string
}) {
  return (
    <Card className="flex items-center gap-4 p-4 sm:p-4">
      <div className="w-20 shrink-0">{illustration}</div>
      <div className="min-w-0">
        <p className="font-semibold">{title}</p>
        <p className="mt-0.5 text-sm text-muted">{hint}</p>
      </div>
    </Card>
  )
}
