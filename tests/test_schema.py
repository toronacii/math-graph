import pytest
from pydantic import ValidationError

from schema.models import Proof, Statement


def _valid_statement_kwargs() -> dict:
    return {
        "id": "definition.function",
        "type": "definition",
        "title": {"en": "Function", "es": "Función"},
        "statement": {
            "natural": {"es": "Una función asigna a cada entrada un único valor."},
        },
    }


def _valid_proof_kwargs() -> dict:
    return {
        "id": "proof.theorem-foo.direct",
        "proves": "theorem.foo",
        "uses": ["definition.function"],
    }


def test_statement_minimal_ok():
    Statement(**_valid_statement_kwargs())


def test_statement_id_prefix_must_match_type():
    kw = _valid_statement_kwargs()
    kw["id"] = "theorem.function"  # mismatch
    with pytest.raises(ValidationError):
        Statement(**kw)


def test_statement_id_must_be_lowercase_dotted():
    kw = _valid_statement_kwargs()
    kw["id"] = "Definition.Function"
    with pytest.raises(ValidationError):
        Statement(**kw)


def test_statement_title_requires_at_least_one_language():
    kw = _valid_statement_kwargs()
    kw["title"] = {}
    with pytest.raises(ValidationError):
        Statement(**kw)


def test_statement_natural_requires_non_empty_text():
    kw = _valid_statement_kwargs()
    kw["statement"] = {"natural": {"es": "   "}}
    with pytest.raises(ValidationError):
        Statement(**kw)


def test_statement_proved_by_must_be_proof_ids():
    kw = _valid_statement_kwargs()
    kw["proved_by"] = ["theorem.bar"]
    with pytest.raises(ValidationError):
        Statement(**kw)


def test_statement_extra_keys_forbidden():
    kw = _valid_statement_kwargs()
    kw["unknown_key"] = "x"
    with pytest.raises(ValidationError):
        Statement(**kw)


def test_proof_minimal_ok():
    Proof(**_valid_proof_kwargs())


def test_proof_id_must_have_proof_prefix():
    kw = _valid_proof_kwargs()
    kw["id"] = "theorem.foo.direct"
    with pytest.raises(ValidationError):
        Proof(**kw)


def test_proof_proves_must_be_statement_id():
    kw = _valid_proof_kwargs()
    kw["proves"] = "proof.theorem-foo.direct"
    with pytest.raises(ValidationError):
        Proof(**kw)


def test_proof_uses_must_be_statement_ids():
    kw = _valid_proof_kwargs()
    kw["uses"] = ["proof.something.x"]
    with pytest.raises(ValidationError):
        Proof(**kw)
