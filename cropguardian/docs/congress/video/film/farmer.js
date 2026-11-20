// Procedural Bangladeshi rice farmer: palm-leaf hat (mathal), half-sleeve shirt, gamchha on the
// shoulder, lungi tucked to the knee, bare feet. A joint hierarchy driven by named poses.
import * as THREE from 'three'
import { canvasTex, plaidTex, pixelTex, fbm, clamp, lerp } from './lib.js'

const SKIN = '#5a3620'

function cap(r, len, mat, seg = 12) {
  const m = new THREE.Mesh(new THREE.CapsuleGeometry(r, len, 6, seg), mat)
  m.castShadow = true
  m.receiveShadow = true
  return m
}

export function makeFarmer({ shirt = '#d9d4c7', lungi = ['#24476b', '#2f6b4f'], seed = 1, hat = true } = {}) {
  const skinMat = new THREE.MeshStandardMaterial({ color: SKIN, roughness: 0.68 })
  const shirtTex = pixelTex(128, 128, (x, y) => {
    const n = fbm(x / 9 + seed, y / 9, 3) * 30
    const c = new THREE.Color(shirt)
    return [c.r * 255 - n + 10, c.g * 255 - n + 10, c.b * 255 - n + 10]
  }, { repeat: [3, 3] })
  const shirtMat = new THREE.MeshStandardMaterial({ map: shirtTex, roughness: 0.92 })
  const lungiMat = new THREE.MeshStandardMaterial({
    map: plaidTex([lungi[0]], [[0.1, 0.08, lungi[1]], [0.45, 0.04, '#e8e2d0'], [0.7, 0.12, lungi[1]], [0.9, 0.03, '#111']], 256, [5, 3]),
    roughness: 0.95,
    side: THREE.DoubleSide,
  })
  const gamchhaMat = new THREE.MeshStandardMaterial({
    map: plaidTex(['#b3261e'], [[0.0, 0.18, '#f1ece0'], [0.5, 0.18, '#f1ece0'], [0.3, 0.03, '#1d3f8f']], 128, [3, 3]),
    roughness: 0.95,
    side: THREE.DoubleSide,
  })
  const hairMat = new THREE.MeshStandardMaterial({ color: '#14100d', roughness: 0.7 })
  const hatTex = canvasTex(256, 256, (g, w, h) => {
    g.fillStyle = '#c9a15f'
    g.fillRect(0, 0, w, h)
    for (let i = 0; i < 80; i++) {
      g.strokeStyle = i % 2 ? 'rgba(90,60,25,0.45)' : 'rgba(240,215,160,0.35)'
      g.lineWidth = 2
      g.beginPath()
      g.moveTo(w / 2, h / 2)
      const a = (i / 80) * Math.PI * 2
      g.lineTo(w / 2 + Math.cos(a) * w, h / 2 + Math.sin(a) * h)
      g.stroke()
    }
    for (let r = 8; r < w / 2; r += 9) {
      g.strokeStyle = 'rgba(80,50,20,0.35)'
      g.beginPath()
      g.arc(w / 2, h / 2, r, 0, Math.PI * 2)
      g.stroke()
    }
  })
  const hatMat = new THREE.MeshStandardMaterial({ map: hatTex, color: '#b8a080', roughness: 0.9, side: THREE.DoubleSide })

  const J = {} // joints
  const root = new THREE.Group()
  const pelvis = (J.pelvis = new THREE.Group())
  pelvis.position.y = 0.92
  root.add(pelvis)

  // lungi: a tube from the waist to just above the knee, slightly flared, tucked up
  const lungiGeo = new THREE.LatheGeometry(
    [[0.155, 0.08], [0.172, 0.0], [0.19, -0.12], [0.205, -0.26], [0.212, -0.36], [0.2, -0.4]].map(([r, y]) => new THREE.Vector2(r, y)),
    28,
  )
  const lungiMesh = new THREE.Mesh(lungiGeo, lungiMat)
  lungiMesh.scale.set(1, 1, 0.78)
  lungiMesh.castShadow = true
  pelvis.add(lungiMesh)
  J.lungi = lungiMesh
  // knot at the waist
  const knot = new THREE.Mesh(new THREE.SphereGeometry(0.035, 10, 8), lungiMat)
  knot.position.set(0, 0.06, 0.125)
  pelvis.add(knot)

  // spine / chest
  const spine = (J.spine = new THREE.Group())
  spine.position.y = 0.06
  pelvis.add(spine)
  const torsoGeo = new THREE.LatheGeometry(
    [[0.0, 0], [0.155, 0.0], [0.165, 0.12], [0.18, 0.26], [0.19, 0.36], [0.17, 0.44], [0.1, 0.5], [0.06, 0.52]].map(([r, y]) => new THREE.Vector2(r, y)),
    28,
  )
  const torso = new THREE.Mesh(new THREE.CapsuleGeometry(0.165, 0.26, 10, 24), shirtMat)
  torso.position.y = 0.26
  torso.scale.set(1.08, 1, 0.66)
  const chest = new THREE.Mesh(new THREE.SphereGeometry(0.17, 24, 16), shirtMat)
  chest.position.y = 0.36
  chest.scale.set(1.25, 0.75, 0.72)
  spine.add(chest)
  torso.castShadow = true
  spine.add(torso)
  // buttons placket
  const placket = new THREE.Mesh(new THREE.BoxGeometry(0.02, 0.4, 0.01), new THREE.MeshStandardMaterial({ color: '#bdb6a6', roughness: 0.9 }))
  placket.position.set(0, 0.25, 0.118)
  spine.add(placket)

  // gamchha over the left shoulder, hanging front and back
  const gNeck = new THREE.Mesh(new THREE.TorusGeometry(0.11, 0.026, 8, 24, Math.PI * 1.4), gamchhaMat)
  gNeck.rotation.set(Math.PI / 2, 0, -0.3)
  gNeck.position.set(0, 0.5, 0)
  gNeck.scale.set(1, 0.85, 1)
  spine.add(gNeck)
  const gHang = new THREE.Mesh(new THREE.PlaneGeometry(0.11, 0.42, 1, 6), gamchhaMat)
  gHang.position.set(0.07, 0.3, 0.125)
  gHang.rotation.set(-0.08, 0, 0.05)
  spine.add(gHang)
  const gHang2 = gHang.clone()
  gHang2.position.set(0.08, 0.3, -0.12)
  spine.add(gHang2)
  J.gamchha = gHang

  // neck + head
  const neck = (J.neck = new THREE.Group())
  neck.position.y = 0.5
  spine.add(neck)
  const neckMesh = cap(0.045, 0.06, skinMat)
  neckMesh.position.y = 0.05
  neck.add(neckMesh)
  const head = (J.head = new THREE.Group())
  head.position.y = 0.12
  neck.add(head)
  const skull = new THREE.Mesh(new THREE.SphereGeometry(0.1, 28, 22), skinMat)
  skull.scale.set(0.92, 1.12, 1.0)
  skull.position.y = 0.09
  skull.castShadow = true
  head.add(skull)
  const jaw = new THREE.Mesh(new THREE.SphereGeometry(0.075, 20, 14), skinMat)
  jaw.scale.set(1, 0.8, 1)
  jaw.position.set(0, 0.025, 0.02)
  head.add(jaw)
  const nose = new THREE.Mesh(new THREE.ConeGeometry(0.018, 0.045, 10), skinMat)
  nose.rotation.x = Math.PI / 2.4
  nose.position.set(0, 0.085, 0.1)
  head.add(nose)
  for (const s of [-1, 1]) {
    const ear = new THREE.Mesh(new THREE.SphereGeometry(0.022, 10, 8), skinMat)
    ear.scale.set(0.5, 1, 0.8)
    ear.position.set(s * 0.093, 0.09, 0)
    head.add(ear)
    const eye = new THREE.Mesh(new THREE.SphereGeometry(0.011, 10, 8), new THREE.MeshStandardMaterial({ color: '#120c08', roughness: 0.2 }))
    eye.position.set(s * 0.035, 0.11, 0.087)
    head.add(eye)
    const brow = new THREE.Mesh(new THREE.BoxGeometry(0.035, 0.008, 0.01), hairMat)
    brow.position.set(s * 0.035, 0.128, 0.09)
    brow.rotation.z = -s * 0.12
    head.add(brow)
    J['brow' + (s > 0 ? 'R' : 'L')] = brow
  }
  const moustache = new THREE.Mesh(new THREE.CapsuleGeometry(0.009, 0.05, 4, 8), hairMat)
  moustache.rotation.z = Math.PI / 2
  moustache.position.set(0, 0.052, 0.095)
  head.add(moustache)
  // short beard stubble shell
  const stubble = new THREE.Mesh(new THREE.SphereGeometry(0.078, 20, 14, 0, Math.PI * 2, Math.PI * 0.45, Math.PI * 0.5), new THREE.MeshStandardMaterial({ color: '#2a1d14', roughness: 0.9, transparent: true, opacity: 0.55 }))
  stubble.position.set(0, 0.03, 0.022)
  head.add(stubble)
  const hair = new THREE.Mesh(new THREE.SphereGeometry(0.103, 24, 16, 0, Math.PI * 2, 0, Math.PI * 0.42), hairMat)
  hair.scale.set(0.93, 1.12, 1.02)
  hair.position.y = 0.1
  head.add(hair)
  if (hat) {
    // mathal: wide shallow cone of woven palm leaf
    const hatMesh = new THREE.Mesh(new THREE.ConeGeometry(0.33, 0.17, 40, 1, true), hatMat)
    hatMesh.position.y = 0.245
    hatMesh.castShadow = true
    head.add(hatMesh)
    const rim = new THREE.Mesh(new THREE.TorusGeometry(0.33, 0.008, 6, 48), hatMat)
    rim.rotation.x = Math.PI / 2
    rim.position.y = 0.16
    head.add(rim)
    J.hat = hatMesh
  }

  // arms
  for (const side of ['L', 'R']) {
    const s = side === 'L' ? -1 : 1
    const sh = (J['shoulder' + side] = new THREE.Group())
    sh.position.set(s * 0.19, 0.43, 0)
    spine.add(sh)
    const sleeve = cap(0.058, 0.13, shirtMat)
    sleeve.position.y = -0.08
    sh.add(sleeve)
    const shBall = new THREE.Mesh(new THREE.SphereGeometry(0.066, 16, 12), shirtMat)
    sh.add(shBall)
    const upper = cap(0.05, 0.17, skinMat)
    upper.position.y = -0.14
    sh.add(upper)
    const el = (J['elbow' + side] = new THREE.Group())
    el.position.y = -0.27
    sh.add(el)
    const fore = cap(0.043, 0.18, skinMat)
    fore.position.y = -0.12
    el.add(fore)
    el.add(new THREE.Mesh(new THREE.SphereGeometry(0.047, 12, 10), skinMat))
    const wr = (J['wrist' + side] = new THREE.Group())
    wr.position.y = -0.25
    el.add(wr)
    const palm = new THREE.Mesh(new THREE.BoxGeometry(0.07, 0.085, 0.03), skinMat)
    palm.geometry.translate(0, -0.045, 0)
    palm.castShadow = true
    wr.add(palm)
    const fingers = new THREE.Mesh(new THREE.BoxGeometry(0.068, 0.06, 0.026), skinMat)
    fingers.position.y = -0.11
    fingers.rotation.x = 0.35
    wr.add(fingers)
    const thumb = cap(0.012, 0.035, skinMat, 6)
    thumb.position.set(-s * 0.038, -0.05, 0.015)
    thumb.rotation.z = s * 0.6
    wr.add(thumb)
    J['hand' + side] = wr
  }

  // legs: thighs mostly inside the lungi, shins and feet bare
  for (const side of ['L', 'R']) {
    const s = side === 'L' ? -1 : 1
    const hip = (J['hip' + side] = new THREE.Group())
    hip.position.set(s * 0.09, -0.02, 0)
    pelvis.add(hip)
    const thigh = cap(0.068, 0.3, skinMat)
    thigh.position.y = -0.2
    hip.add(thigh)
    const knee = (J['knee' + side] = new THREE.Group())
    knee.position.y = -0.43
    hip.add(knee)
    const shin = cap(0.055, 0.33, skinMat)
    shin.position.y = -0.2
    knee.add(shin)
    knee.add(new THREE.Mesh(new THREE.SphereGeometry(0.056, 12, 10), skinMat))
    const ankle = (J['ankle' + side] = new THREE.Group())
    ankle.position.y = -0.42
    knee.add(ankle)
    const foot = new THREE.Mesh(new THREE.CapsuleGeometry(0.038, 0.13, 4, 8), skinMat)
    foot.rotation.x = Math.PI / 2
    foot.position.set(0, -0.035, 0.06)
    foot.scale.set(1.15, 1, 0.6)
    foot.castShadow = true
    ankle.add(foot)
  }

  // phone (hidden until needed), held in the right hand
  const phone = new THREE.Group()
  const body = new THREE.Mesh(new THREE.BoxGeometry(0.075, 0.155, 0.009), new THREE.MeshStandardMaterial({ color: '#16181c', roughness: 0.35, metalness: 0.6 }))
  phone.add(body)
  const screen = new THREE.Mesh(new THREE.PlaneGeometry(0.069, 0.149), new THREE.MeshBasicMaterial({ color: '#000', toneMapped: false }))
  screen.position.z = 0.0048
  phone.add(screen)
  phone.position.set(0, -0.11, 0.03)
  phone.rotation.set(0, Math.PI, 0)
  phone.visible = false
  J.wristR.add(phone)
  J.phone = phone
  J.screen = screen

  root.userData.J = J
  root.traverse((o) => {
    if (o.isMesh) {
      o.castShadow = true
      o.receiveShadow = true
    }
  })
  return root
}

// ---- poses: joint -> [x, y, z] Euler (radians); pelvis also has 'y' height offset
const P = {
  stand: { hipL: [0, 0, 0.03], hipR: [0, 0, -0.03], kneeL: [0.05, 0, 0], kneeR: [0.05, 0, 0], ankleL: [-0.05, 0, 0], ankleR: [-0.05, 0, 0], shoulderL: [0.05, 0, -0.12], shoulderR: [0.05, 0, 0.12], elbowL: [-0.2, 0, 0], elbowR: [-0.2, 0, 0], spine: [0.02, 0, 0], neck: [0, 0, 0], head: [0.05, 0, 0], wristL: [0, 0, 0], wristR: [0, 0, 0], drop: 0 },
  // squat beside the plants, right hand reaching to a leaf
  squat: { hipL: [-1.85, 0, 0.35], hipR: [-1.6, 0, -0.3], kneeL: [2.35, 0, 0], kneeR: [2.25, 0, 0], ankleL: [-0.5, 0, 0], ankleR: [-0.6, 0, 0], spine: [0.42, 0, 0], neck: [0.15, 0, 0], head: [0.35, 0, 0], shoulderL: [-0.4, 0, -0.25], elbowL: [-1.2, 0, 0], shoulderR: [-1.1, 0, 0.15], elbowR: [-0.5, 0, 0], wristR: [0.2, 0, 0], wristL: [0, 0, 0], drop: 0.47 },
  // worried: right hand on the forehead, left hand on the hip, head down
  worry: { hipL: [0, 0, 0.05], hipR: [0, 0, -0.05], kneeL: [0.05, 0, 0], kneeR: [0.08, 0, 0], ankleL: [-0.05, 0, 0], ankleR: [-0.08, 0, 0], spine: [0.12, 0, 0], neck: [0.15, 0, 0], head: [0.35, 0.15, 0], shoulderR: [-2.4, 0.2, 0.45], elbowR: [-2.0, 0, 0], wristR: [0.3, 0, 0], shoulderL: [0.2, 0, -0.55], elbowL: [-1.6, 0, 0], wristL: [0, 0, 0], drop: 0 },
  // looking at the phone held at chest height
  phone: { hipL: [0, 0, 0.04], hipR: [0, 0, -0.04], kneeL: [0.05, 0, 0], kneeR: [0.05, 0, 0], ankleL: [-0.05, 0, 0], ankleR: [-0.05, 0, 0], spine: [0.06, 0, 0], neck: [0.25, 0, 0], head: [0.35, 0, 0], shoulderR: [-0.75, 0.25, 0.1], elbowR: [-1.55, 0, 0], wristR: [-0.2, 0, 0], shoulderL: [-0.6, -0.25, -0.1], elbowL: [-1.35, 0, 0], wristL: [0.1, 0, 0], drop: 0 },
  // photographing a leaf: crouched slightly, phone held out
  photo: { hipL: [-0.9, 0, 0.25], hipR: [-0.7, 0, -0.2], kneeL: [1.3, 0, 0], kneeR: [1.2, 0, 0], ankleL: [-0.4, 0, 0], ankleR: [-0.45, 0, 0], spine: [0.38, 0, 0], neck: [0.1, 0, 0], head: [0.25, 0, 0], shoulderR: [-1.25, 0.15, 0.1], elbowR: [-0.55, 0, 0], wristR: [-0.5, 0, 0], shoulderL: [-0.5, 0, -0.3], elbowL: [-1.1, 0, 0], wristL: [0, 0, 0], drop: 0.2 },
  // relieved and happy: chest open, phone raised a little, head up
  happy: { hipL: [0, 0, 0.06], hipR: [0, 0, -0.06], kneeL: [0.03, 0, 0], kneeR: [0.03, 0, 0], ankleL: [-0.03, 0, 0], ankleR: [-0.03, 0, 0], spine: [-0.06, 0, 0], neck: [-0.1, 0, 0], head: [-0.12, 0, 0], shoulderR: [-1.0, 0.2, 0.25], elbowR: [-1.2, 0, 0], wristR: [-0.2, 0, 0], shoulderL: [-0.2, 0, -0.9], elbowL: [-0.6, 0, 0], wristL: [0, 0, 0], drop: 0 },
}

function walkPose(phase) {
  const s = Math.sin(phase), c = Math.cos(phase)
  const lift = (x) => Math.max(0, x)
  return {
    hipL: [-0.42 * s, 0, 0.03], hipR: [0.42 * s, 0, -0.03],
    kneeL: [0.15 + 0.75 * lift(c), 0, 0], kneeR: [0.15 + 0.75 * lift(-c), 0, 0],
    ankleL: [-0.15 + 0.2 * s, 0, 0], ankleR: [-0.15 - 0.2 * s, 0, 0],
    shoulderL: [0.35 * s, 0, -0.12], shoulderR: [-0.35 * s, 0, 0.12],
    elbowL: [-0.35 - 0.15 * lift(-s), 0, 0], elbowR: [-0.35 - 0.15 * lift(s), 0, 0],
    spine: [0.06, 0.06 * s, 0], neck: [0, -0.04 * s, 0], head: [0.06, 0, 0], wristL: [0, 0, 0], wristR: [0, 0, 0],
    drop: -0.025 * Math.abs(Math.cos(phase)) + 0.02,
  }
}

function mix(a, b, k) {
  const out = {}
  for (const key of new Set([...Object.keys(a), ...Object.keys(b)])) {
    const x = a[key] ?? b[key], y = b[key] ?? a[key]
    out[key] = Array.isArray(x) ? x.map((v, i) => lerp(v, y[i], k)) : lerp(x, y, k)
  }
  return out
}

/** Apply a blend of poses. spec: { a: 'walk'|'stand'|..., b?, k?, phase?, breathe? } */
export function pose(farmer, spec, t = 0) {
  const J = farmer.userData.J
  const get = (name) => (name === 'walk' ? walkPose(spec.phase ?? 0) : P[name])
  let p = get(spec.a)
  if (spec.b) p = mix(p, get(spec.b), clamp(spec.k ?? 0))
  const breathe = Math.sin(t * 1.6) * 0.015
  for (const [k, v] of Object.entries(p)) {
    if (k === 'drop' || !J[k]) continue
    J[k].rotation.set(v[0] + (k === 'spine' ? breathe : 0), v[1], v[2])
  }
  J.pelvis.position.y = 0.92 - (p.drop ?? 0)
  // lungi sways with the gait
  J.lungi.rotation.x = (spec.a === 'walk' ? Math.sin((spec.phase ?? 0) * 2) * 0.04 : 0) + (p.hipL?.[0] ?? 0) * 0.12
  J.gamchha.rotation.x = -0.08 + Math.sin(t * 1.3) * 0.04
}
