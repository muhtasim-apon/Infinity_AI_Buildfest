import { Slot } from '@radix-ui/react-slot'
import { cva, type VariantProps } from 'class-variance-authority'
import { LoaderCircle } from 'lucide-react'
import { forwardRef, type ButtonHTMLAttributes } from 'react'
import { cn } from '../../lib/cn'

/**
 * Button (spec 15.3). Sizes keep the touch-target rules: >= 44 px everywhere, >= 48 px in the
 * farmer app, and the farmer's single primary action is `xl-farmer` (>= 56 px, spec 15.5.1).
 * Heights are `min-h` so Bangla text at 130% size wraps instead of clipping (CC-40).
 */
export const buttonVariants = cva(
  [
    'relative inline-flex items-center justify-center gap-2 rounded-md text-center font-semibold',
    'transition-[color,background-color,border-color,box-shadow,transform] duration-fast ease-standard',
    'motion-ok:hover:-translate-y-px motion-ok:hover:shadow-sm motion-ok:active:scale-[0.97]',
    'disabled:pointer-events-none disabled:opacity-60 aria-disabled:pointer-events-none aria-disabled:opacity-60',
  ],
  {
    variants: {
      variant: {
        primary: 'bg-primary text-primary-on hover:bg-primary-hover',
        secondary: 'bg-primary-soft text-primary hover:bg-surface-2',
        outline: 'border border-border bg-surface text-text hover:bg-surface-2',
        ghost: 'text-text hover:bg-surface-2',
        destructive: 'bg-danger text-primary-on hover:opacity-90',
        link: 'min-h-0 px-0 text-primary underline underline-offset-4 hover:text-primary-hover',
      },
      size: {
        sm: 'min-h-[44px] px-3 text-sm',
        md: 'min-h-[48px] px-4',
        lg: 'min-h-[52px] px-6 text-lg',
        'xl-farmer': 'min-h-[56px] w-full px-6 text-lg',
        icon: 'min-h-[44px] min-w-[44px] p-0',
      },
    },
    defaultVariants: { variant: 'primary', size: 'md' },
  },
)

export interface ButtonProps
  extends ButtonHTMLAttributes<HTMLButtonElement>, VariantProps<typeof buttonVariants> {
  /** Render the child element (e.g. a router <Link>) with button styling. */
  asChild?: boolean
  /** Shows a spinner, disables the button and keeps its width (the label stays, invisible). */
  loading?: boolean
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(function Button(
  { className, variant, size, asChild = false, loading = false, disabled, children, ...rest },
  ref,
) {
  const classes = cn(buttonVariants({ variant, size }), className)
  if (asChild) {
    return (
      <Slot ref={ref} className={classes} {...rest}>
        {children}
      </Slot>
    )
  }
  return (
    <button
      ref={ref}
      // type defaults to "button": a button inside a form must never submit by accident
      type={rest.type ?? 'button'}
      className={classes}
      disabled={disabled || loading}
      aria-busy={loading || undefined}
      {...rest}
    >
      <span className={cn('inline-flex items-center justify-center gap-2', loading && 'invisible')}>
        {children}
      </span>
      {loading ? (
        <span className="absolute inset-0 flex items-center justify-center" aria-hidden="true">
          <LoaderCircle className="h-5 w-5 motion-ok:animate-spin" />
        </span>
      ) : null}
    </button>
  )
})

export type IconButtonProps = Omit<ButtonProps, 'size' | 'children' | 'aria-label'> & {
  /** Icon-only buttons have no visible text, so an accessible name is mandatory (spec 15.3). */
  'aria-label': string
  children: ButtonProps['children']
}

export const IconButton = forwardRef<HTMLButtonElement, IconButtonProps>(function IconButton(
  { variant = 'ghost', ...rest },
  ref,
) {
  return <Button ref={ref} variant={variant} size="icon" {...rest} />
})
