import { useEffect, useRef } from 'react'
import {
  AmbientLight,
  BufferAttribute,
  Color,
  DirectionalLight,
  DoubleSide,
  DynamicDrawUsage,
  Euler,
  Fog,
  InstancedMesh,
  Matrix4,
  MeshLambertMaterial,
  PerspectiveCamera,
  PlaneGeometry,
  Quaternion,
  Scene,
  SphereGeometry,
  Vector3,
  WebGLRenderer,
} from 'three'

/**
 * Full-page ambient 3D layer (lazy chunk, hero3d budget): rice leaves and golden grains float in
 * depth, tumble slowly and drift with the wind; the camera follows scroll (parallax) and the
 * pointer. Transparent canvas over the CSS gradient backdrop, colours from the design tokens (live
 * re-tint on theme change). Kept faint so text above it always stays readable. Decorative only.
 */

function token(name: string): Color {
  const v = getComputedStyle(document.documentElement).getPropertyValue(name).trim()
  return new Color(v || 'white')
}

function lcg(seed: number) {
  let s = seed
  return () => (s = (s * 16807) % 2147483647) / 2147483647
}

type Flake = {
  p: Vector3
  v: Vector3
  rot: Euler
  spin: Vector3
  scale: number
  phase: number
}

function makeFlakes(n: number, seed: number, spread: number): Flake[] {
  const r = lcg(seed)
  return Array.from({ length: n }, () => ({
    p: new Vector3((r() - 0.5) * spread, (r() - 0.5) * 16, -2 - r() * 16),
    v: new Vector3(0.05 + r() * 0.12, 0.04 + r() * 0.08, 0),
    rot: new Euler(r() * Math.PI, r() * Math.PI, r() * Math.PI),
    spin: new Vector3((r() - 0.5) * 0.6, (r() - 0.5) * 0.8, (r() - 0.5) * 0.5),
    scale: 0.6 + r() * 0.8,
    phase: r() * Math.PI * 2,
  }))
}

export default function AmbientThree({
  animate,
  onReady,
  className,
}: {
  animate: boolean
  onReady?: () => void
  className?: string
}) {
  const host = useRef<HTMLDivElement>(null)
  const readyRef = useRef(onReady)
  useEffect(() => {
    readyRef.current = onReady
  }, [onReady])

  useEffect(() => {
    const el = host.current
    if (!el) return
    let renderer: WebGLRenderer
    try {
      renderer = new WebGLRenderer({ antialias: true, alpha: true, powerPreference: 'low-power' })
    } catch {
      return // the CSS gradient backdrop stays on its own
    }
    renderer.setPixelRatio(1)
    renderer.setClearColor(0x000000, 0)
    const canvas = renderer.domElement
    canvas.setAttribute('aria-hidden', 'true')
    canvas.style.width = '100%'
    canvas.style.height = '100%'
    canvas.style.display = 'block'
    el.appendChild(canvas)

    const scene = new Scene()
    const fog = new Fog(0xffffff, 10, 30)
    scene.fog = fog
    const camera = new PerspectiveCamera(55, 1, 0.1, 60)
    camera.position.set(0, 0, 6)
    scene.add(new AmbientLight(0xffffff, 1.5))
    const key = new DirectionalLight(0xffffff, 1.3)
    key.position.set(3, 5, 4)
    scene.add(key)

    // rice leaf: long tapered blade with a gentle curl
    const leafGeo = new PlaneGeometry(0.16, 1.1, 1, 8)
    const lp = leafGeo.getAttribute('position') as BufferAttribute
    for (let i = 0; i < lp.count; i++) {
      const y = lp.getY(i) + 0.55 // 0..1.1
      const k = y / 1.1
      lp.setX(i, lp.getX(i) * Math.sin(Math.PI * Math.min(1, k * 1.05)) * 1.2)
      lp.setZ(i, Math.sin(k * Math.PI * 0.9) * 0.18)
      lp.setY(i, y - 0.55)
    }
    leafGeo.computeVertexNormals()
    const grainGeo = new SphereGeometry(0.07, 12, 8)

    const leafMat = new MeshLambertMaterial({ side: DoubleSide, transparent: true, opacity: 0.75 })
    const grainMat = new MeshLambertMaterial({ transparent: true, opacity: 0.8 })
    const wide = window.innerWidth > 900
    const leaves = makeFlakes(wide ? 70 : 38, 7, wide ? 22 : 10)
    const grains = makeFlakes(wide ? 60 : 32, 19, wide ? 22 : 10)
    const leafMesh = new InstancedMesh(leafGeo, leafMat, leaves.length)
    const grainMesh = new InstancedMesh(grainGeo, grainMat, grains.length)
    leafMesh.instanceMatrix.setUsage(DynamicDrawUsage)
    grainMesh.instanceMatrix.setUsage(DynamicDrawUsage)
    leafMesh.frustumCulled = false
    grainMesh.frustumCulled = false
    scene.add(leafMesh, grainMesh)

    // per-instance tint: a mix of the greens (leaves) and golds (grains)
    const applyPalette = () => {
      fog.color.copy(token('--bg'))
      const greens = [token('--primary'), token('--success'), token('--primary-hover')]
      const golds = [token('--accent'), token('--warning'), token('--disease-1')]
      leaves.forEach((_, i) => leafMesh.setColorAt(i, greens[i % greens.length]!))
      grains.forEach((_, i) => grainMesh.setColorAt(i, golds[i % golds.length]!))
      if (leafMesh.instanceColor) leafMesh.instanceColor.needsUpdate = true
      if (grainMesh.instanceColor) grainMesh.instanceColor.needsUpdate = true
      if (!running) draw(0)
    }

    const m = new Matrix4()
    const q = new Quaternion()
    const s = new Vector3()
    const pos = new Vector3()
    const place = (mesh: InstancedMesh, list: Flake[], dt: number, t: number, grain: boolean) => {
      const halfW = camera.aspect * 6
      list.forEach((f, i) => {
        if (dt > 0) {
          // wind: drift sideways and up, with a slow sinusoidal sway
          f.p.x += (f.v.x + Math.sin(t * 0.4 + f.phase) * 0.08) * dt
          f.p.y += (f.v.y + Math.cos(t * 0.3 + f.phase) * 0.05) * dt
          f.rot.x += f.spin.x * dt
          f.rot.y += f.spin.y * dt
          f.rot.z += f.spin.z * dt
          if (f.p.x > halfW + 3) f.p.x = -halfW - 3
          if (f.p.y > 9) f.p.y = -9
        }
        pos.copy(f.p)
        q.setFromEuler(f.rot)
        const k = grain ? f.scale * 0.9 : f.scale
        s.set(grain ? k : k, grain ? k * 1.7 : k, k)
        m.compose(pos, q, s)
        mesh.setMatrixAt(i, m)
      })
      mesh.instanceMatrix.needsUpdate = true
    }

    let running = false
    let raf = 0
    let last = performance.now()
    let t = 0
    let visible = true
    const pointer = { x: 0, y: 0 }
    const draw = (dt: number) => {
      t += dt
      const scroll = window.scrollY || 0
      const k = Math.min(1, dt * 2 || 1)
      camera.position.x += (pointer.x * 0.5 - camera.position.x) * k
      camera.position.y += (-scroll * 0.003 + pointer.y * 0.3 - camera.position.y) * k
      camera.rotation.z = Math.sin(t * 0.1) * 0.02
      place(leafMesh, leaves, dt, t, false)
      place(grainMesh, grains, dt, t, true)
      renderer.render(scene, camera)
    }
    // 30 fps is plenty for a slow ambient drift and halves battery use
    let acc = 0
    const frame = (now: number) => {
      const dt = Math.min(0.1, (now - last) / 1000)
      last = now
      acc += dt
      if (acc >= 1 / 30) {
        draw(acc)
        acc = 0
      }
      raf = running ? requestAnimationFrame(frame) : 0
    }
    const schedule = () => {
      const should = animate && visible && document.visibilityState === 'visible'
      if (should && !running) {
        running = true
        last = performance.now()
        raf = requestAnimationFrame(frame)
      } else if (!should && running) {
        running = false
        cancelAnimationFrame(raf)
      }
    }

    const resize = () => {
      const w = el.clientWidth || 1
      const h = el.clientHeight || 1
      renderer.setSize(w, h, false)
      camera.aspect = w / h
      camera.updateProjectionMatrix()
      if (!running) draw(0)
    }
    const ro = new ResizeObserver(resize)
    ro.observe(el)
    const onPointer = (e: PointerEvent) => {
      pointer.x = (e.clientX / window.innerWidth) * 2 - 1
      pointer.y = -((e.clientY / window.innerHeight) * 2 - 1)
    }
    const onScroll = () => {
      if (!running) draw(0)
    }
    window.addEventListener('pointermove', onPointer, { passive: true })
    window.addEventListener('scroll', onScroll, { passive: true })
    const mo = new MutationObserver(applyPalette)
    mo.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] })
    const mq = window.matchMedia('(prefers-color-scheme: dark)')
    mq.addEventListener('change', applyPalette)
    const onVis = () => {
      visible = document.visibilityState === 'visible'
      schedule()
    }
    document.addEventListener('visibilitychange', onVis)

    applyPalette()
    resize()
    schedule()
    readyRef.current?.()

    return () => {
      running = false
      cancelAnimationFrame(raf)
      document.removeEventListener('visibilitychange', onVis)
      window.removeEventListener('pointermove', onPointer)
      window.removeEventListener('scroll', onScroll)
      mq.removeEventListener('change', applyPalette)
      mo.disconnect()
      ro.disconnect()
      leafMesh.dispose()
      grainMesh.dispose()
      leafGeo.dispose()
      grainGeo.dispose()
      leafMat.dispose()
      grainMat.dispose()
      renderer.dispose()
      canvas.remove()
    }
  }, [animate])

  return <div ref={host} className={className} aria-hidden="true" />
}
