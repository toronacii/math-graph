# Chapter 5 — Structural Analysis

## 1. Conceptual Density

Chapter 5 produces 13 statements + 9 proofs = 22 nodes across 5
sections (4.4 per section). All sections contributed new entities.

| Section | Defs | Props | Thms | Cors | Proofs | Density |
|---------|------|-------|------|------|--------|---------|
| 5.1     | 2    | 0     | 0    | 0    | 0      | low     |
| 5.2     | 1    | 2     | 1    | 0    | 3      | high    |
| 5.3     | 0    | 0     | 2    | 0    | 2      | high    |
| 5.4     | 1    | 0     | 1    | 0    | 1      | medium  |
| 5.5     | 0    | 1     | 2    | 0    | 3      | high    |

Section 5.1 is purely definitional (sigma notation, area under curve).
Sections 5.2, 5.3, and 5.5 are the densest, containing the core
integration theorems.

## 2. Dependency Growth

| Metric              | After Ch4 | After Ch5 | Change    |
|---------------------|-----------|-----------|-----------|
| Total nodes         | 183       | 205       | +12%      |
| Total edges         | 194       | 226       | +16%      |
| Largest component   | 144       | 165       | +15%      |
| Isolated nodes      | 36        | 37        | +1        |
| Isolation ratio     | 20%       | 18%       | -2pp      |
| Graph density       | 0.0058    | 0.0054    | -7%       |

The largest component absorbed all new theorem/proof nodes from
Chapter 5, growing from 144 to 165. The only new isolated node is
`definition.sigma-notation`, which is not referenced by any proof.
Graph density decreased slightly due to 4 new definitions that are
not yet consumed.

## 3. Type Distribution

| Type       | Ch4 cumul | Ch5 cumul | Shift                 |
|------------|-----------|-----------|------------------------|
| definition | 55%       | 53%       | slight decrease        |
| proposition| 11%       | 12%       | slight increase        |
| theorem    | 30%       | 32%       | increase (6 new thms)  |
| corollary  | 4%        | 4%        | stable                 |

Theorem proportion increased because Chapter 5 contains major named
results (FTC Parts 1 and 2, Substitution Rule, Net Change Theorem).

## 4. Hub Nodes

| Node                              | Degree | Role                     |
|-----------------------------------|--------|--------------------------|
| theorem.limit-laws                | 17     | Central theorem (Ch2)    |
| definition.derivative-function    | 10     | Foundational def (Ch2)   |
| theorem.chain-rule                | 9      | Differentiation key      |
| proof.ftc-part1.stewart           | 6      | New hub (Ch5)            |
| proof.mean-value-theorem.stewart  | 6      | Critical proof (Ch4)     |
| definition.inverse-function       | 6      | Inverse function key     |
| definition.continuity-on-interval | 5      | Used by EVT, integrals   |

The FTC Part 1 proof emerged as a new hub node with degree 6, drawing
on 5 prior entities (definite-integral, derivative-at-point,
continuity-at-point, squeeze-theorem, integral-comparison).

`theorem.chain-rule` gained one edge (used by substitution-rule proof),
increasing from 8 to 9.

## 5. Key Dependency Chains

### Chain A — FTC chain (new, central)

```
definition.definite-integral
  + definition.derivative-at-point
  + definition.continuity-at-point
  + theorem.squeeze-theorem
  + proposition.integral-comparison
    → theorem.ftc-part1
      + corollary.equal-derivatives-differ-by-constant
        → theorem.ftc-part2
          → theorem.net-change-theorem
```

This is the deepest new chain: definite-integral → FTC1 → FTC2 →
net-change-theorem (4 statement hops through proofs).

### Chain B — Substitution chain (new)

```
theorem.chain-rule + definition.antiderivative
  → theorem.substitution-rule
    + theorem.ftc-part2
      → theorem.substitution-rule-definite
        + definition.even-function + definition.odd-function
          → proposition.integrals-symmetric-functions
```

The substitution rule connects differentiation (chain rule) to
integration, then extends to definite integrals and symmetric functions.

### Chain C — MVT → FTC bridge (cross-chapter)

```
extreme-value-theorem → rolles-theorem → mean-value-theorem
  → zero-derivative-constant → equal-derivatives-differ-by-constant
    → ftc-part2
```

The MVT cascade from Chapter 4 now feeds directly into FTC Part 2,
making it the longest chain in the graph (7+ statement hops).

## 6. Cross-Chapter Dependencies

Chapter 5 proofs reference 11 distinct entities from Chapters 1-4:

| Earlier entity                               | Used by Ch5 proofs         |
|----------------------------------------------|----------------------------|
| definition.continuity-at-point               | FTC1 proof                 |
| definition.continuity-on-interval            | integrability proof        |
| definition.derivative-at-point               | FTC1 proof                 |
| definition.antiderivative                    | FTC2, substitution proofs  |
| definition.even-function                     | symmetric-functions proof  |
| definition.odd-function                      | symmetric-functions proof  |
| theorem.squeeze-theorem                      | FTC1 proof                 |
| theorem.limit-laws                           | integral-properties, comparison proofs |
| theorem.chain-rule                           | substitution-rule proof    |
| corollary.equal-derivatives-differ-by-constant| FTC2 proof                |
| theorem.ftc-part1                            | FTC2 proof (intra-chapter) |

## 7. Growth Expectations

### Chapter 6 — Applications of Integration

Expected impact:

- **Primarily application-oriented.** Area between curves, volumes
  (disks, shells), arc length, surface area, work.
- **Few new theorems.** Most results are definitions + formulas
  derived from the definite integral.
- **Estimated: ~8-12 new nodes, ~10-15 new edges.**
- **Key new definitions:** area between curves, volume of revolution,
  arc length formula, surface area of revolution.
- **No major new theorems expected** — results are applications of FTC
  and the definite integral.
