import { Inbox, TriangleAlert, type LucideIcon } from 'lucide-react'
import type { HTMLAttributes, ReactNode } from 'react'
import { useTranslation } from 'react-i18next'
import { cn } from '../../lib/cn'
import { Button } from './button'

/**
 * Skeleton: a shimmering placeholder shaped like the final layout (spec 15.13.8). The shimmer only
 * runs when motion is allowed (`motion-ok:`); otherwise it is a static block.
 */
export function Skeleton({ className, ...rest }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      aria-hidden="true"
      className={cn(
        'rounded-md bg-gradient-to-r from-surface-2 via-border to-surface-2 bg-[length:200%_100%] motion-ok:animate-shimmer',
        className,
      )}
      {...rest}
    />
  )
}

/** Announces "loading" once to assistive tech while the (aria-hidden) skeleton shapes are visible. */
export function SkeletonGroup({
  children,
  className,
}: {
  children: ReactNode
  className?: string
}) {
  const { t } = useTranslation()
  return (
    <div role="status" aria-live="polite" aria-busy="true" className={className}>
      <span className="sr-only">{t('common.loading')}</span>
      {children}
    </div>
  )
}

export function SkeletonText({ lines = 3, className }: { lines?: number; className?: string }) {
  const count = Number.isInteger(lines) && lines > 0 ? Math.min(lines, 12) : 3
  return (
    <div className={cn('space-y-2', className)}>
      {Array.from({ length: count }, (_, i) => (
        <Skeleton key={i} className={cn('h-4', i === count - 1 ? 'w-2/3' : 'w-full')} />
      ))}
    </div>
  )
}

export function SkeletonCard({ className }: { className?: string }) {
  return (
    <div className={cn('rounded-lg border border-border bg-surface p-4', className)}>
      <Skeleton className="h-5 w-1/3" />
      <SkeletonText lines={3} className="mt-4" />
    </div>
  )
}

interface StateProps {
  icon?: LucideIcon
  title: string
  description?: string
  action?: ReactNode
  className?: string
}

/** Empty state: icon, title, one line, one action (spec 15.3). Never a blank area. */
export function EmptyState({
  icon: Icon = Inbox,
  title,
  description,
  action,
  className,
}: StateProps) {
  return (
    <div className={cn('flex flex-col items-center px-4 py-10 text-center', className)}>
      <Icon className="h-10 w-10 text-subtle" aria-hidden="true" />
      <p className="mt-3 text-lg font-semibold">{title}</p>
      {description ? <p className="mt-1 max-w-sm text-muted">{description}</p> : null}
      {action ? <div className="mt-4">{action}</div> : null}
    </div>
  )
}

/**
 * Error state: what happened, a retry, and the request id so a farmer can read it to support
 * (spec 15.3, 15.13.8). Wording says what to do, never who is to blame (spec 15.5.8).
 */
export function ErrorState({
  title,
  message,
  requestId,
  onRetry,
  className,
}: {
  title?: string
  message?: string
  requestId?: string
  onRetry?: () => void
  className?: string
}) {
  const { t } = useTranslation()
  return (
    <div
      role="alert"
      className={cn(
        'flex flex-col items-center rounded-lg border border-danger bg-danger-bg px-4 py-8 text-center',
        className,
      )}
    >
      <TriangleAlert className="h-10 w-10 text-danger" aria-hidden="true" />
      <p className="mt-3 text-lg font-semibold text-danger">{title ?? t('errors.generic')}</p>
      {message ? <p className="mt-1 max-w-sm">{message}</p> : null}
      {requestId ? (
        <p className="mt-2 text-xs text-muted">{t('errors.requestId', { id: requestId })}</p>
      ) : null}
      {onRetry ? (
        <Button className="mt-4" variant="outline" onClick={onRetry}>
          {t('common.retry')}
        </Button>
      ) : null}
    </div>
  )
}
