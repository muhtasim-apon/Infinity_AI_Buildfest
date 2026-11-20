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

/** হোম · ইতিহাস · (ছবি) · সতর্কতা · আরও: a floating pill bar; scan sits in the centre as a gold disc. */
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
      className="fixed inset-x-3 bottom-[calc(12px+env(safe-area-inset-bottom))] z-40 mx-auto max-w-[456px] rounded-full bg-primary px-2 shadow-lg"
    >
      <ul className="grid h-[68px] grid-cols-5 items-center">
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
                    'min-h-[56px] rounded-full',
                    isActive ? 'text-primary-on' : 'text-primary-on opacity-80',
                  )
                }
              >
                {({ isActive }) => (
                  <>
                    {tab.primary ? (
                      <span
                        className={cn(
                          'flex h-11 w-11 items-center justify-center rounded-full bg-accent text-text',
                          'shadow-md transition-transform duration-fast ease-standard',
                          'motion-ok:active:scale-95',
                        )}
                      >
                        <Icon className="h-6 w-6" aria-hidden="true" />
                      </span>
                    ) : (
                      <>
                        {isActive ? (
                          <motion.span
                            layoutId={`tab-pill-${group}`}
                            transition={transition}
                            className="absolute inset-x-1 inset-y-1 rounded-full bg-primary-hover"
                            aria-hidden="true"
                          />
                        ) : null}
                        <Icon className="relative h-5 w-5" aria-hidden="true" />
                      </>
                    )}
                    <span className="relative text-[11px] leading-tight">{t(tab.label)}</span>
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
