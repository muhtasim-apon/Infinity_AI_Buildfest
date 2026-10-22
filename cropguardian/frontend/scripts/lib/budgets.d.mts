export const BUDGET_KB: {
  initial: number
  route: number
  staff: number
  hero3d: number
  bengaliFonts: number
}
export function gzipKb(buffer: Buffer): number
export function evaluate(input: {
  manifest: Record<string, unknown>
  readFile: (file: string) => Buffer
  bengaliFontFiles: { file: string; bytes: number }[]
}): {
  rows: { name: string; kind: string; kb: number; limit: number; ok: boolean }[]
  problems: string[]
}
