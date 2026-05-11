# Chapter 11 — Structural Analysis

## 1. Conceptual Density

Chapter 11 produces 18 statements + 13 proofs = 31 nodes across 9
extracted sections (3.4 per section). Two sections were skipped
(methodology overview, applications). This is the densest chapter
in the book by total nodes and edges.

| Section | Defs | Props | Thms | Cors | Proofs | Density |
|---------|------|-------|------|------|--------|---------|
| 11.1    | 1    | 0     | 1    | 0    | 1      | medium  |
| 11.2    | 1    | 0     | 2    | 0    | 2      | high    |
| 11.3    | 0    | 0     | 1    | 0    | 1      | medium  |
| 11.4    | 0    | 0     | 2    | 0    | 2      | high    |
| 11.5    | 0    | 0     | 1    | 0    | 1      | medium  |
| 11.6    | 1    | 0     | 3    | 0    | 3      | high    |
| 11.8    | 1    | 0     | 1    | 0    | 1      | medium  |
| 11.9    | 0    | 0     | 1    | 0    | 1      | medium  |
| 11.10   | 1    | 0     | 1    | 0    | 1      | medium  |

## 2. Dependency Growth

| Metric              | After Ch10 | After Ch11 | Change    |
|---------------------|------------|------------|-----------|
| Total nodes         | 235        | 266        | +13%      |
| Total edges         | 248        | 293        | +18%      |
| Largest component   | 180        | 210        | +17%      |
| Isolated nodes      | 53         | 53         | +0        |
| Isolation ratio     | 23%        | 20%        | -3pp      |
| Graph density       | 0.0045     | 0.0042     | -7%       |

The largest component absorbed all 31 new nodes — no new isolated
nodes. This dramatically improved the isolation ratio from 23% to
20%. Edge growth (+18%) outpaced node growth (+13%), indicating
dense internal connectivity.

## 3. Type Distribution (Final)

| Type       | Cumulative | Percentage |
|------------|-----------|------------|
| definition | 98        | 54%        |
| proposition| 18        | 10%        |
| theorem    | 61        | 34%        |
| corollary  | 5         | 3%         |
| proof      | 84        | —          |

## 4. Hub Nodes (Final)

| Node                                       | Degree | Role                       |
|--------------------------------------------|--------|----------------------------|
| theorem.limit-laws                         | 17     | Central theorem (Ch2)      |
| theorem.chain-rule                         | 10     | Differentiation key (Ch3)  |
| definition.derivative-function             | 10     | Foundational def (Ch2)     |
| proof.mean-value-theorem-integrals.stewart | 7      | MVT-integrals proof (Ch6)  |
| definition.infinite-series                 | 6      | Series foundation (Ch11)   |
| theorem.comparison-test-series             | 6      | Series hub (Ch11)          |
| definition.continuity-on-interval          | 6      | Continuity key             |
| proof.mean-value-theorem.stewart           | 6      | MVT proof (Ch4)            |

Two Chapter 11 entities emerged as hubs: `definition.infinite-series`
(degree 6) and `theorem.comparison-test-series` (degree 6). The
comparison test is the foundational convergence tool used by
absolute-convergence, ratio test, root test, and limit comparison.

## 5. Key Dependency Chains

### Chain A — Convergence test hierarchy (new, central)

```
definition.sequence
  → theorem.monotonic-sequence-theorem
    → theorem.comparison-test-series
      → theorem.limit-comparison-test
      → theorem.absolute-convergence-implies-convergence
        → theorem.ratio-test
        → theorem.root-test
```

The Monotonic Sequence Theorem (via completeness) feeds the
Comparison Test, which is the foundation for all other convergence
tests.

### Chain B — Geometric series branches

```
definition.infinite-series + definition.sequence
  → theorem.geometric-series
    → theorem.ratio-test (comparison with geometric)
    → theorem.root-test (comparison with geometric)
    → theorem.power-series-convergence
```

### Chain C — Taylor convergence chain

```
definition.taylor-series
  + theorem.mean-value-theorem (from Ch4)
  + theorem.squeeze-theorem (from Ch2)
    → theorem.taylor-convergence
```

Taylor's theorem connects back to the MVT, creating a cross-chapter
dependency from differentiation to series.

### Chain D — Power series chain

```
definition.power-series
  → theorem.power-series-convergence
    → theorem.power-series-differentiation-integration
      → definition.taylor-series
        → theorem.taylor-convergence
```

## 6. Cross-Chapter Dependencies

Chapter 11 proofs reference 5 entities from Chapters 2-5:

| Earlier entity                  | Used by Ch11 proofs              |
|---------------------------------|----------------------------------|
| proposition.integral-comparison | integral-test proof              |
| definition.improper-integral-type1 | integral-test proof           |
| theorem.mean-value-theorem      | taylor-convergence proof         |
| theorem.squeeze-theorem         | taylor-convergence proof         |

## 7. Final Graph Summary

With Chapter 11 complete, all 11 chapters of Stewart's single-variable
calculus have been processed.

**Final statistics:**
- 266 nodes (182 statements + 84 proofs)
- 293 edges (209 uses + 84 proves)
- 210 nodes in the main component (79%)
- 53 isolated nodes (20%, mostly Ch1 definitions and Ch10 geometry)
- Longest dependency chain: ~10+ hops (EVT → ... → Taylor)
