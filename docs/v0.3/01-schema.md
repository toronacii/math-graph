# 01 — Schema Specification (v0.3.1)

The authoritative implementation lives in [`schema/v03.py`](../../schema/v03.py).
This document is the specification it implements.

> **Version note (v0.3.1, 2026-05-11).** v0.3.1 is an *additive* enum
> extension over v0.3.0: `SemanticKind` adds `notation`, `pedagogical`;
> `GeneralityRelation` adds `sibling`, `disjoint`. The loader accepts both
> `schema_version: "0.3.0"` and `"0.3.1"` (`SUPPORTED_SCHEMA_VERSIONS`),
> so existing pilot files do not need to be rewritten. **New files SHOULD
> declare `schema_version: "0.3.1"`.**

## Top-level shape

Every entity (statement or proof) is a YAML mapping that MUST declare:

```yaml
schema_version: "0.3.1"
id: <type>.<normalized-name>
type: <statement-type | proof>
status: <lifecycle-status>
```

Files without a `schema_version` in `SUPPORTED_SCHEMA_VERSIONS`
(`{"0.3.0", "0.3.1"}`) are ignored by the v0.3 loader and treated as
legacy.

## ID rules

- Lowercase ASCII, dot-separated segments, hyphens within segments.
- Pattern: `^(axiom|definition|lemma|...|proof)(\.[a-z0-9][a-z0-9-]*)+$`.
- Statement ID prefix MUST equal `type`.
- Proof ID prefix MUST be `proof`.
- Recommended proof form: `proof.<statement-name>.<source-or-style>`.

## Statement entity

```
Statement
├─ schema_version: "0.3.1"
├─ id, type, status
├─ language: { original: LangCode, available: [LangCode] }
├─ title:     MultilingualBlock              (required)
├─ statement: { natural: MultilingualBlock,  (required)
│               latex:   LatexBlock          (required, default missing) }
├─ proved_by: [proof IDs]
├─ depends_on: [ConceptDependency]           (NEW: definitional / conceptual edges)
├─ sources:   [Source]
├─ domains:   { primary: [str], secondary: [str] }       (NEW)
├─ ambient:   { structures: [str], logic, foundations }  (NEW)
├─ ontology:  { semantic_kind: [str], keywords: [str] }  (NEW)
├─ generality: [GeneralityEdge]              (NEW: cross-statement specialization)
├─ quality:   QualityBlock                   (NEW: decomposed confidence)
├─ provenance: ProvenanceBlock               (NEW: rerun + derived-from)
└─ notes:     str
```

Invariants enforced by the validator:

1. `language.original` must appear in both `title` and `statement.natural`.
2. The original-language entry in `title` and `statement.natural` must
   have `is_original: true`. Exactly one entry per multilingual block may
   carry that flag.
3. ID prefix matches `type`.
4. Every `proved_by` ID begins with `proof.`.
5. `depends_on[*].id` and `generality[*].target` reference statement
   types only.

## Proof entity

```
Proof
├─ schema_version: "0.3.1"
├─ id, type ("proof"), status
├─ proves:   <statement id>
├─ style:    str (free-form, recommended vocabulary in templates)
├─ uses:     [ProofDependency]               (NEW: structured edges)
├─ parts:    [ProofPart]                     (NEW: optional sub-sections)
├─ sources:  [Source]
├─ sketch:   MultilingualBlock | null        (NEW: optional informal sketch)
├─ quality:  QualityBlock                    (NEW)
├─ provenance: ProvenanceBlock               (NEW)
└─ notes:    str
```

## MultilingualBlock

```
MultilingualBlock = { LangCode: TranslatedText }

TranslatedText:
  text:           non-empty string
  is_original:    bool
  origin:         original | human | llm | imported
  generated_by:   str | null   ("llm:claude-opus-4.7", "human:alice")
  review_status:  unreviewed | reviewed | approved | rejected
  notes:          str | null
```

Exactly one entry per block must have `is_original: true`.

## LatexBlock

```
LatexBlock:
  body:          str | null
  status:        present | informal | needs_review | missing | not_applicable
  review_status: unreviewed | reviewed | approved | rejected
  notes:         str | null
```

Constraints:

- `status: present` requires non-empty `body`.
- `status: not_applicable` requires no `body`.

## ProofDependency (replaces flat `uses` list)

```
ProofDependency:
  id:         <statement id>
  role:       essential | background | notation | existence
              | definition | lemma_local | implicit
  confidence: low | medium | high           (default high)
  implicit:   bool                          (default false)
  locality:   str | null                    (e.g. "forward", "case_3")
  notes:      str | null
```

## ConceptDependency (definitional / conceptual edges, NOT proof edges)

```
ConceptDependency:
  id:         <statement id>
  role:       specializes | uses_concept | extends | instance_of | ambient
  confidence: low | medium | high
  notes:      str | null
```

These edges form a separate **concept layer** of the graph. They are not
part of `Statement → Proof → Statement` derivations. They exist for:

- Navigation ("what concepts does this definition build on?").
- Disambiguation ("two `definition.continuity` nodes — which lives in
  which ambient structure?").
- Bundled-definition unpacking ("this concept specializes that bundled
  definition's `closed-set` part").

## QualityBlock

```
QualityBlock:
  extraction_confidence:        low | medium | high | null
  dependency_confidence:        low | medium | high | null   (is `uses`/`depends_on` complete?)
  semantic_confidence:          low | medium | high | null   (does the formulation faithfully capture the math?)
  translation_confidence:       low | medium | high | null
  latex_confidence:             low | medium | high | null
  source_alignment_confidence:  low | medium | high | null
  notes:                        str | null
```

All axes are independent. The validator does not infer one from another.

## DomainsBlock / AmbientBlock / OntologyBlock

Free-form vocabularies; suggested values appear in
[`06-domains-ambient.md`](06-domains-ambient.md) and
[`07-ontology-tags.md`](07-ontology-tags.md). The validator does not
restrict the values: enforcement happens at audit time.

## ProvenanceBlock

```
ProvenanceBlock:
  schema_version: "0.3.1"
  rerun_id:       str | null     # e.g. "v0.3-2026-06-01"
  extracted_by:   str | null     # "llm:claude-opus-4.7", "human:alice"
  extracted_at:   str | null     # ISO-8601 date
  derived_from:   [str]          # IDs this entity replaces (split / merge tracking)
  redirected_to:  str | null     # if this id is being retired
  rerun_notes:    str | null
```

## Status lifecycle

```
extracted → reviewed → validated → audited → stable → canonical
```

See [`08-status-lifecycle.md`](08-status-lifecycle.md) for promotion rules
and what each status guarantees.

## What is NOT in the schema

- No proof AST.
- No formal logical context (beyond a string `ambient.logic`).
- No machine-checkable mathematical assertions.
- No cross-entity computed fields. Everything derived (centrality, hub
  metrics, component counts) belongs in reports, not in the YAML.
