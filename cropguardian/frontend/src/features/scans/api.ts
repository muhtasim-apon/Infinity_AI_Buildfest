import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '../../lib/api'

export type ScanStatus = 'diagnosed' | 'not_sure' | 'healthy'
export type NotSureReason =
  'model_error' | 'not_rice' | 'poor_image' | 'unknown_disease' | 'low_confidence' | 'not_a_plant'

export interface Citation {
  id: string
  source_id: string
  title: string
  publisher: string
  url: string
  page: number
  excerpt: string
}

export interface Advice {
  summary_bn: string
  steps_bn: string[]
  chemical: null
  safety_bn: string
  citations: string[]
}

export interface Scan {
  id: string
  created_at: string
  status: ScanStatus
  crop: string | null
  disease: string | null
  disease_bn: string | null
  disease_en: string | null
  confidence_band: 'high' | 'medium' | null
  reason: NotSureReason | null
  region_code: string
  advice: Advice | null
  advice_source: 'llm' | 'static_card' | 'none'
  citations: Citation[]
  model: string | null
  prompt_version: string | null
  latency_ms: number | null
  kb_version: string
  reviewed_by_agronomist: false
  synthetic: boolean
}

export interface OutbreakAlert {
  id: string
  disease: string
  disease_bn: string | null
  disease_en: string | null
  region_code: string
  region_bn: string
  region_en: string
  case_count: number
  window_start: string
  window_end: string
  status: 'draft' | 'approved' | 'rejected'
  decided_at: string | null
  created_at: string
  unverified: true
  synthetic: boolean
}

export interface KbSources {
  kb_version: string
  transcription: string
  policy: string
  sources: {
    id: string
    title: string
    publisher: string
    url: string
    printed_pages: string
    chunks: number
  }[]
  excluded: { source_id: string; page: number; reason: string }[]
  diseases: Record<string, { bn: string; en: string }>
  divisions: Record<string, { bn: string; en: string }>
  limits: {
    abstain_below: number
    confidence: string
    retrieval: string
    crops: string[]
    image_retention: string
    outbreak_rule: { min_cases: number; window_days: number; needs_reviewer_approval: boolean }
  }
}

/** Division codes (ISO 3166-2:BD). Coarse location only: the app never asks for GPS. */
export const DIVISIONS = ['BD-C', 'BD-B', 'BD-E', 'BD-D', 'BD-A', 'BD-G', 'BD-F', 'BD-H'] as const

export const UPLOAD_TIMEOUT_MS = 90_000

export function newIdempotencyKey(): string {
  return crypto.randomUUID().replace(/-/g, '')
}

export function uploadScan(blob: Blob, regionCode: string, key: string): Promise<Scan> {
  const form = new FormData()
  form.append('image', blob, 'leaf.jpg')
  form.append('region_code', regionCode)
  return api.post<Scan>('/api/v1/scans', form, {
    headers: { 'Idempotency-Key': key },
    timeoutMs: UPLOAD_TIMEOUT_MS,
  })
}

export const scanKeys = {
  all: ['scans'] as const,
  one: (id: string) => ['scans', id] as const,
  alerts: ['alerts'] as const,
  kb: ['kb-sources'] as const,
}

export function useScans() {
  return useQuery({
    queryKey: scanKeys.all,
    queryFn: () => api.get<{ scans: Scan[] }>('/api/v1/scans').then((r) => r.scans),
  })
}

export function useScan(id: string) {
  return useQuery({
    queryKey: scanKeys.one(id),
    queryFn: () => api.get<Scan>(`/api/v1/scans/${encodeURIComponent(id)}`),
  })
}

export function useAlerts() {
  return useQuery({
    queryKey: scanKeys.alerts,
    queryFn: () => api.get<{ alerts: OutbreakAlert[] }>('/api/v1/alerts').then((r) => r.alerts),
  })
}

export function useDecideAlert() {
  const client = useQueryClient()
  return useMutation({
    mutationFn: ({ id, decision }: { id: string; decision: 'approve' | 'reject' }) =>
      api.post<OutbreakAlert>(`/api/v1/alerts/${encodeURIComponent(id)}/decision`, { decision }),
    onSuccess: () => client.invalidateQueries({ queryKey: scanKeys.alerts }),
  })
}

export interface DivisionStats {
  region_code: string
  region_bn: string
  region_en: string
  diagnosed: number
  not_sure: number
  healthy: number
}

export function useScanStats() {
  return useQuery({
    queryKey: ['scan-stats'],
    queryFn: () => api.get<{ days: number; divisions: DivisionStats[] }>('/api/v1/scans-stats'),
  })
}

export function useKbSources() {
  return useQuery({
    queryKey: scanKeys.kb,
    queryFn: () => api.get<KbSources>('/api/v1/kb/sources'),
    staleTime: 60 * 60 * 1000,
  })
}

/**
 * Shrink a camera photo on the device before upload (data-light rule): longest side 1600 px, JPEG.
 * Canvas re-encoding also drops EXIF/GPS on the phone itself; the server strips it again anyway.
 */
export async function compressPhoto(file: File, maxSide = 1600): Promise<Blob> {
  if (typeof createImageBitmap !== 'function') return file
  try {
    const bitmap = await createImageBitmap(file)
    const scale = Math.min(1, maxSide / Math.max(bitmap.width, bitmap.height))
    const canvas = document.createElement('canvas')
    canvas.width = Math.round(bitmap.width * scale)
    canvas.height = Math.round(bitmap.height * scale)
    const ctx = canvas.getContext('2d')
    if (!ctx) return file
    ctx.drawImage(bitmap, 0, 0, canvas.width, canvas.height)
    bitmap.close()
    const blob = await new Promise<Blob | null>((resolve) =>
      canvas.toBlob(resolve, 'image/jpeg', 0.85),
    )
    return blob ?? file
  } catch {
    return file // the server validates and rejects anything unusable
  }
}
