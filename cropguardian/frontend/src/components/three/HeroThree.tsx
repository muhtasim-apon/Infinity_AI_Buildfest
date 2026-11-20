import { useEffect, useRef } from 'react'
import {
  AdditiveBlending,
  AmbientLight,
  BoxGeometry,
  BufferAttribute,
  BufferGeometry,
  CircleGeometry,
  Color,
  ConeGeometry,
  CylinderGeometry,
  DirectionalLight,
  DoubleSide,
  Fog,
  Group,
  InstancedMesh,
  Matrix4,
  Mesh,
  MeshBasicMaterial,
  MeshLambertMaterial,
  PerspectiveCamera,
  PlaneGeometry,
  Points,
  PointsMaterial,
  Quaternion,
  Scene,
  ShaderMaterial,
  SphereGeometry,
  Vector3,
  WebGLRenderer,
} from 'three'

/**
 * Lazy 3D background (its own chunk, hero3d budget): a living paddy field with a scarecrow
 * (কাকতাড়ুয়া), wind-swept rice (GPU shader), drifting pollen and gentle camera parallax. Plain
 * three.js (no React renderer) keeps the chunk small. Colours come from the CSS design tokens and
 * re-tint live with light/dark mode. Decorative only; the parent decides whether 3D is allowed.
 */

const BLADE_VERTEX = /* glsl */ `
  uniform float uTime;
  varying float vH;
  varying float vDepth;
  void main() {
    vec4 world = instanceMatrix * vec4(position, 1.0);
    float h = position.y;
    float phase = world.x * 0.55 + world.z * 0.35;
    float gust = sin(uTime * 0.6 + world.x * 0.08) * 0.5 + 0.5;
    float sway = (sin(uTime * 1.7 + phase) * 0.12 + sin(uTime * 0.9 + phase * 1.7) * 0.06) * (0.6 + gust);
    world.x += sway * h * h;
    world.z += sway * 0.4 * h * h;
    vec4 mv = modelViewMatrix * world;
    vH = h;
    vDepth = -mv.z;
    gl_Position = projectionMatrix * mv;
  }
`
const BLADE_FRAGMENT = /* glsl */ `
  uniform vec3 uBase;
  uniform vec3 uTip;
  uniform vec3 uFog;
  uniform float uFogNear;
  uniform float uFogFar;
  varying float vH;
  varying float vDepth;
  void main() {
    vec3 col = mix(uBase, uTip, smoothstep(0.0, 1.0, vH));
    float fog = smoothstep(uFogNear, uFogFar, vDepth);
    gl_FragColor = vec4(mix(col, uFog, fog), 1.0);
  }
`

function token(name: string): Color {
  const v = getComputedStyle(document.documentElement).getPropertyValue(name).trim()
  return new Color(v || 'white')
}

function lcg(seed: number) {
  let s = seed
  return () => (s = (s * 16807) % 2147483647) / 2147483647
}

export default function HeroThree({
  animate,
  onReady,
  scarecrow = true,
  className,
}: {
  animate: boolean
  onReady?: () => void
  scarecrow?: boolean
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
      renderer = new WebGLRenderer({ antialias: false, alpha: false, powerPreference: 'low-power' })
    } catch {
      return // no WebGL after all: the SVG scene stays visible
    }
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.5))
    el.appendChild(renderer.domElement)
    renderer.domElement.setAttribute('aria-hidden', 'true')
    renderer.domElement.style.width = '100%'
    renderer.domElement.style.height = '100%'
    renderer.domElement.style.display = 'block'

    const scene = new Scene()
    const camera = new PerspectiveCamera(48, 1, 0.1, 80)
    camera.position.set(0, 1.25, 4.2)
    const target = new Vector3(0, 0.45, -5)
    const disposables: { dispose: () => void }[] = []
    const track = <T extends { dispose: () => void }>(x: T): T => {
      disposables.push(x)
      return x
    }

    // --- lights, ground, sun
    scene.add(new AmbientLight(0xffffff, 1.4))
    const sunLight = new DirectionalLight(0xffffff, 1.6)
    sunLight.position.set(4, 6, 3)
    scene.add(sunLight)
    const groundMat = track(new MeshLambertMaterial())
    const ground = new Mesh(track(new PlaneGeometry(60, 40)), groundMat)
    ground.rotation.x = -Math.PI / 2
    ground.position.z = -12
    scene.add(ground)
    const sunMat = track(new MeshBasicMaterial({ transparent: true, opacity: 0.9, fog: false }))
    const sun = new Mesh(track(new CircleGeometry(1.6, 40)), sunMat)
    sun.position.set(4.5, 3.6, -24)
    scene.add(sun)

    // --- rice: instanced tapered blades swayed on the GPU
    const uniforms = {
      uTime: { value: 0 },
      uBase: { value: new Color() },
      uTip: { value: new Color() },
      uFog: { value: new Color() },
      uFogNear: { value: 8 },
      uFogFar: { value: 34 },
    }
    const bladeGeo = track(new PlaneGeometry(0.07, 1, 1, 4))
    const pos = bladeGeo.getAttribute('position') as BufferAttribute
    for (let i = 0; i < pos.count; i++) {
      const y = pos.getY(i) + 0.5
      pos.setY(i, y)
      pos.setX(i, pos.getX(i) * (1 - y * 0.85))
    }
    const bladeMat = track(
      new ShaderMaterial({
        vertexShader: BLADE_VERTEX,
        fragmentShader: BLADE_FRAGMENT,
        side: DoubleSide,
        uniforms,
      }),
    )
    const maxBlades = 2400
    const rice = new InstancedMesh(bladeGeo, bladeMat, maxBlades)
    rice.frustumCulled = false
    const rnd = lcg(11)
    const m = new Matrix4()
    const up = new Vector3(0, 1, 0)
    const axis = new Vector3()
    let n = 0
    for (let row = 0; row < 40 && n < maxBlades; row++) {
      const z = -1.5 - row * 0.75
      for (let col = -16; col <= 16 && n < maxBlades; col++) {
        const x0 = col * 0.62 + (row % 2) * 0.31
        for (let b = 0; b < 2 && n < maxBlades; b++, n++) {
          axis.set(rnd() - 0.5, 0, rnd() - 0.5).normalize()
          const q = new Quaternion().setFromAxisAngle(up, rnd() * Math.PI)
          q.multiply(new Quaternion().setFromAxisAngle(axis, (rnd() - 0.5) * 0.35))
          m.compose(
            new Vector3(x0 + (rnd() - 0.5) * 0.25, 0, z + (rnd() - 0.5) * 0.2),
            q,
            new Vector3(1, 0.75 + rnd() * 0.55, 1),
          )
          rice.setMatrixAt(n, m)
        }
      }
    }
    rice.count = n
    scene.add(rice)

    // --- scarecrow (কাকতাড়ুয়া)
    const crow = new Group()
    const wood = track(new MeshLambertMaterial())
    const shirt = track(new MeshLambertMaterial())
    const pants = track(new MeshLambertMaterial())
    const head = track(new MeshLambertMaterial())
    const part = (geo: BufferGeometry, mat: MeshLambertMaterial, x: number, y: number) => {
      const mesh = new Mesh(track(geo), mat)
      mesh.position.set(x, y, 0)
      crow.add(mesh)
    }
    part(new CylinderGeometry(0.035, 0.045, 2.2, 8), wood, 0, 1.1)
    part(new BoxGeometry(1.3, 0.07, 0.07), wood, 0, 1.55)
    part(new BoxGeometry(0.55, 0.55, 0.22), shirt, 0, 1.42)
    part(new BoxGeometry(0.45, 0.25, 0.2), pants, 0, 1.05)
    part(new SphereGeometry(0.2, 16, 12), head, 0, 1.92)
    part(new ConeGeometry(0.36, 0.3, 20), wood, 0, 2.16)
    crow.position.set(1.25, 0, -2.6)
    crow.rotation.y = -0.35
    if (scarecrow) scene.add(crow)

    // --- pollen
    const pollenCount = 180
    const prnd = lcg(5)
    const pollen = new Float32Array(pollenCount * 3)
    for (let i = 0; i < pollenCount; i++) {
      pollen[i * 3] = (prnd() - 0.5) * 14
      pollen[i * 3 + 1] = prnd() * 3.5
      pollen[i * 3 + 2] = -prnd() * 14
    }
    const pollenAttr = new BufferAttribute(pollen, 3)
    const pollenGeo = track(new BufferGeometry())
    pollenGeo.setAttribute('position', pollenAttr)
    const pollenMat = track(
      new PointsMaterial({
        size: 0.045,
        sizeAttenuation: true,
        transparent: true,
        opacity: 0.85,
        depthWrite: false,
        blending: AdditiveBlending,
      }),
    )
    scene.add(new Points(pollenGeo, pollenMat))

    // --- loop state (declared before anything can render)
    let running = false
    let raf = 0
    let last = performance.now()
    let t = 0
    let visible = true

    // --- theme: re-read the design tokens whenever the theme changes
    const fog = new Fog(0xffffff, 10, 36)
    scene.fog = fog
    const applyPalette = () => {
      const haze = token('--accent-bg')
      scene.background = token('--sky-bg')
      fog.color.copy(haze)
      uniforms.uFog.value.copy(haze)
      uniforms.uBase.value.copy(token('--primary'))
      uniforms.uTip.value.copy(token('--success'))
      groundMat.color.copy(token('--primary-hover'))
      sunMat.color.copy(token('--accent'))
      pollenMat.color.copy(token('--accent'))
      wood.color.copy(token('--accent'))
      shirt.color.copy(token('--danger'))
      pants.color.copy(token('--sky'))
      head.color.copy(token('--accent-bg'))
      if (!running) renderer.render(scene, camera)
    }
    const mo = new MutationObserver(applyPalette)
    mo.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] })
    const mq = window.matchMedia('(prefers-color-scheme: dark)')
    mq.addEventListener('change', applyPalette)

    // --- size and pointer parallax
    const resize = () => {
      const w = el.clientWidth || 1
      const h = el.clientHeight || 1
      renderer.setSize(w, h, false)
      camera.aspect = w / h
      camera.updateProjectionMatrix()
      if (!running) renderer.render(scene, camera)
    }
    const ro = new ResizeObserver(resize)
    ro.observe(el)
    const pointer = { x: 0, y: 0 }
    const onPointer = (e: PointerEvent) => {
      const r = el.getBoundingClientRect()
      pointer.x = Math.max(-1, Math.min(1, ((e.clientX - r.left) / r.width) * 2 - 1))
      pointer.y = Math.max(-1, Math.min(1, -(((e.clientY - r.top) / r.height) * 2 - 1)))
    }
    window.addEventListener('pointermove', onPointer, { passive: true })

    const frame = (now: number) => {
      const dt = Math.min(0.05, (now - last) / 1000)
      last = now
      t += dt
      uniforms.uTime.value = t
      const k = Math.min(1, dt * 1.6)
      camera.position.x += (pointer.x * 0.6 + Math.sin(t * 0.15) * 0.4 - camera.position.x) * k
      camera.position.y +=
        (1.25 + pointer.y * 0.15 + Math.sin(t * 0.2) * 0.05 - camera.position.y) * k
      camera.lookAt(target)
      crow.rotation.z = Math.sin(t * 0.7) * 0.025
      for (let i = 0; i < pollenCount; i++) {
        let y = (pollen[i * 3 + 1] ?? 0) + dt * 0.12
        if (y > 3.6) y = 0.2
        pollen[i * 3 + 1] = y
        pollen[i * 3] = (pollen[i * 3] ?? 0) + Math.sin(t * 0.8 + i) * dt * 0.05
      }
      pollenAttr.needsUpdate = true
      renderer.render(scene, camera)
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
    const io = new IntersectionObserver(([e]) => {
      visible = Boolean(e?.isIntersecting)
      schedule()
    })
    io.observe(el)
    document.addEventListener('visibilitychange', schedule)

    camera.lookAt(target)
    applyPalette()
    resize()
    schedule()
    readyRef.current?.()

    return () => {
      running = false
      cancelAnimationFrame(raf)
      document.removeEventListener('visibilitychange', schedule)
      window.removeEventListener('pointermove', onPointer)
      mq.removeEventListener('change', applyPalette)
      mo.disconnect()
      ro.disconnect()
      io.disconnect()
      rice.dispose()
      disposables.forEach((d) => d.dispose())
      renderer.dispose()
      renderer.domElement.remove()
    }
  }, [animate, scarecrow])

  return <div ref={host} className={className} aria-hidden="true" />
}
