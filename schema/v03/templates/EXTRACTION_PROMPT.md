# v0.3 Extraction Prompt

> **Audience.** LLM agents (and human extractors) producing v0.3 YAML for the
> Mathematical Knowledge Graph. This document is the system-message-level
> guidance: it consolidates the v0.3 schema rules into actionable extraction
> instructions and references the canonical templates in this directory.
>
> **Templates.**
> - `schema/v03/templates/statement.template.yml`
> - `schema/v03/templates/proof.template.yml`
>
> **Authoritative spec.** `schema/v03.py` + `docs/v0.3/`. If this document
> ever conflicts with them, the spec wins — open a PR fixing this doc.
>
> **Policies (READ FIRST).** The semantic-freeze policies in
> `docs/v0.3/policies/` are binding for every extraction decision. They
> codify what is FROZEN (vocabularies, ID identity, granularity,
> edge-role taxonomy) versus OPEN (extractor judgement). When this
> prompt and a policy conflict, the policy wins.
>
> Minimum reading order before extraction:
> `policies/02-domain-vocabulary.md`,
> `policies/03-ontology-vocabulary.md`,
> `policies/04-edge-role-taxonomy.md`,
> `policies/05-id-equivalence-policy.md`,
> `policies/06-theorem-granularity-policy.md`,
> `policies/07-semantic-freeze.md`.

---

## 0. Context pack — MANDATORY pre-extraction step

Before extracting ANY chapter, you MUST:

1. Generate the context pack:
   ```bash
   uv run mkg-context-pack --source <source-key> --chapter <N>
   ```
2. Read the output file:
   `generated/v0.3/context-packs/<source>-chapter-<NN>.md`

The context pack is a compact summary of the entire graph state
(built from the SQLite DB) relevant to the chapter you are about to
extract. It contains: prior-chapter frontier nodes, source locator
map, domain-relevant neighborhood, multi-source collision candidates,
quality backlog, naming conventions, and canonical template pointers.

**Do NOT extract without loading the context pack.** Extracting
without it leads to:
- duplicate node IDs (re-introducing an existing statement),
- missed `depends_on` / `uses` edges to prior chapters,
- inconsistent domain/ambient/ontology tags,
- naming convention drift.

---

## 1. Core invariants

1. Every file MUST set `schema_version: "0.3.1"` (the loader still accepts `"0.3.0"` for legacy pilot files; new extractions use `"0.3.1"`).
2. Every file's `id` MUST match its file name AND obey
   `<type>.<normalized-name>`. Statement ids start with one of:
   `axiom | definition | lemma | proposition | theorem | corollary | conjecture`.
   Proof ids start with `proof.`.
3. Every Pydantic model has `extra="forbid"`. Unknown keys FAIL validation.
4. Fresh extraction outputs MUST start at `status: extracted`. Validators
   gate promotion to `reviewed | validated | audited | stable | canonical`.
5. The graph remains `Statement → Proof → Statement`. Statements never link
   directly to other statements via proof edges. Conceptual (definition-level)
   links live on `Statement.depends_on` — a SEPARATE layer, not a derivation.

---

## 2. i18n rules

The source material's language is the **original**. Translations get
explicit provenance.

- Top-level `language.original` is the language of the textbook/article.
- `language.available` enumerates every language present in the entity.
- Each multilingual block (`title`, `statement.natural`, `sketch`) is a
  `dict[lang_code, TranslatedText]`.
- **Exactly one** entry per multilingual block has `is_original: true`. That
  entry MUST be in `language.original`.
- `origin` values:
  - `original`  — verbatim from the source (only on the original entry).
  - `human`     — produced by a human translator/editor.
  - `llm`       — produced by an LLM. Set `generated_by`, e.g.
    `"llm:claude-opus-4.7"`.
  - `imported`  — imported from another graph/dataset.
- Preserve the source's wording with minimal cleanup (typos, spurious
  hyphens, broken line wraps). Do NOT paraphrase the original entry.
- Translations may be idiomatic but MUST preserve mathematical content.
- Language codes: BCP-47 short form (`en`, `es`, `fr`, `de`, `en-US`).
  Two-letter lowercase preferred.

See `docs/v0.3/02-i18n.md` for edge cases.

---

## 3. LaTeX lifecycle

`statement.latex.status` is the lifecycle marker:

| status            | requires body? | semantics                                |
|-------------------|----------------|------------------------------------------|
| `present`         | YES, non-empty | canonical LaTeX is provided              |
| `informal`        | optional       | partial / placeholder formula            |
| `needs_review`    | optional       | present but math review pending          |
| `missing`         | NO             | ought to exist but not yet authored      |
| `not_applicable`  | NO (forbidden) | purely conceptual; no formula required   |

Rules:

- Definitions of named objects (e.g., "even function") often use
  `not_applicable`.
- Theorems and propositions SHOULD reach `present`. If unsure, choose
  `informal` and flag for review, not `present` with a fudge.
- The validator rejects `status: present` with empty body, and
  `status: not_applicable` with any body.
- Set `latex_confidence` accordingly:
  - `present` + verified → `latex_confidence: high`
  - `informal` → typically `medium` or `low`
  - `missing` / `not_applicable` → leave `latex_confidence: null`

See `docs/v0.3/03-latex-lifecycle.md`.

---

## 4. Structured `uses` edges (proofs)

`Proof.uses` is a list of structured objects, NOT strings. The v0.2 flat
list is gone.

Each `ProofDependency`:

```yaml
- id: theorem.continuous-image-connected   # MUST be a statement id
  role: essential                           # see role taxonomy below
  confidence: high                          # low | medium | high (required)
  implicit: false                           # true if INFERRED, not cited
  locality: "case-1"                        # optional; usually populated via parts
  notes: "imported by ambient context"      # optional
```

### Role taxonomy

The validator accepts EXACTLY these strings (case-sensitive):

```text
essential | background | notation | existence |
definition | lemma_local | implicit
```

| role          | use when…                                                  |
|---------------|------------------------------------------------------------|
| `essential`   | the proof would fail without this statement (use this for **external** lemmas/propositions/theorems cited as key steps) |
| `background`  | supplies context; proof could be reframed without it       |
| `notation`    | supplies only symbols / vocabulary                         |
| `existence`   | supplies an existence / completeness principle             |
| `definition`  | supplies a definitional unfolding                          |
| `lemma_local` | a lemma INTERNAL to this proof (used in exactly one direction / case — prefer `parts`) |
| `implicit`    | implicitly imported convention (e.g., ZFC, classical logic)|

**Common mistake:** there is no `lemma` role. An external proposition
or theorem cited as a key derivation step uses `essential`.
`lemma_local` is reserved for internal sub-arguments that are NOT
their own statement node.

**Common mistake:** `role: existence` on a **definition** node. A
definition introduces meaning — it does NOT supply existence. When a
proof assumes an object exists (e.g., "let F be an antiderivative of
f"), ask: *what guarantees F exists?* The definition of antiderivative
tells you what F *is*; a theorem (e.g., FTC1, completeness) tells you
F *exists*. Use `role: definition` on the definition node, and add a
separate `uses` edge with `role: existence` to the theorem that
guarantees existence. If the author does not cite the existence source,
mark that edge `implicit: true` with a note explaining the inference.

**Common mistake:** `role: background` on a hypothesis that the proof
**actively uses** in a derivation step. `background` means the proof
could be reframed without this dependency. If removing the statement
would break the argument (e.g., continuity used to take a limit,
compactness used to extract a convergent subsequence), the role is
`essential`, not `background`. Reserve `background` for "see also"
references and framing context.

`role: implicit` is the **mathematical role**.
`implicit: true` is the **provenance flag** (we inferred this edge; the
author did not cite it). They are orthogonal.

### Completeness > confidence

Prefer over-including with `confidence: medium` to under-including with
`confidence: high`. Reviewers can downgrade noise; they cannot recover
missing edges.

### Proof parts

Use `parts[]` only when the proof has cleanly separable sub-arguments
(forward/converse, multiple cases, an explicit construction step).
Each part's `uses` follows the same schema. If you use `parts`, top-level
`uses` may be empty (or contain only the truly shared dependencies).

See `docs/v0.3/04-dependency-edges.md`.

---

## 5. `Statement.depends_on` — the concept layer

`Statement.depends_on` is the second graph layer. It records that a
statement CONCEPTUALLY refers to another statement, without claiming a
derivation.

```yaml
depends_on:
  - id: definition.metric-space
    role: ambient
    confidence: high
  - id: definition.continuity-metric
    role: uses_concept
```

Roles (`ConceptDependencyRole`). Validator accepts EXACTLY these strings:

```text
specializes | uses_concept | extends | instance_of | ambient
```

| role            | use when…                                                   |
|-----------------|-------------------------------------------------------------|
| `specializes`   | this is a special case of the referenced statement          |
| `uses_concept`  | references the concept in its own statement                 |
| `extends`       | extends / enriches the referenced concept                   |
| `instance_of`   | this is an instance of an abstract structure                |
| `ambient`       | operates inside the referenced ambient structure            |

**Common mistake:** there is no `uses` role. Use `uses_concept`.

**Common mistake:** `role: specializes` when the relationship is
actually a **consequence or application**, not a specialization. The
`specializes` role means "this statement IS a special case of the
referenced statement" — i.e., the referenced statement is strictly
more general, and this one restricts the hypotheses. If statement A
is *derived from* or *applies* statement B (e.g., a definite-integral
version of a substitution rule that adds limit transformation rather
than restricting hypotheses), the correct role is `uses_concept`. Use
`specializes` only when A's hypotheses are a strict superset of B's
(more restrictive) and A's conclusion is a strict subset of B's
(narrower).

Use cases:

- Definitions never have proofs. They reach the graph through
  `depends_on`. v0.2 left definitions as isolated roots; v0.3 fixes this.
- Theorems whose statement names a structure (e.g., "in a metric space…")
  should link `ambient` to that structure.
- `depends_on.id` MUST be a statement id; proof ids are rejected.

`depends_on` is NEVER a substitute for `Proof.uses`. A theorem and the
definitions it cites are concept-linked; the proof of that theorem records
the actual derivation edges separately.

See `docs/v0.3/04-dependency-edges.md`.

---

## 6. Domains, ambient, ontology

These three blocks are free-form retrieval metadata. They are NOT
enforced as enums — consistency matters more than completeness.

### `domains`

- `primary`: principal mathematical area(s).
- `secondary`: bridge areas.
- Suggested vocabulary: `real-analysis`, `complex-analysis`, `topology`,
  `metric-spaces`, `set-theory`, `linear-algebra`, `abstract-algebra`,
  `number-theory`, `category-theory`, `mathematical-logic`, `geometry`,
  `differential-geometry`.

### `ambient`

- `structures`: ambient mathematical structures the statement lives in.
  This is the canonical disambiguator for "same name, different setting".
  Suggested vocabulary: `metric-space`, `topological-space`,
  `complete-ordered-field`, `ordered-field`, `normed-vector-space`,
  `smooth-manifold`, `abelian-category`.
- `logic`: optional logical context (e.g., `classical-first-order-logic`).
- `foundations`: optional foundational system (e.g., `ZFC`).

### `ontology`

- `semantic_kind`: one or more of (validator-enforced enum, v0.3.1):

  ```text
  object | property | relation | operator | construction |
  criterion | schema | principle | notation | pedagogical
  ```

  | kind          | use when…                                                       |
  |---------------|-----------------------------------------------------------------|
  | `object`      | introduces a mathematical object                                |
  | `property`    | asserts a property of an object                                 |
  | `relation`    | defines a relation                                              |
  | `operator`    | defines an operation / operator                                 |
  | `construction`| builds a new object from prior data                             |
  | `criterion`   | gives a test / equivalence                                      |
  | `schema`      | parameterized family of statements (bundle)                     |
  | `principle`   | foundational principle / axiom-like                             |
  | `notation`    | introduces notation / naming convention only (e.g., independent vs. dependent variable) |
  | `pedagogical` | didactic device, not a mathematical object per se (e.g., "mathematical model") |

- `keywords`: lowercase, hyphenated, descriptive (e.g.,
  `intermediate-value`, `monotone-convergence`).

`generality.relation` enum (validator-enforced, v0.3.1):

```text
equivalent | stronger_than | weaker_than | special_case_of |
incomparable | overlapping | sibling | disjoint
```

See `docs/v0.3/policies/04-edge-role-taxonomy.md` §C for the choice
guide between `incomparable`, `sibling`, `disjoint`, `overlapping`.

When in doubt, use existing tags found via the context pack §"Active
domains/ambient structures" rather than coining new ones.

See `docs/v0.3/06-domains-ambient.md` and `docs/v0.3/07-ontology-tags.md`.

---

## 7. Quality — six independent axes

`QualityBlock` decomposes the v0.2 single `confidence` field. Each axis is
`low | medium | high | null`. `null` means **unassessed**; do not default
to `high`.

| axis                          | tracks…                                            |
|-------------------------------|----------------------------------------------------|
| `extraction_confidence`       | the parse / wording capture                        |
| `dependency_confidence`       | is `uses` (proof) / `depends_on` (statement) COMPLETE? |
| `semantic_confidence`         | mathematical faithfulness to the source            |
| `translation_confidence`      | quality of non-original-language renderings        |
| `latex_confidence`            | quality of the formal `latex` block                |
| `source_alignment_confidence` | does the entity match the cited source?            |

Promotion gates enforced by the validator:

- `status: reviewed → validated` requires `dependency_confidence != null`
  AND at least one source AND `statement.latex.status != missing`.
- `status: validated → audited` requires `semantic_confidence != null`.

When you do not have evidence to set an axis, leave it `null` — that is the
correct signal for "audit this axis later".

See `docs/v0.3/05-quality-metadata.md`.

---

## 8. Status / review lifecycle

Two distinct concepts:

1. **Entity-level `status`** (top of every file) follows the linear chain
   `extracted → reviewed → validated → audited → stable → canonical`. Fresh
   extraction always sets `extracted`. Reviewers advance it manually after
   running the validator.
2. **Per-text `review_status`** on each `TranslatedText` and the `LatexBlock`:
   `unreviewed | reviewed | approved | rejected`. Used to track translation
   and LaTeX hygiene separately from the entity-level status.

Both are first-class. Promotion at the entity level does NOT require every
inner `review_status` to be `approved`, but reaching `audited` typically
implies most have at least `reviewed`.

See `docs/v0.3/08-status-lifecycle.md`.

---

## 9. Source locator requirements

Every `Source` entry SHOULD pin the result with maximum precision available:

- `work`            — REQUIRED. The work title (matches `sources/<key>/metadata.yml`).
- `author`          — recommended.
- `edition`, `year` — when known.
- `chapter`         — string. Matches the textbook's chapter numbering.
- `section`         — string. The textbook's section number (e.g., `"4.23"`).
- `theorem_label`   — REQUIRED when the source labels the result (e.g.,
  `"Theorem 4.23"`, `"Definition 6.1"`, `"Lemma 2.7"`). This is the field
  the context-pack §3 locator map keys on; missing labels mean nodes
  cannot be retrieved by textbook reference.
- `page`            — page number as printed (string).
- `locator`         — free-form fallback for things like
  `"Exercise 7, p.114"` or `"Remark following 3.21"`.
- `source_language` — language of THIS source (may differ from
  `language.original` only in unusual cases where the extractor reads a
  translation).

Multi-source nodes list ALL sources. Each proof, however, gets ONE source
(the source whose argument it transcribes); two sources → two proof nodes.

See `docs/v0.3/01-schema.md §Source`.

---

## 10. Multi-source / reconciliation rules

Reconciliation decisions happen at extraction time, NOT at audit time.

### When two sources state the "same" result

Decide whether they are **logically equivalent in full generality**. NOT
"equivalent on the real line", NOT "equivalent in spirit".

- **Equivalent (modulo notation / phrasing) → SAME NODE.** Add the new
  `Source` to `sources[]`. Add additional language entries to `title` and
  `statement.natural` if the new source contributes them. Add a SEPARATE
  proof node per source — proofs are never merged.
- **Strictly more general** → SEPARATE NODE for the general result. The
  specialized result becomes a `corollary` or carries a
  `generality.special_case_of` edge to the general one.
- **Strictly less general** → SEPARATE NODE (specialized). Optionally
  carries `generality.special_case_of` to the existing general node.
- **Overlapping / incomparable** → SEPARATE NODES. No `generality` edge,
  or `relation: overlapping`.

Record the reconciliation rationale in `notes` whenever the decision is
non-trivial.

### ID stability

When extending an existing v0.3 node with a new source, KEEP the existing
id. When creating a new node that replaces or splits a v0.2/v0.3 node,
set:

- new node's `provenance.derived_from: [<prior-id>]`
- old node's `provenance.redirected_to: <new-id>` if retiring it.

### Author labels

Two authors may use the same NAME for different results (or different
names for the same result). The MKG `id` follows the most standard
mathematical name, not any particular author's editorial convention.
Capture both names via `title` entries.

### Classification across sources

If two sources classify the same result differently (theorem vs
proposition), use the classification that best fits the Entity
Classification Guide in `AGENTS.md` §"Entity Classification Guide". Note
the discrepancy in `notes`.

See `docs/v0.3/01-schema.md` and the v0.2 "Multi-Source Disambiguation
Guide" in `AGENTS.md` (the disambiguation logic carries over verbatim).

---

## 11. Output discipline

When you produce v0.3 YAML:

1. Write ONE file per entity. Filename = `<id>.yml`.
2. Statements go to `data/statements/`. Proofs go to `data/proofs/`.
3. Validate immediately with `uv run mkg-validate` (or
   `uv run python -m scripts.v03.validate`).
4. Build with `uv run mkg-build` to verify the SQLite + graph outputs.
5. Snapshot with
   `uv run mkg-snapshot --label v0.3-<rerun-id>` once a meaningful unit
   (chapter, source) is complete.
6. Do NOT edit files inside `generated/snapshots/`. Snapshots are
   read-only.

When you receive a validation error, FIX the YAML rather than work around
the validator. The schema's strictness is intentional.

---

## 12. Reference index

| Topic                       | Spec / docs                                            |
|-----------------------------|--------------------------------------------------------|
| Schema source of truth      | `schema/v03.py`                                        |
| JSON Schema (machine)       | `schema/v03.statement.schema.json`, `v03.proof.schema.json` |
| Overall design              | `docs/v0.3/00-overview.md`, `01-schema.md`             |
| i18n                        | `docs/v0.3/02-i18n.md`                                 |
| LaTeX lifecycle             | `docs/v0.3/03-latex-lifecycle.md`                      |
| Dependency edges            | `docs/v0.3/04-dependency-edges.md`                     |
| Quality metadata            | `docs/v0.3/05-quality-metadata.md`                     |
| Domains / ambient           | `docs/v0.3/06-domains-ambient.md`                      |
| Ontology tags               | `docs/v0.3/07-ontology-tags.md`                        |
| Status lifecycle            | `docs/v0.3/08-status-lifecycle.md`                     |
| Rerun architecture          | `docs/v0.3/09-rerun-architecture.md`                   |
| Rerun checklist             | `docs/v0.3/13-rerun-checklist.md`                      |
| Entity classification       | `AGENTS.md` §"Entity Classification Guide"             |
| Multi-source disambiguation | `AGENTS.md` §"Multi-Source Disambiguation Guide"       |
| Policy index (FROZEN)       | `docs/v0.3/policies/README.md`                          |
| Bundled-definition splits   | `docs/v0.3/policies/01-bundled-definitions-audit.md`    |
| Domain vocabulary           | `docs/v0.3/policies/02-domain-vocabulary.md`            |
| Ontology vocabulary         | `docs/v0.3/policies/03-ontology-vocabulary.md`          |
| Edge-role taxonomy          | `docs/v0.3/policies/04-edge-role-taxonomy.md`           |
| ID equivalence (merge/split)| `docs/v0.3/policies/05-id-equivalence-policy.md`        |
| Theorem granularity         | `docs/v0.3/policies/06-theorem-granularity-policy.md`   |
| Semantic freeze + change ctl| `docs/v0.3/policies/07-semantic-freeze.md`              |
| Pilot readiness (Stewart Ch1)| `docs/v0.3/policies/08-pilot-readiness.md`             |
