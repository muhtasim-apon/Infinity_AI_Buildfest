// Closing scene: a 3D Bangladesh (simplified outline) whose 8 divisions light up one by one, plus
// the KPI TARGETS. Clearly labelled as a vision, not adoption, endorsement or results.
import * as THREE from 'three'
import { seg, lerp, v3, clamp } from './lib.js'

// simplified outline, lon/lat (approximate; decorative)
const OUTLINE = [
  [88.4, 26.63], [88.75, 26.3], [89.1, 26.15], [89.55, 26.0], [89.85, 25.95], [89.85, 25.3], [90.1, 25.22], [90.6, 25.17], [91.25, 25.2], [92.0, 25.18],
  [92.48, 24.95], [92.25, 24.4], [91.9, 24.15], [91.4, 24.1], [91.2, 23.65], [91.35, 23.1], [91.6, 22.95], [91.85, 23.25], [92.3, 23.55], [92.6, 22.0],
  [92.6, 21.4], [92.32, 20.75], [92.05, 21.2], [91.85, 22.2], [91.5, 22.5], [91.0, 22.75], [90.6, 22.2], [90.2, 21.85], [89.8, 21.85], [89.3, 21.65],
  [89.05, 21.7], [89.0, 22.2], [88.95, 22.9], [88.75, 23.25], [88.6, 23.6], [88.75, 24.1], [88.1, 24.45], [88.05, 24.7], [88.45, 25.2], [88.1, 25.5],
  [88.2, 25.8], [88.1, 26.2],
]
const DIVISIONS = [
  ['Dhaka', 90.4, 23.8], ['Rangpur', 89.25, 25.75], ['Rajshahi', 88.6, 24.37], ['Mymensingh', 90.4, 24.75],
  ['Sylhet', 91.87, 24.9], ['Khulna', 89.55, 22.8], ['Barishal', 90.35, 22.7], ['Chattogram', 91.8, 22.35],
]
const P = (lon, lat) => new THREE.Vector2((lon - 90.3) * 4, (lat - 23.7) * 4.5)

export function createMap() {
  const scene = new THREE.Scene()
  scene.background = new THREE.Color('#030a08')
  scene.fog = new THREE.FogExp2('#030a08', 0.012)
  const cam = new THREE.PerspectiveCamera(42, 1920 / 1080, 0.1, 400)
  scene.add(new THREE.AmbientLight('#ffffff', 0.5))
  const key = new THREE.DirectionalLight('#fff1d6', 2.2)
  key.position.set(-10, 25, 15)
  scene.add(key)

  const shape = new THREE.Shape(OUTLINE.map(([a, b]) => P(a, b)))
  const geo = new THREE.ExtrudeGeometry(shape, { depth: 0.9, bevelEnabled: true, bevelThickness: 0.15, bevelSize: 0.12, bevelSegments: 3 })
  geo.rotateX(-Math.PI / 2)
  const land = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ color: '#1f5a30', roughness: 0.55, metalness: 0.1, emissive: '#0d3a1c', emissiveIntensity: 0.4 }))
  scene.add(land)
  const edge = new THREE.LineSegments(new THREE.EdgesGeometry(geo, 30), new THREE.LineBasicMaterial({ color: '#7dffb0' }))
  scene.add(edge)
  // rivers suggestion: a glowing grid on the surface
  const grid = new THREE.GridHelper(80, 80, '#1d6b3a', '#123d24')
  grid.position.y = -0.01
  scene.add(grid)

  const divs = DIVISIONS.map(([name, lon, lat], i) => {
    const p = P(lon, lat)
    const pos = v3(p.x, 1.1, -p.y)
    const pin = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.12, 1, 12), new THREE.MeshBasicMaterial({ color: '#ffcf6b', toneMapped: false }))
    pin.position.copy(pos)
    scene.add(pin)
    const rings = [0, 1, 2].map(() => {
      const r = new THREE.Mesh(new THREE.RingGeometry(0.4, 0.5, 48), new THREE.MeshBasicMaterial({ color: '#7dffb0', transparent: true, side: THREE.DoubleSide, toneMapped: false, depthWrite: false }))
      r.rotation.x = -Math.PI / 2
      r.position.copy(pos).setY(1.08)
      scene.add(r)
      return r
    })
    return { name, pos, pin, rings, i }
  })

  // HUD (DOM) for labels + KPI targets
  const hudRoot = document.getElementById('hud')
  const labels = divs.map((d) => {
    const e = document.createElement('div')
    e.className = 'lbl'
    e.style.position = 'absolute'
    e.style.color = '#e9ffe9'
    e.textContent = d.name
    hudRoot.appendChild(e)
    return e
  })
  const kpi = document.createElement('div')
  kpi.className = 'card'
  Object.assign(kpi.style, { right: '80px', top: '150px', width: '560px' })
  kpi.innerHTML =
    '<span class="tag vision" style="margin:0 0 12px">TARGETS · not results yet</span>' +
    '<h3>0 wrong advice shown</h3><p>abstain below 0.60 · validator V1–V6</p><br/>' +
    '<h3>Alerts verified ≤ 7 days</h3><p>3 scans · 1 division · human approval</p><br/>' +
    '<h3>Fewer unnecessary sprays</h3><p>advice only from BRRI factsheets</p>' +
    '<small>Next: labelled field evaluation · agronomist review · more crops · vector search</small>'
  hudRoot.appendChild(kpi)
  const visionTag = document.createElement('div')
  visionTag.className = 'card'
  Object.assign(visionTag.style, { left: '80px', top: '150px', width: '520px' })
  visionTag.innerHTML = '<h3>Our vision: all 8 divisions</h3><p>free for farmers · sponsored by cooperatives, NGOs and extension programmes</p><span class="tag vision">VISION · not yet real</span>'
  hudRoot.appendChild(visionTag)

  function update(t, t0, t1) {
    const k = seg(t, t0, t1)
    const a = lerp(-0.35, 0.25, k)
    const r = lerp(30, 24, k)
    cam.position.set(Math.sin(a) * r, lerp(26, 19, k), Math.cos(a) * r)
    cam.lookAt(0, 0, 1)
    divs.forEach((d) => {
      const on = t0 + 0.8 + d.i * 0.55
      const lit = clamp((t - on) / 0.4)
      d.pin.scale.y = lerp(0.01, 2.2, lit)
      d.pin.position.y = 1.1 + d.pin.scale.y / 2
      d.rings.forEach((ring, j) => {
        const ph = ((t - on) * 0.6 + j / 3) % 1
        ring.visible = t > on
        ring.scale.setScalar(0.5 + ph * 3.5)
        ring.material.opacity = (1 - ph) * 0.8 * lit
      })
    })
    return cam
  }

  function hud(t, t0, t1) {
    const active = t >= t0
    const fadeIn = seg(t, t0 + 0.6, t0 + 1.4), fadeOut = 1 - seg(t, t1 - 0.4, t1 + 0.4)
    labels.forEach((e, i) => {
      const d = divs[i]
      const lit = active ? clamp((t - (t0 + 0.8 + i * 0.55)) / 0.4) * fadeOut : 0
      e.style.opacity = lit.toFixed(3)
      if (lit > 0) {
        const p = d.pos.clone().setY(d.pin.position.y + d.pin.scale.y / 2 + 0.4).project(cam)
        e.style.left = ((p.x * 0.5 + 0.5) * 1920 - 40).toFixed(0) + 'px'
        e.style.top = ((-p.y * 0.5 + 0.5) * 1080 - 30).toFixed(0) + 'px'
      }
    })
    kpi.style.opacity = active ? (seg(t, t0 + 4.0, t0 + 4.8) * fadeOut).toFixed(3) : 0
    visionTag.style.opacity = active ? (fadeIn * (1 - seg(t, t0 + 3.6, t0 + 4.2)) * fadeOut).toFixed(3) : 0
  }

  return { scene, update, hud }
}
