import copy
from pathlib import Path

import pytest
import yaml

from app.rag.sources import (
    SourcesError,
    allowed_hosts,
    is_ingestion_url_allowed,
    load,
    load_validated,
    validate,
)

SOURCES = Path(__file__).resolve().parents[3] / "kb" / "sources.yaml"


def good_doc(**over):
    doc = {
        "id": "doc_one",
        "title": "T",
        "publisher": "P",
        "url": "https://example.org/a.pdf",
        "edition_date": "2020",
        "language": "bn",
        "licence_note": "L",
        "retrieved_at": "2026-10-21",
        "status": "downloaded",
        "sha256": "a" * 64,
        "bytes": 10,
        "extraction": "text",
    }
    doc.update(over)
    return doc


def data_of(*docs):
    return {"documents": list(docs)}


# --- the committed registry ---------------------------------------------------------------------
def test_committed_sources_yaml_is_valid():
    assert validate(load(SOURCES)) == []


def test_every_document_has_publisher_edition_licence():
    for doc in load_validated(SOURCES)["documents"]:
        for key in ("publisher", "edition_date", "licence_note"):
            assert str(doc[key]).strip(), (doc["id"], key)


def test_registry_covers_each_required_source_family():
    docs = load_validated(SOURCES)["documents"]
    publishers = " ".join(d["publisher"] for d in docs)
    assert "BRRI" in publishers or "Bangladesh Rice Research Institute" in publishers
    assert "Department of Agricultural Extension" in publishers
    assert "IRRI" in publishers or "International Rice Research Institute" in publishers


def test_known_gaps_are_declared_not_hidden():
    gaps = yaml.safe_load(SOURCES.read_text(encoding="utf-8"))["gaps"]
    ids = {g["id"] for g in gaps}
    assert {"gap_bd_banned_pesticide_list", "gap_expert_review"} <= ids


def test_no_document_claims_expert_review():
    for doc in load_validated(SOURCES)["documents"]:
        assert doc.get("expert_reviewed", False) is False


def test_ocr_documents_are_flagged_not_marked_as_text():
    for doc in load_validated(SOURCES)["documents"]:
        if doc["status"] == "downloaded" and not doc["text_layer"]:
            assert doc["extraction"] == "needs_ocr", doc["id"]


def test_allow_list_derived_from_registry():
    hosts = allowed_hosts(load_validated(SOURCES))
    assert "knowledgebank-brri.org" in hosts
    assert "evil.example.com" not in hosts


# --- validator behaviour (invalid input) -----------------------------------------------------------
@pytest.mark.parametrize(
    "field",
    ["id", "title", "publisher", "url", "edition_date", "language", "licence_note", "retrieved_at"],
)
def test_missing_required_field_reported(field):
    doc = good_doc()
    del doc[field]
    assert any(field in p for p in validate(data_of(doc)))


def test_empty_string_counts_as_missing():
    assert validate(data_of(good_doc(publisher="  ")))


def test_duplicate_ids_and_bad_ids():
    assert any("duplicate" in p for p in validate(data_of(good_doc(), good_doc())))
    assert validate(data_of(good_doc(id="Bad ID!")))


@pytest.mark.parametrize(
    "url", ["ftp://x.org/a", "file:///etc/passwd", "https://", "notaurl", "https://u:p@x.org/a"]
)
def test_bad_urls_rejected(url):
    assert validate(data_of(good_doc(url=url)))


def test_downloaded_requires_hash_extraction_and_bytes():
    assert validate(data_of(good_doc(sha256="xyz")))
    assert validate(data_of(good_doc(sha256="A" * 64)))  # upper case is not canonical
    assert validate(data_of(good_doc(extraction="magic")))
    assert validate(data_of(good_doc(bytes=0)))
    assert validate(data_of(good_doc(bytes="10")))


def test_hash_without_download_is_suspicious():
    assert validate(data_of(good_doc(status="candidate_not_downloaded")))
    cand = good_doc(status="candidate_not_downloaded")
    for k in ("sha256", "bytes", "extraction"):
        del cand[k]
    assert validate(data_of(cand)) == []


def test_unknown_status_and_bad_date():
    assert validate(data_of(good_doc(status="done")))
    assert validate(data_of(good_doc(retrieved_at="21/10/2026")))


def test_expert_review_cannot_be_asserted():
    assert validate(data_of(good_doc(expert_reviewed=True)))
    assert validate(data_of(good_doc(expert_reviewed=False))) == []


def test_verified_hint_needs_a_hint():
    assert validate(data_of(good_doc(disease_hint_verified=True)))


def test_non_mapping_entry_and_bad_top_level(tmp_path):
    assert validate({"documents": ["oops"]})
    p = tmp_path / "s.yaml"
    p.write_text("documents: 3\n")
    with pytest.raises(SourcesError):
        load(p)
    p.write_text("- a\n- b\n")
    with pytest.raises(SourcesError):
        load(p)


def test_load_validated_raises_with_all_problems(tmp_path):
    bad = data_of(good_doc(url="ftp://x"), good_doc(id="doc_two", sha256="nope"))
    p = tmp_path / "s.yaml"
    p.write_text(yaml.safe_dump(bad))
    with pytest.raises(SourcesError) as exc:
        load_validated(p)
    assert "doc_one" in str(exc.value) and "doc_two" in str(exc.value)


# --- SSRF allow-list (CC-45) -------------------------------------------------------------------------
@pytest.mark.security
@pytest.mark.parametrize(
    "url",
    [
        "https://example.org.evil.com/a.pdf",
        "https://evil-example.org/a.pdf",
        "https://sub.example.org/a.pdf",  # exact host only, no suffix matching
        "http://127.0.0.1/a.pdf",
        "http://169.254.169.254/latest/meta-data",
        "https://example.org@evil.com/a.pdf",
        "https://user:pw@example.org/a.pdf",
        "file:///etc/passwd",
        "gopher://example.org/",
        "",
    ],
)
def test_ingestion_blocks_everything_not_listed(url):
    assert not is_ingestion_url_allowed(url, data_of(good_doc()))


@pytest.mark.security
def test_ingestion_allows_exact_listed_host_case_insensitively():
    d = data_of(good_doc())
    assert is_ingestion_url_allowed("https://EXAMPLE.org/other.pdf", d)
    assert is_ingestion_url_allowed("http://example.org/other.pdf", d)


def test_validate_does_not_mutate_input():
    d = data_of(good_doc())
    snapshot = copy.deepcopy(d)
    validate(d)
    assert d == snapshot
