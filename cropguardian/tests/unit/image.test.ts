// Unit (Vitest): apps/web/src/lib/image.ts
import { describe, expect, it } from "vitest";
import { coarsen } from "../../apps/web/src/lib/image";

describe("coarsen", () => {
  it("rounds to 2 decimals (~1 km) before anything is stored or sent", () => {
    expect(coarsen(23.85678)).toBe(23.86);
    expect(coarsen(90.2649)).toBe(90.26);
  });
  it.todo("prepareImage strips EXIF (output JPEG has no APP1 segment)");
  it.todo("prepareImage resizes long side to ≤ 1024 px");
  it.todo("flags dark images (mean luminance < 50)");
});
