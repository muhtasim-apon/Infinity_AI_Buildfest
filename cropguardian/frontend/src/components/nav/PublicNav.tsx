import { Menu } from 'lucide-react'
import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Link } from 'react-router-dom'
import { LogoMark } from '../illustrations'
import { Button, IconButton } from '../ui/button'
import { Sheet } from '../ui/modal'
import { LanguageSwitch } from './LanguageSwitch'

/** Public pages list only pages that exist; Trust, Map and Pitch join as they are built. */
const LINKS = [{ to: '/#how', label: 'nav.howItWorks' }] as const

/**
 * Public navigation: logo, section links, language, Sign in, and the one primary action "Try the
 * demo" (spec 15.4). On phones the links move into a side sheet (a native <dialog>, so focus and
 * Escape work without a library).
 */
export function PublicNav() {
  const { t } = useTranslation()
  const [open, setOpen] = useState(false)
  return (
    <header className="sticky top-0 z-30 border-b border-border bg-surface">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between gap-3 px-4">
        <Link
          to="/"
          className="flex min-h-[44px] items-center gap-2 text-lg font-semibold text-primary"
        >
          <LogoMark className="h-9 w-9" />
          <span>{t('app.name')}</span>
        </Link>
        <nav aria-label={t('navShell.main')} className="hidden items-center gap-1 md:flex">
          {LINKS.map((link) => (
            <Button key={link.to} asChild variant="ghost" size="sm">
              <a href={link.to}>{t(link.label)}</a>
            </Button>
          ))}
        </nav>
        <div className="flex items-center gap-2">
          <LanguageSwitch />
          <Button asChild variant="ghost" size="sm" className="hidden md:inline-flex">
            <Link to="/login">{t('nav.signIn')}</Link>
          </Button>
          <Button asChild size="sm" className="hidden sm:inline-flex">
            <Link to="/demo">{t('nav.tryDemo')}</Link>
          </Button>
          <IconButton
            aria-label={t('navShell.openMenu')}
            className="md:hidden"
            onClick={() => setOpen(true)}
          >
            <Menu className="h-5 w-5" aria-hidden="true" />
          </IconButton>
        </div>
      </div>
      <Sheet open={open} onOpenChange={setOpen} title={t('navShell.menu')} side="side">
        <nav aria-label={t('navShell.main')} className="flex flex-col gap-1">
          {LINKS.map((link) => (
            <Button
              key={link.to}
              asChild
              variant="ghost"
              className="justify-start"
              onClick={() => setOpen(false)}
            >
              <a href={link.to}>{t(link.label)}</a>
            </Button>
          ))}
          <Button asChild variant="ghost" className="justify-start" onClick={() => setOpen(false)}>
            <Link to="/login">{t('nav.signIn')}</Link>
          </Button>
          <Button asChild className="mt-2" onClick={() => setOpen(false)}>
            <Link to="/demo">{t('nav.tryDemo')}</Link>
          </Button>
        </nav>
      </Sheet>
    </header>
  )
}
