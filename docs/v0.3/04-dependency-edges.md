# 04 — Dependency Edges

v0.3 splits the v0.2 single `uses` list into two distinct edge layers
and gives each edge structured metadata.

## The two layers

### Layer 1 — Proof edges (`Proof.uses`)

These edges form the derivation graph. They live on **proof nodes** and
say "this proof relies on these statements". They are the basis for:

- Acyclicity checks.
- Dependency-depth queries.
- Foundation-tracing ("which axioms does this theorem depend on?").

### Layer 2 — Concept edges (`Statement.depends_on`)

These edges form the *concept graph*. They live on **statement nodes**
(typically definitions) and say "this concept is built on / specializes
/ lives in these other concepts". They are NOT proof edges. They do
NOT participate in `Statement → Proof → Statement` derivations.

This separation directly addresses audit issue 4.1: in v0.2 every
definition is a graph root because definitions cannot depend on
anything. v0.3 lets `definition.compact-set` declare a concept
dependency on `definition.open-cover` without violating the proof
discipline.

## Edge metadata — `ProofDependency`

```yaml
uses:
  - id: definition.supremum
    role: notation        # essential | background | notation | existence
                          # | definition | lemma_local | implicit
    confidence: high
    implicit: false
    locality: forward     # optional: name of a part / direction / case
    notes: used to denote sup E without invoking existence
```

### Role vocabulary

| Role          | Meaning                                                      |
|---------------|--------------------------------------------------------------|
| `essential`   | The proof would fail without this statement.                 |
| `background`  | Provides context but the proof can be reframed without it.   |
| `notation`    | Provides only symbols / vocabulary, not a math fact.         |
| `existence`   | Supplies an existence / completeness principle.              |
| `definition`  | Supplies a definitional unfolding.                           |
| `lemma_local` | Used only in one part / case of the proof.                   |
| `implicit`    | Implicitly imported (foundational, conventional).            |

This vocabulary lets the graph distinguish e.g.
`definition.supremum` used as `notation` from `definition.supremum`
used as `existence` — directly resolving audit issue 1.2.

### `implicit: true`

Marks an edge that the extractor inferred but the source did not state.
Used for conventional foundational imports (e.g., the field axioms
behind a real-arithmetic step). Implicit edges should always carry a
note explaining why they are implicit.

### `locality`

A free-form name matching a `ProofPart.name` (or any sub-claim label).
Edges without `locality` are global to the proof.

## Edge metadata — `ConceptDependency`

```yaml
depends_on:
  - id: definition.metric-space
    role: ambient          # specializes | uses_concept | extends | instance_of | ambient
    confidence: high
    notes: continuity is defined inside a metric space
```

### Role vocabulary

| Role           | Meaning                                                                |
|----------------|------------------------------------------------------------------------|
| `specializes`  | This concept is a special case of the referenced concept.              |
| `uses_concept` | References the concept in its own definition.                          |
| `extends`      | Extends or enriches the referenced concept.                            |
| `instance_of`  | An instance of an abstract structure (e.g., R as instance of field).   |
| `ambient`      | Operates inside the referenced ambient structure.                      |

## Generality edges (`Statement.generality`)

Records when one statement is a general/specialized form of another:

```yaml
generality:
  - target: theorem.continuous-image-compact
    relation: special_case_of
```

`relation` is one of: `equivalent`, `stronger_than`, `weaker_than`,
`special_case_of`, `incomparable`, `overlapping`.

Generality edges do not enter the derivation graph. They support
disambiguation when multiple sources state related-but-not-equal forms
(audit issue 1.3).

## What about packed (bundled) definitions?

v0.3 does not split bundled v0.2 definitions automatically. The audit
(issue 2.1) recommends splitting nodes such as
`definition.neighborhood-limit-point-open-closed`. v0.3 enables this
in two ways:

1. The full rerun re-extracts, with extractors instructed to keep
   atomic concepts atomic.
2. `Statement.depends_on` lets a new atomic concept declare itself a
   `specializes` of the legacy bundled node when needed for backward
   reference.

## Validator behavior

- All `uses[*].id` and `depends_on[*].id` must reference an existing
  statement (L2 references).
- A proof with empty `uses` and empty `parts` whose target is not a
  definition or axiom triggers a warning (L6).
- `implicit: true` edges are not penalized but should be reviewed
  during audit.
