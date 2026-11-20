import { useLocation, useOutlet } from 'react-router-dom'
import { cn } from '../../lib/cn'

/**
 * 3D page transition, CSS only (no animation library in the initial bundle): each new screen swings
 * in with a slight Y-rotation from depth (`.cg-page-in` in index.css, motion tokens). The keyframes
 * end at `transform: none`, so fixed children (the bottom bar) sit normally at rest. Reduced motion
 * (OS or in-app) swaps it for a 120 ms fade in CSS.
 *
 * `depth` picks the key: 'section' animates only between top-level areas, 'page' on every route.
 */
export function AnimatedOutlet({
  depth = 'page',
  stagger = false,
}: {
  depth?: 'section' | 'page'
  stagger?: boolean
}) {
  const location = useLocation()
  const outlet = useOutlet()
  const section = location.pathname.split('/')[1] || 'root'
  const key = depth === 'section' ? section : location.pathname
  // The farmer app has a fixed bottom bar: a transformed ancestor would move it mid-animation, so
  // entering it fades at section level and the 3D swing happens inside it (page level).
  const cls = depth === 'section' && section === 'app' ? 'cg-fade-only' : 'cg-page-in'
  return (
    <div key={key} className={cn(cls, stagger && 'cg-stagger')}>
      {outlet}
    </div>
  )
}
