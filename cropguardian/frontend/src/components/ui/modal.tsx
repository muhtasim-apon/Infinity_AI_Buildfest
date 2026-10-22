import { motion, type Variants } from 'framer-motion'
import { X } from 'lucide-react'
import { useEffect, useId, useRef, useState, type ReactNode } from 'react'
import { useTranslation } from 'react-i18next'
import { useMotionPolicy } from '../../design/useMotion'
import { dialogPanel, sheetBottom, sheetSide } from '../../design/variants'
import { cn } from '../../lib/cn'
import { Button, IconButton } from './button'
import { FormField, Input } from './input'

/**
 * Modal surfaces on the native <dialog> element (DECISIONS D-025): `showModal()` gives the focus
 * trap, inert background, Escape handling and top layer without Radix's scroll-lock, which injects a
 * <style> element the strict CSP blocks. Where `showModal` is missing (very old browsers, CC-38) the
 * dialog still opens non-modally via the `open` attribute, so content is never unreachable.
 */
export type ModalPlacement = 'center' | 'bottom' | 'side'

export interface ModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  title: string
  description?: string
  children?: ReactNode
  placement?: ModalPlacement
  /** `alertdialog` for confirmations that interrupt the user (destructive actions). */
  role?: 'dialog' | 'alertdialog'
  /** When false Escape, the backdrop and the X do nothing: use only while an action is in flight. */
  dismissible?: boolean
  className?: string
}

function placementClass(placement: ModalPlacement): string {
  switch (placement) {
    case 'bottom':
      return 'm-0 mt-auto w-full max-w-none'
    case 'side':
      return 'm-0 me-auto h-full max-h-none w-80 max-w-[90vw]'
    default:
      return 'm-auto w-[calc(100%-2rem)] max-w-lg'
  }
}

function panelVariants(placement: ModalPlacement): Variants {
  if (placement === 'bottom') return sheetBottom
  if (placement === 'side') return sheetSide
  return dialogPanel
}

export function Modal({
  open,
  onOpenChange,
  title,
  description,
  children,
  placement = 'center',
  role = 'dialog',
  dismissible = true,
  className,
}: ModalProps) {
  const { t } = useTranslation()
  const { pick } = useMotionPolicy()
  const ref = useRef<HTMLDialogElement>(null)
  const titleId = useId()
  const descId = useId()

  useEffect(() => {
    const dialog = ref.current
    if (!dialog) return
    if (open && !dialog.open) {
      if (typeof dialog.showModal === 'function') dialog.showModal()
      else dialog.setAttribute('open', '')
      // native <dialog> focuses its first control; a confirmation wants the SAFE one (data-autofocus)
      dialog.querySelector<HTMLElement>('[data-autofocus]')?.focus()
    } else if (!open && dialog.open) {
      if (typeof dialog.close === 'function') dialog.close()
      else dialog.removeAttribute('open')
    }
  }, [open])

  // A press on the backdrop (outside the panel) lands on the <dialog> element itself. Attached here,
  // not as a JSX prop: the dialog is not an interactive element, the backdrop is a pointer shortcut
  // (Escape and the close button remain the accessible ways to dismiss).
  useEffect(() => {
    const dialog = ref.current
    if (!dialog || !dismissible) return
    const onMouseDown = (event: MouseEvent) => {
      if (event.target === dialog) onOpenChange(false)
    }
    dialog.addEventListener('mousedown', onMouseDown)
    return () => dialog.removeEventListener('mousedown', onMouseDown)
  }, [dismissible, onOpenChange])

  return (
    <dialog
      ref={ref}
      role={role === 'alertdialog' ? 'alertdialog' : undefined}
      aria-labelledby={titleId}
      aria-describedby={description ? descId : undefined}
      // the browser closed it (Escape): tell the owner so state and DOM never disagree
      onClose={() => onOpenChange(false)}
      onCancel={(event) => {
        if (!dismissible) event.preventDefault()
      }}
      className={cn(
        'max-h-[100dvh] overflow-visible border-0 bg-transparent p-0 text-text',
        placementClass(placement),
      )}
    >
      {open ? (
        <motion.div
          variants={pick(panelVariants(placement))}
          initial="hidden"
          animate="show"
          className={cn(
            'relative max-h-[90dvh] overflow-y-auto border border-border bg-surface p-6 shadow-lg',
            placement === 'bottom'
              ? 'rounded-t-xl'
              : placement === 'side'
                ? 'h-full'
                : 'rounded-xl',
            className,
          )}
        >
          <div className="flex items-start justify-between gap-3">
            <h2 id={titleId} className="text-xl font-semibold">
              {title}
            </h2>
            {dismissible ? (
              <IconButton
                aria-label={t('common.close')}
                onClick={() => onOpenChange(false)}
                className="-me-2 -mt-2"
              >
                <X className="h-5 w-5" aria-hidden="true" />
              </IconButton>
            ) : null}
          </div>
          {description ? (
            <p id={descId} className="mt-2 text-muted">
              {description}
            </p>
          ) : null}
          <div className="mt-4">{children}</div>
        </motion.div>
      ) : null}
    </dialog>
  )
}

export const Dialog = Modal

/** A sheet is a modal anchored to the bottom (mobile) or the side (desktop drawers). */
export function Sheet(props: Omit<ModalProps, 'placement'> & { side?: 'bottom' | 'side' }) {
  const { side = 'bottom', ...rest } = props
  return <Modal placement={side} {...rest} />
}

export interface ConfirmDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  title: string
  description?: string
  onConfirm: () => void
  confirmLabel?: string
  cancelLabel?: string
  destructive?: boolean
  /** The user must type this exact text before the confirm button is enabled (destructive actions). */
  requireText?: string
  loading?: boolean
}

/** Compare typed text with the required text after Unicode normalisation (Bangla IMEs vary). */
export function matchesRequiredText(typed: string, required: string): boolean {
  return typed.normalize('NFC').trim() === required.normalize('NFC').trim()
}

function ConfirmBody({
  requireText,
  onConfirm,
  onCancel,
  confirmLabel,
  cancelLabel,
  destructive,
  loading,
}: {
  requireText?: string
  onConfirm: () => void
  onCancel: () => void
  confirmLabel?: string
  cancelLabel?: string
  destructive: boolean
  loading: boolean
}) {
  const { t } = useTranslation()
  // lives in a child that only exists while the dialog is open, so it resets on every open
  const [typed, setTyped] = useState('')
  const canConfirm = requireText === undefined || matchesRequiredText(typed, requireText)
  return (
    <>
      {requireText !== undefined ? (
        <FormField label={t('ui.confirm.typeToConfirm', { text: requireText })}>
          {(props) => (
            <Input
              {...props}
              value={typed}
              onChange={(event) => setTyped(event.target.value)}
              autoComplete="off"
              spellCheck={false}
            />
          )}
        </FormField>
      ) : null}
      <div className="mt-6 flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
        {/* initial focus is Cancel: the safe choice is the one Enter picks */}
        <Button variant="outline" data-autofocus onClick={onCancel} disabled={loading}>
          {cancelLabel ?? t('common.cancel')}
        </Button>
        <Button
          variant={destructive ? 'destructive' : 'primary'}
          disabled={!canConfirm}
          loading={loading}
          onClick={onConfirm}
        >
          {confirmLabel ?? t('ui.confirm.confirm')}
        </Button>
      </div>
    </>
  )
}

export function ConfirmDialog({
  open,
  onOpenChange,
  title,
  description,
  onConfirm,
  confirmLabel,
  cancelLabel,
  destructive = true,
  requireText,
  loading = false,
}: ConfirmDialogProps) {
  return (
    <Modal
      open={open}
      onOpenChange={onOpenChange}
      title={title}
      description={description}
      role="alertdialog"
      dismissible={!loading}
    >
      <ConfirmBody
        requireText={requireText}
        onConfirm={onConfirm}
        onCancel={() => onOpenChange(false)}
        confirmLabel={confirmLabel}
        cancelLabel={cancelLabel}
        destructive={destructive}
        loading={loading}
      />
    </Modal>
  )
}
