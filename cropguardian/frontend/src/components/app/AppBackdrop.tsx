import { useEffect, useRef, useState } from 'react'
import { useUiPrefs } from '../../lib/uiPrefs'

// Swaying-grass footage (Cheshire Wildlife Trust GIF, see docs/CREDITS.md) re-encoded as a 231 KB
// seamless H.264 loop: ~17x smaller than the 3.9 MB GIF. Served from our own origin (CSP media-src).
const VIDEO = '/media/grass.mp4'
const POSTER = '/media/grass.jpg'

function dataSaver(): boolean {
  const c = (navigator as Navigator & { connection?: { saveData?: boolean } }).connection
  return Boolean(c?.saveData)
}

/** A real media pipeline (all current browsers); test DOMs and very old browsers get the still. */
function canPlayVideo(): boolean {
  return (
    typeof HTMLVideoElement !== 'undefined' &&
    'requestVideoFrameCallback' in HTMLVideoElement.prototype
  )
}

function osReducedMotion(): boolean {
  return (
    typeof window !== 'undefined' && window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
  )
}

/**
 * Whole-app background behind every page: a living field of swaying grass with depth. The footage
 * sits on a slow 3D drift (perspective tilt + zoom) and moves with scroll (parallax); a token-tinted
 * wash keeps every text/background pair readable in light and dark mode. Reduced motion or data
 * saver => the still poster frame, no video download.
 */
export function AppBackdrop() {
  const [prefs] = useUiPrefs()
  const still = prefs.reducedMotion || osReducedMotion() || dataSaver() || !canPlayVideo()
  const layer = useRef<HTMLDivElement>(null)
  const [playing, setPlaying] = useState(false)

  // scroll parallax: the field moves slower than the page, so it reads as far away
  useEffect(() => {
    const el = layer.current
    if (!el || still) return
    let raf = 0
    const apply = () => {
      raf = 0
      const y = Math.min(window.scrollY || 0, 4000)
      el.style.setProperty('--cg-parallax', `${(-y * 0.06).toFixed(1)}px`)
    }
    const onScroll = () => {
      if (!raf) raf = requestAnimationFrame(apply)
    }
    window.addEventListener('scroll', onScroll, { passive: true })
    apply()
    return () => {
      window.removeEventListener('scroll', onScroll)
      if (raf) cancelAnimationFrame(raf)
    }
  }, [still])

  return (
    <div className="pointer-events-none fixed inset-0 -z-10 overflow-hidden" aria-hidden="true">
      <div className="cg-backdrop absolute inset-0" />
      <div ref={layer} className="cg-grass absolute inset-0">
        <img src={POSTER} alt="" className="cg-grass-media" />
        {still ? null : (
          <video
            className={playing ? 'cg-grass-media cg-grass-on' : 'cg-grass-media cg-grass-off'}
            src={VIDEO}
            poster={POSTER}
            autoPlay
            muted
            loop
            playsInline
            preload="auto"
            disablePictureInPicture
            onPlaying={() => setPlaying(true)}
          />
        )}
      </div>
      <div className="cg-grass-wash absolute inset-0" />
    </div>
  )
}
