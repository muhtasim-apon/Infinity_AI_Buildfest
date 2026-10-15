# Evaluation plan

All targets are **targets**. Measured values replace "—" only with split id + commit.

## 1. Vision classifier
| Metric | Target (proposal, agree with mentor) | Measured |
|---|---|---|
| Test macro-F1 (field images) | ≥ 0.85 | — |
| Recall, each notifiable disease (blast, BLB, tungro) | ≥ 0.85 | — |
| ECE after temperature scaling | ≤ 0.05 | — |
| Selective accuracy @ τ | ≥ 0.95 | — |
| Coverage @ τ | report (no target yet) | — |
| OOD AUROC | ≥ 0.90 | — |
| int8 parity (top-1 agreement vs FP32) | ≥ 99 % | — |
| CPU latency p95 per image | ≤ 1 s | — |

## 2. End-to-end API
| Metric | Target | Measured |
|---|---|---|
| Warm p95 scan → advice | ≤ 5 s (cached advice) / ≤ 20 s (fresh LLM) | — |
| Cold start to first response | ≤ 90 s, UI handles gracefully | — |
| Error rate under 20 concurrent users | < 1 % | — |

## 3. RAG & agent
| Metric | Target | Measured |
|---|---|---|
| Retrieval Recall@8 on golden set | ≥ 0.90 | — |
| Faithfulness (supported claims) | ≥ 0.95 | — |
| Citation coverage | **1.00 (hard gate)** | — |
| Banned-ingredient leakage | **0 (hard gate)** | — |
| Red-team failures | **0 (hard gate)** | — |
| Bangla fluency (native raters 1–5) | ≥ 4.0 | — |

## 4. Usability (Phase 3 sessions, Raisa + Sara)
Task success (scan → read advice unaided) ≥ 80 % of participants; SUS score reported; time on task.
Participants: farmers and extension officers, consented; no personal data in notes.

## 5. Field outcome (winning signal — later)
Pilot design with a partner extension office: pilot vs comparison plots, same variety/season;
outcomes: time-to-correct-treatment, disease-affected area, yield. Pre-registered in
`docs/product/pilot-protocol.md` before data collection. **No loss-reduction claim before this.**
