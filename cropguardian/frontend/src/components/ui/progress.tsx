import * as ProgressPrimitive from '@radix-ui/react-progress'
import { motion } from 'framer-motion'
import { Check, Circle, LoaderCircle, type LucideIcon } from 'lucide-react'
import type { ReactNode } from 'react'
import { duration, ease } from '../../design/motion'
import { useMotionPolicy } from '../../design/useMotion'
import { cn } from '../../lib/cn'

function clamp01(n: number): number {
  return Number.isFinite(n) ? Math.min(1, Math.max(0, n)) : 0
}

/** Determinate progress bar (upload, import). `label` is the accessible name. */
export function Progress({
  value,
  label,
  className,
}: {
  /** 0..1 */
  value: number
  label: string
  className?: string
}) {
  const fraction = clamp01(value)
  return (
    <ProgressPrimitive.Root
      value={Math.round(fraction * 100)}
      aria-label={label}
      className={cn('relative h-2 w-full overflow-hidden rounded-full bg-surface-2', className)}
    >
      <ProgressPrimitive.Indicator
        className="h-full bg-primary transition-[width] duration-base ease-standard"
        style={{ width: `${fraction * 100}%` }}
      />
    </ProgressPrimitive.Root>
  )
}

/**
 * Meter (a gauge, not a task): exposes role="meter" with a text alternative via `valueText`,
 * because a coloured bar alone says nothing to a screen reader (spec 15.8).
 */
export function Meter({
  value,
  min = 0,
  max = 1,
  label,
  valueText,
  className,
}: {
  value: number
  min?: number
  max?: number
  label: string
  valueText: string
  className?: string
}) {
  const span = max - min
  const safe = Number.isFinite(value) ? Math.min(max, Math.max(min, value)) : min
  const fraction = span > 0 ? (safe - min) / span : 0
  return (
    <div
      role="meter"
      aria-label={label}
      aria-valuemin={min}
      aria-valuemax={max}
      aria-valuenow={safe}
      aria-valuetext={valueText}
      className={cn('h-2 w-full overflow-hidden rounded-full bg-surface-2', className)}
    >
      <div className="h-full bg-primary" style={{ width: `${fraction * 100}%` }} />
    </div>
  )
}

/**
 * Confidence ring: the stroke draws to its band over 600 ms (spec 15.2 "Result reveal"); under
 * reduced motion it renders at its final state. `label` ("উচ্চ নিশ্চয়তা") is what assistive tech reads.
 */
export function Ring({
  value,
  label,
  size = 96,
  children,
  className,
}: {
  /** 0..1 */
  value: number
  label: string
  size?: number
  children?: ReactNode
  className?: string
}) {
  const { reduced } = useMotionPolicy()
  const fraction = clamp01(value)
  return (
    <div
      role="img"
      aria-label={label}
      className={cn('relative inline-flex items-center justify-center', className)}
      style={{ width: size, height: size }}
    >
      <svg viewBox="0 0 100 100" className="h-full w-full -rotate-90" aria-hidden="true">
        <circle cx="50" cy="50" r="44" fill="none" strokeWidth="8" className="stroke-surface-2" />
        <motion.circle
          cx="50"
          cy="50"
          r="44"
          fill="none"
          strokeWidth="8"
          strokeLinecap="round"
          className="stroke-primary"
          initial={reduced ? false : { pathLength: 0 }}
          animate={{ pathLength: fraction }}
          transition={{ duration: duration.draw, ease: ease.emphasized }}
        />
      </svg>
      {children ? (
        <div className="absolute inset-0 flex items-center justify-center">{children}</div>
      ) : null}
    </div>
  )
}

export type StepState = 'done' | 'current' | 'upcoming'

export interface StepperStep {
  id: string
  label: string
  state: StepState
}

function stepIcon(state: StepState): { icon: LucideIcon; spin: boolean } {
  if (state === 'done') return { icon: Check, spin: false }
  if (state === 'current') return { icon: LoaderCircle, spin: true }
  return { icon: Circle, spin: false }
}

/**
 * Ordered stages (scan progress: photo check -> diagnosis -> advice). States are driven by real
 * events from the caller, never by timers (spec 15.2). Each state has an icon and the current step
 * carries aria-current, so progress is never conveyed by colour alone.
 */
export function Stepper({ steps, className }: { steps: StepperStep[]; className?: string }) {
  return (
    <ol className={cn('flex flex-col gap-2 sm:flex-row sm:gap-4', className)}>
      {steps.map((step) => {
        const { icon: Icon, spin } = stepIcon(step.state)
        return (
          <li
            key={step.id}
            aria-current={step.state === 'current' ? 'step' : undefined}
            data-state={step.state}
            className={cn(
              'flex min-h-[44px] items-center gap-2 rounded-full border px-3 py-1',
              step.state === 'done' && 'border-success bg-success-bg text-success',
              step.state === 'current' && 'border-primary bg-primary-soft text-primary',
              step.state === 'upcoming' && 'border-border text-muted',
            )}
          >
            <Icon
              className={cn('h-4 w-4 shrink-0', spin && 'motion-ok:animate-spin')}
              aria-hidden="true"
            />
            <span>{step.label}</span>
          </li>
        )
      })}
    </ol>
  )
}
