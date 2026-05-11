"""Tests for the v0.3 schema (`schema/v03.py`)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from schema.v03 import Proof, Statement


def _stmt_kwargs() -> dict:
    return {
        "schema_version": "0.3.0",
        "id": "definition.function",
        "type": "definition",
        "language": {"original": "en", "available": ["en"]},
        "title": {
            "en": {"text": "Function", "is_original": True, "origin": "original"},
        },
        "statement": {
            "natural": {
                "en": {
                    "text": "A function assigns to each input a unique output.",
                    "is_original": True,
                    "origin": "original",
                },
            },
            "latex": {"status": "not_applicable"},
        },
    }


def _proof_kwargs() -> dict:
    return {
        "schema_version": "0.3.0",
        "id": "proof.theorem-foo.direct",
        "proves": "theorem.foo",
        "uses": [
            {"id": "definition.function", "role": "essential", "confidence": "high"},
        ],
    }


def test_statement_minimal_ok():
    Statement(**_stmt_kwargs())


def test_statement_id_prefix_must_match_type():
    kw = _stmt_kwargs()
    kw["id"] = "theorem.function"
    with pytest.raises(ValidationError):
        Statement(**kw)


def test_statement_requires_original_in_each_block():
    kw = _stmt_kwargs()
    kw["language"]["original"] = "es"  # but title and natural only have 'en'
    with pytest.raises(ValidationError):
        Statement(**kw)


def test_statement_exactly_one_original_per_block():
    kw = _stmt_kwargs()
    kw["title"]["es"] = {"text": "Función", "is_original": True, "origin": "human"}
    with pytest.raises(ValidationError):
        Statement(**kw)


def test_latex_present_requires_body():
    kw = _stmt_kwargs()
    kw["statement"]["latex"] = {"status": "present"}
    with pytest.raises(ValidationError):
        Statement(**kw)


def test_latex_not_applicable_forbids_body():
    kw = _stmt_kwargs()
    kw["statement"]["latex"] = {"status": "not_applicable", "body": "x"}
    with pytest.raises(ValidationError):
        Statement(**kw)


def test_statement_proved_by_must_be_proof_ids():
    kw = _stmt_kwargs()
    kw["proved_by"] = ["theorem.bar"]
    with pytest.raises(ValidationError):
        Statement(**kw)


def test_depends_on_must_be_statement():
    kw = _stmt_kwargs()
    kw["depends_on"] = [{"id": "proof.foo.bar", "role": "uses_concept"}]
    with pytest.raises(ValidationError):
        Statement(**kw)


def test_extra_keys_forbidden():
    kw = _stmt_kwargs()
    kw["unknown_key"] = "x"
    with pytest.raises(ValidationError):
        Statement(**kw)


def test_proof_minimal_ok():
    Proof(**_proof_kwargs())


def test_proof_id_must_have_proof_prefix():
    kw = _proof_kwargs()
    kw["id"] = "theorem.foo.direct"
    with pytest.raises(ValidationError):
        Proof(**kw)


def test_proof_proves_must_be_statement():
    kw = _proof_kwargs()
    kw["proves"] = "proof.something"
    with pytest.raises(ValidationError):
        Proof(**kw)


def test_proof_uses_must_be_statement_ids():
    kw = _proof_kwargs()
    kw["uses"] = [{"id": "proof.something", "role": "essential"}]
    with pytest.raises(ValidationError):
        Proof(**kw)


def test_proof_default_quality_and_provenance():
    p = Proof(**_proof_kwargs())
    assert p.quality.extraction_confidence is None
    assert p.provenance.schema_version == "0.3.1"
    assert p.status == "extracted"


def test_proof_part_localized_uses():
    kw = _proof_kwargs()
    kw["parts"] = [
        {
            "name": "forward",
            "kind": "direction",
            "uses": [
                {"id": "definition.function", "role": "essential", "confidence": "high"},
            ],
        }
    ]
    Proof(**kw)


def test_generality_target_must_be_statement():
    kw = _stmt_kwargs()
    kw["generality"] = [{"target": "proof.foo", "relation": "equivalent"}]
    with pytest.raises(ValidationError):
        Statement(**kw)


def test_translation_provenance_round_trip():
    kw = _stmt_kwargs()
    kw["language"] = {"original": "en", "available": ["en", "es"]}
    kw["title"]["es"] = {
        "text": "Función",
        "is_original": False,
        "origin": "llm",
        "generated_by": "llm:claude-opus-4.7",
        "review_status": "unreviewed",
    }
    s = Statement(**kw)
    assert s.title["es"].origin == "llm"
    assert s.title["en"].is_original is True
