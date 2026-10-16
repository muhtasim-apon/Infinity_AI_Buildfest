# Training notebook outline (Colab / Kaggle)

Owner: Taeen. One notebook per candidate, same skeleton. Log everything to CSV; commit configs, never weights.

1. **Setup** — `pip install timm torch torchvision onnx onnxruntime scikit-learn pytorch-grad-cam imagehash`;
   mount Drive / Kaggle input; set seed.
2. **Data** — download D1, D2 (and D3 for OOD); verify counts vs `docs/data/datasets.md`; pHash dedup;
   map labels via `configs/labels.yaml`; build/load `split_v1.csv` (group-stratified).
3. **Preprocess** — exactly as `services/api/app/ml/preprocess.py`: resize short side 256 → centre crop 224
   for eval; train-time augments from `train_base.yaml`.
4. **Model** — `timm.create_model(name, pretrained=True, num_classes=7)`.
5. **Train** — stage 1 head only; stage 2 fine-tune; AMP; checkpoint every epoch (Colab disconnects — C6).
6. **CV** — 5 folds for model selection; record mean ± std macro-F1.
7. **Calibrate** — fit temperature T on validation NLL (LBFGS); ECE before/after; reliability diagram.
8. **Threshold** — risk–coverage curve; choose τ per `docs/ai/eval-plan.md`.
9. **OOD** — energy score on D3 non-rice + random non-leaf images; AUROC; OOD threshold.
10. **Explain** — Grad-CAM on 50 validation images per class → gallery PNGs, checked by the team against public disease descriptions.
11. **Confound probe** — logistic regression predicting source dataset from penultimate embeddings.
12. **Export** — see `export_onnx.md`.
13. **Report** — fill `ml/evaluation/report_template.md`; numbers go to the model card only from here.

Baseline (classical): colour histograms (HSV, 32 bins) + GLCM texture + LBP → StandardScaler → SVM (RBF),
grid search C/γ with the same CV folds.
