import { lazy, Suspense, useState } from 'react'
import { useUiPrefs } from '../../lib/uiPrefs'
import { cn } from '../../lib/cn'
import { FieldScene } from './FieldScene'

// three.js never reaches the initial bundle: this chunk (hero3d budget, 220 KB) loads on demand.
const HeroThree = lazy(() => import('../three/HeroThree'))

/** WebGL present, not a weak device, not data saver. Anything doubtful => the SVG scene. */
function dataSaver(): boolean {
  const c = (navigator as Navigator & { connection?: { saveData?: boolean } }).connection
  return Boolean(c?.saveData)
}

function osReducedMotion(): boolean {
  return (
    typeof window !== 'undefined' && window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
  )
}

export function canUse3D(): boolean {
  if (typeof window === 'undefined' || dataSaver()) return false
  const mem = (navigator as Navigator & { deviceMemory?: number }).deviceMemory
  if (typeof mem === 'number' && mem < 2) return false
  try {
    const canvas = document.createElement('canvas')
    return Boolean(canvas.getContext('webgl2') ?? canvas.getContext('webgl'))
  } catch {
    return false
  }
}

/**
 * Hero/header background: the SVG field scene paints instantly; on capable devices the live 3D
 * paddy field fades in over it once WebGL is ready. Reduced motion keeps the still SVG.
 */
export function HeroBackground({
  scarecrow = true,
  className,
}: {
  scarecrow?: boolean
  className?: string
}) {
  // no animation library here: this wrapper sits in the initial bundle (landing page)
  const [prefs] = useUiPrefs()
  const reduced = prefs.reducedMotion || osReducedMotion()
  const loopsAllowed = !reduced
  const [allowed] = useState(canUse3D)
  const [ready, setReady] = useState(false)
  return (
    <div className={cn('absolute inset-0', className)} aria-hidden="true">
      <FieldScene
        className={cn(
          'absolute inset-0 transition-opacity duration-slow ease-standard',
          ready && 'opacity-0',
        )}
        scarecrow={scarecrow}
      />
      {allowed && !reduced ? (
        <Suspense fallback={null}>
          <HeroThree
            className={cn(
              'absolute inset-0 opacity-0 transition-opacity duration-slow ease-standard',
              ready && 'opacity-100',
            )}
            animate={loopsAllowed}
            scarecrow={scarecrow}
            onReady={() => setReady(true)}
          />
        </Suspense>
      ) : null}
    </div>
  )
}
