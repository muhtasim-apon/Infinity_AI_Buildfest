"""Crop Guardian ML library (spec section 9).

Pure, typed, unit-tested library code. Notebooks (Kaggle/Colab) only call `python -m cg_ml ...`
so every result is reproducible from a commit. No dataset or weight is ever committed.
"""

__version__ = "0.1.0"
SEED = 20261016  # spec 9.4 step 7: the one seed for splits and sampling
