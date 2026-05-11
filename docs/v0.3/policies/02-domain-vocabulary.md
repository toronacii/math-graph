# 02 — Domain Vocabulary

> Frozen controlled vocabulary for `domains.primary` and `domains.secondary`
> (see `schema/v03.py::DomainsBlock`). The schema is permissive (free-form
> strings); enforcement is by **convention + audit**, not validator rejection.
> This freeze gives reviewers and the context-pack generator a stable set
> to retrieve against.

## Naming rules (all entries MUST satisfy)

1. **Lowercase ASCII**, hyphen-separated, no spaces, no underscores.
2. **Singular nouns** for the area name itself
   (`real-analysis`, NOT `real-analyses`).
3. **Plural ONLY for explicitly plural objects** (`metric-spaces`,
   `differential-equations`).
4. **Hyphen always separates words** (`real-analysis`, never `realanalysis`
   or `real_analysis`).
5. **Avoid abbreviations** unless the abbreviation is more standard than
   the long form (`category-theory`, never `cat-theory`; but `pde` is
   acceptable as a *secondary* tag).
6. **No author or textbook names** (`stewart-calculus` is forbidden).

## Tier 1 — frozen primary vocabulary

These are the canonical primary domains. New nodes MUST pick at least
one Tier-1 entry for `domains.primary`.

| Tag                       | Scope                                                              |
|---------------------------|--------------------------------------------------------------------|
| `set-theory`              | Sets, relations, functions, cardinality, ZFC.                      |
| `mathematical-logic`      | First-order logic, quantifiers, classical / intuitionistic logic.  |
| `abstract-algebra`        | Groups, rings, fields, modules (algebraic structures).             |
| `linear-algebra`          | Vector spaces, linear maps, matrices, eigenvalues.                 |
| `real-analysis`           | Real-line analysis: limits, continuity, derivatives, integrals.    |
| `complex-analysis`        | Complex-valued functions, analyticity, contour integration.        |
| `calculus`                | Pedagogical real-analysis (Stewart-style: derivatives, integrals,  |
|                           | sequences, series at single-variable level).                       |
| `multivariable-calculus`  | Vector calculus, partial derivatives, multiple integrals.          |
| `topology`                | General / point-set topology, topological spaces, continuous maps. |
| `metric-spaces`           | Metric-space-specific results (Cauchy completeness, compactness).  |
| `functional-analysis`     | Banach / Hilbert spaces, bounded operators, dual spaces.           |
| `measure-theory`          | σ-algebras, measures, integration in the Lebesgue sense.           |
| `differential-equations`  | ODEs, PDEs, existence / uniqueness, qualitative theory.            |
| `number-theory`           | Integers, primes, congruences, Diophantine analysis.               |
| `combinatorics`           | Counting, generating functions, graph theory, Ramsey theory.       |
| `geometry`                | Euclidean / non-Euclidean / projective / synthetic geometry.       |
| `differential-geometry`   | Manifolds, tensor fields, curvature, Lie groups.                   |
| `category-theory`         | Categories, functors, natural transformations, limits / colimits.  |
| `probability`             | Probability spaces, random variables, distributions.               |
| `statistics`              | Estimation, hypothesis testing, regression.                        |
| `numerical-analysis`      | Discretization, error analysis, computational methods.             |

## Tier 2 — bridge / sub-area tags (allowed in `secondary`)

Use these in `domains.secondary` to expose bridges. They MAY also appear
in `primary` if the node is genuinely about the bridge concept.

| Tag                            | Bridges                                          |
|--------------------------------|--------------------------------------------------|
| `algebraic-topology`           | algebra ↔ topology                                |
| `algebraic-geometry`           | algebra ↔ geometry                                |
| `harmonic-analysis`            | analysis ↔ functional-analysis                    |
| `dynamical-systems`            | analysis ↔ DEs ↔ topology                         |
| `representation-theory`        | algebra ↔ functional-analysis                     |
| `combinatorial-topology`       | combinatorics ↔ topology                          |
| `analytic-number-theory`       | analysis ↔ number-theory                          |
| `differential-topology`        | topology ↔ differential-geometry                  |
| `mathematical-physics`         | analysis / DE / geometry ↔ physics                |
| `homological-algebra`          | algebra ↔ category-theory                         |

## Multi-domain rules

- **Always at least one `primary`.** Empty `domains.primary` is allowed
  by the schema but FORBIDDEN by this policy for any node beyond
  foundational set-theoretic axioms.
- **At most three `primary`** entries. A node with 4+ primary domains
  is almost certainly mis-classified or genuinely bridge-y; promote it
  to a Tier-2 tag in `secondary` instead.
- **Bridges go in `secondary`.** A theorem in `real-analysis` whose
  proof uses topology has `primary: [real-analysis]`,
  `secondary: [topology]`. A theorem genuinely *about* the bridge (e.g.,
  Heine–Borel as a bridge between metric spaces and topology) may use
  `primary: [metric-spaces, topology]`.

## `calculus` vs `real-analysis`

This is the most common ambiguity. Rule:

- **`calculus`** when the source is pedagogical (Stewart, Spivak,
  Apostol Vol. 1), the result is treated informally, and the audience
  is undergraduate-introductory.
- **`real-analysis`** when the source is rigorous (Rudin, Royden,
  Folland), the result handles general domains (metric spaces,
  arbitrary subsets of ℝ), and the audience is upper-division /
  graduate.
- A theorem with **both** Stewart and Rudin sources gets
  `primary: [real-analysis]` (the general statement) with
  `secondary: [calculus]` to signal the pedagogical reach.

## Aliases

Aliases are FORBIDDEN. Each concept has exactly one tag. If a synonym
arises, add it to this document under the canonical tag and forbid the
synonym.

Currently disallowed synonyms:

| Use this | Not this |
|---|---|
| `real-analysis` | `analysis-real`, `mathematical-analysis-1` |
| `metric-spaces` | `metric-space-theory` |
| `functional-analysis` | `banach-space-theory`, `hilbert-space-theory` |
| `differential-equations` | `ode-theory`, `pde-theory` |
| `category-theory` | `categorical-algebra` |

## Extension policy

Adding a new tag requires:

1. A PR adding it to the appropriate tier in this document.
2. At least 3 existing or planned nodes that justify the tag (no
   speculative tags).
3. An explicit rationale for why a Tier-1 / Tier-2 entry does not
   suffice.

Removing or renaming a tag requires:

1. A migration PR re-tagging every using node atomically.
2. Snapshot before and after, listed in the rerun manifest.

## Validator behavior

The v0.3 validator does **not** enforce this vocabulary as of the
freeze (it is intentionally permissive). The context-pack generator
(`scripts.v03.make_context_pack`) reports the *active* vocabulary in
its §"Active domains" line, so vocabulary drift surfaces immediately
in any pack. After two reruns of stable vocabulary, the validator
should be tightened to warn on out-of-vocabulary tags (NOT reject them).
