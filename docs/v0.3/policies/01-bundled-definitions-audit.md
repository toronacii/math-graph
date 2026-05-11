# 01 — Bundled Definitions Audit

> Data-driven audit of `data/statements/definition.*.yml` (v0.2 baseline,
> 149 definition files) identifying nodes that bundle multiple distinct
> mathematical concepts into one definition. For each, prescribes a v0.3
> split (or "keep as-is") with replacement IDs and migration semantics.

## Methodology

A definition is **bundled** when it encodes ≥2 mathematical concepts that
are referenced **independently** elsewhere in the corpus. Heuristics used
to surface candidates (in order of strength):

1. **ID with ≥3 hyphenated concept words** (e.g.,
   `definition.neighborhood-limit-point-open-closed`).
2. **Title containing `,` / `and` / `&`** between distinct concept names.
3. **`statement.natural` body containing labeled enumeration** (`(a)…(b)…`)
   where each label introduces a different definiendum.
4. **High in-degree** of the bundled node — an artificial-hub signal.

A definition is **NOT bundled** (despite multi-token id/title) when:

- the concepts are mutually defining (`upper-bound` + `bounded-above` are
  one concept under two grammatical guises);
- the second concept is a synonym / alternative spelling of the first
  (`function-mapping`);
- the body is a **single concept defined by a list of axioms** (a `field`
  is one concept; its 11 axioms are not separate definitions).

## Decision matrix

| Decision | Meaning |
|---|---|
| **SPLIT** | The bundled node is replaced by N atomic v0.3 definitions. The bundled id is RETIRED via `provenance.redirected_to: null` (no single replacement). Every replacement records `provenance.derived_from: [<old-id>]`. |
| **KEEP** | The node is genuinely one concept; no action. |
| **RESHAPE** | Keep one node but rename + tighten body so it no longer pretends to define multiple things. |

## Audit results (v0.2 baseline)

### A. SPLIT (heavy bundles)

#### A.1 `definition.neighborhood-limit-point-open-closed`

- **Source.** Rudin Definition 2.18.
- **Bundles.** 10 concepts: neighborhood, limit point, isolated point,
  closed set, interior point, open set, complement, perfect set,
  bounded set, dense set.
- **Why SPLIT.** Every concept appears independently in proofs. The
  bundled id is the largest artificial hub in the v0.2 graph. Reviewers
  cannot tell whether `proof.X` uses "open" or "limit point" or "perfect"
  when the dependency is just to this node.
- **Replacement IDs (10):**
  - `definition.neighborhood-metric`
  - `definition.limit-point`
  - `definition.isolated-point`
  - `definition.closed-set`
  - `definition.interior-point`
  - `definition.open-set`
  - `definition.complement-set`
  - `definition.perfect-set`
  - `definition.bounded-set`
  - `definition.dense-set`
- **Concept-layer wiring.** `closed-set`, `open-set`, `interior-point`,
  `perfect-set`, `dense-set` carry `depends_on: [{id: definition.limit-point,
  role: uses_concept}]`. All ten carry `ambient.structures: [metric-space]`.
- **Migration aid.** `scripts/v03/extraction_helpers/` (future) may emit a
  bundled→atomic mapping table; for now the split is performed during
  extraction by referring to this audit.

#### A.2 `definition.segment-interval-cell-ball`

- **Source.** Rudin Definition 2.17.
- **Bundles.** 5 concepts: segment, interval (closed), k-cell, ball
  (open + closed counted as one), convex set.
- **Why SPLIT.** "Convex set" is reused far outside the contexts where
  segments / cells appear (linear-algebra, geometry). Conflating them
  fragments retrieval.
- **Replacement IDs (5):**
  - `definition.open-interval` (Rudin's "segment")
  - `definition.closed-interval`
  - `definition.k-cell`
  - `definition.ball` (with body covering both open and closed via
    parameter)
  - `definition.convex-set`
- **Concept-layer wiring.** `k-cell` and `ball` carry
  `ambient.structures: [euclidean-space]`. `convex-set` carries
  `ambient.structures: [vector-space]` (broader than ℝᵏ).

#### A.3 `definition.union-intersection`

- **Source.** Rudin Definition 2.9.
- **Bundles.** 2 concepts: union of an indexed family, intersection of
  an indexed family. (Plus the auxiliary "intersect / disjoint" pair.)
- **Why SPLIT.** Theorems frequently cite ONE of the two; bundling
  doubles the apparent fan-out of every such citation.
- **Replacement IDs (2):**
  - `definition.union-indexed-family`
  - `definition.intersection-indexed-family`
- **Auxiliary handling.** "Disjoint sets" is a separate, well-known
  concept and is split off as `definition.disjoint-sets`.

#### A.4 `definition.separated-connected`

- **Source.** Rudin Definition 2.45.
- **Bundles.** 2 concepts: separated sets (a relation between two sets)
  and connected set (a property of one set).
- **Why SPLIT.** Connectedness is referenced widely; "separated" is
  used almost exclusively in the definition of connectedness. The
  cleanest model has `connected-set` as the primary node with
  `depends_on: [{id: definition.separated-sets, role: uses_concept}]`.
- **Replacement IDs (2):**
  - `definition.separated-sets`
  - `definition.connected-set`

#### A.5 `definition.set-membership-subset`

- **Source.** Rudin pre-Ch.1 set-theory primer.
- **Bundles.** 3 micro-concepts: set, membership (∈), subset (⊆).
- **Why SPLIT.** These are foundational and referenced by hundreds of
  potential downstream nodes; they should be the cleanest possible
  atomic axioms / definitions.
- **Replacement IDs (3):**
  - `definition.set` (informal naive-set definition; mark
    `ambient.foundations: ZFC`)
  - `definition.membership-relation`
  - `definition.subset-relation`
- **Note.** All three may stay extremely terse (one line each); that is
  acceptable — atomicity is the goal.

#### A.6 `definition.function-mapping`

- **Source.** Rudin Definition 2.1.
- **Bundles.** 7 concepts: function/mapping, domain, range, image,
  inverse image, one-to-one (injection), onto (surjection).
- **Why SPLIT.** Each of these is referenced independently throughout
  Ch3–7 (sequences are functions ℕ→X, continuity uses inverse image,
  bijections drive countability). A single bundled hub here would
  dominate centrality artificially.
- **Replacement IDs (7):**
  - `definition.function` (function = mapping; one node, both names in
    `title`)
  - `definition.domain-of-function`
  - `definition.range-of-function`
  - `definition.image-of-set-under-function`
  - `definition.inverse-image-of-set`
  - `definition.injective-function`
  - `definition.surjective-function`
- **Concept-layer wiring.** All six derived nodes carry
  `depends_on: [{id: definition.function, role: uses_concept}]`.

#### A.7 `definition.finite-countable-sets`

- **Source.** Rudin Definition 2.4.
- **Bundles.** 5 concepts: finite, infinite, countable, uncountable, at
  most countable.
- **Why SPLIT.** Countability theorems (2.8, 2.12, 2.13, 2.14) cite
  `countable` or `at-most-countable` specifically. Bundling produces
  the worst kind of false-equivalence edge ("uses cardinality
  classification" instead of "uses countability").
- **Replacement IDs (5):**
  - `definition.finite-set`
  - `definition.infinite-set`
  - `definition.countable-set`
  - `definition.uncountable-set`
  - `definition.at-most-countable-set`
- **Note.** All five `depends_on` `definition.equinumerous-sets` (the
  ~ relation), which itself should be split out from any node that
  bundles it.

### B. RESHAPE (rename + tighten)

#### B.1 `definition.right-left-limits`

- **Source.** Rudin Definition 4.25 / Stewart §2.2.
- **Bundles.** 2 concepts (right-hand limit, left-hand limit), but
  these are **dual definitions of the same shape**.
- **Decision.** SPLIT into `definition.right-hand-limit` and
  `definition.left-hand-limit`. They are referenced independently in
  one-sided continuity discussions.

#### B.2 `definition.monotonically-increasing-function`

- **Source.** Rudin Definition 4.28.
- **Bundles.** "Monotonically increasing" + "monotonically decreasing"
  in one body.
- **Decision.** SPLIT into
  `definition.monotonically-increasing-function` and
  `definition.monotonically-decreasing-function`. They are cited
  independently (e.g., monotone-bounded-convergence cites only one
  direction in many contexts).
- Stewart's `definition.increasing-function` and
  `.decreasing-function` (already split) should NOT be merged with
  Rudin's; see `05-id-equivalence-policy.md` §"Strict vs non-strict
  monotonicity".

#### B.3 `definition.upper-lower-limits`

- **Source.** Rudin Definition 3.16.
- **Bundles.** lim sup + lim inf of a sequence.
- **Decision.** SPLIT into `definition.limit-superior-sequence` and
  `definition.limit-inferior-sequence`.

#### B.4 `definition.simple-discontinuity`

- **Source.** Rudin Definition 4.26.
- **Bundles.** "Discontinuity of the first kind" (jump) + "second kind"
  (essential).
- **Decision.** SPLIT into
  `definition.discontinuity-first-kind` and
  `definition.discontinuity-second-kind`. They appear independently in
  the discussion of monotonic-function discontinuities.

#### B.5 `definition.curve-arc-rectifiable`

- **Source.** Rudin Definition 6.26.
- **Bundles.** Curve / arc / closed-curve / rectifiable curve / arc
  length.
- **Decision.** SPLIT into:
  - `definition.curve` (continuous γ:[a,b]→ℝᵏ)
  - `definition.arc` (curve with γ injective)
  - `definition.closed-curve` (curve with γ(a)=γ(b))
  - `definition.rectifiable-curve` (finite arc length)
  - `definition.arc-length`

### C. KEEP (genuinely atomic despite multi-token ID/title)

| Node | Reason kept |
|---|---|
| `definition.field` | One concept; the 11 axioms are its definition, not separate concepts. |
| `definition.ordered-field` | One concept; "positive / negative" naming is a corollary inside the same concept. |
| `definition.upper-bound` | "Upper bound" and "bounded above" are the same concept under two grammatical forms. |
| `definition.function-mapping` (the BASE concept) | After split (A.6), the base node `definition.function` keeps "mapping" as a synonym in `title`. |
| `definition.limit-of-function-metric` | One concept (limit in metric space); no bundling. |
| `definition.horizontal-stretch-compression`, `definition.vertical-stretch-compression` | Each is one pedagogical transformation pair (Stewart); not referenced atomically elsewhere. |
| `definition.continuity-on-interval` | One concept (interval continuity), not "interval" + "continuity". |

## Summary table

| Bundle | Concepts | Replacement count | Action |
|---|---:|---:|---|
| `neighborhood-limit-point-open-closed` | 10 | 10 | SPLIT |
| `function-mapping` | 7 | 7 (incl. base) | SPLIT |
| `finite-countable-sets` | 5 | 5 | SPLIT |
| `segment-interval-cell-ball` | 5 | 5 | SPLIT |
| `curve-arc-rectifiable` | 5 | 5 | SPLIT |
| `set-membership-subset` | 3 | 3 | SPLIT |
| `union-intersection` | 2 (+1 aux) | 3 | SPLIT |
| `separated-connected` | 2 | 2 | SPLIT |
| `right-left-limits` | 2 | 2 | SPLIT |
| `monotonically-increasing-function` | 2 | 2 | SPLIT |
| `upper-lower-limits` | 2 | 2 | SPLIT |
| `simple-discontinuity` | 2 | 2 | SPLIT |

**Total.** 12 bundled v0.2 nodes → **48 atomic v0.3 nodes** (net +36).

## Migration rules (applies to every SPLIT above)

1. **Provenance.** Every replacement carries
   `provenance.derived_from: [<old-bundled-id>]`.
2. **Old node fate.** The old bundled id is NOT carried into v0.3.
   It does NOT receive a `redirected_to` (because there is no single
   successor). It exists only in the v0.2 frozen snapshot.
3. **Edge re-targeting.** Every v0.2 proof / statement that referenced
   the bundled id must, in v0.3, re-target to the SPECIFIC atomic
   replacement actually used. Over-broad re-targeting (e.g., wiring
   every old edge to the most-popular replacement) is a SEMANTIC ERROR
   and will fail the audit.
4. **`depends_on` chains.** Where one replacement depends on another
   (e.g., `closed-set` → `limit-point`), encode that as a
   `Statement.depends_on` edge with `role: uses_concept`. This is the
   primary use case for v0.3's concept layer.
5. **Pilot scope.** The Stewart Ch1 pilot does NOT need every bundled
   definition split immediately — only those Stewart Ch1 actually
   references (the relevant subset is small: function, domain, range,
   one-to-one). The Rudin-heavy bundles are split during the Rudin
   rerun phase.

## Anti-policy: do NOT atomize further

Atomization beyond this list is forbidden during the pilot. In
particular do NOT split:

- single-concept definitions whose body lists axioms
  (`field`, `ordered-field`, `metric-space`);
- single-concept definitions with two grammatical forms
  (`upper-bound` / `bounded-above`);
- pedagogical "transformation pair" definitions in Stewart
  (horizontal/vertical stretch).

Excessive atomization fragments the graph and makes navigation worse,
not better. The objective is **semantic atomicity**, not maximal
fragmentation.
