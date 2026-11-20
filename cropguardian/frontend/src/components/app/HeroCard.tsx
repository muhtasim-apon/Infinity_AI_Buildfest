import { useInView } from 'framer-motion'
import { Camera } from 'lucide-react'
import { useRef } from 'react'
import { useTranslation } from 'react-i18next'
import { Link } from 'react-router-dom'
import { useMotionPolicy } from '../../design/useMotion'
import { cn } from '../../lib/cn'
import { BracketFrame, LeafScan } from '../illustrations'
import { Button } from '../ui/button'

/**
 * The crop-doctor card: the one thing a farmer opens the app to do. A big paddy-green card with the
 * leaf-in-viewfinder picture and a single 56 px action. The button "breathes" with a soft ring while
 * idle (spec 15.2), but only when motion and looping are allowed and the card is on screen.
 */
export function HeroCard({ className }: { className?: string }) {
  const { t } = useTranslation()
  const { loopsAllowed } = useMotionPolicy()
  const ref = useRef<HTMLDivElement>(null)
  const visible = useInView(ref)
  return (
    <section
      aria-labelledby="hero-title"
      className={cn(
        'overflow-hidden rounded-xl bg-primary p-5 text-primary-on shadow-md',
        className,
      )}
    >
      <div className="flex items-center gap-4">
        <div className="min-w-0 flex-1">
          <h2 id="hero-title" className="text-2xl font-semibold">
            {t('farmerHome.hero.title')}
          </h2>
          <p className="mt-1">{t('farmerHome.hero.body')}</p>
          <div ref={ref} className="relative mt-4">
            {loopsAllowed && visible ? (
              <span
                aria-hidden="true"
                className="pointer-events-none absolute inset-0 rounded-md border-2 border-primary-on motion-ok:animate-breathe"
              />
            ) : null}
            <Button
              asChild
              size="xl-farmer"
              className="bg-surface text-primary hover:bg-surface-2 hover:text-primary"
            >
              <Link to="/app/scan">
                <Camera className="h-6 w-6" aria-hidden="true" />
                {t('farmerHome.hero.cta')}
              </Link>
            </Button>
          </div>
        </div>
        <BracketFrame size="sm" className="w-28 shrink-0 p-1.5 sm:w-32">
          <LeafScan />
        </BracketFrame>
      </div>
    </section>
  )
}
