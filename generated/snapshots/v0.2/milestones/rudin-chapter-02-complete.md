# Milestone: Rudin Chapter 2 Complete

## Source

- **Textbook:** Walter Rudin — Principles of Mathematical Analysis
- **Edition:** 3rd
- **Publisher:** McGraw-Hill, 1976
- **Language:** English
- **Chapter:** 2 — Basic Topology
- **Sections processed:** 2.1 through 2.47

## Extraction Date

2026-05-10

## Graph Summary

| Metric               | Value |
|----------------------|-------|
| Total nodes          | 72    |
| Total edges          | 94    |
| Statements           | 42    |
| Proofs               | 30    |
| Definitions          | 12    |
| Propositions         | 10    |
| Theorems             | 12    |
| Lemmas               | 2     |
| Corollaries          | 6     |
| Axioms               | 0     |
| Conjectures          | 0     |
| Isolated nodes       | 0     |
| Connected components | 1     |
| Cross-chapter edges  | 12    |

## Validation Status

- Schema validation: PASS
- ID uniqueness: PASS
- Reference integrity: PASS
- Symmetry (proved_by <-> proves): PASS
- Acyclicity: PASS

All 72 entities pass the full validation pipeline.

## Entity Inventory

### Definitions (12)

| ID | Section | Title |
|----|---------|-------|
| definition.function-mapping | 2.1 | Function and Mapping |
| definition.equivalence-cardinality | 2.3 | Cardinal Equivalence |
| definition.finite-countable-sets | 2.4 | Finite, Countable, and Uncountable Sets |
| definition.sequence | 2.7 | Sequence |
| definition.union-intersection | 2.9 | Union and Intersection of Families of Sets |
| definition.metric-space | 2.15 | Metric Space |
| definition.segment-interval-cell-ball | 2.17 | Segment, Interval, k-Cell, and Ball |
| definition.neighborhood-limit-point-open-closed | 2.18 | Topological Concepts in Metric Spaces |
| definition.closure | 2.26 | Closure of a Set |
| definition.open-cover | 2.31 | Open Cover |
| definition.compact-set | 2.32 | Compact Set |
| definition.separated-connected | 2.45 | Separated and Connected Sets |

### Propositions (10)

| ID | Section | Title |
|----|---------|-------|
| proposition.infinite-subset-countable | 2.8 | Every Infinite Subset of a Countable Set is Countable |
| proposition.n-tuples-countable | 2.13 | Set of n-Tuples from a Countable Set is Countable |
| proposition.neighborhood-is-open | 2.19 | Every Neighborhood is an Open Set |
| proposition.limit-point-infinite-points | 2.20 | Limit Points Contain Infinitely Many Points |
| proposition.de-morgan | 2.22 | De Morgan's Law |
| proposition.open-iff-complement-closed | 2.23 | A Set is Open Iff Its Complement is Closed |
| proposition.closure-properties | 2.27 | Properties of the Closure of a Set |
| proposition.sup-in-closure | 2.28 | Supremum Belongs to the Closure |
| proposition.compact-is-closed | 2.34 | Compact Subsets of Metric Spaces are Closed |
| proposition.closed-subset-compact | 2.35 | Closed Subsets of Compact Sets are Compact |

### Theorems (12)

| ID | Section | Title |
|----|---------|-------|
| theorem.countable-union-countable | 2.12 | Countable Union of Countable Sets is Countable |
| theorem.binary-sequences-uncountable | 2.14 | The Set of All Binary Sequences is Uncountable |
| theorem.unions-intersections-open-closed | 2.24 | Unions and Intersections of Open and Closed Sets |
| theorem.open-relative | 2.30 | Characterization of Relatively Open Sets |
| theorem.compactness-relative | 2.33 | Compactness is Independent of the Ambient Space |
| theorem.finite-intersection-compact | 2.36 | Finite Intersection Property for Compact Sets |
| theorem.infinite-subset-compact-limit-point | 2.37 | Infinite Subset of a Compact Set Has a Limit Point |
| theorem.k-cell-compact | 2.40 | Every k-Cell is Compact |
| theorem.heine-borel | 2.41 | Heine-Borel Theorem |
| theorem.bolzano-weierstrass | 2.42 | Bolzano-Weierstrass Theorem |
| theorem.perfect-set-uncountable | 2.43 | Nonempty Perfect Sets in Rk are Uncountable |
| theorem.connected-subsets-of-r | 2.47 | Characterization of Connected Subsets of R |

### Lemmas (2)

| ID | Section | Title |
|----|---------|-------|
| lemma.nested-intervals | 2.38 | Nested Intervals Theorem |
| lemma.nested-k-cells | 2.39 | Nested k-Cells Theorem |

### Corollaries (6)

| ID | Section | Title |
|----|---------|-------|
| corollary.at-most-countable-union | 2.12 | At Most Countable Union of At Most Countable Sets |
| corollary.rationals-countable | 2.13 | The Rational Numbers are Countable |
| corollary.finite-set-no-limit-points | 2.20 | A Finite Point Set Has No Limit Points |
| corollary.closed-intersect-compact | 2.35 | Intersection of a Closed Set and a Compact Set is Compact |
| corollary.nested-compact-nonempty | 2.36 | Nested Sequence of Compact Sets Has Nonempty Intersection |
| corollary.interval-uncountable | 2.43 | Every Interval [a,b] is Uncountable |

### Proofs (30)

All proofs have confidence: high. Proof IDs follow the pattern
`proof.<statement>.rudin` with source = rudin.

## Reclassification Summary

12 entities were reclassified during Phase 3:

- **10 theorem → proposition:** Basic utility facts (neighborhood-is-open,
  de-morgan, compact-is-closed, etc.) that follow directly from
  definitions without deep structural significance.
- **2 theorem → lemma:** nested-intervals and nested-k-cells, which
  exist primarily as stepping stones toward k-cell compactness and
  Heine-Borel.

## Observations

1. **Fully connected chapter.** All 72 nodes belong to a single
   connected component with no isolated nodes. Every definition
   participates in at least one proof. This is tighter connectivity
   than Ch1 (which had 3 components and 3 isolated nodes).

2. **Deep dependency chains.** The longest chain has statement-depth
   6+, culminating at Heine-Borel. This is deeper than Ch1 (depth
   4+), reflecting the multi-layered buildup from metric spaces to
   compactness.

3. **Hub node concentration.** `definition.neighborhood-limit-point-open-closed`
   is the most connected node (degree 11), serving as the definitional
   backbone for the entire chapter. This single node packs open,
   closed, limit point, interior, complement, perfect, bounded, and
   dense into one definition — a deliberate Rudin design choice.

4. **Cross-chapter integration.** 12 edges connect Ch2 to Ch1,
   primarily through `definition.supremum` (3 edges) and
   `definition.least-upper-bound-property`. The completeness of R
   underpins nested intervals, sup-in-closure, and connected subsets.

5. **No weak dependencies.** All 30 proofs have confidence: high.
   Rudin's Chapter 2 is fully rigorous with no epistemic debt.

## Cumulative Graph (All Sources)

| Metric               | After Rudin Ch1 | After Rudin Ch2 |
|----------------------|-----------------|-----------------|
| Total nodes          | 318             | 389             |
| Total edges          | 358             | 459             |
| Definitions          | 114             | 125             |
| Propositions         | 23              | 33              |
| Theorems             | 73              | 85              |
| Lemmas               | 0               | 2               |
| Corollaries          | 6               | 12              |
| Proofs               | 102             | 132             |
| Graph density        | 0.0071          | 0.0030          |
| Connected components | 58              | 59              |
