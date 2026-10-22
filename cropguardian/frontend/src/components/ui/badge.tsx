import { cva, type VariantProps } from 'class-variance-authority'
import { CircleAlert, CircleCheck, CircleX, FlaskConical, Info } from 'lucide-react'
import type { HTMLAttributes, ReactNode } from 'react'
import { useTranslation } from 'react-i18next'
import { cn } from '../../lib/cn'

/**
 * Status is never carried by colour alone (spec 15.8): every tone has its own icon AND text.
 */
const badgeVariants = cva(
  'inline-flex min-h-[28px] items-center gap-1.5 rounded-full px-2.5 py-0.5 text-sm font-medium',
  {
    variants: {
      tone: {
        neutral: 'bg-surface-2 text-text',
        success: 'bg-success-bg text-success',
        warning: 'bg-warning-bg text-warning',
        danger: 'bg-danger-bg text-danger',
        info: 'bg-sky-bg text-sky',
        simulated: 'bg-simulated-bg text-simulated',
      },
    },
    defaultVariants: { tone: 'neutral' },
  },
)

export type BadgeTone = NonNullable<VariantProps<typeof badgeVariants>['tone']>

/** The tone's icon, already rendered: the lookup returns an element, not a component type. */
function toneIcon(tone: BadgeTone) {
  const props = { className: 'h-4 w-4 shrink-0', 'aria-hidden': true } as const
  switch (tone) {
    case 'success':
      return <CircleCheck {...props} />
    case 'warning':
      return <CircleAlert {...props} />
    case 'danger':
      return <CircleX {...props} />
    case 'simulated':
      return <FlaskConical {...props} />
    default:
      return <Info {...props} />
  }
}

export interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  tone?: BadgeTone
  /** Visible label. Required content: a badge without text would be colour-only. */
  children: ReactNode
}

export function Badge({ tone = 'neutral', className, children, ...rest }: BadgeProps) {
  return (
    <span className={cn(badgeVariants({ tone }), className)} {...rest}>
      {toneIcon(tone)}
      <span>{children}</span>
    </span>
  )
}

/**
 * The purple SIMULATED / DEMO DATA label (spec 0.2.6): shown on every component that renders
 * demo-tenant or simulated data. check_honesty.py fails a component that renders demo data without it.
 */
export function SimulatedBadge({ className }: { className?: string }) {
  const { t } = useTranslation()
  return (
    <Badge tone="simulated" className={cn('font-semibold uppercase', className)} data-simulated>
      {t('demo.simulated')}
    </Badge>
  )
}
