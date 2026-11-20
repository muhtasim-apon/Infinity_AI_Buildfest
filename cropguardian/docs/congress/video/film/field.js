// The field world: a Bangladeshi aman paddy at golden-hour afternoon. Physical sky (Preetham),
// sun + sky light + image-based reflections, flooded paddy water, instanced rice clumps swaying in
// the wind (GPU), earthen bunds (aal), palm/broadleaf tree lines, tin-roof homesteads, egrets.
import * as THREE from 'three'
import { Sky } from 'three/addons/objects/Sky.js'
import { Lensflare, LensflareElement } from 'three/addons/objects/Lensflare.js'
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js'
import { canvasTex, pixelTex, fbm, rng, noise } from './lib.js'
import { makeFarmer } from './farmer.js'

export const SUN_DIR = new THREE.Vector3(0.42, 0.2, -0.88).normalize()
export const PATCH = new THREE.Vector3(0.75, 0, -21) // the diseased clumps beside the bund

function windMaterial(mat, uniforms, strength = 1) {
  mat.onBeforeCompile = (sh) => {
    sh.uniforms.uTime = uniforms.uTime
    sh.vertexShader = sh.vertexShader
      .replace('#include <common>', '#include <common>\nuniform float uTime;')
      .replace(
        '#include <begin_vertex>',
        `#include <begin_vertex>
        {
          vec4 wp = instanceMatrix * vec4(0.0, 0.0, 0.0, 1.0);
          float h = clamp(position.y, 0.0, 1.4);
          float g = sin(uTime * 0.55 + wp.x * 0.06 + wp.z * 0.035) * 0.5 + 0.5;
          float w = sin(uTime * 1.9 + wp.x * 0.7 + wp.z * 0.45) * 0.07 + sin(uTime * 3.1 + wp.x * 1.3) * 0.025;
          float bend = (w + g * 0.11) * ${strength.toFixed(2)};
          transformed.x += bend * h * h;
          transformed.z += bend * 0.6 * h * h;
          transformed.y -= abs(bend) * 0.25 * h * h;
        }`,
      )
  }
  mat.customProgramCacheKey = () => 'wind' + strength
  return mat
}

/** One rice hill: ~10 curved tapering blades plus 2 drooping panicles, merged; vertex colours. */
function riceClumpGeometry(seed) {
  const r = rng(seed)
  const parts = []
  const colBase = new THREE.Color('#2f5a1c'), colMid = new THREE.Color('#5f8f2a'), colTip = new THREE.Color('#b9b04a')
  for (let i = 0; i < 10; i++) {
    const len = 0.75 + r() * 0.45, wid = 0.012 + r() * 0.006
    const segs = 6
    const g = new THREE.PlaneGeometry(wid, len, 1, segs)
    g.translate(0, len / 2, 0)
    const pos = g.getAttribute('position')
    const lean = 0.15 + r() * 0.5, yaw = r() * Math.PI * 2
    const cols = []
    for (let v = 0; v < pos.count; v++) {
      const y = pos.getY(v), k = y / len
      pos.setX(v, pos.getX(v) * (1 - k * 0.85))
      // arc outward: blades bow away from the clump centre
      const out = Math.sin(k * 1.4) * lean * len * 0.55 + k * k * lean * 0.25
      pos.setZ(v, out)
      pos.setY(v, y - k * k * lean * 0.18)
      const c = k < 0.5 ? colBase.clone().lerp(colMid, k * 2) : colMid.clone().lerp(colTip, (k - 0.5) * 1.4)
      cols.push(c.r, c.g, c.b)
    }
    g.setAttribute('color', new THREE.Float32BufferAttribute(cols, 3))
    g.rotateY(yaw)
    g.translate((r() - 0.5) * 0.05, 0, (r() - 0.5) * 0.05)
    parts.push(g)
  }
  for (let i = 0; i < 2; i++) {
    // panicle: a thin golden stalk that droops at the top
    const len = 0.9 + r() * 0.2
    const g = new THREE.PlaneGeometry(0.02, 0.32, 1, 5)
    g.translate(0, 0.16, 0)
    const pos = g.getAttribute('position')
    const cols = []
    const gold = new THREE.Color('#d6b65a'), dark = new THREE.Color('#9b8a3a')
    for (let v = 0; v < pos.count; v++) {
      const k = pos.getY(v) / 0.32
      pos.setZ(v, Math.sin(k * 1.6) * 0.18)
      pos.setY(v, len - 0.1 + pos.getY(v) * 0.6 - k * k * 0.18)
      const c = dark.clone().lerp(gold, k)
      cols.push(c.r, c.g, c.b)
    }
    g.setAttribute('color', new THREE.Float32BufferAttribute(cols, 3))
    g.rotateY(r() * Math.PI * 2)
    parts.push(g)
  }
  const m = mergeGeometries(parts)
  m.computeVertexNormals()
  return m
}

function frondTexture() {
  return canvasTex(256, 512, (g, w, h) => {
    g.clearRect(0, 0, w, h)
    g.strokeStyle = '#6b6a2a'
    g.lineWidth = 5
    g.beginPath()
    g.moveTo(w / 2, h)
    g.lineTo(w / 2, 0)
    g.stroke()
    for (let y = 20; y < h; y += 7) {
      const k = 1 - y / h
      const len = (0.12 + 0.36 * Math.sin(k * Math.PI)) * w
      for (const s of [-1, 1]) {
        g.strokeStyle = `rgba(${40 + Math.random() * 30},${85 + Math.random() * 40},${25 + Math.random() * 20},1)`
        g.lineWidth = 3.2
        g.beginPath()
        g.moveTo(w / 2, y)
        g.quadraticCurveTo(w / 2 + s * len * 0.6, y + 8, w / 2 + s * len, y + 26)
        g.stroke()
      }
    }
  })
}

function leafCardTexture(seed) {
  const r = rng(seed)
  return canvasTex(256, 256, (g, w, h) => {
    g.clearRect(0, 0, w, h)
    for (let i = 0; i < 220; i++) {
      const x = w / 2 + (r() - 0.5) * w * 0.85, y = h / 2 + (r() - 0.5) * h * 0.85
      const d = Math.hypot(x - w / 2, y - h / 2) / (w * 0.45)
      if (d > 1) continue
      const shade = 30 + r() * 50
      g.fillStyle = `rgb(${shade * 0.6},${shade + 35},${shade * 0.4})`
      g.beginPath()
      g.ellipse(x, y, 9 + r() * 8, 4 + r() * 4, r() * Math.PI, 0, Math.PI * 2)
      g.fill()
    }
  })
}

export function createField(renderer, ui) {
  const scene = new THREE.Scene()
  const uniforms = { uTime: { value: 0 } }

  // --- sky + environment light
  const sky = new Sky()
  sky.scale.setScalar(4000)
  const su = sky.material.uniforms
  su.turbidity.value = 5.5
  su.rayleigh.value = 1.25
  su.mieCoefficient.value = 0.0035
  su.mieDirectionalG.value = 0.86
  su.sunPosition.value.copy(SUN_DIR)
  scene.add(sky)
  const pmrem = new THREE.PMREMGenerator(renderer)
  const envScene = new THREE.Scene()
  const sky2 = new Sky()
  sky2.scale.setScalar(4000)
  Object.assign(sky2.material.uniforms.sunPosition.value, SUN_DIR)
  for (const k of ['turbidity', 'rayleigh', 'mieCoefficient', 'mieDirectionalG']) sky2.material.uniforms[k].value = su[k].value
  envScene.add(sky2)
  scene.environment = pmrem.fromScene(envScene, 0.02).texture
  scene.environmentIntensity = 0.45
  scene.fog = new THREE.FogExp2(new THREE.Color('#b9ab8c'), 0.0055)

  const sun = new THREE.DirectionalLight('#ffd6a8', 2.6)
  sun.position.copy(SUN_DIR).multiplyScalar(60)
  sun.castShadow = true
  sun.shadow.mapSize.set(4096, 4096)
  sun.shadow.camera.left = -9
  sun.shadow.camera.right = 9
  sun.shadow.camera.top = 9
  sun.shadow.camera.bottom = -9
  sun.shadow.camera.near = 1
  sun.shadow.camera.far = 140
  sun.shadow.bias = -0.0004
  sun.shadow.normalBias = 0.03
  scene.add(sun, sun.target)
  scene.add(new THREE.HemisphereLight('#b9cdf0', '#5b4a2c', 0.75))

  // lens flare at the sun
  const flareTex = (core) =>
    canvasTex(128, 128, (g, w) => {
      const gr = g.createRadialGradient(w / 2, w / 2, 0, w / 2, w / 2, w / 2)
      gr.addColorStop(0, core)
      gr.addColorStop(1, 'rgba(255,200,120,0)')
      g.fillStyle = gr
      g.fillRect(0, 0, w, w)
    })
  const flare = new Lensflare()
  flare.addElement(new LensflareElement(flareTex('rgba(255,240,210,0.9)'), 170, 0, new THREE.Color('#ffe6c0')))
  flare.addElement(new LensflareElement(flareTex('rgba(255,190,110,0.35)'), 80, 0.5))
  flare.addElement(new LensflareElement(flareTex('rgba(255,210,150,0.25)'), 140, 0.8))
  flare.addElement(new LensflareElement(flareTex('rgba(200,220,255,0.18)'), 60, 1.0))
  const flareHolder = new THREE.PointLight('#ffffff', 0, 0)
  flareHolder.position.copy(SUN_DIR).multiplyScalar(1500)
  flareHolder.add(flare)
  scene.add(flareHolder)

  // --- flooded paddy water + mud
  const waterNormal = pixelTex(256, 256, (x, y) => {
    const n1 = fbm(x / 18, y / 18, 4), n2 = fbm(x / 18 + 0.3, y / 18, 4), n3 = fbm(x / 18, y / 18 + 0.3, 4)
    return [128 + (n2 - n1) * 400, 128 + (n3 - n1) * 400, 255]
  }, { repeat: [40, 40], srgb: false })
  const water = new THREE.Mesh(
    new THREE.PlaneGeometry(400, 400),
    new THREE.MeshStandardMaterial({ color: '#3d4a2c', roughness: 0.14, metalness: 0.0, normalMap: waterNormal, normalScale: new THREE.Vector2(0.25, 0.25), envMapIntensity: 1.4 }),
  )
  water.rotation.x = -Math.PI / 2
  water.position.y = 0.02
  water.receiveShadow = true
  scene.add(water)

  // distant canopy (beyond the instanced rice): a raised textured surface hidden in haze
  const canopyTex = pixelTex(512, 512, (x, y) => {
    const n = fbm(x / 6, y / 30, 5)
    const row = Math.sin(x * 0.9) * 0.08
    const k = n + row
    return [70 + k * 70, 110 + k * 70, 34 + k * 30]
  }, { repeat: [30, 10] })
  const canopy = new THREE.Mesh(new THREE.PlaneGeometry(520, 300), new THREE.MeshStandardMaterial({ map: canopyTex, roughness: 0.9 }))
  canopy.rotation.x = -Math.PI / 2
  canopy.position.set(0, 0.72, -215)
  scene.add(canopy)
  for (const s of [-1, 1]) {
    const side = canopy.clone()
    side.scale.set(0.35, 0.55, 1)
    side.position.set(s * 120, 0.72, -10)
    scene.add(side)
  }

  // --- bunds (aal): raised earth paths with grassy edges
  const soilTex = pixelTex(256, 256, (x, y) => {
    const n = fbm(x / 10, y / 10, 5), g = fbm(x / 3 + 9, y / 3, 3)
    const grass = g > 0.62 ? 1 : 0
    return grass ? [70 + n * 40, 95 + n * 50, 38] : [118 + n * 60, 92 + n * 45, 62 + n * 30]
  }, { repeat: [1, 30] })
  const soilMat = new THREE.MeshStandardMaterial({ map: soilTex, roughness: 0.96 })
  const bunds = []
  const addBund = (x, z, len, rotY) => {
    const g = new THREE.BoxGeometry(0.62, 0.26, len, 4, 1, Math.max(4, Math.round(len)))
    const p = g.getAttribute('position')
    for (let i = 0; i < p.count; i++) {
      if (p.getY(i) > 0) p.setX(i, p.getX(i) * 0.82) // trapezoid section
      p.setY(i, p.getY(i) + (noise(p.getX(i) * 3, p.getZ(i) * 0.8) - 0.5) * 0.04)
    }
    g.computeVertexNormals()
    const m = new THREE.Mesh(g, soilMat)
    m.position.set(x, 0.11, z)
    m.rotation.y = rotY
    m.receiveShadow = true
    m.castShadow = true
    scene.add(m)
    bunds.push(m)
  }
  addBund(0, -40, 110, 0) // the main path the farmer walks
  addBund(-14, -40, 110, 0)
  addBund(14, -40, 110, 0)
  for (const z of [-8, -36, -64, -92]) addBund(0, z, 80, Math.PI / 2)
  // short grass tufts on the main bund
  {
    const tuft = new THREE.ConeGeometry(0.03, 0.14, 4, 1, true)
    tuft.translate(0, 0.07, 0)
    const tm = new THREE.InstancedMesh(tuft, windMaterial(new THREE.MeshStandardMaterial({ color: '#557a2c', roughness: 0.9, side: THREE.DoubleSide }), uniforms, 0.4), 1800)
    const r = rng(77), m4 = new THREE.Matrix4()
    for (let i = 0; i < 1800; i++) {
      const side = r() < 0.5 ? -1 : 1
      m4.compose(new THREE.Vector3(side * (0.2 + r() * 0.1), 0.22, 10 - r() * 100), new THREE.Quaternion().setFromEuler(new THREE.Euler((r() - 0.5) * 0.5, 0, (r() - 0.5) * 0.5)), new THREE.Vector3(1, 0.6 + r(), 1))
      tm.setMatrixAt(i, m4)
    }
    scene.add(tm)
  }

  // --- rice: instanced hills in transplanted rows, two geometry variants
  const riceMat = windMaterial(new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.62, side: THREE.DoubleSide, envMapIntensity: 0.6 }), uniforms, 1)
  const variants = [riceClumpGeometry(3), riceClumpGeometry(11), riceClumpGeometry(29)]
  const spots = []
  {
    const r = rng(1234)
    for (let z = 9; z > -72; z -= 0.34)
      for (let x = -22; x < 22; x += 0.3) {
        if (Math.abs(x) < 0.45 || Math.abs(x + 14) < 0.42 || Math.abs(x - 14) < 0.42) continue // bunds
        if ([-8, -36, -64].some((b) => Math.abs(z - b) < 0.42)) continue
        if (Math.hypot(x - PATCH.x - 0.15, z - PATCH.z) < 0.32) continue // room for the hero leaves
        // farther rows thin out a little (hidden by haze anyway)
        const far = Math.max(0, -z - 30) / 45
        if (r() < far * 0.45) continue
        spots.push([x + (r() - 0.5) * 0.06, z + (r() - 0.5) * 0.06, r(), r(), r()])
      }
  }
  const per = Math.ceil(spots.length / variants.length)
  const diseased = new THREE.Color('#a67a33'), healthy = new THREE.Color('#ffffff')
  variants.forEach((geo, vi) => {
    const list = spots.slice(vi * per, (vi + 1) * per)
    const im = new THREE.InstancedMesh(geo, riceMat, list.length)
    const m4 = new THREE.Matrix4()
    list.forEach(([x, z, a, b, c], i) => {
      m4.compose(new THREE.Vector3(x, 0, z), new THREE.Quaternion().setFromEuler(new THREE.Euler(0, a * Math.PI * 2, 0)), new THREE.Vector3(0.9 + b * 0.25, 0.85 + c * 0.3, 0.9 + b * 0.25))
      im.setMatrixAt(i, m4)
      const d = Math.hypot(x - PATCH.x - 1.2, (z - PATCH.z) * 0.8)
      const sick = Math.max(0, 1 - d / 3.2)
      im.setColorAt(i, healthy.clone().lerp(diseased, sick * (0.55 + 0.45 * c)))
    })
    im.castShadow = true
    im.receiveShadow = true
    im.frustumCulled = false
    scene.add(im)
  })

  // --- hero diseased leaf (macro shot): brown-spot lesions on a yellowing blade
  const lesionTex = canvasTex(256, 1024, (g, w, h) => {
    const gr = g.createLinearGradient(0, h, 0, 0)
    gr.addColorStop(0, '#4f7d22')
    gr.addColorStop(0.55, '#88952c')
    gr.addColorStop(1, '#c2a43c')
    g.fillStyle = gr
    g.fillRect(0, 0, w, h)
    g.strokeStyle = 'rgba(230,235,180,0.35)'
    for (let x = 18; x < w; x += 22) {
      g.beginPath()
      g.moveTo(x, 0)
      g.lineTo(x, h)
      g.stroke()
    }
    const r = rng(42)
    for (let i = 0; i < 55; i++) {
      const x = 30 + r() * (w - 60), y = 60 + r() * (h - 140), rx = 6 + r() * 9, ry = rx * (1.8 + r())
      g.fillStyle = 'rgba(214,170,60,0.85)'
      g.beginPath()
      g.ellipse(x, y, rx * 1.6, ry * 1.5, 0, 0, Math.PI * 2)
      g.fill()
      g.fillStyle = 'rgba(110,55,20,0.95)'
      g.beginPath()
      g.ellipse(x, y, rx, ry, 0, 0, Math.PI * 2)
      g.fill()
      g.fillStyle = 'rgba(170,150,120,0.8)'
      g.beginPath()
      g.ellipse(x, y, rx * 0.35, ry * 0.35, 0, 0, Math.PI * 2)
      g.fill()
    }
  })
  const heroLeafGeo = new THREE.PlaneGeometry(0.055, 0.85, 4, 24)
  heroLeafGeo.translate(0, 0.425, 0)
  {
    const p = heroLeafGeo.getAttribute('position')
    for (let i = 0; i < p.count; i++) {
      const k = p.getY(i) / 0.85
      p.setX(i, p.getX(i) * (1 - k * 0.8))
      p.setZ(i, Math.sin(k * 1.5) * 0.25 + p.getX(i) * p.getX(i) * 8)
    }
    heroLeafGeo.computeVertexNormals()
  }
  const heroLeaf = new THREE.Mesh(heroLeafGeo, new THREE.MeshStandardMaterial({ map: lesionTex, roughness: 0.55, side: THREE.DoubleSide }))
  heroLeaf.position.set(PATCH.x + 0.12, 0.02, PATCH.z)
  heroLeaf.scale.set(1.35, 1.1, 1.35)
  heroLeaf.rotation.y = -Math.PI / 2 + 0.25
  heroLeaf.castShadow = true
  scene.add(heroLeaf)
  const heroLeaf2 = heroLeaf.clone()
  heroLeaf2.position.set(PATCH.x + 0.22, 0.05, PATCH.z - 0.08)
  heroLeaf2.rotation.y = -Math.PI / 2 - 0.45
  heroLeaf2.scale.set(1.2, 1.0, 1.2)
  scene.add(heroLeaf2)
  for (const [dx, dz, ry, s] of [[0.05, 0.12, -Math.PI / 2 + 0.7, 1.1], [0.3, 0.05, -Math.PI / 2 - 0.1, 1.25], [0.18, -0.16, -Math.PI / 2 + 0.15, 0.95]]) {
    const l = heroLeaf.clone()
    l.position.set(PATCH.x + dx, 0.02, PATCH.z + dz)
    l.rotation.y = ry
    l.scale.setScalar(s)
    scene.add(l)
  }

  // --- tree lines: coconut palms + broadleaf trees + bamboo, homesteads with tin roofs
  const frondMat = new THREE.MeshStandardMaterial({ map: frondTexture(), alphaTest: 0.45, side: THREE.DoubleSide, roughness: 0.8 })
  const barkMat = new THREE.MeshStandardMaterial({ map: pixelTex(64, 256, (x, y) => { const n = fbm(x / 6, y / 3, 3); const ring = (y % 16) < 2 ? -30 : 0; return [95 + n * 40 + ring, 80 + n * 35 + ring, 62 + n * 25 + ring] }, { repeat: [1, 3] }), roughness: 0.95 })
  const leafMats = [1, 2, 3].map((s) => new THREE.MeshStandardMaterial({ map: leafCardTexture(s), alphaTest: 0.4, side: THREE.DoubleSide, roughness: 0.85 }))
  function palm(x, z, h, r) {
    const g = new THREE.Group()
    const curve = new THREE.CatmullRomCurve3([v(0, 0, 0), v(0.25 * r, h * 0.4, 0.1), v(0.6 * r, h * 0.75, 0.15), v(0.9 * r, h, 0.1)])
    const trunk = new THREE.Mesh(new THREE.TubeGeometry(curve, 16, 0.16, 8), barkMat)
    g.add(trunk)
    const top = curve.getPoint(1)
    for (let i = 0; i < 14; i++) {
      const fg = new THREE.PlaneGeometry(1.1, 3.4, 1, 8)
      fg.translate(0, 1.7, 0)
      const p = fg.getAttribute('position')
      for (let k = 0; k < p.count; k++) {
        const y = p.getY(k) / 3.4
        p.setZ(k, -y * y * 1.6)
      }
      const f = new THREE.Mesh(fg, frondMat)
      f.position.copy(top)
      f.rotation.set(-0.4 - Math.random() * 0.6, (i / 14) * Math.PI * 2, 0, 'YXZ')
      g.add(f)
    }
    g.position.set(x, 0, z)
    return g
  }
  function broadleaf(x, z, s, seed) {
    const g = new THREE.Group()
    const r = rng(seed)
    const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.18 * s, 0.3 * s, 3.5 * s, 8), barkMat)
    trunk.position.y = 1.75 * s
    g.add(trunk)
    for (let i = 0; i < 46; i++) {
      const card = new THREE.Mesh(new THREE.PlaneGeometry(2.4 * s, 2.4 * s), leafMats[i % 3])
      const a = r() * Math.PI * 2, b = r() * Math.PI
      card.position.set(Math.cos(a) * Math.sin(b) * 2.3 * s, 4.6 * s + Math.cos(b) * 1.8 * s, Math.sin(a) * Math.sin(b) * 2.3 * s)
      card.rotation.set(r() * Math.PI, r() * Math.PI, r() * Math.PI)
      g.add(card)
    }
    g.position.set(x, 0, z)
    return g
  }
  function hut(x, z, rot) {
    const g = new THREE.Group()
    const wallTex = pixelTex(128, 128, (px, py) => { const n = fbm(px / 5, py / 14, 3); return [150 + n * 40, 120 + n * 35, 80 + n * 25] })
    const walls = new THREE.Mesh(new THREE.BoxGeometry(5, 2.4, 3.4), new THREE.MeshStandardMaterial({ map: wallTex, roughness: 0.95 }))
    walls.position.y = 1.2
    g.add(walls)
    const tinTex = canvasTex(64, 256, (cg, w, h) => { for (let x = 0; x < w; x++) { const k = Math.sin(x * 0.8) * 0.5 + 0.5; cg.fillStyle = `rgb(${120 + k * 70},${115 + k * 65},${108 + k * 60})`; cg.fillRect(x, 0, 1, h) } cg.fillStyle = 'rgba(140,70,30,0.35)'; cg.fillRect(0, h * 0.7, w, h * 0.3) }, { repeat: [6, 1] })
    const tin = new THREE.MeshStandardMaterial({ map: tinTex, metalness: 0.75, roughness: 0.38, side: THREE.DoubleSide })
    for (const s of [-1, 1]) {
      const roof = new THREE.Mesh(new THREE.PlaneGeometry(5.6, 2.3), tin)
      roof.position.set(0, 2.95, s * 0.95)
      roof.rotation.set(s * -1.05 + (s > 0 ? 0 : 0), 0, 0)
      roof.rotation.x = s > 0 ? -Math.PI / 2 + 0.55 : Math.PI / 2 - 0.55
      roof.rotation.x = -s * (Math.PI / 2 - 0.55)
      g.add(roof)
    }
    g.position.set(x, 0, z)
    g.rotation.y = rot
    return g
  }
  const v = (x, y, z) => new THREE.Vector3(x, y, z)
  {
    const r = rng(9)
    for (let x = -140; x <= 140; x += 6 + r() * 6) {
      const z = -112 - r() * 30
      const kind = r()
      if (kind < 0.4) scene.add(palm(x, z, 9 + r() * 5, r() - 0.5))
      else scene.add(broadleaf(x, z, 1.3 + r() * 0.9, Math.floor(r() * 1000)))
    }
    for (let i = 0; i < 26; i++) {
      const s = i % 2 ? 1 : -1
      const x = s * (40 + r() * 70), z = -20 - r() * 90
      scene.add(r() < 0.5 ? palm(x, z, 8 + r() * 5, r() - 0.5) : broadleaf(x, z, 1.2 + r() * 0.8, i * 31))
    }
    for (const [x, z, rot] of [[-30, -122, 0.2], [18, -126, -0.3], [55, -118, 0.4], [-70, -128, 0.1]]) scene.add(hut(x, z, rot))
  }

  // --- egrets gliding across the sky
  const birds = []
  {
    const bodyMat = new THREE.MeshStandardMaterial({ color: '#f4f2ea', roughness: 0.6 })
    for (let i = 0; i < 6; i++) {
      const b = new THREE.Group()
      const body = new THREE.Mesh(new THREE.CapsuleGeometry(0.12, 0.5, 4, 8), bodyMat)
      body.rotation.z = Math.PI / 2
      b.add(body)
      const wings = []
      for (const s of [-1, 1]) {
        const w = new THREE.Mesh(new THREE.PlaneGeometry(0.5, 1.1), bodyMat)
        w.geometry.translate(0, 0, 0)
        w.geometry.rotateX(Math.PI / 2)
        w.geometry.translate(0, 0, s * 0.55)
        b.add(w)
        wings.push(w)
      }
      b.userData = { wings, i }
      scene.add(b)
      birds.push(b)
    }
  }

  // --- the farmers: Rahim + neighbours (impact scene)
  const rahim = makeFarmer({ seed: 1 })
  scene.add(rahim)
  const others = [
    makeFarmer({ shirt: '#b8c9d6', lungi: ['#5b2a3a', '#2f4f6b'], seed: 2 }),
    makeFarmer({ shirt: '#e3d6b5', lungi: ['#2e5b3a', '#6b5a2f'], seed: 3 }),
    makeFarmer({ shirt: '#c9b0a0', lungi: ['#1f3d63', '#7a2e2e'], seed: 4, hat: false }),
    makeFarmer({ shirt: '#d8d8d0', lungi: ['#3a3a6b', '#2f6b5a'], seed: 5 }),
  ]
  others.forEach((f) => {
    f.visible = false
    scene.add(f)
  })

  function update(t) {
    uniforms.uTime.value = t
    // shadows follow the action
    const focus = rahim.position
    sun.target.position.copy(focus)
    sun.position.copy(focus).addScaledVector(SUN_DIR, 60)
    birds.forEach((b) => {
      const { wings, i } = b.userData
      const k = (t * 0.035 + i * 0.07) % 1
      b.position.set(-60 + k * 140 + i * 3, 16 + i * 1.4 + Math.sin(t * 0.3 + i) * 0.6, -70 - i * 6)
      b.rotation.y = -0.1
      const flap = Math.sin(t * 5 + i * 1.3) * 0.5
      wings[0].rotation.x = flap
      wings[1].rotation.x = -flap
    })
  }

  // hero phone for the point-of-view shots: phone + the hand holding it
  const heroPhone = new THREE.Group()
  {
    const skin = new THREE.MeshStandardMaterial({ color: '#7a4a2c', roughness: 0.6, emissive: '#2b170c', emissiveIntensity: 0.6 })
    const body = new THREE.Mesh(new THREE.BoxGeometry(0.076, 0.158, 0.0085), new THREE.MeshStandardMaterial({ color: '#15171b', roughness: 0.3, metalness: 0.7 }))
    heroPhone.add(body)
    const screen = new THREE.Mesh(new THREE.PlaneGeometry(0.0705, 0.1525), new THREE.MeshBasicMaterial({ color: '#000', toneMapped: false, fog: false }))
    screen.position.z = 0.0044
    heroPhone.add(screen)
    heroPhone.userData.screen = screen
    const lens = new THREE.Mesh(new THREE.CylinderGeometry(0.006, 0.006, 0.003, 16), new THREE.MeshStandardMaterial({ color: '#050505', roughness: 0.1 }))
    lens.rotation.x = Math.PI / 2
    lens.position.set(-0.024, 0.065, -0.0055)
    heroPhone.add(lens)
    // hand: palm behind, fingers wrapping the left edge, thumb on the right edge
    const palm = new THREE.Mesh(new THREE.CapsuleGeometry(0.03, 0.05, 6, 12), skin)
    palm.rotation.z = Math.PI / 2.4
    palm.scale.set(1, 1, 0.55)
    palm.position.set(0.012, -0.06, -0.02)
    heroPhone.add(palm)
    for (let i = 0; i < 4; i++) {
      const f = new THREE.Mesh(new THREE.CapsuleGeometry(0.0085, 0.03, 4, 8), skin)
      f.rotation.z = Math.PI / 2
      f.position.set(-0.042, -0.035 - i * 0.019, -0.002)
      heroPhone.add(f)
    }
    const thumb = new THREE.Mesh(new THREE.CapsuleGeometry(0.01, 0.04, 4, 8), skin)
    thumb.rotation.z = -0.5
    thumb.position.set(0.04, -0.045, 0.004)
    heroPhone.add(thumb)
    const wrist = new THREE.Mesh(new THREE.CapsuleGeometry(0.03, 0.16, 6, 12), skin)
    wrist.rotation.set(0.9, 0, -0.5)
    wrist.position.set(0.05, -0.15, -0.07)
    heroPhone.add(wrist)
    heroPhone.visible = false
    heroPhone.traverse((o) => { if (o.isMesh) { o.castShadow = true; o.receiveShadow = true } })
    scene.add(heroPhone)
  }

  return { scene, sun, rahim, others, heroLeaf, heroPhone, update, uniforms, ui }
}
