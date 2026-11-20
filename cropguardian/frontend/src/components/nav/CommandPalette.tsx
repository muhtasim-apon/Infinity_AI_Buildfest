import { Command } from 'cmdk'
import { LogOut, Moon, Search } from 'lucide-react'
import { useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../app/auth'
import type { StaffNavItem } from '../../app/navConfig'
import { useUiPrefs } from '../../lib/uiPrefs'
import { Modal } from '../ui/modal'

/** Ctrl+K / Cmd+K opens the palette (spec 15.4 staff console). */
export function usePaletteShortcut(toggle: () => void): void {
  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') {
        event.preventDefault()
        toggle()
      }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [toggle])
}

const itemClass =
  'flex min-h-[44px] cursor-pointer items-center gap-3 rounded-md px-3 text-text aria-selected:bg-surface-2'

/**
 * Staff command palette: jump to a built page or run a quick action. It lives inside our native
 * <dialog> modal (DECISIONS D-025), so focus trapping, Escape and the backdrop are the browser's.
 * Only built pages are offered: a screen that does not exist yet is not searchable.
 */
export function CommandPalette({
  open,
  onOpenChange,
  items,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  items: StaffNavItem[]
}) {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { signOut } = useAuth()
  const [prefs, setPrefs] = useUiPrefs()
  const run = (action: () => void) => {
    onOpenChange(false)
    action()
  }
  const pages = items.filter((item) => item.to)
  return (
    <Modal open={open} onOpenChange={onOpenChange} title={t('staff.palette.open')}>
      <Command label={t('staff.palette.open')} loop>
        <div className="flex items-center gap-2 rounded-md border border-border px-3">
          <Search className="h-4 w-4 text-muted" aria-hidden="true" />
          <Command.Input
            placeholder={t('staff.palette.placeholder')}
            className="min-h-[48px] w-full bg-transparent text-text placeholder:text-subtle focus:outline-none"
          />
        </div>
        <Command.List className="mt-3 max-h-72 overflow-y-auto">
          <Command.Empty className="px-3 py-6 text-center text-muted">
            {t('staff.palette.empty')}
          </Command.Empty>
          <Command.Group heading={t('staff.palette.pages')} className="text-sm text-muted">
            {pages.map((item) => {
              const Icon = item.icon
              return (
                <Command.Item
                  key={item.id}
                  value={t(item.label)}
                  className={itemClass}
                  onSelect={() => run(() => navigate(item.to ?? '/'))}
                >
                  <Icon className="h-4 w-4" aria-hidden="true" />
                  {t(item.label)}
                </Command.Item>
              )
            })}
          </Command.Group>
          <Command.Group heading={t('staff.palette.actions')} className="mt-2 text-sm text-muted">
            <Command.Item
              value={t('staff.palette.theme')}
              className={itemClass}
              onSelect={() =>
                run(() => setPrefs({ theme: prefs.theme === 'dark' ? 'light' : 'dark' }))
              }
            >
              <Moon className="h-4 w-4" aria-hidden="true" />
              {t('staff.palette.theme')}
            </Command.Item>
            <Command.Item
              value={t('auth.logout')}
              className={itemClass}
              onSelect={() => run(() => void signOut())}
            >
              <LogOut className="h-4 w-4" aria-hidden="true" />
              {t('auth.logout')}
            </Command.Item>
          </Command.Group>
        </Command.List>
      </Command>
    </Modal>
  )
}
