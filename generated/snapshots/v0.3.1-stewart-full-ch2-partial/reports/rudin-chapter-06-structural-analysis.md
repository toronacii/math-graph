# Rudin Chapter 6 — Structural Analysis

## Overview

Chapter 6 introduces the Riemann-Stieltjes integral, a generalization of the
Riemann integral that unifies summation and integration under a single
framework. The chapter is self-contained in the sense that it builds its own
machinery (partition → upper/lower sums → integrability criterion) and then
derives all results from the criterion.

## Hub Nodes

The extraction introduces a clear hub structure:

1. **`theorem.riemann-stieltjes-integrability-criterion`** — Used by 11 proofs.
   This is the workhorse of the chapter: every integrability result (6.8–6.11)
   and most property proofs (6.12, 6.17, 6.19) depend on it.

2. **`definition.riemann-stieltjes-integral`** — Foundational definition for
   the entire chapter. Referenced by 12 entities.

3. **`theorem.composition-preserves-integrability`** (6.11) — Key enabler for
   6.13 (products, absolute values) and 6.25 (vector norms).

## Layering

The chapter has a clean layered structure:

```
Layer 0: definition.partition, definition.riemann-stieltjes-integral
Layer 1: definition.refinement-partition
Layer 2: theorem.refinement-upper-lower-sums
Layer 3: theorem.lower-leq-upper-integral
Layer 4: theorem.riemann-stieltjes-integrability-criterion (THE hub)
Layer 5: 6.7, 6.8, 6.9, 6.10, 6.11
Layer 6: 6.12, 6.13
Layer 7: 6.15, 6.16, 6.17, 6.19
Layer 8: 6.20, 6.21 (FTC)
Layer 9: 6.22, 6.24, 6.25, 6.27
```

## Cross-Chapter Dependencies

Proofs in this chapter depend on nodes from previous chapters:

- `theorem.compact-uniform-continuity` (Ch4) — used by 6.8, 6.10, 6.11, 6.27
- `theorem.mean-value-theorem` (Ch5) — used by 6.17, 6.21
- `theorem.intermediate-value-theorem` (Ch4) — used by 6.9
- `definition.continuity-metric` (Ch4) — used by 6.10, 6.15, 6.20
- `definition.compact-set` (Ch2) — used by 6.10
- `definition.derivative-at-point` (Ch5) — used by 6.21
- `theorem.comparison-test-series` (Ch3) — used by 6.16

## Growth Expectations

Chapter 7 (Sequences and Series of Functions) will likely:
- Depend heavily on the integrability criterion (6.6) and integral properties (6.12)
- Introduce uniform convergence theorems that interact with integration
- Reference `theorem.continuous-integrable-stieltjes` when integrating uniform limits

Chapter 8 (Some Special Functions) will likely:
- Use change of variable (6.19) and integration by parts (6.22)
- Reference the FTC (6.21) for power series integration
