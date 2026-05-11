# Milestone: Rudin Chapter 5 — Differentiation

**Date:** 2026-05-11
**Status:** Complete

## Summary

Extracted all mathematical content from Chapter 5 of Rudin's *Principles of
Mathematical Analysis* (3rd edition).

## Statistics

| Metric | Value |
|--------|-------|
| New statements | 6 |
| New proofs | 15 |
| Total new entities | 21 |
| Shared statements updated | 13 |
| Reclassifications | 0 |
| Cumulative nodes | 527 |
| Cumulative edges | 687 |

## Entities Extracted

### Shared with Stewart (source + proof added)

**Definitions (4):**
- `definition.derivative-at-point` (5.1)
- `definition.local-maximum` (5.7)
- `definition.local-minimum` (5.7)
- `definition.second-derivative` (5.14)

**Theorems/Propositions/Corollaries (9):**
- `theorem.differentiable-implies-continuous` (5.2)
- `theorem.product-rule` (5.3b)
- `theorem.quotient-rule` (5.3c)
- `theorem.chain-rule` (5.5)
- `theorem.fermat-theorem` (5.8)
- `theorem.mean-value-theorem` (5.10)
- `theorem.lhopitals-rule` (5.13)
- `proposition.increasing-decreasing-test` (5.11a,c)
- `corollary.zero-derivative-constant` (5.11b)

### New Entities

**Theorems (5):**
- `theorem.derivative-sum-rule` (5.3a)
- `theorem.generalized-mean-value-theorem` (5.9)
- `theorem.darboux-theorem` (5.12)
- `theorem.taylor-theorem` (5.15)
- `theorem.mean-value-inequality-vector` (5.19)

**Corollaries (1):**
- `corollary.derivative-no-simple-discontinuities` (after 5.12)

## Key Decisions

- **High overlap chapter**: 13 shared statements vs 6 new — differentiation on R
  is essentially the same subject in both books
- **No Rolle's theorem from Rudin**: Rudin goes directly to the generalized MVT,
  bypassing Rolle's as a separate result
- **Generalized MVT as new node**: Stewart mentions it implicitly in L'Hospital's
  proof but doesn't give it a theorem number
- **Taylor's theorem vs Taylor series**: `theorem.taylor-theorem` (finite
  approximation with Lagrange remainder) is distinct from Stewart's
  `theorem.taylor-convergence` (infinite series convergence)
- **Local max/min**: Added Rudin source to existing nodes despite Rudin defining
  on metric spaces — on R they are logically equivalent

## Validation

- `scripts.validate`: pass
- `scripts.build_graph`: pass (527 nodes, 687 edges)
- All integrity checks: pass
