import { Bell, ChevronDown, Menu, Search } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../app/auth'
import { homePath, isDemo } from '../../lib/authApi'
import { LogoMark } from '../illustrations'
import { Button, IconButton } from '../ui/button'
import { SimulatedBadge } from '../ui/badge'
import { DropdownMenu } from '../ui/overlays'
import { LanguageSwitch } from './LanguageSwitch'

/**
 * Staff top bar, 64 px (spec 15.4): menu button below 1024 px, logo to the role home, command palette
 * (Ctrl+K), the DEMO / SIMULATED badge when it applies, language, notifications and the account menu.
 */
export function StaffTopBar({ onMenu, onSearch }: { onMenu: () => void; onSearch: () => void }) {
  const { t } = useTranslation()
  const { state, signOut } = useAuth()
  const navigate = useNavigate()
  const name = state?.display_name ?? ''
  const initial = Array.from(name)[0] ?? '?'
  const home = state?.role ? homePath(state.role) : '/'
  return (
    <header className="sticky top-0 z-30 flex h-16 items-center gap-2 border-b border-border bg-surface px-4">
      <IconButton aria-label={t('navShell.openMenu')} className="lg:hidden" onClick={onMenu}>
        <Menu className="h-5 w-5" aria-hidden="true" />
      </IconButton>
      <Link to={home} className="flex min-h-[44px] items-center gap-2 font-semibold text-primary">
        <LogoMark className="h-8 w-8" />
        <span className="hidden sm:inline">{t('app.name')}</span>
      </Link>
      <div className="ms-auto flex items-center gap-1">
        <Button
          variant="outline"
          size="sm"
          className="hidden gap-2 text-muted sm:inline-flex"
          onClick={onSearch}
        >
          <Search className="h-4 w-4" aria-hidden="true" />
          {t('staff.palette.open')}
          <kbd className="rounded border border-border px-1.5 text-xs">{t('staff.shortcut')}</kbd>
        </Button>
        <IconButton aria-label={t('staff.palette.open')} className="sm:hidden" onClick={onSearch}>
          <Search className="h-5 w-5" aria-hidden="true" />
        </IconButton>
        {isDemo(state?.role) ? <SimulatedBadge className="hidden md:inline-flex" /> : null}
        <LanguageSwitch className="hidden sm:inline-flex" />
        <IconButton aria-label={t('ui.notifications')}>
          <Bell className="h-5 w-5" aria-hidden="true" />
        </IconButton>
        <DropdownMenu
          trigger={
            <Button
              variant="ghost"
              className="gap-1 px-2"
              aria-label={name || t('settings.account.title')}
            >
              <span
                aria-hidden="true"
                className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-sm font-semibold text-primary-on"
              >
                {initial}
              </span>
              <ChevronDown className="h-4 w-4 text-muted" aria-hidden="true" />
            </Button>
          }
          items={[
            {
              id: 'sessions',
              label: t('auth.sessions.title'),
              onSelect: () => navigate('/account/sessions'),
            },
            { id: 'logout', label: t('auth.logout'), onSelect: () => void signOut() },
          ]}
        />
      </div>
    </header>
  )
}
