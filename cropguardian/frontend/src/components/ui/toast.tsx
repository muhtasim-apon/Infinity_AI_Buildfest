import * as ToastPrimitive from '@radix-ui/react-toast'
import { motion } from 'framer-motion'
import { CircleAlert, CircleCheck, Info, TriangleAlert, X } from 'lucide-react'
import { useSyncExternalStore } from 'react'
import { useTranslation } from 'react-i18next'
import { TOAST_DISMISS_MS } from '../../design/motion'
import { useMotionPolicy } from '../../design/useMotion'
import { toastSlide } from '../../design/variants'
import { cn } from '../../lib/cn'

export type ToastTone = 'success' | 'error' | 'warning' | 'info'

interface ToastItem {
  id: number
  title: string
  description?: string
  tone: ToastTone
}

/** At most this many toasts are on screen; a burst of errors must not bury the page. */
const MAX_VISIBLE = 3

let items: ToastItem[] = []
let nextId = 1
const listeners = new Set<() => void>()

function emit(): void {
  listeners.forEach((l) => l())
}

/** Imperative API: `toast.show({ title })` from anywhere (event handlers, query callbacks). */
export const toast = {
  show(input: { title: string; description?: string; tone?: ToastTone }): number {
    const id = nextId++
    items = [...items.slice(-(MAX_VISIBLE - 1)), { tone: 'info', ...input, id }]
    emit()
    return id
  },
  dismiss(id: number): void {
    items = items.filter((i) => i.id !== id)
    emit()
  },
  clear(): void {
    items = []
    emit()
  },
}

function subscribe(listener: () => void): () => void {
  listeners.add(listener)
  return () => listeners.delete(listener)
}

function useToasts(): ToastItem[] {
  return useSyncExternalStore(
    subscribe,
    () => items,
    () => items,
  )
}

function toneIcon(tone: ToastTone) {
  const props = { className: 'mt-0.5 h-5 w-5 shrink-0', 'aria-hidden': true } as const
  switch (tone) {
    case 'success':
      return <CircleCheck {...props} />
    case 'error':
      return <CircleAlert {...props} />
    case 'warning':
      return <TriangleAlert {...props} />
    default:
      return <Info {...props} />
  }
}

function toneClass(tone: ToastTone): string {
  switch (tone) {
    case 'success':
      return 'border-success text-success'
    case 'error':
      return 'border-danger text-danger'
    case 'warning':
      return 'border-warning text-warning'
    default:
      return 'border-border text-text'
  }
}

/**
 * Toast region. Mount once near the app root. `type="background"` makes Radix announce each toast
 * politely (aria-live="polite", spec 15.8); timers pause on hover and keyboard focus (Radix).
 */
export function Toaster() {
  const { t } = useTranslation()
  const list = useToasts()
  const { pick } = useMotionPolicy()
  return (
    <ToastPrimitive.Provider
      duration={TOAST_DISMISS_MS}
      label={t('ui.notifications')}
      swipeDirection="right"
    >
      {list.map((item) => (
        <ToastPrimitive.Root
          key={item.id}
          type="background"
          onOpenChange={(open) => {
            if (!open) toast.dismiss(item.id)
          }}
          className="group relative overflow-hidden rounded-lg border bg-surface shadow-md"
          asChild
        >
          <motion.li variants={pick(toastSlide)} initial="hidden" animate="show">
            <div className={cn('flex items-start gap-3 p-3 pe-2', toneClass(item.tone))}>
              {toneIcon(item.tone)}
              <div className="min-w-0 flex-1 text-text">
                <ToastPrimitive.Title className="font-semibold">{item.title}</ToastPrimitive.Title>
                {item.description ? (
                  <ToastPrimitive.Description className="mt-0.5 text-sm text-muted">
                    {item.description}
                  </ToastPrimitive.Description>
                ) : null}
              </div>
              <ToastPrimitive.Close
                aria-label={t('common.close')}
                className="inline-flex min-h-[44px] min-w-[44px] items-center justify-center rounded-md text-muted hover:bg-surface-2"
              >
                <X className="h-5 w-5" aria-hidden="true" />
              </ToastPrimitive.Close>
            </div>
            <div className="h-1 bg-surface-2" aria-hidden="true">
              <div
                data-toast-progress
                className="h-full origin-left bg-current text-primary motion-ok:animate-drain motion-ok:group-hover:[animation-play-state:paused]"
                style={{ ['--toast-duration' as string]: `${TOAST_DISMISS_MS}ms` }}
              />
            </div>
          </motion.li>
        </ToastPrimitive.Root>
      ))}
      <ToastPrimitive.Viewport
        label={`${t('ui.notifications')} ({hotkey})`}
        className="fixed inset-x-0 bottom-0 z-50 m-0 flex list-none flex-col gap-2 p-4 outline-none sm:inset-x-auto sm:end-0 sm:w-96"
      />
    </ToastPrimitive.Provider>
  )
}
