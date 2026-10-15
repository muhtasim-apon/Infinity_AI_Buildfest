// The ONLY module that talks to the API. Stub — signatures and behaviour contract only.
//
// Cold-start contract (docs/deployment/challenges-and-recovery.md A1):
//   - warmUp() is called on app open; while /healthz is not 200, components read
//     `serverState === "waking"` and show "সার্ভার চালু হচ্ছে…".
//   - requests time out at 90 s during waking, 30 s otherwise; retried with exponential
//     backoff + jitter (max 3) ONLY for idempotent calls or calls carrying an Idempotency-Key.
//   - 429 respects Retry-After. problem+json errors map to i18n keys `error.<code>`.

export type ServerState = "unknown" | "waking" | "ready" | "down";

export interface ScanCreateIn {
  crop: "rice";
  field_id?: string | null;
  sha256: string;
  lat_coarse?: number | null;
  lon_coarse?: number | null;
  captured_at?: string;
  client_quality_flag?: "dark" | "blurry" | null;
}

export interface Prediction { code: string; name_bn: string; name_en: string; prob: number }
export interface Citation { title: string; publisher: string; page: number | null; url: string }
export interface Advisory {
  status: "ok" | "fallback" | "blocked";
  summary_bn: string;
  steps_bn: string[];
  chemical: { active_ingredient: string; dose: string; interval: string | null; phi_days: number | null } | null;
  safety_bn: string;
  citations: Citation[];
}
export interface AnalyzeOut {
  scan_id: string;
  status: "diagnosed" | "needs_review";
  diagnosis: { model_version: string; top3: Prediction[]; abstained: boolean; confidence_band: "high" | "medium" | "low" };
  advisory: Advisory | null;
}

export declare function warmUp(): Promise<ServerState>;
export declare function createScan(body: ScanCreateIn, idempotencyKey: string): Promise<{ scan_id: string; upload_url: string; upload_expires_at: string }>;
export declare function uploadToSignedUrl(url: string, jpeg: Blob): Promise<void>;
export declare function analyzeScan(scanId: string): Promise<AnalyzeOut>;
export declare function listScans(cursor?: string): Promise<{ items: unknown[]; next_cursor: string | null }>;
export declare function startDemo(role: "user" | "admin"): Promise<{ access_token: string; expires_in: number }>;
