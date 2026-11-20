// Shared helpers for the v2 film: deterministic noise, canvas textures, easing and timing.
import * as THREE from 'three'

export const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x))
export const lerp = (a, b, k) => a + (b - a) * k
export const smooth = (k) => k * k * (3 - 2 * k)
export const ease = (k) => (k < 0.5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2)
/** 0..1 progress of t inside [a, b], eased. */
export const seg = (t, a, b, f = ease) => f(clamp((t - a) / (b - a)))
export const v3 = (x, y, z) => new THREE.Vector3(x, y, z)
export const lerpV = (a, b, k) => new THREE.Vector3().lerpVectors(a, b, k)

/** Seeded PRNG (deterministic film: every render of a frame is identical). */
export function rng(seed) {
  let s = seed >>> 0 || 1
  return () => {
    s ^= s << 13
    s ^= s >>> 17
    s ^= s << 5
    return (s >>> 0) / 4294967296
  }
}

// 2D value noise + fbm
function hash(x, y) {
  const h = Math.sin(x * 127.1 + y * 311.7) * 43758.5453
  return h - Math.floor(h)
}
export function noise(x, y) {
  const xi = Math.floor(x), yi = Math.floor(y)
  const xf = x - xi, yf = y - yi
  const u = xf * xf * (3 - 2 * xf), v = yf * yf * (3 - 2 * yf)
  const a = hash(xi, yi), b = hash(xi + 1, yi), c = hash(xi, yi + 1), d = hash(xi + 1, yi + 1)
  return a + (b - a) * u + (c - a) * v + (a - b - c + d) * u * v
}
export function fbm(x, y, oct = 5) {
  let s = 0, a = 0.5, f = 1
  for (let i = 0; i < oct; i++) {
    s += a * noise(x * f, y * f)
    f *= 2.03
    a *= 0.5
  }
  return s
}

export function canvasTex(w, h, draw, { repeat = null, srgb = true } = {}) {
  const c = document.createElement('canvas')
  c.width = w
  c.height = h
  const g = c.getContext('2d')
  draw(g, w, h)
  const t = new THREE.CanvasTexture(c)
  if (srgb) t.colorSpace = THREE.SRGBColorSpace
  t.anisotropy = 8
  if (repeat) {
    t.wrapS = t.wrapT = THREE.RepeatWrapping
    t.repeat.set(repeat[0], repeat[1])
  }
  return t
}

/** Per-pixel painter: f(x, y) -> [r, g, b, a?] in 0..255. */
export function pixelTex(w, h, f, opts) {
  return canvasTex(
    w,
    h,
    (g) => {
      const img = g.createImageData(w, h)
      for (let y = 0; y < h; y++)
        for (let x = 0; x < w; x++) {
          const [r, gg, b, a = 255] = f(x, y)
          const i = (y * w + x) * 4
          img.data[i] = r
          img.data[i + 1] = gg
          img.data[i + 2] = b
          img.data[i + 3] = a
        }
      g.putImageData(img, 0, 0)
    },
    opts,
  )
}

/** Plaid / check cloth (lungi, gamchha). */
export function plaidTex(colors, bands, size = 256, repeat = [4, 4]) {
  return canvasTex(
    size,
    size,
    (g, w, h) => {
      g.fillStyle = colors[0]
      g.fillRect(0, 0, w, h)
      g.globalAlpha = 0.55
      for (const [pos, width, col] of bands) {
        g.fillStyle = col
        g.fillRect(pos * w, 0, width * w, h)
        g.fillRect(0, pos * h, w, width * h)
      }
      g.globalAlpha = 0.08
      for (let i = 0; i < 2600; i++) {
        g.fillStyle = i % 2 ? '#000' : '#fff'
        g.fillRect(Math.random() * w, Math.random() * h, 1, 1)
      }
    },
    { repeat },
  )
}

export async function loadImage(src) {
  const img = new Image()
  img.src = src
  await img.decode()
  return img
}
