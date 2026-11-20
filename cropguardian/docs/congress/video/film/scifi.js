// Sci-fi system world (1:00-2:30): the REAL Kaktarua pipeline as a glowing node graph with a data
// packet travelling through it, then an illustration of how a vision-language transformer reads a
// leaf (patches -> vectors -> attention), then contextual retrieval over the 39 real BRRI chunks.
import * as THREE from 'three'
import { CSS3DObject } from 'three/addons/renderers/CSS3DRenderer.js'
import { clamp, lerp, seg, smooth, v3, rng } from './lib.js'

const PX = 0.016 // css px -> world units

function css3d(html, cls, pos, rotY = 0, scale = PX) {
  const d = document.createElement('div')
  d.className = cls
  d.innerHTML = html
  const o = new CSS3DObject(d)
  o.position.copy(pos)
  o.rotation.y = rotY
  o.scale.setScalar(scale)
  return o
}

export async function createSciFi({ TL, leafPhoto, uiBase }) {
  const scene = new THREE.Scene()
  scene.background = new THREE.Color('#02070d')
  scene.fog = new THREE.FogExp2('#02070d', 0.018)
  const cssScene = new THREE.Scene()
  const cam = new THREE.PerspectiveCamera(50, 1920 / 1080, 0.1, 500)

  // floor grid + dust
  const grid = new THREE.GridHelper(600, 300, '#0e6f8a', '#06303d')
  grid.position.y = -4
  grid.material.transparent = true
  grid.material.opacity = 0.55
  scene.add(grid)
  {
    const n = 4000, r = rng(5), pos = new Float32Array(n * 3)
    for (let i = 0; i < n; i++) {
      pos[i * 3] = (r() - 0.5) * 300
      pos[i * 3 + 1] = -3 + r() * 40
      pos[i * 3 + 2] = (r() - 0.5) * 300
    }
    const g = new THREE.BufferGeometry()
    g.setAttribute('position', new THREE.BufferAttribute(pos, 3))
    scene.add(new THREE.Points(g, new THREE.PointsMaterial({ color: '#4fd8ff', size: 0.08, transparent: true, opacity: 0.6 })))
  }

  // ------------------------------------------------------------ pipeline graph (flow scene)
  const F = TL.flow
  const fl = (i) => F.lines[i].start
  // [id, key, title, body, position, appear time, cls]
  const N = [
    ['phone', 'CLIENT', 'React app · Vercel', 'Bangla-first PWA · photo + division only', v3(0, 0, 0), fl(0)],
    ['api', 'API', 'FastAPI · Render', 'session auth · CSRF · rate limits · RBAC', v3(9, 0, -6), fl(0) + 2.6],
    ['harden', 'STEP 1', 'Upload hardening', 'type + size + magic bytes · decompression-bomb guard · EXIF/GPS stripped by re-encoding · SHA-256', v3(18, 0, -12), fl(1)],
    ['quality', 'STEP 2', 'Local quality gate', 'blurry / dark photo → abstain, no AI call', v3(27, 0, -18), fl(2)],
    ['vision', 'STEP 3', 'Vision LLM · Meta Muse Spark', 'strict JSON · one of 9 rice diseases (or healthy) · confidence 0..1', v3(36, 0, -24), fl(3)],
    ['decide', 'DECISION', 'Threshold 0.60', 'confidence < 0.60 → not sure', v3(45, 0, -30), fl(4)],
    ['retrieve', 'RETRIEVAL', 'BRRI knowledge base', '≤ 8 of 39 passages · disease filter + keyword overlap on contextual chunks', v3(54, 0, -36), fl(4) + 3.6],
    ['advice', 'STEP 4', 'Advice LLM', 'plain-Bangla steps written ONLY from the retrieved passages', v3(63, 0, -42), fl(5)],
    ['validate', 'GUARD', 'Validator V1–V6', 'shape · citations · numbers · no chemicals · Bangla · injection', v3(72, 0, -48), fl(5) + 3.2],
    ['store', 'DATA', 'Postgres · row-level security', 'scan stored without image bytes', v3(81, 0, -54), fl(6)],
    ['outbreak', 'RULE', '3 scans · 1 division · 7 days', '→ draft outbreak alert', v3(90, 0, -60), fl(6) + 2.2],
    ['human', 'HUMAN', 'Reviewer approves (+2FA)', 'only then: “possible outbreak, unverified” reaches farmers', v3(99, 0, -66), fl(6) + 4.2],
  ]
  const side = [
    ['notsure', 'ABSTAIN', 'আমি নিশ্চিত নই · not sure', 'retake tips instead of a guess', v3(36, -7.5, -18), fl(2) + 2, 'warn'],
    ['static', 'FALLBACK', 'Static BRRI card', 'if validation fails twice: text quoted verbatim from the factsheet', v3(72, -7.5, -42), fl(5) + 5, 'warn'],
    ['vector', 'NEXT', 'Vector search (pgvector)', 'planned, not built yet', v3(54, 7, -40), fl(4) + 5, 'dim'],
  ]
  const nodes = {}
  for (const [id, k, title, body, pos, at, cls = ''] of [...N, ...side]) {
    const o = css3d(`<div class="k">${k}</div><h4>${title}</h4><p>${body}</p>`, 'node ' + cls, pos, -0.55)
    cssScene.add(o)
    nodes[id] = { o, pos, at, cls }
  }
  // edges: glowing tubes with a flowing pulse
  const edgeMat = (color) =>
    new THREE.ShaderMaterial({
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
      uniforms: { uT: { value: 0 }, uShow: { value: 0 }, uC: { value: new THREE.Color(color) } },
      vertexShader: 'varying vec2 vUv; void main(){ vUv=uv; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0); }',
      fragmentShader: `uniform float uT, uShow; uniform vec3 uC; varying vec2 vUv;
        void main(){
          if (vUv.x > uShow) discard;
          float dash = smoothstep(0.6, 1.0, fract(vUv.x * 6.0 - uT * 1.2));
          float a = 0.35 + dash * 0.9;
          gl_FragColor = vec4(uC * (1.2 + dash * 2.5), a);
        }`,
    })
  const edges = []
  const edge = (a, b, color = '#3fe0ff', at = null) => {
    const pa = nodes[a].pos, pb = nodes[b].pos
    const mid = pa.clone().lerp(pb, 0.5).add(v3(0, 1.2, 0))
    const curve = new THREE.QuadraticBezierCurve3(pa.clone().add(v3(2.6, -1.2, 0)), mid, pb.clone().add(v3(-2.6, -1.2, 0)))
    const mesh = new THREE.Mesh(new THREE.TubeGeometry(curve, 64, 0.07, 8), edgeMat(color))
    scene.add(mesh)
    edges.push({ mesh, curve, at: at ?? nodes[b].at - 0.8, a, b })
  }
  for (let i = 0; i < N.length - 1; i++) edge(N[i][0], N[i + 1][0])
  edge('quality', 'notsure', '#ffcf6b')
  edge('decide', 'notsure', '#ffcf6b', nodes.decide.at + 2.5)
  edge('validate', 'static', '#ffcf6b')

  // the data packet: a glowing core carrying the leaf photo
  const packet = new THREE.Group()
  const core = new THREE.Mesh(new THREE.SphereGeometry(0.35, 24, 16), new THREE.MeshBasicMaterial({ color: '#bff7ff' }))
  const halo = new THREE.Mesh(new THREE.SphereGeometry(0.7, 24, 16), new THREE.MeshBasicMaterial({ color: '#2fd0ff', transparent: true, opacity: 0.25, blending: THREE.AdditiveBlending, depthWrite: false }))
  const leafTex = new THREE.Texture(leafPhoto)
  leafTex.colorSpace = THREE.SRGBColorSpace
  leafTex.needsUpdate = true
  const thumb = new THREE.Mesh(new THREE.PlaneGeometry(1.4, 1.4), new THREE.MeshBasicMaterial({ map: leafTex, transparent: true }))
  thumb.position.y = 1.2
  packet.add(core, halo, thumb)
  scene.add(packet)

  // real app screens floating beside the graph
  const holo = (src, pos, rot, at, crop = 0) =>
    Object.assign(cssScene.add(css3d(`<img src="${uiBase}${src}" style="margin-top:-${crop}px"/>`, 'holo', pos, rot, 0.0068)).children.at(-1), { userData: { at } })
  const holos = [
    holo('diag_2_selected.png', v3(-5.5, 1, -2), 0.5, fl(0)),
    holo('unsure_4_result.png', v3(28, -9, -22), -0.4, fl(2) + 2.2),
    holo('diag_full.png', v3(80, 2, -46), -0.5, fl(5) + 4),
  ]

  // camera schedule over the graph: [time, focus node]
  const camKeys = [
    [F.start, 'phone'], [fl(0) + 2.6, 'api'], [fl(1), 'harden'], [fl(2), 'quality'], [fl(2) + 3, 'notsure'],
    [fl(3), 'vision'], [fl(4), 'decide'], [fl(4) + 3.6, 'retrieve'], [fl(5), 'advice'], [fl(5) + 3.2, 'validate'],
    [fl(6), 'store'], [fl(6) + 2.2, 'outbreak'], [fl(6) + 4.2, 'human'],
  ]

  // ------------------------------------------------------------ AI approach (transformer + RAG)
  const A = TL.ai
  const al = (i) => A.lines[i].start
  const AO = v3(160, 0, 0) // separate region of the world
  const aiGroup = new THREE.Group()
  aiGroup.position.copy(AO)
  scene.add(aiGroup)
  // 8x8 patches of the real leaf photo
  const G = 8, patches = []
  for (let gy = 0; gy < G; gy++)
    for (let gx = 0; gx < G; gx++) {
      const geo = new THREE.PlaneGeometry(0.5, 0.5)
      const uv = geo.getAttribute('uv')
      for (let i = 0; i < uv.count; i++) uv.setXY(i, (gx + uv.getX(i)) / G, (G - 1 - gy + uv.getY(i)) / G)
      const m = new THREE.Mesh(geo, new THREE.MeshBasicMaterial({ map: leafTex, transparent: true, color: '#9a9a9a' }))
      aiGroup.add(m)
      patches.push({ m, gx, gy })
    }
  // token vectors: a column of cubes per token (16 shown)
  const T = 16, D = 10, r = rng(77)
  const cubeGeo = new THREE.BoxGeometry(0.22, 0.22, 0.22)
  const vec = new THREE.InstancedMesh(cubeGeo, new THREE.MeshBasicMaterial({ toneMapped: false }), T * D)
  const vecVals = Array.from({ length: T * D }, () => r())
  aiGroup.add(vec)
  // attention matrix 16x16
  const att = new THREE.InstancedMesh(new THREE.BoxGeometry(0.3, 1, 0.3), new THREE.MeshBasicMaterial({ toneMapped: false }), T * T)
  att.position.set(0, -2.5, -6)
  aiGroup.add(att)
  const attVals = Array.from({ length: T * T }, (_, i) => {
    const a = Math.floor(i / T), b = i % T
    return Math.exp(-((a - b) ** 2) / 10) * 0.6 + r() * 0.4
  })
  const eq = css3d('softmax( Q·Kᵀ / √d ) · V', 'eq', AO.clone().add(v3(0, 4.6, -6)), 0, 0.012)
  cssScene.add(eq)
  const illus = css3d('illustration: how transformer models read an image · the model runs on Meta’s servers', 'lbl', AO.clone().add(v3(0, -5.8, -2)), 0, 0.011)
  cssScene.add(illus)
  // output probabilities (illustrative) -> brown spot
  // the app's 9 BRRI disease classes (kb_brri_rice.json) + healthy
  const diseases = ['brown spot', 'rice blast', 'bacterial leaf blight', 'sheath blight', 'sheath rot', 'bakanae', 'leaf scald', 'tungro', 'ufra', 'healthy']
  const probs = [0.68, 0.08, 0.05, 0.04, 0.03, 0.03, 0.03, 0.02, 0.02, 0.02]
  const bars = css3d(
    '<div style="width:640px;padding:20px 26px;border-radius:18px;background:rgba(4,20,30,.85);border:2px solid rgba(90,230,255,.5)">' +
      '<div class="lbl" style="margin-bottom:12px">output · probability per class (illustrative)</div>' +
      diseases.map((d, i) => `<div style="display:flex;align-items:center;gap:12px;margin:7px 0"><span class="lbl" style="width:230px;font-size:17px">${d}</span><div style="position:relative;flex:1;height:18px;background:rgba(255,255,255,.08);border-radius:6px"><div class="bar" data-p="${probs[i]}" style="width:0"></div></div></div>`).join('') +
      '</div>',
    '',
    AO.clone().add(v3(8.5, 0.5, -4)),
    -0.35,
    0.011,
  )
  cssScene.add(bars)
  // RAG ring: the 39 real chunks
  const kb = await (await fetch('/backend/app/data/kb_brri_rice.json')).json()
  const RAG = v3(160, 0, -40)
  const chunks = kb.chunks.map((c, i) => {
    const a = (i / kb.chunks.length) * Math.PI * 2
    const pos = RAG.clone().add(v3(Math.cos(a) * 11, Math.sin(a * 3) * 0.6, Math.sin(a) * 11))
    const o = css3d(`<b>${c.id}</b><br/>${c.disease} · ${c.topic} · p.${c.page}<br/><span class="bn" style="font-size:12px;opacity:.8">${(c.context || '').slice(0, 46)}…</span>`, 'chunk', pos, -a + Math.PI / 2, 0.012)
    cssScene.add(o)
    return { o, c, pos, hit: c.disease === 'brown_spot' }
  })
  const hits = chunks.filter((c) => c.hit).slice(0, 8)
  const query = css3d('<div class="k">QUERY</div><h4>brown_spot · Bangla</h4><p>disease filter → keyword overlap on text + AI-written context line → top ≤ 8</p>', 'node on', RAG.clone().add(v3(0, 3, 0)), 0, 0.012)
  cssScene.add(query)
  const ragNote = css3d('39 BRRI passages · contextual retrieval · vector search: next step', 'lbl', RAG.clone().add(v3(0, -4, 6)), 0, 0.012)
  cssScene.add(ragNote)
  const beams = hits.map((h) => {
    const g = new THREE.BufferGeometry().setFromPoints([RAG.clone().add(v3(0, 1.5, 0)), h.pos])
    const l = new THREE.Line(g, new THREE.LineBasicMaterial({ color: '#7dffb0', transparent: true, opacity: 0 }))
    scene.add(l)
    return l
  })
  const mcp = css3d('<div class="k">DEVELOPERS</div><h4>MCP server · cropguardian-kb</h4><p>the same knowledge base, as tools for AI agents</p>', 'node', RAG.clone().add(v3(-4.5, 5.5, 4)), 0.3, 0.012)
  const tests = css3d('<div class="k">QUALITY</div><h4 style="font-size:64px;margin:4px 0">1,000+</h4><p>automated tests on every push</p>', 'node on', RAG.clone().add(v3(5, 5.5, 4)), -0.1, 0.012)
  cssScene.add(mcp, tests)

  const tmpM = new THREE.Matrix4(), tmpC = new THREE.Color()
  const camPos = new THREE.Vector3(), camTgt = new THREE.Vector3()

  function setOpacity(o, k) {
    o.element.style.opacity = clamp(k).toFixed(3)
    o.visible = k > 0.001
  }

  function update(t) {
    // ---- pipeline nodes + edges + packet
    for (const id in nodes) {
      const n = nodes[id]
      setOpacity(n.o, seg(t, n.at - 0.4, n.at + 0.4))
      n.o.element.classList.toggle('on', t > n.at && t < n.at + 4 && !n.cls)
    }
    for (const e of edges) {
      e.mesh.material.uniforms.uT.value = t
      e.mesh.material.uniforms.uShow.value = seg(e.at, e.at, e.at + 1) * 0 + seg(t, e.at, e.at + 1.1)
    }
    holos.forEach((h) => setOpacity(h, seg(t, h.userData.at, h.userData.at + 0.8) * (t < A.start ? 1 : 0)))
    // packet travels the main chain
    let pk = null
    for (let i = 0; i < N.length - 1; i++) {
      const a = nodes[N[i][0]], b = nodes[N[i + 1][0]]
      if (t >= a.at && t < b.at) {
        const e = edges[i]
        const k = seg(t, Math.max(a.at, b.at - 1.6), b.at)
        pk = e.curve.getPoint(k)
      }
    }
    packet.visible = !!pk && t < A.start
    if (pk) packet.position.copy(pk)
    packet.rotation.y = t
    halo.scale.setScalar(1 + Math.sin(t * 6) * 0.12)

    // ---- camera
    if (t < A.start) {
      let i = 0
      while (i < camKeys.length - 1 && t >= camKeys[i + 1][0]) i++
      const [t0, idA] = camKeys[i]
      const [t1, idB] = camKeys[Math.min(i + 1, camKeys.length - 1)]
      const k = idA === idB ? 0 : seg(t, Math.max(t0, t1 - 1.6), t1)
      const pa = nodes[idA].pos, pb = nodes[idB].pos
      camTgt.lerpVectors(pa, pb, k)
      const off = v3(-8.5, 3.6, 17 + Math.sin(t * 0.3) * 0.8)
      if (t < F.start + 2.5) off.multiplyScalar(lerp(2.6, 1, seg(t, F.start, F.start + 2.5))) // arrive from far
      camPos.copy(camTgt).add(off)
      cam.position.copy(camPos)
      cam.lookAt(camTgt.clone().add(v3(1.2, -0.8, -1.0)))
    } else {
      // ---- AI approach
      const t0 = al(0), t1 = al(1), t2 = al(2), t3 = al(3)
      // patches: whole image -> split -> line of tokens
      const kSplit = seg(t, t0 + 0.8, t0 + 2.6), kLine = seg(t, t0 + 2.6, t0 + 4.4)
      patches.forEach(({ m, gx, gy }) => {
        const grid = v3((gx - 3.5) * (0.5 + kSplit * 0.22), (3.5 - gy) * (0.5 + kSplit * 0.22) + 1, 0)
        const idx = gy * G + gx
        const line = v3((idx % 32) * 0.36 - 5.6, 3.2 - Math.floor(idx / 32) * 0.45, -1)
        m.position.lerpVectors(grid, line, kLine)
        m.scale.setScalar(lerp(1, 0.6, kLine))
        m.material.opacity = 1 - seg(t, t1 + 2, t1 + 3)
        m.rotation.y = Math.sin(kSplit * Math.PI) * 0.4
      })
      // vectors grow under the first 16 tokens
      const kVec = seg(t, t0 + 4, t0 + 6)
      for (let i = 0; i < T; i++)
        for (let d = 0; d < D; d++) {
          const val = vecVals[i * D + d]
          tmpM.makeTranslation(i * 0.72 - 5.4, 2.2 - d * 0.26 * kVec - 0.3, -1)
          tmpM.scale(v3(kVec, kVec, kVec))
          vec.setMatrixAt(i * D + d, tmpM)
          vec.setColorAt(i * D + d, tmpC.setHSL(0.52 - val * 0.4, 0.85, 0.22 + val * 0.2))
        }
      vec.instanceMatrix.needsUpdate = true
      vec.instanceColor.needsUpdate = true
      // attention matrix heights pulse
      const kAtt = seg(t, t1 - 0.5, t1 + 1.5)
      for (let i = 0; i < T * T; i++) {
        const a = Math.floor(i / T), b = i % T
        const v = attVals[i] * (0.6 + 0.4 * Math.sin(t * 2 + a * 0.4 + b * 0.3))
        const h = 0.05 + v * 2.2 * kAtt
        tmpM.makeTranslation((b - 7.5) * 0.36, h / 2, (a - 7.5) * 0.36)
        tmpM.scale(v3(1, h, 1))
        att.setMatrixAt(i, tmpM)
        att.setColorAt(i, tmpC.setHSL(0.55 - v * 0.45, 0.9, 0.18 + v * 0.3))
      }
      att.instanceMatrix.needsUpdate = true
      att.instanceColor.needsUpdate = true
      setOpacity(eq, seg(t, t1, t1 + 0.8) * (1 - seg(t, t2 - 0.6, t2)))
      setOpacity(illus, seg(t, t0 + 0.5, t0 + 1.2) * (1 - seg(t, t2 - 0.6, t2)))
      setOpacity(bars, seg(t, t1 + 4.5, t1 + 5.2) * (1 - seg(t, t2 - 0.6, t2)))
      bars.element.querySelectorAll('.bar').forEach((b) => (b.style.width = (Number(b.dataset.p) * 100 * seg(t, t1 + 5, t1 + 7)).toFixed(1) + '%'))
      // RAG
      const kR = seg(t, t2 - 0.4, t2 + 1)
      chunks.forEach((c, i) => {
        setOpacity(c.o, kR)
        const lit = c.hit && t > t2 + 2.5 + hits.indexOf(c) * 0.25
        c.o.element.classList.toggle('hit', lit)
        const pull = lit ? seg(t, t2 + 4.5, t2 + 6.5) * 0.35 : 0
        c.o.position.lerpVectors(c.pos, RAG.clone().add(v3(0, 1.5, 0)), pull)
      })
      beams.forEach((b, i) => (b.material.opacity = t > t2 + 2.5 + i * 0.25 ? 0.9 : 0))
      setOpacity(query, seg(t, t2 + 0.6, t2 + 1.4))
      setOpacity(ragNote, seg(t, t2 + 1.4, t2 + 2.2))
      setOpacity(mcp, seg(t, t3, t3 + 0.8))
      setOpacity(tests, seg(t, t3 + 1.8, t3 + 2.6))
      // camera: transformer stage, then the RAG ring
      if (t < t2 - 0.4) {
        const k = seg(t, A.start, t2)
        cam.position.copy(AO).add(v3(lerp(-1.0, 2.5, k), lerp(1.5, 3.2, k), lerp(13, 15.5, k)))
        cam.lookAt(AO.clone().add(v3(lerp(0, 2.5, k), 0.3, -3)))
      } else {
        const k = seg(t, t2 - 0.4, TL.ai.end + 0.5)
        const a = lerp(-0.5, 0.6, k)
        cam.position.copy(RAG).add(v3(Math.sin(a) * lerp(19, 15, k), lerp(6.5, 4.5, k), Math.cos(a) * lerp(19, 15, k)))
        cam.lookAt(RAG.clone().add(v3(0, 1.2, 0)))
      }
    }
    // hide the other stage's css objects
    const inAI = t >= A.start
    for (const id in nodes) if (inAI) setOpacity(nodes[id].o, 0)
    if (!inAI) [eq, illus, bars, query, ragNote, mcp, tests, ...chunks.map((c) => c.o)].forEach((o) => setOpacity(o, 0))
    return cam
  }

  return { scene, cssScene, update }
}
