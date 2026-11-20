import { useTranslation } from 'react-i18next'
import { NavLink } from 'react-router-dom'
import type { StaffNavItem } from '../../app/navConfig'
import { cn } from '../../lib/cn'

/**
 * Staff sidebar list. At 1280 px and up it shows labels; between 1024 and 1279 px it is an icon rail
 * (labels stay in the DOM as screen-reader text, so the rail is still fully named); in the mobile
 * drawer `showLabels` forces them on. Screens not built yet are disabled, never links to nowhere.
 */
export function StaffNav({
  items,
  showLabels = false,
  onNavigate,
}: {
  items: StaffNavItem[]
  showLabels?: boolean
  onNavigate?: () => void
}) {
  const { t } = useTranslation()
  const label = showLabels ? '' : 'sr-only xl:not-sr-only'
  return (
    <nav aria-label={t('navShell.main')}>
      <ul className="space-y-1 p-3">
        {items.map((item) => {
          const Icon = item.icon
          if (!item.to) {
            return (
              <li key={item.id}>
                <span
                  aria-disabled="true"
                  className="flex min-h-[44px] items-center gap-3 rounded-md px-3 text-subtle"
                >
                  <Icon className="h-5 w-5 shrink-0" aria-hidden="true" />
                  <span className={label}>{t(item.label)}</span>
                  <span
                    className={cn(
                      'ms-auto rounded-full bg-surface-2 px-2 py-0.5 text-xs text-muted',
                      showLabels ? '' : 'hidden xl:inline',
                    )}
                  >
                    {t('staff.soon')}
                  </span>
                </span>
              </li>
            )
          }
          return (
            <li key={item.id}>
              <NavLink
                to={item.to}
                end
                onClick={onNavigate}
                className={({ isActive }) =>
                  cn(
                    'flex min-h-[44px] items-center gap-3 rounded-md px-3 font-medium',
                    'transition-colors duration-fast ease-standard',
                    isActive ? 'bg-primary-soft text-primary' : 'text-text hover:bg-surface-2',
                  )
                }
              >
                <Icon className="h-5 w-5 shrink-0" aria-hidden="true" />
                <span className={label}>{t(item.label)}</span>
              </NavLink>
            </li>
          )
        })}
      </ul>
    </nav>
  )
}
