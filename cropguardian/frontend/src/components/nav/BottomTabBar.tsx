import { motion } from 'framer-motion'
import { Bell, Camera, Clock, House, Menu, type LucideIcon } from 'lucide-react'
import { useId } from 'react'
import { useTranslation } from 'react-i18next'
import { NavLink } from 'react-router-dom'
import { duration, ease, instantTransition } from '../../design/motion'
import { useMotionPolicy } from '../../design/useMotion'
import { cn } from '../../lib/cn'

interface Tab {
  to: string
  end?: boolean
  icon: LucideIcon
  label: string
  /** The raised centre scan button. */
  primary?: boolean
}

/** হোম · ইতিহাস · (ছবি) · সতর্কতা · আরও: scan sits in the centre, raised (spec 15.4 wireframe F1). */
export const FARMER_TABS: Tab[] = [
  { to: '/app', end: true, icon: House, label: 'nav.home' },
  { to: '/app/history', icon: Clock, label: 'nav.history' },
  { to: '/app/scan', icon: Camera, label: 'nav.scan', primary: true },
  { to: '/app/alerts', icon: Bell, label: 'nav.alerts' },
  { to: '/app/more', icon: Menu, label: 'nav.more' },
]

/**
 * Farmer bottom tab bar: 64 px plus the device safe area, centred 480 px column on large screens.
 * The active tab shows a sliding indicator (one element moving between tabs, 200 ms). Icons never
 * stand alone: every tab has a visible label (spec 15.5.2).
 */
export function BottomTabBar() {
  const { t } = useTranslation()
  const { reduced } = useMotionPolicy()
  const group = useId()
  const transition = reduced ? instantTransition : { duration: duration.base, ease: ease.standard }
  return (
    <nav
      aria-label={t('navShell.tabs')}
      className="fixed inset-x-0 bottom-0 z-40 mx-auto max-w-[480px] border-t border-border bg-surface pb-[env(safe-area-inset-bottom)]"
    >
      <ul className="grid h-16 grid-cols-5">
        {FARMER_TABS.map((tab) => {
          const Icon = tab.icon
          return (
            <li key={tab.to} className="flex justify-center">
              <NavLink
                to={tab.to}
                end={tab.end}
                className={({ isActive }) =>
                  cn(
                    'relative flex w-full flex-col items-center justify-center gap-0.5 text-xs font-medium',
                    'transition-colors duration-fast ease-standard',
                    tab.primary ? '-mt-6 justify-start' : 'min-h-[48px]',
                    isActive ? 'text-primary' : 'text-muted',
                  )
                }
              >
                {({ isActive }) => (
                  <>
                    {tab.primary ? (
                      <span
                        className={cn(
                          'flex h-14 w-14 items-center justify-center rounded-full bg-primary text-primary-on',
                          'shadow-lg ring-4 ring-bg transition-transform duration-fast ease-standard',
                          'motion-ok:active:scale-95',
                        )}
                      >
                        <Icon className="h-7 w-7" aria-hidden="true" />
                      </span>
                    ) : (
                      <>
                        {isActive ? (
                          <motion.span
                            layoutId={`tab-pill-${group}`}
                            transition={transition}
                            className="absolute inset-x-5 top-0 h-0.5 rounded-full bg-primary"
                            aria-hidden="true"
                          />
                        ) : null}
                        <Icon className="h-6 w-6" aria-hidden="true" />
                      </>
                    )}
                    <span className={cn(tab.primary && 'mt-0.5')}>{t(tab.label)}</span>
                  </>
                )}
              </NavLink>
            </li>
          )
        })}
      </ul>
    </nav>
  )
}
