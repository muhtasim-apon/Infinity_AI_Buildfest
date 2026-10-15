# Model card — Lesion detector & severity (roadmap)

**Status:** Roadmap — not started · **Risk tier:** Medium

## Intended use
Locate lesions with bounding boxes (YOLOv8n) and estimate % leaf area affected → severity band
(low / medium / high) to refine advice (e.g. spray thresholds in source guides).

## Data needed
≥ 300 agronomist-annotated images per class with boxes (Label Studio / CVAT), drawn from our
pilot photos and D1/D2 (licence permits derivatives with attribution).

## Evaluation plan
mAP@0.5 per class; severity band agreement with two agronomists (Cohen's κ); latency on CPU.

## Limitations (anticipated)
Box annotation cost; overlapping lesions; severity from a single leaf ≠ field severity.
