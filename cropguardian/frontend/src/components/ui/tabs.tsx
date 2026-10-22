import * as RadioGroup from '@radix-ui/react-radio-group'
import * as TabsPrimitive from '@radix-ui/react-tabs'
import { motion } from 'framer-motion'
import {
  createContext,
  useContext,
  useId,
  useState,
  type ComponentPropsWithoutRef,
  type ReactNode,
} from 'react'
import { duration, ease, instantTransition } from '../../design/motion'
import { useMotionPolicy } from '../../design/useMotion'
import { cn } from '../../lib/cn'

/** Shared state so the sliding indicator (one element moving between triggers) knows who is active. */
const IndicatorContext = createContext<{ value: string; group: string } | null>(null)

function useIndicator() {
  const policy = useMotionPolicy()
  return {
    transition: policy.reduced
      ? instantTransition
      : { duration: duration.base, ease: ease.standard },
  }
}

export interface TabsProps {
  value?: string
  defaultValue: string
  onValueChange?: (value: string) => void
  children: ReactNode
  className?: string
}

export function Tabs({ value, defaultValue, onValueChange, children, className }: TabsProps) {
  const [inner, setInner] = useState(defaultValue)
  const group = useId()
  const current = value ?? inner
  return (
    <IndicatorContext.Provider value={{ value: current, group }}>
      <TabsPrimitive.Root
        value={current}
        onValueChange={(next) => {
          setInner(next)
          onValueChange?.(next)
        }}
        className={className}
      >
        {children}
      </TabsPrimitive.Root>
    </IndicatorContext.Provider>
  )
}

export function TabsList({
  className,
  ...rest
}: ComponentPropsWithoutRef<typeof TabsPrimitive.List>) {
  return (
    <TabsPrimitive.List className={cn('flex gap-1 border-b border-border', className)} {...rest} />
  )
}

export function TabsTrigger({
  value,
  children,
  className,
  ...rest
}: ComponentPropsWithoutRef<typeof TabsPrimitive.Trigger>) {
  const ctx = useContext(IndicatorContext)
  const { transition } = useIndicator()
  const active = ctx?.value === value
  return (
    <TabsPrimitive.Trigger
      value={value}
      className={cn(
        'relative min-h-[44px] px-4 font-medium text-muted transition-colors duration-fast ease-standard',
        'hover:text-text data-[state=active]:text-primary',
        className,
      )}
      {...rest}
    >
      {children}
      {active ? (
        <motion.span
          layoutId={`tab-indicator-${ctx?.group ?? ''}`}
          transition={transition}
          className="absolute inset-x-0 -bottom-px h-0.5 bg-primary"
          aria-hidden="true"
        />
      ) : null}
    </TabsPrimitive.Trigger>
  )
}

export function TabsContent({
  className,
  ...rest
}: ComponentPropsWithoutRef<typeof TabsPrimitive.Content>) {
  return <TabsPrimitive.Content className={cn('pt-4', className)} {...rest} />
}

export interface SegmentedOption {
  value: string
  label: string
}

/** Segmented control (radio semantics): a short, always-visible choice such as Farmers / Services / NGOs. */
export function SegmentedControl({
  options,
  value,
  onValueChange,
  'aria-label': ariaLabel,
  className,
}: {
  options: SegmentedOption[]
  value: string
  onValueChange: (value: string) => void
  'aria-label': string
  className?: string
}) {
  const group = useId()
  const { transition } = useIndicator()
  return (
    <RadioGroup.Root
      value={value}
      onValueChange={onValueChange}
      aria-label={ariaLabel}
      orientation="horizontal"
      className={cn('inline-flex rounded-lg border border-border bg-surface-2 p-1', className)}
    >
      {options.map((option) => (
        <RadioGroup.Item
          key={option.value}
          value={option.value}
          className="relative min-h-[44px] rounded-md px-4 font-medium text-muted data-[state=checked]:text-primary"
        >
          {value === option.value ? (
            <motion.span
              layoutId={`segment-${group}`}
              transition={transition}
              className="absolute inset-0 rounded-md bg-surface shadow-xs"
              aria-hidden="true"
            />
          ) : null}
          <span className="relative">{option.label}</span>
        </RadioGroup.Item>
      ))}
    </RadioGroup.Root>
  )
}
