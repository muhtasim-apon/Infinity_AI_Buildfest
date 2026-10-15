// Offline outbox (ADR 0009). Stub.
// Each item: { id (uuid = Idempotency-Key), jpeg Blob, meta: ScanCreateIn, attempts, createdAt }.
// flush(): only when navigator.onLine && warmUp() === "ready"; create → upload → analyze;
// on success remove; on failure attempts++ with backoff; after 10 attempts mark "stuck" and
// show a manual retry. Items never leave the device except to our API.

import type { ScanCreateIn } from "./api";

export interface OutboxItem {
  id: string;
  jpeg: Blob;
  meta: ScanCreateIn;
  attempts: number;
  createdAt: string;
}

export declare function enqueue(jpeg: Blob, meta: ScanCreateIn): Promise<OutboxItem>;
export declare function pending(): Promise<OutboxItem[]>;
export declare function flush(): Promise<{ sent: number; failed: number }>;
