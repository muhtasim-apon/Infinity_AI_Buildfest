// Director for the v2 film. window.__frame(t) renders the exact frame for time t (deterministic),
// so the renderer can step frame by frame at full quality regardless of GPU speed.
import * as THREE from 'three'
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js'
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js'
import { BokehPass } from 'three/addons/postprocessing/BokehPass.js'
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js'
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js'
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js'
import { CSS3DRenderer } from 'three/addons/renderers/CSS3DRenderer.js'
import { createField, PATCH, SUN_DIR } from './field.js'
import { pose } from './farmer.js'
import { createSciFi } from './scifi.js'
import { createMap } from './map.js'
import { clamp, lerp, seg, smooth, v3, loadImage } from './lib.js'

const W = 1920, H = 1080
const TL = window.__TIMELINE
const sc = Object.fromEntries(TL.scenes.map((s) => [s.id, s]))
const L = (id, i) => sc[id].lines[i].start
const END = 180

// ---------------------------------------------------------------- renderer + post
const canvas = document.getElementById('gl')
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true, powerPreference: 'high-performance' })
renderer.setPixelRatio(1)
renderer.setSize(W, H, false)
renderer.outputColorSpace = THREE.SRGBColorSpace
renderer.toneMapping = THREE.ACESFilmicToneMapping
renderer.toneMappingExposure = 0.5
renderer.shadowMap.enabled = true
renderer.shadowMap.type = THREE.PCFSoftShadowMap

const css = new CSS3DRenderer({ element: document.getElementById('css3d') })
css.setSize(W, H)

const composer = new EffectComposer(renderer)
const renderPass = new RenderPass(new THREE.Scene(), new THREE.PerspectiveCamera())
composer.addPass(renderPass)
const bokeh = new BokehPass(new THREE.Scene(), new THREE.PerspectiveCamera(), { focus: 5, aperture: 0.0012, maxblur: 0.008 })
composer.addPass(bokeh)
const bloom = new UnrealBloomPass(new THREE.Vector2(W, H), 0.25, 0.6, 0.86)
composer.addPass(bloom)
const grade = new ShaderPass({
  uniforms: { tDiffuse: { value: null }, uTime: { value: 0 }, uWarm: { value: 1 }, uVig: { value: 0.32 }, uGrain: { value: 0.035 }, uCA: { value: 0.0012 } },
  vertexShader: 'varying vec2 vUv; void main(){ vUv=uv; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0); }',
  fragmentShader: `
    uniform sampler2D tDiffuse; uniform float uTime, uWarm, uVig, uGrain, uCA; varying vec2 vUv;
    float h(vec2 p){ return fract(sin(dot(p, vec2(12.9898,78.233)) + uTime*7.13) * 43758.5453); }
    void main(){
      vec2 d = vUv - 0.5;
      vec3 c;
      c.r = texture2D(tDiffuse, vUv + d * uCA).r;
      c.g = texture2D(tDiffuse, vUv).g;
      c.b = texture2D(tDiffuse, vUv - d * uCA).b;
      // gentle film grade: warm highlights, teal-ish shadows (only in the field)
      float l = dot(c, vec3(0.299,0.587,0.114));
      vec3 warm = c * vec3(1.06, 1.0, 0.9) + vec3(0.012, 0.004, -0.01);
      vec3 cool = c * vec3(0.94, 1.0, 1.04);
      c = mix(c, mix(cool, warm, smoothstep(0.15, 0.7, l)), uWarm);
      c = mix(vec3(l), c, 1.0 + 0.08 * uWarm); // saturation
      c *= 1.0 - uVig * dot(d, d) * 2.2;
      c += (h(vUv * vec2(1920.0,1080.0)) - 0.5) * uGrain;
      gl_FragColor = vec4(c, 1.0);
    }`,
})
composer.addPass(grade)
composer.addPass(new OutputPass())

// ---------------------------------------------------------------- assets: real app captures
const UI = '/ui/'
const full = await (await fetch(UI + 'full.json')).json()
const img = {}
for (const n of ['home', 'diag', 'unsure']) {
  img[n + '_full'] = await loadImage(UI + n + '_full.png')
  img[n + '_header'] = await loadImage(UI + n + '_header.png')
  img[n + '_nav'] = await loadImage(UI + n + '_nav.png')
}
for (const n of ['diag_1_capture', 'diag_2_selected', 'diag_3_analyzing', 'unsure_4_result']) img[n] = await loadImage(UI + n + '.png')
const leafPhoto = await loadImage(UI + 'leaf.jpg')

// phone screen = header + scrolling content + bottom bar, exactly like the live app
const screenCanvas = document.createElement('canvas')
screenCanvas.width = 780
screenCanvas.height = 1688
const sg = screenCanvas.getContext('2d')
const screenTex = new THREE.CanvasTexture(screenCanvas)
screenTex.colorSpace = THREE.SRGBColorSpace
screenTex.anisotropy = 16
let lastScreen = ''
function drawScreen(page, scroll = 0, flash = 0) {
  const key = page + ':' + Math.round(scroll) + ':' + flash.toFixed(2)
  if (key === lastScreen) return
  lastScreen = key
  const k = 2 / 3 // captures are 3x, the screen canvas is 2x
  sg.fillStyle = '#f6f8f3'
  sg.fillRect(0, 0, 780, 1688)
  if (['home', 'diag', 'unsure'].includes(page)) {
    const f = img[page + '_full']
    const maxScroll = Math.max(0, full[page].height - 844)
    const s = clamp(scroll, 0, maxScroll) * 3
    sg.drawImage(f, 0, s, 1170, 2532, 0, 0, 780, 1688)
    const hd = img[page + '_header']
    sg.drawImage(hd, 0, 0, hd.width * k, hd.height * k)
    const nv = img[page + '_nav']
    sg.drawImage(nv, 0, 1688 - nv.height * k, nv.width * k, nv.height * k)
  } else {
    sg.drawImage(img[page], 0, 0, 780, 1688)
  }
  if (flash > 0) {
    sg.fillStyle = `rgba(255,255,255,${flash})`
    sg.fillRect(0, 0, 780, 1688)
  }
  screenTex.needsUpdate = true
}

// ---------------------------------------------------------------- worlds
const field = createField(renderer)
window.__field = field
window.__cams = () => fieldCam
const fieldCam = new THREE.PerspectiveCamera(42, W / H, 0.03, 3000)
field.rahim.userData.J.screen.material = new THREE.MeshBasicMaterial({ map: screenTex, toneMapped: false })
field.heroPhone.userData.screen.material = new THREE.MeshBasicMaterial({ map: screenTex, toneMapped: false, fog: false })
const otherScreens = field.others.map((f) => {
  f.userData.J.phone.visible = true
  f.userData.J.screen.material = new THREE.MeshBasicMaterial({ color: '#cfe9d6', toneMapped: false })
  return f
})
const scifi = await createSciFi({ renderer, W, H, TL: sc, leafPhoto, uiBase: UI })
const bdmap = createMap({ W, H })

// ---------------------------------------------------------------- HUD
const hud = document.getElementById('hud')
const fade = document.getElementById('fade')
function el(html, cls, style = {}) {
  const d = document.createElement('div')
  d.className = cls
  d.innerHTML = html
  Object.assign(d.style, style)
  hud.appendChild(d)
  return d
}
const H_ = {
  title: el('<h1>কাকতাড়ুয়া</h1><p>Kaktarua · Bangladesh · aman rice season</p>', 'title'),
  chip1: el('<b>01</b><span>The problem</span>', 'chip'),
  chip2: el('<b>02</b><span>The solution · real app screens</span>', 'chip'),
  chip3: el('<b>03</b><span>System flow · how it works</span>', 'chip'),
  chip4: el('<b>04</b><span>AI approach</span>', 'chip'),
  chip5: el('<b>05</b><span>Impact &amp; next step</span>', 'chip'),
  blast: el('<p>Rice blast</p><h3 class="big">up to 80%</h3><p>yield loss</p><small>Source: BRRI factsheet (in our knowledge base)</small>', 'card', { right: '90px', top: '170px', width: '420px' }),
  blb: el('<p>Bacterial leaf blight</p><h3 class="big">~30%</h3><p>yield loss</p><small>Source: BRRI factsheet (in our knowledge base)</small>', 'card', { right: '90px', top: '520px', width: '420px' }),
  expert: el('<h3>No expert nearby</h3><p>Advice is rarely in plain Bangla</p>', 'card', { left: '90px', top: '190px', width: '520px' }),
  wrong: el('<h3>Wrong guess → wrong spray</h3><p>wasted money, harvest still at risk</p>', 'card', { left: '90px', top: '190px', width: '600px' }),
  app: el('<h3 class="bn">কাকতাড়ুয়া</h3><p>Bangla-first web app · any phone · works offline</p>', 'card', { left: '90px', top: '170px', width: '560px' }),
  strip: el('<h3>Before any AI call</h3><p>GPS/EXIF stripped by re-encoding<br/>blurry or dark photos are refused</p>', 'card', { left: '90px', top: '170px', width: '560px' }),
  thr: el('<p>Model confidence</p><h3 class="big">≥ 0.60</h3><p>diagnose · below it: <span class="bn">আমি নিশ্চিত নই</span> (I am not sure)</p>', 'card', { left: '90px', top: '170px', width: '560px' }),
  unsure: el('<img src="/ui/unsure_4_result.png" style="width:300px;border-radius:24px;display:block"/><small>Same app, poor photo: it says “not sure” and gives retake tips</small>', 'card', { right: '90px', top: '120px', width: '300px' }),
  cited: el('<h3>Every step cited</h3><p>BRRI factsheet + page, plain Bangla<br/>“ask the agriculture office before any chemical”</p>', 'card', { left: '90px', top: '170px', width: '600px' }),
  office: el('<h3>Knows what to do</h3><p>and calls the Upazila agriculture office before any chemical</p>', 'card', { left: '90px', top: '170px', width: '600px' }),
  vision: el('<h3>Every rice farmer, all 8 divisions</h3><p>an honest second opinion in their pocket</p><span class="tag vision">VISION · not yet real</span>', 'card', { left: '90px', top: '170px', width: '640px' }),
  end: el('<h1>কাকতাড়ুয়া</h1><p>Kaktarua · Honest help for every rice field</p><p style="font-size:24px;opacity:.8;margin-top:22px">infinityaibuildfest-prototype-five.vercel.app</p>', 'title', { top: '300px' }),
  flash: el('', 'flash'),
}
function show(e, t, a, b, fi = 0.5, fo = 0.5) {
  const o = t < a || t > b ? 0 : Math.min(1, (t - a) / fi, (b - t) / fo)
  e.style.opacity = o.toFixed(3)
  e.style.transform = `translateY(${((1 - o) * 14).toFixed(1)}px)`
}

// ---------------------------------------------------------------- shots
function look(cam, pos, target, fov = 42) {
  cam.position.copy(pos)
  cam.fov = fov
  cam.updateProjectionMatrix()
  cam.lookAt(target)
}
const farmerHead = () => field.rahim.userData.J.head.getWorldPosition(new THREE.Vector3())
const phoneWorld = () => field.rahim.userData.J.phone.getWorldPosition(new THREE.Vector3())
const phoneQuat = () => field.rahim.userData.J.phone.getWorldQuaternion(new THREE.Quaternion())

function fieldFrame(t) {
  const R = field.rahim
  const J = R.userData.J
  let focus = 6
  J.phone.visible = false
  field.heroPhone.visible = false
  field.others.forEach((f) => (f.visible = false))
  R.visible = true
  field.heroLeaf.visible = true

  const P1 = L('problem', 1), P2 = L('problem', 2), P3 = L('problem', 3)
  const S0 = sc.solution.start, S1 = L('solution', 1), S2 = L('solution', 2), S3 = L('solution', 3)
  const I0 = sc.impact.start, I1 = L('impact', 1), I2 = L('impact', 2)

  if (t < P2) {
    // walking along the bund towards the sick patch
    const zStart = -6, zStop = PATCH.z + 0.6
    const k = clamp((t - 0) / (P2 + 0.8))
    const z = lerp(zStart, zStop, smooth(k))
    R.position.set(0, 0.22, z)
    R.rotation.y = Math.PI // facing -z
    const walking = t < P2 + 0.6
    pose(R, walking ? { a: 'walk', phase: (z - zStart) * -2.6 } : { a: 'stand' }, t)
    if (t < P1) {
      // establishing crane: high, behind, the sun ahead
      const k2 = seg(t, 0, P1)
      look(fieldCam, v3(lerp(-4.5, -2.5, k2), lerp(7.5, 3.2, k2), lerp(9, 4, k2)), v3(0, 1.0, z - 6), 44)
      focus = fieldCam.position.distanceTo(R.position)
    } else {
      // tracking shot from behind-right
      const k2 = seg(t, P1, P2)
      const p = R.position.clone().add(v3(lerp(1.9, 1.3, k2), 1.55, lerp(3.4, 2.4, k2)))
      look(fieldCam, p, R.position.clone().add(v3(0, 1.25, -1.5)), 38)
      focus = p.distanceTo(R.position.clone().add(v3(0, 1.2, 0)))
    }
  } else if (t < P3) {
    // squat at the sick plants: macro on the lesions
    R.position.set(0.05, 0.22, PATCH.z + 0.6)
    R.rotation.y = Math.PI - 0.5
    pose(R, { a: 'stand', b: 'squat', k: seg(t, P2, P2 + 1.4) }, t)
    const k = seg(t, P2, P3)
    const leafMid = field.heroLeaf.position.clone().add(v3(0, 0.42, 0))
    R.visible = false
    const p = v3(lerp(0.3, 0.5, k), lerp(0.6, 0.53, k), PATCH.z + lerp(-0.18, -0.06, k))
    look(fieldCam, p, leafMid.clone().add(v3(0.05, 0.0, 0)), 36)
    focus = p.distanceTo(leafMid)
  } else if (t < S0 + 0.2) {
    // stands up, worried; low orbit against the sun
    R.position.set(0.05, 0.22, PATCH.z + 0.6)
    R.rotation.y = Math.PI - 0.5
    pose(R, { a: 'squat', b: 'worry', k: seg(t, P3, P3 + 1.6) }, t)
    const k = seg(t, P3, S0 + 0.2, (x) => x)
    // from behind-left, against the low sun: the posture tells the worry
    const a = lerp(2.35, 2.75, k)
    const head = farmerHead()
    const p = R.position.clone().add(v3(Math.sin(a) * 3.0, 1.05, -Math.cos(a) * 3.0))
    look(fieldCam, p, head.clone().add(v3(0, -0.25, 0)), 38)
    focus = p.distanceTo(head)
  } else if (t < I0) {
    // ---- solution: point of view, the REAL app screens on the phone in his hand
    R.position.set(0.05, 0.22, PATCH.z + 0.6)
    R.rotation.y = Math.PI - 0.5
    R.visible = false
    const eye = v3(0.12, 1.42, PATCH.z + 0.75)
    const leafMid = field.heroLeaf.position.clone().add(v3(0, 0.45, 0))
    const gaze = leafMid.clone().add(v3(Math.sin(t * 0.4) * 0.05, 0.15 + seg(t, S0, S1) * 0.1, 0))
    fieldCam.position.copy(eye)
    fieldCam.fov = 40
    fieldCam.updateProjectionMatrix()
    fieldCam.lookAt(gaze)
    let off = v3(0.04, -0.03, -0.29), rot = new THREE.Euler(0.08, -0.12, 0.04)
    const rise = seg(t, S0, S0 + 1.3)
    off.y -= (1 - rise) * 0.28
    let page = 'home', scroll = 0, flash = 0
    if (t < S1) {
      scroll = seg(t, S0 + 1.8, S1 + 0.3) * 160
    } else if (t < S2) {
      // aim at the leaf: the phone moves aside so the leaf shows, the screen stays readable
      const k = seg(t, S1, S1 + 1.2)
      off = off.lerp(v3(0.085, -0.05, -0.31), k)
      rot = new THREE.Euler(lerp(0.08, -0.1, k), lerp(-0.12, -0.3, k), 0.04)
      const shutter = S1 + 3.2
      page = t < S1 + 1.8 ? 'diag_1_capture' : 'diag_2_selected'
      flash = t > shutter && t < shutter + 0.35 ? 1 - (t - shutter) / 0.35 : 0
      H_.flash.style.opacity = t > shutter && t < shutter + 0.22 ? (0.55 * (1 - (t - shutter) / 0.22)).toFixed(2) : 0
    } else {
      // bring it close to read the result
      const k = seg(t, S2, S2 + 1.2)
      off = v3(0.085, -0.05, -0.31).lerp(v3(0.0, -0.002, -0.235), k)
      rot = new THREE.Euler(lerp(-0.1, 0.02, k), lerp(-0.3, 0, k), lerp(0.04, 0, k))
      page = t < S2 + 1.6 ? 'diag_3_analyzing' : 'diag'
      scroll = t < S3 ? 0 : seg(t, S3 + 0.6, sc.solution.end + 2.5) * 1350
      const dive = seg(t, sc.solution.end + 1.5, 60)
      off.z = lerp(off.z, -0.03, dive)
      fade.style.background = '#e9fbff'
      fade.style.opacity = seg(t, 59.1, 60, (x) => x).toFixed(3)
    }
    drawScreen(page, scroll, flash)
    const hp = field.heroPhone
    hp.visible = true
    hp.position.copy(fieldCam.localToWorld(off.clone()))
    hp.quaternion.copy(fieldCam.quaternion).multiply(new THREE.Quaternion().setFromEuler(rot))
    focus = Math.abs(off.z)
  } else {
    // ---- impact: back in the field, relief; neighbours with phones
    R.position.set(0.05, 0.22, PATCH.z + 0.6)
    R.rotation.y = Math.PI - 0.2
    J.phone.visible = true
    drawScreen('diag', 260)
    pose(R, { a: 'phone', b: 'happy', k: seg(t, I0, I0 + 2.2) }, t)
    const others = [
      [-6.5, -26, 0.4], [7.5, -30, -0.6], [-9, -41, 0.9], [11, -45, -1.1],
    ]
    field.others.forEach((f, i) => {
      f.visible = t > I1 - 1.5
      const [x, z, ry] = others[i]
      f.position.set(x, 0, z)
      f.rotation.y = ry
      pose(f, { a: 'phone' }, t + i)
      f.userData.J.screen.material.color.set(i % 2 ? '#d9f2df' : '#e6efe0')
    })
    if (t < I1) {
      const k = seg(t, I0, I1)
      const head = farmerHead()
      const a = lerp(2.0, 2.5, k)
      const p = R.position.clone().add(v3(Math.sin(a) * 2.8, 1.25, -Math.cos(a) * 2.8))
      look(fieldCam, p, head.clone().add(v3(0, -0.2, 0)), 40)
      focus = p.distanceTo(head)
    } else {
      // crane up and back: many farmers, many fields
      const k = seg(t, I1, I2 + 0.6)
      const p = v3(lerp(-2, -10, k), lerp(1.8, 22, k), lerp(-17, 6, k))
      look(fieldCam, p, v3(0, 0, lerp(-21, -34, k)), 46)
      focus = 30
    }
    fade.style.background = '#fff'
    fade.style.opacity = (1 - seg(t, I0, I0 + 0.9, (x) => x)).toFixed(3)
  }
  field.update(t)
  return focus
}

// ---------------------------------------------------------------- frame
const F = sc.flow.start, A = sc.ai.start, I = sc.impact.start
const MAP0 = L('impact', 2) - 0.6, END0 = L('impact', 3) - 0.4

window.__frame = (t) => {
  grade.uniforms.uTime.value = t
  fade.style.opacity = 0
  H_.flash.style.opacity = 0
  const inSciFi = t >= F && t < I
  const inMap = t >= MAP0
  document.getElementById('css3d').style.display = inSciFi ? 'block' : 'none'

  if (inMap) {
    const cam = bdmap.update(t, MAP0, END0)
    renderPass.scene = bdmap.scene
    renderPass.camera = cam
    bokeh.enabled = false
    bloom.strength = 0.9
    grade.uniforms.uWarm.value = 0.25
    grade.uniforms.uVig.value = 0.45
    renderer.toneMappingExposure = 1.0
    fade.style.background = '#000'
    fade.style.opacity = (1 - seg(t, MAP0, MAP0 + 0.8, (x) => x)).toFixed(3)
  } else if (inSciFi) {
    const cam = scifi.update(t)
    renderPass.scene = scifi.scene
    renderPass.camera = cam
    bokeh.enabled = false
    bloom.strength = 0.8
    bloom.threshold = 0.5
    grade.uniforms.uWarm.value = 0
    grade.uniforms.uVig.value = 0.5
    renderer.toneMappingExposure = 1.0
    css.render(scifi.cssScene, cam)
    fade.style.background = '#e9fbff'
    fade.style.opacity = Math.max(1 - seg(t, F, F + 0.8, (x) => x), seg(t, I - 0.6, I, (x) => x)).toFixed(3)
    if (t > I - 0.6) fade.style.background = '#fff'
  } else {
    const focus = fieldFrame(t)
    renderPass.scene = field.scene
    renderPass.camera = fieldCam
    bokeh.enabled = true
    bokeh.scene = field.scene
    bokeh.camera = fieldCam
    bokeh.uniforms.focus.value = focus
    bokeh.uniforms.aperture.value = focus < 0.6 ? 0.012 : focus < 1.2 ? 0.004 : 0.0011
    bloom.strength = 0.14
    bloom.threshold = 0.93
    grade.uniforms.uWarm.value = 1
    grade.uniforms.uVig.value = 0.32
    renderer.toneMappingExposure = 0.5
  }

  // HUD timing
  show(H_.title, t, 0.6, L('problem', 1) - 0.4, 0.9, 0.8)
  show(H_.chip1, t, L('problem', 1), sc.problem.end + 3)
  show(H_.chip2, t, sc.solution.start + 0.5, sc.solution.end + 3)
  show(H_.chip3, t, F + 1, A - 0.5)
  show(H_.chip4, t, A + 0.5, I - 0.6)
  show(H_.chip5, t, I + 1.2, END0)
  show(H_.expert, t, L('problem', 1) + 0.3, L('problem', 2) - 0.2)
  show(H_.blast, t, L('problem', 2) + 0.5, L('problem', 3) + 0.4)
  show(H_.blb, t, L('problem', 2) + 3.6, L('problem', 3) + 0.4)
  show(H_.wrong, t, L('problem', 3), sc.problem.end + 3.5)
  show(H_.app, t, sc.solution.start + 0.8, L('solution', 1) - 0.2)
  show(H_.strip, t, L('solution', 1) + 0.4, L('solution', 2) - 0.2)
  show(H_.thr, t, L('solution', 2) + 1.8, L('solution', 3) - 0.2)
  show(H_.unsure, t, L('solution', 2) + 4.0, L('solution', 3) - 0.2)
  show(H_.cited, t, L('solution', 3) + 0.3, sc.solution.end + 2.2)
  show(H_.office, t, I + 1.0, L('impact', 1) - 0.2)
  show(H_.vision, t, L('impact', 1) + 0.2, MAP0 + 0.2)
  show(H_.end, t, END0 + 0.4, END + 1, 1.0, 0.1)
  if (t >= END0) {
    // end card over a darkened map
    fade.style.background = '#000'
    fade.style.opacity = (0.78 * seg(t, END0, END0 + 1.2, (x) => x)).toFixed(3)
  }
  bdmap.hud(t, MAP0, END0)
  composer.render()
  return true
}

// wait for fonts + first compile
await document.fonts.ready
window.__frame(0.5)
window.__ready = true
