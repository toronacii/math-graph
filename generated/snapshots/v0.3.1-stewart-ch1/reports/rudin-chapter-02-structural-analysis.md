# Rudin Chapter 2 — Structural Analysis

## 1. Conceptual Density

Chapter 2 of Rudin produces 42 statements and 30 proofs across
sections 2.1 through 2.47. The chapter divides into four major
conceptual blocks:

| Block                    | Sections    | Defs | Props | Thms | Lemmas | Cors | Proofs |
|--------------------------|-------------|------|-------|------|--------|------|--------|
| Functions & Countability | 2.1–2.14    | 5    | 2     | 2    | 0      | 2    | 6      |
| Metric Space Topology    | 2.15–2.30   | 5    | 6     | 3    | 0      | 1    | 10     |
| Compactness              | 2.31–2.43   | 2    | 2     | 6    | 2      | 3    | 13     |
| Connectedness            | 2.45–2.47   | 1    | 0     | 1    | 0      | 0    | 1      |

The Compactness block (2.31–2.43) is the mathematical core. It
contains the major structural results: Heine-Borel, Bolzano-Weierstrass,
and the uncountability of perfect sets.

## 2. Dependency Structure

The Rudin Ch2 subgraph has 72 nodes, 94 internal edges, and 12
cross-chapter edges to Ch1.

Key structural features:

- 1 weakly connected component within the Ch2 subgraph — fully
  connected with no isolated nodes.
- 12 root nodes, all definitions — these are the foundational
  vocabulary of the chapter.
- Internal density 0.0184 (comparable to Ch1's 0.0245).

## 3. Hub Nodes

The most connected nodes in the Rudin Ch2 subgraph:

| Node                                              | Degree | Role                           |
|----------------------------------------------------|--------|--------------------------------|
| definition.neighborhood-limit-point-open-closed     | 11     | Core topology vocabulary       |
| definition.compact-set                              | 6      | Central to compactness block   |
| proof.heine-borel.rudin                             | 6      | Uses 5 prior results           |
| definition.sequence                                 | 5      | Used across multiple blocks    |
| definition.metric-space                             | 5      | Foundation for all topology    |

`definition.neighborhood-limit-point-open-closed` is the single most
connected node in Ch2, serving as a dependency for 10 proofs and
statements. This reflects its role as the definitional backbone of
metric space topology — open, closed, limit point, interior, and
complement are all packed into this one definition node.

## 4. Graph Layering

The Rudin Ch2 graph exhibits a natural five-layer structure:

```
Layer 0 (set theory):      function-mapping, equivalence-cardinality,
                           finite-countable-sets, sequence,
                           union-intersection

Layer 1 (metric spaces):   metric-space, segment-interval-cell-ball,
                           neighborhood-limit-point-open-closed

Layer 2 (basic topology):  neighborhood-is-open, limit-point-infinite-points,
                           de-morgan, open-iff-complement-closed,
                           unions-intersections-open-closed,
                           closure, closure-properties, sup-in-closure,
                           open-relative

Layer 3 (compactness):     open-cover, compact-set, compactness-relative,
                           compact-is-closed, closed-subset-compact,
                           finite-intersection-compact,
                           infinite-subset-compact-limit-point,
                           nested-intervals, nested-k-cells,
                           k-cell-compact, heine-borel,
                           bolzano-weierstrass, perfect-set-uncountable

Layer 4 (connectedness):   separated-connected, connected-subsets-of-r
```

This layering reflects Rudin's pedagogical approach: set-theoretic
foundations (countability), then metric space structure, then topology,
then compactness as the deep core, and finally connectedness.

## 5. Dependency Chains

The longest dependency chain in Ch2 (statement depth 6):

```
definition.metric-space
  -> definition.segment-interval-cell-ball
    -> definition.neighborhood-limit-point-open-closed
      -> proposition.compact-is-closed
        -> proposition.closed-subset-compact
          -> theorem.heine-borel
            -> theorem.bolzano-weierstrass
```

A second important chain runs through the compactness core:

```
definition.neighborhood-limit-point-open-closed
  -> proposition.neighborhood-is-open
    -> theorem.unions-intersections-open-closed
      -> theorem.compactness-relative
        -> theorem.k-cell-compact
          -> theorem.heine-borel
```

The convergence of multiple chains at `theorem.heine-borel` confirms
its role as the central theorem of the chapter.

## 6. Cross-Chapter Dependencies

Ch2 has 12 edges connecting to Ch1 entities:

| Ch2 proof                           | Ch1 dependency                           |
|-------------------------------------|------------------------------------------|
| proof.de-morgan.rudin               | definition.set-membership-subset         |
| proof.rationals-countable.rudin     | definition.rational-numbers              |
| proof.nested-intervals.rudin        | definition.supremum                      |
| proof.nested-intervals.rudin        | definition.least-upper-bound-property    |
| proof.k-cell-compact.rudin          | theorem.archimedean-density              |
| proof.sup-in-closure.rudin          | definition.supremum                      |
| proof.connected-subsets-of-r.rudin  | definition.supremum                      |

`definition.supremum` is the most referenced Ch1 entity (3 edges),
confirming the central role of the least-upper-bound property in
metric space topology.

## 7. Reclassification Summary

12 entities were reclassified from Rudin's original labels:

- **10 theorem → proposition:** infinite-subset-countable,
  n-tuples-countable, neighborhood-is-open, limit-point-infinite-points,
  de-morgan, open-iff-complement-closed, closure-properties,
  sup-in-closure, compact-is-closed, closed-subset-compact.
  These are reusable utility facts that follow relatively directly
  from definitions.

- **2 theorem → lemma:** nested-intervals, nested-k-cells.
  These exist primarily as stepping stones toward k-cell compactness
  (2.40) and Heine-Borel (2.41).

## 8. Growth Expectations

### Rudin Chapter 3 — Numerical Sequences and Series

Expected impact:

- **New concepts:** convergent sequence, Cauchy sequence, subsequence,
  upper/lower limits, series, absolute convergence, power series.
- **Key theorems:** Completeness of Rk, comparison test, root test,
  ratio test, Abel's theorem.
- **Dependencies on Ch2:** definition.metric-space,
  definition.compact-set, theorem.bolzano-weierstrass,
  definition.sequence.
- **Cross-source:** Rudin's rigorous sequence convergence will
  provide foundations for Stewart's limit laws and convergence tests.

### Rudin Chapter 4 — Continuity

Expected impact:

- **Continuity, uniform continuity, compactness preservation**
  will build heavily on Ch2's metric space and compactness machinery.
- **Intermediate value theorem** will connect to Ch2's connectedness.

## 9. Comparison: Rudin Ch1 vs Ch2

| Metric                  | Rudin Ch1 | Rudin Ch2 |
|-------------------------|-----------|-----------|
| Total nodes             | 52        | 72        |
| Statements              | 34        | 42        |
| Proofs                  | 18        | 30        |
| Definitions             | 16        | 12        |
| Propositions            | 5         | 10        |
| Theorems                | 12        | 12        |
| Lemmas                  | 0         | 2         |
| Corollaries             | 1         | 6         |
| Internal edges          | 65        | 94        |
| Cross-chapter edges     | 0         | 12        |
| Internal density        | 0.0245    | 0.0184    |
| Isolated nodes          | 3 (6%)    | 0 (0%)    |
| Connected components    | 3         | 1         |
| Max dependency depth    | 4+        | 6+        |

Key differences:

1. **Ch2 is larger and more connected.** 72 nodes vs 52, fully
   connected with no isolated nodes. Every definition participates
   in at least one proof.
2. **Ch2 has deeper dependency chains.** Maximum depth 6+ vs 4+,
   reflecting the multi-layered buildup to Heine-Borel.
3. **Ch2 introduces lemmas.** The nested intervals/k-cells results
   are the first entities in the Rudin graph classified as lemmas.
4. **Ch2 is more corollary-rich.** 6 corollaries vs 1, reflecting
   the many immediate consequences of the major compactness theorems.
