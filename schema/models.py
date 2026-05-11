"""Pydantic models and validators for MKG entities (statements and proofs).

Schema rules (see AGENTS.md and CONTRIBUTING.md):

- All schema keys are English.
- Human-readable text is i18n: a mapping ``{lang_code: text}``.
- IDs follow ``<type>.<normalized-name>``; the prefix MUST match ``type``.
- Statements never reference each other directly; the link is always
  ``statement -> proof -> statement``.
"""

from __future__ import annotations

import re
from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
    model_validator,
)

# ---------------------------------------------------------------------------
# Shared primitives
# ---------------------------------------------------------------------------

STATEMENT_TYPES = (
    "axiom",
    "definition",
    "lemma",
    "proposition",
    "theorem",
    "corollary",
    "conjecture",
)

ALL_TYPES = (*STATEMENT_TYPES, "proof")

# id ::= <type>.<segment>(.<segment>)*
ID_PATTERN = re.compile(
    r"^(?:axiom|definition|lemma|proposition|theorem|corollary|conjecture|proof)"
    r"(?:\.[a-z0-9][a-z0-9-]*)+$"
)

LangCode = Annotated[str, StringConstraints(pattern=r"^[a-z]{2}(-[A-Z]{2})?$")]
NonEmptyStr = Annotated[str, StringConstraints(min_length=1, strip_whitespace=True)]

# Limited primitives, no schema extensibility for now.
StatementType = Literal[
    "axiom", "definition", "lemma", "proposition", "theorem", "corollary", "conjecture"
]
Status = Literal["draft", "reviewed", "published"]
Confidence = Literal["low", "medium", "high"]


def _validate_id(value: str, expected_type: str) -> str:
    if not ID_PATTERN.match(value):
        raise ValueError(
            f"invalid id {value!r}: must match <type>.<normalized-name> with "
            "lowercase ASCII segments separated by dots"
        )
    prefix = value.split(".", 1)[0]
    if prefix != expected_type:
        raise ValueError(
            f"id prefix {prefix!r} does not match declared type {expected_type!r}"
        )
    return value


def _i18n_non_empty(value: dict[str, str]) -> dict[str, str]:
    if not value:
        raise ValueError("at least one language entry is required")
    for lang, text in value.items():
        if not text or not text.strip():
            raise ValueError(f"language {lang!r} has empty text")
    return value


# ---------------------------------------------------------------------------
# Sources
# ---------------------------------------------------------------------------


class Source(BaseModel):
    """Bibliographic locator for a statement or proof."""

    model_config = ConfigDict(extra="forbid")

    work: NonEmptyStr
    author: str | None = None
    edition: str | None = None
    chapter: str | None = None
    section: str | None = None
    page: str | None = None
    locator: str | None = None
    url: str | None = None


# ---------------------------------------------------------------------------
# Statement
# ---------------------------------------------------------------------------


class StatementBody(BaseModel):
    model_config = ConfigDict(extra="forbid")

    natural: dict[LangCode, NonEmptyStr] = Field(default_factory=dict)
    latex: str | None = None

    @field_validator("natural")
    @classmethod
    def _natural_non_empty(cls, v: dict[str, str]) -> dict[str, str]:
        return _i18n_non_empty(v)


class Statement(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: NonEmptyStr
    type: StatementType
    status: Status = "draft"

    title: dict[LangCode, NonEmptyStr]
    statement: StatementBody

    proved_by: list[NonEmptyStr] = Field(default_factory=list)
    sources: list[Source] = Field(default_factory=list)

    confidence: Confidence | None = None
    notes: str | None = None

    @field_validator("title")
    @classmethod
    def _title_non_empty(cls, v: dict[str, str]) -> dict[str, str]:
        return _i18n_non_empty(v)

    @field_validator("proved_by")
    @classmethod
    def _proof_refs(cls, v: list[str]) -> list[str]:
        for ref in v:
            if not ref.startswith("proof."):
                raise ValueError(f"proved_by entry {ref!r} must start with 'proof.'")
        return v

    @model_validator(mode="after")
    def _check_id(self) -> Statement:
        _validate_id(self.id, self.type)
        return self


# ---------------------------------------------------------------------------
# Proof
# ---------------------------------------------------------------------------


class Proof(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: NonEmptyStr
    type: Literal["proof"] = "proof"
    status: Status = "draft"

    proves: NonEmptyStr
    uses: list[NonEmptyStr] = Field(default_factory=list)

    style: str | None = None
    sources: list[Source] = Field(default_factory=list)

    confidence: Confidence | None = None
    notes: str | None = None

    @field_validator("proves")
    @classmethod
    def _proves_is_statement(cls, v: str) -> str:
        if v.startswith("proof."):
            raise ValueError(f"proves={v!r} must reference a statement, not a proof")
        prefix = v.split(".", 1)[0]
        if prefix not in STATEMENT_TYPES:
            raise ValueError(f"proves={v!r} must reference a statement type")
        return v

    @field_validator("uses")
    @classmethod
    def _uses_are_statements(cls, v: list[str]) -> list[str]:
        for ref in v:
            if ref.startswith("proof."):
                raise ValueError(f"uses entry {ref!r} must reference a statement, not a proof")
            prefix = ref.split(".", 1)[0]
            if prefix not in STATEMENT_TYPES:
                raise ValueError(f"uses entry {ref!r} must reference a statement type")
        return v

    @model_validator(mode="after")
    def _check_id(self) -> Proof:
        _validate_id(self.id, "proof")
        return self


# ---------------------------------------------------------------------------
# Schema export helpers
# ---------------------------------------------------------------------------


def statement_json_schema() -> dict:
    return Statement.model_json_schema()


def proof_json_schema() -> dict:
    return Proof.model_json_schema()
