from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from cg_ml import SEED
from cg_ml.data.integrity import check_image, image_stats, laplacian_variance, normalise_image
from cg_ml.data.prepare import prepare_dataset, raw_class_of, summarise
from cg_ml.data.taxonomy import Taxonomy, UnknownClassError, load_labels, normalise_name

LABELS = Path(__file__).resolve().parents[1] / "configs" / "labels.yaml"


def save(path: Path, size=(200, 160), color=(30, 160, 60), fmt="JPEG", exif_orientation=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    im = Image.new("RGB", size, color)
    kwargs = {}
    if exif_orientation:
        exif = Image.Exif()
        exif[0x0112] = exif_orientation
        exif[0x010F] = "SecretPhoneMaker"
        kwargs["exif"] = exif
    im.save(path, fmt, **kwargs)
    return path


@pytest.fixture(scope="module")
def taxonomy():
    return Taxonomy(load_labels(LABELS))


# --- integrity -------------------------------------------------------------------------------------
def test_good_image_ok(tmp_path):
    c = check_image(save(tmp_path / "a.jpg"))
    assert c.ok and (c.width, c.height) == (200, 160)


def test_tiny_image_dropped(tmp_path):
    c = check_image(save(tmp_path / "a.jpg", size=(100, 300)))
    assert not c.ok and c.reason == "too_small"


def test_exact_boundary_128_is_kept(tmp_path):
    assert check_image(save(tmp_path / "a.jpg", size=(128, 128))).ok
    assert not check_image(save(tmp_path / "b.jpg", size=(127, 300))).ok


def test_corrupt_and_truncated_and_non_image_dropped(tmp_path):
    good = save(tmp_path / "g.jpg", size=(300, 300))
    data = good.read_bytes()
    trunc = tmp_path / "t.jpg"
    trunc.write_bytes(data[: len(data) // 2])
    junk = tmp_path / "j.jpg"
    junk.write_bytes(b"this is not an image")
    empty = tmp_path / "e.jpg"
    empty.write_bytes(b"")
    for p in (trunc, junk, empty):
        c = check_image(p)
        assert not c.ok and c.reason == "corrupt", p.name


def test_exif_rotation_is_applied_and_size_swapped(tmp_path):
    p = save(tmp_path / "r.jpg", size=(300, 200), exif_orientation=6)  # rotate 90 CW
    c = check_image(p)
    assert (c.width, c.height) == (200, 300)
    assert normalise_image(p).size == (200, 300)


def test_normalise_strips_metadata_and_converts_rgb(tmp_path):
    p = save(tmp_path / "m.jpg", exif_orientation=1)
    assert b"SecretPhoneMaker" in p.read_bytes()  # precondition: the source has EXIF
    out = tmp_path / "clean.jpg"
    normalise_image(p).save(out, "JPEG")
    assert b"SecretPhoneMaker" not in out.read_bytes()
    assert len(Image.open(out).getexif()) == 0
    gray = tmp_path / "g.png"
    Image.new("L", (200, 200), 128).save(gray)
    assert normalise_image(gray).mode == "RGB"


def test_laplacian_variance_sharp_vs_flat_and_bad_input():
    flat = np.full((50, 50), 100.0)
    noisy = np.random.default_rng(SEED).integers(0, 255, (50, 50)).astype(float)
    assert laplacian_variance(flat) == 0.0
    assert laplacian_variance(noisy) > 100
    with pytest.raises(ValueError):
        laplacian_variance(np.zeros((2, 2)))
    with pytest.raises(ValueError):
        laplacian_variance(np.zeros((5, 5, 3)))


def test_image_stats_known_values():
    s = image_stats(Image.new("RGB", (64, 32), (255, 255, 255)))
    assert s["brightness_mean"] == pytest.approx(255)
    assert s["laplacian_var"] == 0.0
    assert (s["width"], s["height"]) == (64.0, 32.0)


# --- taxonomy --------------------------------------------------------------------------------------
def test_seven_classes_and_notifiable_flags(taxonomy):
    assert len(taxonomy.codes) == 7
    assert taxonomy.notifiable["blast"] and taxonomy.notifiable["tungro"]
    assert not taxonomy.notifiable["healthy"] and not taxonomy.notifiable["brown_spot"]


def test_spec_mapping_table_9_3(taxonomy):
    expect = {
        ("D1", "Healthy"): "healthy", ("D2", "Normal Leaf"): "healthy",
        ("D1", "Bacterial Leaf Blight"): "bacterial_leaf_blight", ("D1", "Brown Spot"): "brown_spot",
        ("D2", "Narrow Brown Spot"): "narrow_brown_spot", ("D2", "Blast"): "blast",
        ("D2", "Sheath Blight"): "sheath_blight", ("D1", "Tungro"): "tungro", ("D2", "Tungro"): "tungro",
    }  # fmt: skip
    for (ds, raw), code in expect.items():
        assert taxonomy.map_label(ds, raw) == code


def test_mapping_ignores_case_and_punctuation(taxonomy):
    assert taxonomy.map_label("D2", "narrow_brown-spot") == "narrow_brown_spot"
    assert normalise_name("Bacterial  Leaf_Blight!") == "bacterialleafblight"


def test_unknown_class_is_an_error_not_a_guess(taxonomy):
    with pytest.raises(UnknownClassError):
        taxonomy.map_label("D1", "Rice Hispa")
    with pytest.raises(UnknownClassError):
        taxonomy.map_label("D9", "Healthy")
    assert not taxonomy.knows("D1", "Blast")  # blast exists only in D2


def test_labels_yaml_rejects_unknown_target(tmp_path):
    p = tmp_path / "l.yaml"
    p.write_text("classes:\n - {code: a, notifiable: false}\nmapping:\n  D1: {X: nope}\n")
    with pytest.raises(ValueError, match="unknown class"):
        load_labels(p)


# --- prepare ---------------------------------------------------------------------------------------
def test_prepare_end_to_end_on_synthetic_dataset(tmp_path, taxonomy):
    root = tmp_path / "ext"
    save(root / "Healthy" / "a.jpg")
    save(root / "Brown Spot" / "b.jpg", exif_orientation=6)
    save(root / "Tungro" / "tiny.jpg", size=(50, 50))
    (root / "Tungro").mkdir(exist_ok=True)
    (root / "Tungro" / "broken.jpg").write_bytes(b"junk")
    save(root / "Rice Hispa" / "x.jpg")  # not in the taxonomy
    (root / "Healthy" / "notes.txt").write_text("ignored: not an image")
    recs = prepare_dataset("D1", root, tmp_path / "proc", taxonomy)
    by = {r.source_rel_path: r for r in recs}
    assert by["Healthy/a.jpg"].status == "ok" and by["Healthy/a.jpg"].class_code == "healthy"
    assert (by["Brown Spot/b.jpg"].width, by["Brown Spot/b.jpg"].height) == (160, 200)
    assert by["Tungro/tiny.jpg"].status == "too_small"
    assert by["Tungro/broken.jpg"].status == "corrupt"
    assert by["Rice Hispa/x.jpg"].status == "unknown_class"
    assert len(recs) == 5  # the .txt file is not counted
    for r in recs:
        if r.status == "ok":
            out = tmp_path / "proc" / r.processed_rel_path
            assert out.exists() and len(Image.open(out).getexif()) == 0


def test_prepare_is_deterministic(tmp_path, taxonomy):
    root = tmp_path / "ext"
    for i in range(4):
        save(root / "Healthy" / f"{i}.jpg", color=(i * 20, 100, 50))
    a = prepare_dataset("D1", root, tmp_path / "p1", taxonomy)
    b = prepare_dataset("D1", root, tmp_path / "p2", taxonomy)
    assert [(r.source_rel_path, r.brightness_mean, r.processed_rel_path) for r in a] == [
        (r.source_rel_path, r.brightness_mean, r.processed_rel_path) for r in b
    ]


def test_raw_class_uses_nearest_known_ancestor(taxonomy):
    assert raw_class_of(Path("Train/Blast/x.jpg"), "D2", taxonomy) == "Blast"
    assert raw_class_of(Path("Blast/Train/x.jpg"), "D2", taxonomy) == "Blast"
    assert raw_class_of(Path("x.jpg"), "D2", taxonomy) is None


def test_summary_compares_page_claims_with_files_found(tmp_path, taxonomy):
    root = tmp_path / "ext"
    for i in range(3):
        save(root / "Healthy" / f"{i}.jpg")
    recs = prepare_dataset("D1", root, tmp_path / "p", taxonomy)
    s = summarise(recs, {"Healthy": 5}, taxonomy, "D1")
    assert s["page_vs_found"]["Healthy"] == {
        "unified_class": "healthy",
        "page_claim": 5,
        "files_found": 3,
        "difference": -2,
    }
    assert s["by_status"] == {"ok": 3}
