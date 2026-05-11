# Rudin Chapter 4 — Structural Analysis

## Summary

Chapter 4 (Continuity) adds 49 entities (28 statements + 21 proofs) to the graph,
bringing the cumulative total to **506 nodes and 645 edges**.

## Hub Nodes

Within Chapter 4, the most connected nodes are:

- `definition.continuity-metric` (degree ~12) — referenced by most Ch4 theorems
- `theorem.continuity-open-preimage` (degree ~8) — used by 4.14, 4.17, and the corollary
- `theorem.continuous-image-compact` (degree ~7) — foundation for 4.15, 4.16, 4.17
- `definition.compact-set` (degree ~5 within Ch4) — key hypothesis for compactness section

## Layering

The chapter exhibits clear layered structure:

1. **Foundation layer**: definitions of limit and continuity in metric spaces (4.1, 4.5)
2. **Bridge layer**: sequential characterization (4.2), limit arithmetic (4.4), composition (4.7)
3. **Topological characterization**: open-preimage theorem (4.8)
4. **Compactness consequences**: 4.14 → 4.15 → 4.16; 4.14 → 4.17; 4.19
5. **Connectedness consequences**: 4.22 → IVT (4.23)
6. **Monotone functions**: 4.29 → corollary → 4.30

## Cross-Chapter Dependencies

- Heavy reliance on Ch2 topology: `definition.compact-set`, `definition.neighborhood-limit-point-open-closed`, `definition.separated-connected`, `theorem.connected-subsets-of-r`, `theorem.heine-borel`, `proposition.compact-is-closed`, `proposition.closed-subset-compact`
- Depends on Ch3 sequences: `proposition.convergent-sequence-properties`, `definition.convergent-sequence`
- Depends on Ch1: `definition.least-upper-bound-property`, `definition.supremum`

## Growth Expectations

Chapter 5 (Differentiation) should heavily use:
- `definition.continuity-metric` and `proposition.continuity-limit-point-equivalence`
- `definition.limit-of-function-metric`
- `theorem.continuous-image-compact` (for extreme values in MVT proofs)
- `theorem.intermediate-value-theorem` (for Darboux-like results)

Expected ~35-50 new entities from Ch5.

## Multi-Source Notes

Only one theorem shared with Stewart in this chapter: the Intermediate Value Theorem.
Most Rudin Ch4 content is in the general metric-space setting, which is strictly more
general than Stewart's real-function formulations. The Stewart nodes remain as
special cases; no restructuring needed.
