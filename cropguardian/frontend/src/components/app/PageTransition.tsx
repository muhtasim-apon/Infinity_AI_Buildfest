import { useLocation, useOutlet } from 'react-router-dom'

/**
 * 3D page transition, CSS only (no animation library in the initial bundle): each new screen swings
 * in with a slight Y-rotation from depth (`.cg-page-in` in index.css, motion tokens). The keyframes
 * end at `transform: none`, so fixed children (the bottom bar) sit normally at rest. Reduced motion
 * (OS or in-app) swaps it for a 120 ms fade in CSS.
 *
 * `depth` picks the key: 'section' animates only between top-level areas, 'page' on every route.
 */
export function AnimatedOutlet({ depth = 'page' }: { depth?: 'section' | 'page' }) {
  const location = useLocation()
  const outlet = useOutlet()
  const key = depth === 'section' ? location.pathname.split('/')[1] || 'root' : location.pathname
  return (
    <div key={key} className="cg-page-in">
      {outlet}
    </div>
  )
}
