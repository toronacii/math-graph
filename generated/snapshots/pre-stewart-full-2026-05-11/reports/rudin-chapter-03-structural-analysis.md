# Rudin Chapter 3 — Structural Analysis

## Overview

Chapter 3 (Numerical Sequences and Series) is the largest Rudin chapter extracted so far,
contributing 77 entities (44 statements + 33 proofs). It establishes the foundational
theory of convergence for sequences and series in metric spaces and R^k.

## Hub Nodes

- **proposition.cauchy-criterion-series** (degree 6): Referenced by 5 proof files as a
  dependency. Central to all series convergence tests.
- **proposition.convergent-sequence-properties** (degree 4): Basic properties used by
  algebraic limit theorem, special sequences, and monotone convergence.
- **theorem.dirichlet-test** (degree 3): Powers both alternating series test and
  power series boundary convergence.
- **definition.convergent-sequence** (degree ~10): Foundational definition referenced
  throughout the chapter.

## Layering

The chapter has clear dependency layers:

1. **Layer 0 (Foundations)**: Definitions — convergent-sequence, subsequence,
   cauchy-sequence, diameter, complete, monotonic, upper-lower-limits
2. **Layer 1 (Sequence Theory)**: convergent-sequence-properties, algebraic-limit,
   convergence-in-rk, subsequence-compact, subsequential-limits-closed,
   diameter-properties, cauchy-criterion, monotone-convergence
3. **Layer 2 (Series Foundations)**: cauchy-criterion-series, nonnegative-series-bounded,
   comparison-test, geometric-series, divergence-test
4. **Layer 3 (Convergence Tests)**: cauchy-condensation, p-series, root-test, ratio-test,
   summation-by-parts, dirichlet-test, alternating-series
5. **Layer 4 (Advanced)**: power-series-boundary, mertens, riemann-rearrangement,
   absolute-convergence-rearrangement, e-as-limit, e-is-irrational

## Cross-Chapter Dependencies

13 unique dependencies to Ch1/Ch2 entities. Primary imports:
- From Ch2: compact-set, neighborhood-limit-point-open-closed, k-cell-compact,
  Bolzano-Weierstrass, nested-compact-nonempty
- From Ch1: supremum, archimedean-density, euclidean-k-space

## Multi-Source Convergence

8 theorems are now shared between Stewart and Rudin, each with independent proofs.
This validates the multi-source architecture: same mathematical truth, different
proof pathways, different pedagogical contexts.

## Growth Expectations

Chapter 4 (Continuity) will heavily depend on:
- definition.convergent-sequence
- theorem.cauchy-criterion
- definition.complete-metric-space
- definition.compact-set

Expected ~40-60 new entities for Ch4.
