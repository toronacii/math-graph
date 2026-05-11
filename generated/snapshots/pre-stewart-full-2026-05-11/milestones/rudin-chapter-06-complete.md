# Milestone: Rudin Chapter 6 Complete

**Date**: 2026-05-11
**Source**: Walter Rudin — *Principles of Mathematical Analysis*, 3rd ed.
**Chapter**: 6 — The Riemann-Stieltjes Integral

## Summary

- **Entities extracted**: 46 (6 definitions, 19 theorems, 1 proposition, 20 proofs)
- **Reclassifications**: 1 (theorem → proposition for 6.7 consequences)
- **Multi-source merges**: 0
- **Validation**: passed
- **Graph**: 573 nodes, 767 edges

## Key Decisions

1. **No merges with Stewart**: All Rudin Ch6 results are formulated for the
   Riemann-Stieltjes integral, making them strictly more general than
   Stewart's Riemann-only versions. Per multi-source rules, strictly more
   general results get separate nodes.

2. **FTC naming**: Rudin's FTC (6.21) gets `theorem.fundamental-theorem-of-calculus`
   as the standard analysis name. Stewart's versions remain as `theorem.ftc-part1`
   and `theorem.ftc-part2` (calculus-textbook split).

3. **Bundled definition for R-S integral**: Definitions 6.1 and 6.2 are combined
   into a single `definition.riemann-stieltjes-integral` node since 6.1 is
   immediately subsumed by 6.2 (alpha(x) = x is just a special case).

4. **Reclassification of 6.7**: Rudin labels it "Theorem" but its role in the
   graph is as a toolkit proposition — it provides reusable consequences of
   the integrability criterion that other proofs invoke.

## Context Pack Validation

This extraction was the first to use the context-pack system for
retrieval-oriented extraction. See the extraction report for evaluation.

## Verification

```
python -m scripts.validate    → OK
python -m scripts.build_graph → 573 nodes, 767 edges, all checks passed
```
