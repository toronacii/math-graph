# Chapter 7 — Structural Analysis

## 1. Conceptual Density

Chapter 7 produces 5 statements + 3 proofs = 8 nodes across 2
extracted sections (4.0 per section). Six sections were skipped
(methodology/technique sections with no new mathematical entities).

| Section | Defs | Props | Thms | Cors | Proofs | Density |
|---------|------|-------|------|------|--------|---------|
| 7.1     | 0    | 0     | 2    | 0    | 2      | medium  |
| 7.8     | 2    | 0     | 1    | 0    | 1      | medium  |

Section 7.1 introduces integration by parts (indefinite and definite
versions). Section 7.8 introduces improper integrals and the
comparison theorem.

## 2. Dependency Growth

| Metric              | After Ch6 | After Ch7 | Change    |
|---------------------|-----------|-----------|-----------|
| Total nodes         | 212       | 220       | +4%       |
| Total edges         | 233       | 243       | +4%       |
| Largest component   | 168       | 176       | +5%       |
| Isolated nodes      | 41        | 41        | +0        |
| Isolation ratio     | 19%       | 19%       | stable    |
| Graph density       | 0.0052    | 0.0050    | -4%       |

All 8 new nodes joined the main component. No new isolated nodes —
both improper integral definitions are consumed by the comparison
theorem proof. Growth is modest, consistent with this being a
techniques chapter.

## 3. Type Distribution

| Type       | Ch6 cumul | Ch7 cumul | Shift              |
|------------|-----------|-----------|---------------------|
| definition | 54%       | 53%       | slight decrease     |
| proposition| 12%       | 11%       | slight decrease     |
| theorem    | 31%       | 32%       | slight increase     |
| corollary  | 3%        | 3%        | stable              |

## 4. Hub Nodes

No significant hub changes. The integration-by-parts proof connects
to the product rule (Ch3), creating a new cross-chapter link. The
comparison theorem proof connects to integral-comparison (Ch5) and
improper-integral-type1 (Ch7).

## 5. Key Dependency Chains

### Chain A — Integration by parts chain (new)

```
theorem.product-rule + definition.antiderivative
  → theorem.integration-by-parts
    + theorem.ftc-part2
      → theorem.integration-by-parts-definite
```

Integration by parts is the integration counterpart of the product
rule, just as the substitution rule (Ch5) is the counterpart of the
chain rule.

### Chain B — Comparison theorem (new)

```
definition.improper-integral-type1 + proposition.integral-comparison
  → theorem.comparison-theorem-integrals
```

The comparison theorem for improper integrals extends the finite
comparison property to infinite intervals. This pattern will be
echoed in Chapter 11 (series).

## 6. Cross-Chapter Dependencies

| Earlier entity                  | Used by Ch7 proofs               |
|---------------------------------|----------------------------------|
| theorem.product-rule            | integration-by-parts proof       |
| definition.antiderivative       | integration-by-parts proof       |
| definition.indefinite-integral  | integration-by-parts proof       |
| theorem.ftc-part2               | IBP-definite proof               |
| proposition.integral-comparison | comparison-theorem proof         |

## 7. Growth Expectations

### Chapter 8 — Further Applications of Integration

Expected impact:

- **Primarily application-oriented.** Arc length, area of surfaces
  of revolution, applications to physics and engineering.
- **Few new entities.** Definitions of arc length, surface area.
- **Estimated: ~3-6 new nodes.**

### Chapters 9-10 — Differential Equations & Parametric/Polar

- **Chapter 9:** Separable equations, direction fields, Euler's method,
  exponential growth/decay. Mostly methodology.
- **Chapter 10:** Parametric curves, polar coordinates, conic sections.
  Several new definitions expected.

### Chapter 11 — Infinite Sequences and Series

- **Most entity-dense remaining chapter.** Convergence definitions,
  convergence tests (comparison, ratio, root, alternating series),
  power series, Taylor/Maclaurin series, Taylor's theorem.
- **Estimated: 30-50 new nodes.**
