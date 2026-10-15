// Client-side image pipeline. Stub.
// 1. decode with createImageBitmap (imageOrientation: "from-image")
// 2. resize so the long side ≤ 1024 px (OffscreenCanvas / canvas)
// 3. canvas.toBlob("image/jpeg", 0.8) — re-encoding drops EXIF (GPS!) by construction
// 4. sha256 via crypto.subtle.digest
// 5. quality hints: mean luminance < 50 → "dark"; Laplacian variance low → "blurry"
// 6. coarse location: round(lat, 2), round(lon, 2) BEFORE it is stored or sent (privacy.md)

export interface PreparedImage {
  jpeg: Blob;
  sha256: string;
  width: number;
  height: number;
  qualityFlag: "dark" | "blurry" | null;
}

export declare function prepareImage(file: File): Promise<PreparedImage>;

export function coarsen(value: number): number {
  return Math.round(value * 100) / 100;
}
