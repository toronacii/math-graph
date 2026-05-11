# 03 — Ontology Vocabulary

> Frozen `OntologyBlock` vocabulary. Two fields:
>
> - `semantic_kind` — the **closed** enum (LiteralType in
>   `schema/v03.py::SemanticKind`). Adding a kind requires a schema
>   change.
> - `keywords` — **open** free-form list. Convention-only.
>
> Anti-bloat principle: this is a **lightweight** ontology. It is NOT a
> formal type system; it MUST NOT grow unbounded; it must remain useful
> to a human reader at a glance.

## A. `semantic_kind` — frozen closed set

The schema currently defines:

```text
object | property | relation | operator | construction | criterion | schema | principle
```

Reaffirmed and documented for the freeze:

| kind            | Meaning                                                | Examples (statement ids)                                  |
|-----------------|--------------------------------------------------------|------------------------------------------------------------|
| `object`        | Names / introduces a mathematical object.              | `definition.metric-space`, `definition.field`, `definition.compact-set` |
| `property`      | Asserts a property predicate of an object.            | `definition.bounded-set`, `definition.dense-set`            |
| `relation`      | Defines a binary (or n-ary) relation between objects. | `definition.subset-relation`, `definition.equinumerous-sets`|
| `operator`      | Defines an operation that produces a new object.      | `definition.union-indexed-family`, `definition.derivative`  |
| `construction`  | Names a construction (specific produced object).      | `definition.power-set`, `definition.metric-completion`      |
| `criterion`     | Gives a test / equivalent characterization.           | `proposition.vertical-line-test`, `theorem.cauchy-criterion`|
| `schema`        | A parameterized family of statements.                 | `axiom.induction-schema`, `axiom.replacement-schema`        |
| `principle`     | A foundational principle / axiom-like assertion.      | `axiom.choice`, `axiom.completeness`, `axiom.well-ordering` |

### When more than one kind applies

- Up to **2 kinds** per node, max. Most nodes have 1.
- If a node "introduces an operator and the operator's defining
  property", pick `operator` only — the property is implicit.
- A definition that names an object AND lists its characteristic
  properties is still `object`. Use `property` only for stand-alone
  property names (e.g., "compact" as an adjective applied to many
  objects → `definition.compact-set` is `object`, not `property`).

### When NO kind applies

- Theorems and propositions almost always have at least one kind:
  `criterion` is the most common. If none fits, use `principle`
  cautiously.
- Lemmas frequently get `criterion` as well; lemmas without an
  obvious kind may leave `semantic_kind` empty.
- Proofs do NOT have a `semantic_kind` (they have `style`).

### Forbidden vocabulary

The following look like `semantic_kind` candidates but are NOT:

| Disallowed | Use instead |
|---|---|
| `space` | This is `object` with `ambient.structures` carrying the structure name. |
| `theorem-schema` | Already covered: use `schema`. |
| `transformation` | This is `operator` (a map) or `construction` (a derived object). |
| `lemma` / `theorem` | These are entity TYPES, not semantic kinds. |
| `axiom` | Use `principle`. |
| `algorithm` | Out of scope for the v0.3 graph. |

### Extension policy

Adding a `semantic_kind` value requires:

1. A schema change in `schema/v03.py` (the `SemanticKind` Literal).
2. A test in `tests/v03/test_schema.py` for the new value.
3. Justification in this document with at least 3 candidate uses.
4. JSON-Schema re-export (`mkg-export-schema`).

The bar is intentionally high. Reviewers should resist the urge to add
a kind to capture a single edge case.

## B. `keywords` — open list, conventions

Free-form lowercase-hyphenated tokens for retrieval. Held loose so the
context-pack can surface "topic-relevant" candidates without committing
to a taxonomy.

### Conventions

1. **Lowercase ASCII**, hyphen-separated, no spaces / no underscores.
2. **Concept names**, not statement names. (`continuity`, NOT
   `continuity-theorem-3-1`.)
3. **Singular** unless intrinsically plural (`infinity`, `series`,
   `derivatives`).
4. **Prefer existing keywords.** Before coining a new one, check the
   active set via the context-pack §"Topic keywords" or
   `SELECT DISTINCT keyword FROM statement_ontology;`.
5. **Avoid statement-id duplication.** If the keyword would be
   identical to a statement id stem (e.g., `compact-set`), use the
   bare concept (`compactness`) instead.
6. **3–10 keywords per node.** Fewer than 3 reduces retrievability;
   more than 10 dilutes signal.
7. **No author / book names** (forbidden, same as domains).

### Initial seed keyword set

Curated from the v0.2 corpus. Reviewers SHOULD reuse these; new
keywords are allowed but should be additive, not redundant.

```
limit             continuity        compactness      connectedness
convergence       cauchy            completeness     metric
neighborhood      open              closed           interior
boundary          dense             perfect          countability
cardinality       monotonicity      boundedness      supremum
infimum           field             ordering         archimedean
sequence          series            absolute-convergence  power-series
derivative        differentiability mean-value       extremum
integral          fundamental-theorem   riemann       uniform-continuity
intermediate-value    extreme-value     squeeze       l-hopital
chain-rule        product-rule      quotient-rule    inverse-function
implicit-function     parametric    polar-coordinates   arc-length
function          mapping           injection        surjection
bijection         image             inverse-image    composition
even-function     odd-function      exponential      logarithm
trigonometric     polynomial        rational         radical
```

### Anti-patterns

- `keywords: [theorem, mathematics]` — too generic, useless.
- `keywords: [stewart, ch1, exercise-7]` — provenance, not semantics.
- `keywords: [important, basic, advanced]` — judgment, not retrieval.

### When to leave `keywords` empty

- For `axiom` and `principle` nodes whose name is itself the search
  term (`axiom.completeness` → keywords add no signal).
- For deeply technical lemmas whose only audience is the proof they
  serve.

## C. Cross-checks against `semantic_kind` and `keywords`

| Symptom | Likely fix |
|---|---|
| Every node in a chapter has the same single keyword | Split it into more specific keywords or remove. |
| A keyword is used by exactly one node | Remove it (replace with a more general existing keyword). |
| A `semantic_kind` is set but contradicts the type | Recheck classification (probably the type is wrong). |
| `semantic_kind: [object, property]` for every node | Reviewer is being too generous; pick one. |
| Keywords are full statement names | Reviewer is duplicating ids; replace with concepts. |
