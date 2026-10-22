import {
  forwardRef,
  useId,
  type InputHTMLAttributes,
  type ReactNode,
  type TextareaHTMLAttributes,
} from 'react'
import { useTranslation } from 'react-i18next'
import { cn } from '../../lib/cn'
import { formatNumber } from '../../lib/format'
import type { Locale } from '../../i18n'

const control =
  'block w-full min-h-[48px] rounded-md border bg-surface px-3 text-text placeholder:text-subtle ' +
  'transition-[border-color,box-shadow] duration-fast ease-standard disabled:opacity-60'

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  invalid?: boolean
}

export const Input = forwardRef<HTMLInputElement, InputProps>(function Input(
  { className, invalid, ...rest },
  ref,
) {
  return (
    <input
      ref={ref}
      aria-invalid={invalid || undefined}
      className={cn(control, invalid ? 'border-danger' : 'border-border', className)}
      {...rest}
    />
  )
})

export interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  invalid?: boolean
}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(function Textarea(
  { className, invalid, ...rest },
  ref,
) {
  return (
    <textarea
      ref={ref}
      aria-invalid={invalid || undefined}
      className={cn(
        control,
        'min-h-[96px] py-2',
        invalid ? 'border-danger' : 'border-border',
        className,
      )}
      {...rest}
    />
  )
})

/** "12 / 280" character counter; digits follow the locale. Announced politely, not on every key. */
export function CharacterCounter({
  count,
  max,
  locale,
  id,
}: {
  count: number
  max: number
  locale: Locale
  id?: string
}) {
  const over = count > max
  return (
    <p
      id={id}
      className={cn('mt-1 text-end text-sm tabular-nums', over ? 'text-danger' : 'text-muted')}
    >
      {formatNumber(count, locale, 0)} / {formatNumber(max, locale, 0)}
    </p>
  )
}

export interface FieldControlProps {
  id: string
  'aria-describedby'?: string
  'aria-invalid'?: true
  'aria-required'?: true
}

interface FormFieldProps {
  label: string
  hint?: string
  /** Already-translated error text; shown with role="alert" and wired to the control. */
  error?: string
  required?: boolean
  id?: string
  className?: string
  /** Render prop so any control (Input, Textarea, a native select...) gets the right aria wiring. */
  children: (props: FieldControlProps) => ReactNode
}

/** Label + control + hint + error with correct `for`, `aria-describedby`, `aria-invalid` (spec 15.3). */
export function FormField({
  label,
  hint,
  error,
  required,
  id,
  className,
  children,
}: FormFieldProps) {
  const { t } = useTranslation()
  const auto = useId()
  const fieldId = id ?? auto
  const hintId = `${fieldId}-hint`
  const errorId = `${fieldId}-error`
  const describedBy = [hint ? hintId : '', error ? errorId : ''].filter(Boolean).join(' ')
  const props: FieldControlProps = { id: fieldId }
  if (describedBy) props['aria-describedby'] = describedBy
  if (error) props['aria-invalid'] = true
  if (required) props['aria-required'] = true
  return (
    <div className={cn('mt-4', className)}>
      <label htmlFor={fieldId} className="block text-sm font-medium">
        {label}
        {required ? (
          <span className="ms-1 text-danger">
            <span aria-hidden="true">*</span>
            <span className="sr-only">{t('ui.required')}</span>
          </span>
        ) : null}
      </label>
      <div className="mt-1">{children(props)}</div>
      {hint ? (
        <p id={hintId} className="mt-1 text-sm text-muted">
          {hint}
        </p>
      ) : null}
      {error ? (
        <p id={errorId} role="alert" className="mt-1 text-sm text-danger">
          {error}
        </p>
      ) : null}
    </div>
  )
}
