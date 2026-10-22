import * as CheckboxPrimitive from '@radix-ui/react-checkbox'
import * as RadioGroup from '@radix-ui/react-radio-group'
import * as SliderPrimitive from '@radix-ui/react-slider'
import * as SwitchPrimitive from '@radix-ui/react-switch'
import { Check, ChevronDown, type LucideIcon } from 'lucide-react'
import { forwardRef, useId, type ReactNode, type SelectHTMLAttributes } from 'react'
import { cn } from '../../lib/cn'

/** Switch with its label: the whole row is the >= 44 px touch target (spec 15.1). */
export function SwitchField({
  label,
  description,
  checked,
  onCheckedChange,
  disabled,
  className,
}: {
  label: string
  description?: string
  checked: boolean
  onCheckedChange: (checked: boolean) => void
  disabled?: boolean
  className?: string
}) {
  const id = useId()
  const descId = `${id}-desc`
  return (
    <div className={cn('flex min-h-[48px] items-center justify-between gap-4 py-1', className)}>
      <label htmlFor={id} className="flex-1">
        <span className="block font-medium">{label}</span>
        {description ? (
          <span id={descId} className="block text-sm text-muted">
            {description}
          </span>
        ) : null}
      </label>
      <SwitchPrimitive.Root
        id={id}
        checked={checked}
        onCheckedChange={onCheckedChange}
        disabled={disabled}
        aria-describedby={description ? descId : undefined}
        className="relative inline-flex h-8 w-14 shrink-0 items-center rounded-full border border-border bg-surface-2 transition-colors duration-fast ease-standard data-[state=checked]:border-primary data-[state=checked]:bg-primary disabled:opacity-60"
      >
        <SwitchPrimitive.Thumb className="block h-6 w-6 translate-x-1 rounded-full bg-surface shadow-sm transition-transform duration-fast ease-standard data-[state=checked]:translate-x-7 data-[state=checked]:bg-primary-on" />
      </SwitchPrimitive.Root>
    </div>
  )
}

export function CheckboxField({
  label,
  description,
  checked,
  onCheckedChange,
  disabled,
  required,
  className,
}: {
  label: ReactNode
  description?: string
  checked: boolean
  onCheckedChange: (checked: boolean) => void
  disabled?: boolean
  required?: boolean
  className?: string
}) {
  const id = useId()
  return (
    <div className={cn('flex min-h-[48px] items-start gap-3 py-2', className)}>
      <CheckboxPrimitive.Root
        id={id}
        checked={checked}
        onCheckedChange={(next) => onCheckedChange(next === true)}
        disabled={disabled}
        required={required}
        className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-sm border-2 border-border bg-surface transition-colors duration-fast ease-standard data-[state=checked]:border-primary data-[state=checked]:bg-primary disabled:opacity-60"
      >
        <CheckboxPrimitive.Indicator>
          <Check className="h-4 w-4 text-primary-on" aria-hidden="true" />
        </CheckboxPrimitive.Indicator>
      </CheckboxPrimitive.Root>
      <label htmlFor={id} className="flex-1">
        <span className="block">{label}</span>
        {description ? <span className="block text-sm text-muted">{description}</span> : null}
      </label>
    </div>
  )
}

export interface RadioCardOption {
  value: string
  label: string
  description?: string
  icon?: LucideIcon
}

/** Large selectable cards (role picker, radius chips): radio semantics, icon + text, >= 56 px. */
export function RadioCards({
  options,
  value,
  onValueChange,
  'aria-label': ariaLabel,
  className,
}: {
  options: RadioCardOption[]
  value: string
  onValueChange: (value: string) => void
  'aria-label': string
  className?: string
}) {
  return (
    <RadioGroup.Root
      value={value}
      onValueChange={onValueChange}
      aria-label={ariaLabel}
      className={cn('grid gap-3 sm:grid-cols-2', className)}
    >
      {options.map((option) => {
        const Icon = option.icon
        return (
          <RadioGroup.Item
            key={option.value}
            value={option.value}
            className="flex min-h-[56px] items-start gap-3 rounded-lg border-2 border-border bg-surface p-4 text-start transition-colors duration-fast ease-standard hover:bg-surface-2 data-[state=checked]:border-primary data-[state=checked]:bg-primary-soft"
          >
            {Icon ? (
              <Icon className="mt-0.5 h-6 w-6 shrink-0 text-primary" aria-hidden="true" />
            ) : null}
            <span>
              <span className="block font-semibold">{option.label}</span>
              {option.description ? (
                <span className="block text-sm text-muted">{option.description}</span>
              ) : null}
            </span>
          </RadioGroup.Item>
        )
      })}
    </RadioGroup.Root>
  )
}

/** Slider with a visible value label (spec 15.3); `formatValue` formats for the locale. */
export function SliderField({
  label,
  value,
  min,
  max,
  step = 1,
  onValueChange,
  formatValue,
  className,
}: {
  label: string
  value: number
  min: number
  max: number
  step?: number
  onValueChange: (value: number) => void
  formatValue: (value: number) => string
  className?: string
}) {
  const id = useId()
  const safe = Math.min(max, Math.max(min, Number.isFinite(value) ? value : min))
  return (
    <div className={cn('py-2', className)}>
      <div className="flex items-baseline justify-between">
        <label id={id} className="font-medium">
          {label}
        </label>
        <output aria-live="off" className="tabular-nums text-muted">
          {formatValue(safe)}
        </output>
      </div>
      <SliderPrimitive.Root
        value={[safe]}
        min={min}
        max={max}
        step={step}
        onValueChange={([next]) => {
          if (next !== undefined) onValueChange(next)
        }}
        aria-labelledby={id}
        className="relative mt-3 flex h-6 w-full touch-none items-center"
      >
        <SliderPrimitive.Track className="relative h-2 grow rounded-full bg-surface-2">
          <SliderPrimitive.Range className="absolute h-full rounded-full bg-primary" />
        </SliderPrimitive.Track>
        <SliderPrimitive.Thumb
          aria-labelledby={id}
          className="block h-6 w-6 rounded-full border-2 border-primary bg-surface shadow-sm"
        />
      </SliderPrimitive.Root>
    </div>
  )
}

/**
 * Native <select>: the best control on a low-end Android phone and fully keyboard/screen-reader
 * accessible. Used instead of Radix Select (D-025). Pair with FormField for label and errors.
 */
export const NativeSelect = forwardRef<
  HTMLSelectElement,
  SelectHTMLAttributes<HTMLSelectElement> & {
    options: { value: string; label: string }[]
    invalid?: boolean
  }
>(function NativeSelect({ options, invalid, className, ...rest }, ref) {
  return (
    <div className="relative">
      <select
        ref={ref}
        aria-invalid={invalid || undefined}
        className={cn(
          'block min-h-[48px] w-full appearance-none rounded-md border bg-surface ps-3 pe-10 text-text disabled:opacity-60',
          invalid ? 'border-danger' : 'border-border',
          className,
        )}
        {...rest}
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      <ChevronDown
        className="pointer-events-none absolute end-3 top-1/2 h-5 w-5 -translate-y-1/2 text-muted"
        aria-hidden="true"
      />
    </div>
  )
})
