# ONNX export & quantisation

1. `model.eval()`; dummy input `torch.randn(1, 3, 224, 224)`.
2. `torch.onnx.export(model, x, "classifier.fp32.onnx", opset_version=17, input_names=["input"],
   output_names=["logits"], dynamic_axes={"input": {0: "batch"}, "logits": {0: "batch"}})`.
3. `onnx.checker.check_model`.
4. Quantise: `onnxruntime.quantization.quantize_dynamic("classifier.fp32.onnx", "classifier.int8.onnx",
   weight_type=QuantType.QInt8)` (if accuracy drops, try static quantisation with a 200-image calibration set).
5. **Parity gate** on the validation split: top-1 agreement int8 vs FP32 ≥ 99 % and macro-F1 drop ≤ 1 pt.
   Fail → ship FP32 ONNX.
6. Latency: median & p95 over 200 images with `intra_op_num_threads=1`.
7. `sha256sum classifier.int8.onnx` → upload to Supabase `models/` bucket →
   insert `model_versions` (semver, architecture, sha256, τ, T, eval_summary with split id + commit),
   `is_active=false` until admin promotes.
