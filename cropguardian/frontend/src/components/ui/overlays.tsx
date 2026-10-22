import * as DropdownMenuPrimitive from '@radix-ui/react-dropdown-menu'
import * as PopoverPrimitive from '@radix-ui/react-popover'
import * as TooltipPrimitive from '@radix-ui/react-tooltip'
import type { ReactNode } from 'react'
import { TOOLTIP_DELAY_MS } from '../../design/motion'
import { cn } from '../../lib/cn'

const surface = 'z-50 rounded-md border border-border bg-surface p-2 text-text shadow-md'

/**
 * Tooltip: supplementary text only (relative time -> exact time). Anything essential must also be
 * visible without hover, because touch users never see tooltips.
 */
export function Tooltip({ content, children }: { content: ReactNode; children: ReactNode }) {
  return (
    <TooltipPrimitive.Provider delayDuration={TOOLTIP_DELAY_MS}>
      <TooltipPrimitive.Root>
        <TooltipPrimitive.Trigger asChild>{children}</TooltipPrimitive.Trigger>
        <TooltipPrimitive.Portal>
          <TooltipPrimitive.Content sideOffset={6} className={cn(surface, 'px-3 py-1.5 text-sm')}>
            {content}
          </TooltipPrimitive.Content>
        </TooltipPrimitive.Portal>
      </TooltipPrimitive.Root>
    </TooltipPrimitive.Provider>
  )
}

/**
 * Popover is NON-modal on purpose (DECISIONS D-025): the modal variant pulls in react-remove-scroll,
 * which injects a <style> element the strict CSP blocks. Non-modal still closes on Escape/outside click.
 */
export function Popover({
  trigger,
  children,
  className,
}: {
  trigger: ReactNode
  children: ReactNode
  className?: string
}) {
  return (
    <PopoverPrimitive.Root modal={false}>
      <PopoverPrimitive.Trigger asChild>{trigger}</PopoverPrimitive.Trigger>
      <PopoverPrimitive.Portal>
        <PopoverPrimitive.Content sideOffset={6} className={cn(surface, 'p-4', className)}>
          {children}
        </PopoverPrimitive.Content>
      </PopoverPrimitive.Portal>
    </PopoverPrimitive.Root>
  )
}

export interface MenuItem {
  id: string
  label: string
  onSelect: () => void
  destructive?: boolean
  disabled?: boolean
}

/** Dropdown menu, non-modal for the same CSP reason as Popover. Items are >= 44 px tall. */
export function DropdownMenu({ trigger, items }: { trigger: ReactNode; items: MenuItem[] }) {
  return (
    <DropdownMenuPrimitive.Root modal={false}>
      <DropdownMenuPrimitive.Trigger asChild>{trigger}</DropdownMenuPrimitive.Trigger>
      <DropdownMenuPrimitive.Portal>
        <DropdownMenuPrimitive.Content
          align="end"
          sideOffset={6}
          className={cn(surface, 'min-w-48')}
        >
          {items.map((item) => (
            <DropdownMenuPrimitive.Item
              key={item.id}
              disabled={item.disabled}
              onSelect={item.onSelect}
              className={cn(
                'flex min-h-[44px] cursor-pointer items-center rounded-sm px-3 outline-none data-[disabled]:opacity-60 data-[highlighted]:bg-surface-2',
                item.destructive && 'text-danger',
              )}
            >
              {item.label}
            </DropdownMenuPrimitive.Item>
          ))}
        </DropdownMenuPrimitive.Content>
      </DropdownMenuPrimitive.Portal>
    </DropdownMenuPrimitive.Root>
  )
}
