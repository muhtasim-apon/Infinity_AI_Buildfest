import { Bell } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { Link } from 'react-router-dom'
import { LogoMark } from '../illustrations'
import { Button } from '../ui/button'
import { LanguageSwitch } from './LanguageSwitch'

/**
 * Farmer top bar, 56 px (spec 15.4): logo, language switch, notifications. The outbox badge joins it
 * in Phase 7 (it needs the offline queue); the slot is the empty space between the two controls.
 */
export function FarmerTopBar() {
  const { t } = useTranslation()
  return (
    <header className="sticky top-0 z-30 flex h-14 items-center justify-between gap-2 border-b border-border bg-surface px-4">
      <Link
        to="/app"
        className="flex min-h-[44px] items-center gap-2 text-lg font-semibold text-primary"
      >
        <LogoMark className="h-8 w-8" />
        <span>{t('app.name')}</span>
      </Link>
      <div className="flex items-center gap-1">
        <LanguageSwitch />
        <Button asChild variant="ghost" size="icon" aria-label={t('ui.notifications')}>
          <Link to="/app/alerts">
            <Bell className="h-5 w-5" aria-hidden="true" />
          </Link>
        </Button>
      </div>
    </header>
  )
}
