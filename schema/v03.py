"""MKG v0.3 — semantically hardened Pydantic models.

This module defines the v0.3 schema for statements and proofs. It is a clean
redesign, NOT a backward-compatible extension of `schema/models.py` (v0.2).
v0.2 remains in place exclusively to read the frozen prototype baseline
under `generated/snapshots/v0.2/`. All new extraction MUST use v0.3.

Design principles
-----------------
- Single source of truth: YAML files under `data/`, validated by these models.
- Human/LLM/git-friendly: flat keys, explicit nesting, no magic.
- Decomposed quality metadata (no overloaded `confidence`).
- Structured dependency edges with role, locality, and confidence.
- Definitional vs proof dependencies kept distinct.
- i18n with originality + translation provenance.
- LaTeX lifecycle (present | missing | not_applicable | informal | needs_review).
- Lightweight ontology + ambient/domain tags for retrieval and navigation.
- Status lifecycle (extracted → reviewed → validated → audited → stable → canonical).
- Rerun provenance (which extraction pass produced this entity).

The model is intentionally permissive at the leaves (notes, free-form keywords)
and strict at the structural joints (IDs, references, types).
"""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Literal

import yaml

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
    model_validator,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCHEMA_VERSION = "0.3.1"
SUPPORTED_SCHEMA_VERSIONS: tuple[str, ...] = ("0.3.0", "0.3.1")

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

ID_PATTERN = re.compile(
    r"^(?:axiom|definition|lemma|proposition|theorem|corollary|conjecture|proof)"
    r"(?:\.[a-z0-9][a-z0-9-]*)+$"
)

LangCode = Annotated[str, StringConstraints(pattern=r"^[a-z]{2}(-[A-Z]{2})?$")]
NonEmptyStr = Annotated[str, StringConstraints(min_length=1, strip_whitespace=True)]

StatementType = Literal[
    "axiom", "definition", "lemma", "proposition", "theorem", "corollary", "conjecture"
]

# ---- Lifecycle ------------------------------------------------------------

# Status lifecycle (linear, monotonic):
#   extracted  -- raw output of an extraction pass
#   reviewed   -- a human or audit pass has touched it
#   validated  -- passes structural validation + dependency completeness checks
#   audited    -- mathematically audited at content level
#   stable     -- audited + integrated into a release snapshot
#   canonical  -- the project's blessed formulation; rarely rewritten
Status = Literal["extracted", "reviewed", "validated", "audited", "stable", "canonical"]

# Generic confidence levels, used in many places.
Confidence = Literal["low", "medium", "high"]

# LaTeX lifecycle.
LatexStatus = Literal[
    "present",          # complete LaTeX provided
    "informal",         # informal / partially-symbolic placeholder
    "needs_review",     # present but flagged for math review
    "missing",          # ought to be present but isn't yet
    "not_applicable",   # statement is purely conceptual, no formal expression needed
]

ReviewStatus = Literal["unreviewed", "reviewed", "approved", "rejected"]

# How a translation was produced.
TranslationOrigin = Literal["original", "human", "llm", "imported"]

# Roles a statement can play in a proof's dependency edge.
DependencyRole = Literal[
    "essential",     # the proof would fail without this
    "background",    # supplies context but the proof can be reframed without it
    "notation",      # provides only symbols / vocabulary
    "existence",     # supplies an existence/completeness principle
    "definition",    # supplies a definitional unfolding
    "lemma_local",   # used in only one direction/case of the proof
    "implicit",      # implicitly imported (foundational / conventional)
]

# Roles for definitional / conceptual dependencies (depends_on).
ConceptDependencyRole = Literal[
    "specializes",       # this concept is a special case of the referenced one
    "uses_concept",      # references the concept in its own definition
    "extends",           # extends or enriches the referenced concept
    "instance_of",       # instance of an abstract structure
    "ambient",           # operates inside the referenced ambient structure
]

# Generality relations between statement nodes (recorded explicitly when known).
GeneralityRelation = Literal[
    "equivalent",
    "stronger_than",
    "weaker_than",
    "special_case_of",
    "incomparable",
    "overlapping",
    # v0.3.1 additions — disambiguate cases previously overloaded onto
    # `incomparable`. See pilot audit F2.
    "sibling",       # parallel concepts at the same level (e.g. even/odd, h-shift/v-shift)
    "disjoint",      # mutually exclusive by construction (e.g. algebraic vs transcendental)
]

# Semantic kind for ontology tagging.
SemanticKind = Literal[
    "object",        # introduces a mathematical object
    "property",      # asserts a property of an object
    "relation",      # defines a relation
    "operator",      # defines an operation/operator
    "construction",  # builds something from prior data
    "criterion",     # gives a test/equivalence
    "schema",        # parameterized family of statements
    "principle",     # foundational principle / axiom-like
    # v0.3.1 additions — pedagogical scaffolding in textbook sources.
    # See pilot audit F1.
    "notation",      # introduces notation / naming convention only
    "pedagogical",   # didactic device, not a mathematical object per se
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Sources (richer than v0.2)
# ---------------------------------------------------------------------------


class Source(BaseModel):
    """Bibliographic locator. v0.3 splits section-level from theorem-level locators."""

    model_config = ConfigDict(extra="forbid")

    work: NonEmptyStr
    author: str | None = None
    edition: str | None = None
    year: int | None = None
    chapter: str | None = None
    section: str | None = None
    # Theorem-level locator (e.g., "Theorem 4.23", "Definition 6.1"). Distinct from `section`.
    theorem_label: str | None = None
    page: str | None = None
    locator: str | None = None       # free-form additional locator
    url: str | None = None
    source_language: LangCode | None = None  # the language of THIS source
    notes: str | None = None


# ---------------------------------------------------------------------------
# i18n with originality + translation provenance
# ---------------------------------------------------------------------------


class TranslatedText(BaseModel):
    """A single piece of human-readable text in one language with provenance."""

    model_config = ConfigDict(extra="forbid")

    text: NonEmptyStr
    is_original: bool = False
    origin: TranslationOrigin = "human"
    generated_by: str | None = None       # free-form: 'llm:claude-opus-4.7', 'human:alice'
    review_status: ReviewStatus = "unreviewed"
    notes: str | None = None


# A multilingual block. Exactly one entry must be marked `is_original: true`.
MultilingualBlock = dict[LangCode, TranslatedText]


def _validate_multilingual(value: MultilingualBlock, *, field: str) -> MultilingualBlock:
    if not value:
        raise ValueError(f"{field}: at least one language entry is required")
    originals = [lang for lang, t in value.items() if t.is_original]
    if len(originals) == 0:
        raise ValueError(
            f"{field}: exactly one language entry must have is_original: true"
        )
    if len(originals) > 1:
        raise ValueError(
            f"{field}: only one language entry may be is_original: true "
            f"(found {originals!r})"
        )
    return value


# ---------------------------------------------------------------------------
# LaTeX with lifecycle
# ---------------------------------------------------------------------------


class LatexBlock(BaseModel):
    model_config = ConfigDict(extra="forbid")

    body: str | None = None
    status: LatexStatus = "missing"
    review_status: ReviewStatus = "unreviewed"
    notes: str | None = None

    @model_validator(mode="after")
    def _consistency(self) -> LatexBlock:
        if self.status == "present" and not (self.body and self.body.strip()):
            raise ValueError("latex.status='present' requires a non-empty body")
        if self.status == "not_applicable" and self.body:
            raise ValueError("latex.status='not_applicable' requires no body")
        return self


# ---------------------------------------------------------------------------
# Quality metadata (decomposed)
# ---------------------------------------------------------------------------


class QualityBlock(BaseModel):
    """Decomposed quality metadata. Each axis is independently meaningful.

    - extraction_confidence: the LLM/human extractor's confidence in the parse.
    - dependency_confidence: confidence that `uses` / `depends_on` is COMPLETE.
    - semantic_confidence:   confidence that the formulation is mathematically faithful.
    - translation_confidence: confidence in non-original-language translations.
    - latex_confidence:      confidence in the formal LaTeX representation.
    - source_alignment_confidence: confidence the entity matches the cited source.
    """

    model_config = ConfigDict(extra="forbid")

    extraction_confidence: Confidence | None = None
    dependency_confidence: Confidence | None = None
    semantic_confidence: Confidence | None = None
    translation_confidence: Confidence | None = None
    latex_confidence: Confidence | None = None
    source_alignment_confidence: Confidence | None = None
    notes: str | None = None


# ---------------------------------------------------------------------------
# Domains, ambient context, ontology
# ---------------------------------------------------------------------------


class DomainsBlock(BaseModel):
    """Mathematical branch tagging. Free-form to remain practical.

    `primary` should contain the principal area; `secondary` may list bridges.
    Suggested vocabulary (not enforced): real-analysis, complex-analysis,
    topology, metric-spaces, set-theory, linear-algebra, abstract-algebra,
    number-theory, category-theory, mathematical-logic, geometry, etc.
    """

    model_config = ConfigDict(extra="forbid")

    primary: list[NonEmptyStr] = Field(default_factory=list)
    secondary: list[NonEmptyStr] = Field(default_factory=list)


class AmbientBlock(BaseModel):
    """Ambient mathematical / logical context.

    Used to disambiguate identically-named results in different contexts.
    Suggested vocabulary (not enforced): metric-space, topological-space,
    complete-ordered-field, ordered-field, normed-vector-space,
    classical-first-order-logic, intuitionistic-logic, ZFC, manifold,
    smooth-manifold, category, abelian-category, etc.
    """

    model_config = ConfigDict(extra="forbid")

    structures: list[NonEmptyStr] = Field(default_factory=list)
    logic: NonEmptyStr | None = None
    foundations: NonEmptyStr | None = None
    notes: str | None = None


class OntologyBlock(BaseModel):
    """Lightweight semantic typing for retrieval and clustering."""

    model_config = ConfigDict(extra="forbid")

    semantic_kind: list[SemanticKind] = Field(default_factory=list)
    keywords: list[NonEmptyStr] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Rerun provenance
# ---------------------------------------------------------------------------


class ProvenanceBlock(BaseModel):
    """Records which extraction pass produced or last touched this entity."""

    model_config = ConfigDict(extra="forbid")

    schema_version: NonEmptyStr = SCHEMA_VERSION
    rerun_id: str | None = None              # e.g., 'v0.3-2026-06-01'
    extracted_by: str | None = None          # 'llm:claude-opus-4.7', 'human:alice'
    extracted_at: str | None = None          # ISO-8601 date
    derived_from: list[NonEmptyStr] = Field(default_factory=list)  # prior IDs (split/merge tracking)
    redirected_to: NonEmptyStr | None = None    # if this id was retired in favor of another
    rerun_notes: str | None = None


# ---------------------------------------------------------------------------
# Generality relations (between statement nodes)
# ---------------------------------------------------------------------------


class GeneralityEdge(BaseModel):
    """Records a generality / specialization relationship to another statement."""

    model_config = ConfigDict(extra="forbid")

    target: NonEmptyStr
    relation: GeneralityRelation
    notes: str | None = None

    @field_validator("target")
    @classmethod
    def _is_statement(cls, v: str) -> str:
        prefix = v.split(".", 1)[0]
        if prefix not in STATEMENT_TYPES:
            raise ValueError(f"generality.target {v!r} must reference a statement")
        return v


# ---------------------------------------------------------------------------
# Definitional / conceptual dependencies (statements only)
# ---------------------------------------------------------------------------


class ConceptDependency(BaseModel):
    """A conceptual dependency edge between statements (NOT a proof edge).

    Use for: definition uses another concept; theorem operates inside an
    ambient structure recorded elsewhere; statement specializes another.

    These edges DO NOT participate in the Statement -> Proof -> Statement
    derivation graph. They form a separate `concept` graph layer used for
    navigation, retrieval, and ambient-context analysis.
    """

    model_config = ConfigDict(extra="forbid")

    id: NonEmptyStr
    role: ConceptDependencyRole = "uses_concept"
    confidence: Confidence | None = None
    notes: str | None = None

    @field_validator("id")
    @classmethod
    def _is_statement(cls, v: str) -> str:
        prefix = v.split(".", 1)[0]
        if prefix not in STATEMENT_TYPES:
            raise ValueError(f"depends_on.id {v!r} must reference a statement")
        return v


# ---------------------------------------------------------------------------
# Proof-edge dependencies (richer than v0.2)
# ---------------------------------------------------------------------------


class ProofDependency(BaseModel):
    """A dependency edge from a proof to a statement it relies on.

    Replaces the v0.2 flat string list. Each edge carries:
      - id:           the statement this proof uses
      - role:         what kind of usage (essential, notation, existence, ...)
      - confidence:   how confident we are this edge belongs here
      - implicit:     true if this edge was inferred / convention (not stated by author)
      - locality:     optional name of the proof part/case where this is used
      - notes:        free-form
    """

    model_config = ConfigDict(extra="forbid")

    id: NonEmptyStr
    role: DependencyRole = "essential"
    confidence: Confidence = "high"
    implicit: bool = False
    locality: str | None = None
    notes: str | None = None

    @field_validator("id")
    @classmethod
    def _is_statement(cls, v: str) -> str:
        if v.startswith("proof."):
            raise ValueError(f"uses entry {v!r} must reference a statement, not a proof")
        prefix = v.split(".", 1)[0]
        if prefix not in STATEMENT_TYPES:
            raise ValueError(f"uses entry {v!r} must reference a statement type")
        return v


# ---------------------------------------------------------------------------
# Proof internal structure (optional, lightweight)
# ---------------------------------------------------------------------------


class ProofPart(BaseModel):
    """An optional sub-section of a proof (a direction, a case, a sub-claim).

    Allows localizing dependencies. v0.3 does NOT introduce a formal proof
    AST; this is purely an annotation layer.
    """

    model_config = ConfigDict(extra="forbid")

    name: NonEmptyStr
    kind: Literal["direction", "case", "subclaim", "construction", "reduction"] = "subclaim"
    description: str | None = None
    uses: list[ProofDependency] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Statement
# ---------------------------------------------------------------------------


class StatementBody(BaseModel):
    model_config = ConfigDict(extra="forbid")

    natural: MultilingualBlock = Field(default_factory=dict)
    latex: LatexBlock = Field(default_factory=LatexBlock)

    @field_validator("natural")
    @classmethod
    def _natural_ok(cls, v: MultilingualBlock) -> MultilingualBlock:
        return _validate_multilingual(v, field="statement.natural")


class LanguageBlock(BaseModel):
    """Top-level language metadata for the entity."""

    model_config = ConfigDict(extra="forbid")

    original: LangCode
    available: list[LangCode] = Field(default_factory=list)


class Statement(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["0.3.0", "0.3.1"] = SCHEMA_VERSION
    id: NonEmptyStr
    type: StatementType
    status: Status = "extracted"

    language: LanguageBlock
    title: MultilingualBlock
    statement: StatementBody

    # Proof linkage (the only direct statement<->proof edges)
    proved_by: list[NonEmptyStr] = Field(default_factory=list)

    # Conceptual / definitional dependencies (NOT proof edges)
    depends_on: list[ConceptDependency] = Field(default_factory=list)

    # Sources
    sources: list[Source] = Field(default_factory=list)

    # Semantic / retrieval metadata
    domains: DomainsBlock = Field(default_factory=DomainsBlock)
    ambient: AmbientBlock = Field(default_factory=AmbientBlock)
    ontology: OntologyBlock = Field(default_factory=OntologyBlock)

    # Cross-statement generality relations (not proof edges)
    generality: list[GeneralityEdge] = Field(default_factory=list)

    # Quality + provenance
    quality: QualityBlock = Field(default_factory=QualityBlock)
    provenance: ProvenanceBlock = Field(default_factory=ProvenanceBlock)

    notes: str | None = None

    @field_validator("title")
    @classmethod
    def _title_ok(cls, v: MultilingualBlock) -> MultilingualBlock:
        return _validate_multilingual(v, field="title")

    @field_validator("proved_by")
    @classmethod
    def _proof_refs(cls, v: list[str]) -> list[str]:
        for ref in v:
            if not ref.startswith("proof."):
                raise ValueError(f"proved_by entry {ref!r} must start with 'proof.'")
        return v

    @model_validator(mode="after")
    def _check(self) -> Statement:
        _validate_id(self.id, self.type)
        # original language must appear in the multilingual blocks
        original = self.language.original
        for blk_name, blk in (("title", self.title), ("statement.natural", self.statement.natural)):
            if original not in blk:
                raise ValueError(
                    f"{blk_name}: missing entry for declared original language {original!r}"
                )
            if not blk[original].is_original:
                raise ValueError(
                    f"{blk_name}: entry for {original!r} must have is_original: true"
                )
        return self


# ---------------------------------------------------------------------------
# Proof
# ---------------------------------------------------------------------------


class Proof(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["0.3.0", "0.3.1"] = SCHEMA_VERSION
    id: NonEmptyStr
    type: Literal["proof"] = "proof"
    status: Status = "extracted"

    proves: NonEmptyStr
    style: str | None = None  # direct | contradiction | induction | construction | computational | ...

    uses: list[ProofDependency] = Field(default_factory=list)
    parts: list[ProofPart] = Field(default_factory=list)

    sources: list[Source] = Field(default_factory=list)

    # Optional human/LLM proof sketch — stored as multilingual text.
    sketch: MultilingualBlock | None = None

    quality: QualityBlock = Field(default_factory=QualityBlock)
    provenance: ProvenanceBlock = Field(default_factory=ProvenanceBlock)

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

    @field_validator("sketch")
    @classmethod
    def _sketch_ok(cls, v: MultilingualBlock | None) -> MultilingualBlock | None:
        if v is None:
            return v
        return _validate_multilingual(v, field="sketch")

    @model_validator(mode="after")
    def _check(self) -> Proof:
        _validate_id(self.id, "proof")
        # if `parts` are used, top-level `uses` is allowed but should be empty or
        # reflect the union — we do not enforce, but emit no error here.
        return self


# ---------------------------------------------------------------------------
# JSON Schema export helpers
# ---------------------------------------------------------------------------


def statement_json_schema() -> dict:
    return Statement.model_json_schema()


def proof_json_schema() -> dict:
    return Proof.model_json_schema()


# ---------------------------------------------------------------------------
# Source registry (v0.3.1+)
# ---------------------------------------------------------------------------

SOURCES_REGISTRY_PATH = Path(__file__).resolve().parent / "v03" / "sources.yml"


@lru_cache(maxsize=1)
def load_source_registry() -> dict[str, dict]:
    """Load `schema/v03/sources.yml` and return a `{key: entry}` mapping.

    Each entry is the raw dict from the YAML (with `key`, `work`, `author`,
    optional `edition`, `language`, `isbn`, `notes`). Cached for the process
    lifetime.
    """
    if not SOURCES_REGISTRY_PATH.exists():
        return {}
    with SOURCES_REGISTRY_PATH.open("r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh) or {}
    out: dict[str, dict] = {}
    for entry in raw.get("sources", []):
        key = entry.get("key")
        if not key:
            continue
        out[key] = entry
    return out


def known_source_works() -> set[str]:
    """Return the set of canonical `work` titles from the registry."""
    return {e["work"] for e in load_source_registry().values() if e.get("work")}


def source_key_for_work(work: str) -> str | None:
    """Reverse-lookup: canonical work title → registry key."""
    for key, entry in load_source_registry().items():
        if entry.get("work") == work:
            return key
    return None
