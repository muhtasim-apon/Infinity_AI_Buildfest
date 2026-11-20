import { lazy, Suspense, useState } from 'react'
import { useUiPrefs } from '../../lib/uiPrefs'
import { cn } from '../../lib/cn'
import { canUse3D } from './HeroBackground'

// three.js stays out of the initial bundle: this chunk loads after first paint.
const AmbientThree = lazy(() => import('../three/AmbientThree'))

/**
 * Whole-app backdrop, behind every page: a soft multi-colour gradient with slowly moving light
 * (CSS, `.cg-backdrop`), plus floating 3D rice leaves and grains on capable devices. Never a flat
 * white or black page. Reduced motion / data saver / no WebGL => the still gradient only.
 */
export function AppBackdrop() {
  const [prefs] = useUiPrefs()
  const reduced =
    prefs.reducedMotion ||
    (typeof window !== 'undefined' &&
      window.matchMedia?.('(prefers-reduced-motion: reduce)').matches)
  const [allowed] = useState(canUse3D)
  const [ready, setReady] = useState(false)
  return (
    <div className="pointer-events-none fixed inset-0 -z-10 overflow-hidden" aria-hidden="true">
      <div className="cg-backdrop absolute inset-0" />
      {allowed && !reduced ? (
        <Suspense fallback={null}>
          <AmbientThree
            animate
            className={cn(
              'absolute inset-0 opacity-0 transition-opacity duration-slow ease-standard',
              ready && 'opacity-100',
            )}
            onReady={() => setReady(true)}
          />
        </Suspense>
      ) : null}
    </div>
  )
}
