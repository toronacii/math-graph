# Chapter 6 — Structural Analysis

## 1. Conceptual Density

Chapter 6 produces 6 statements + 1 proof = 7 nodes across 4
extracted sections (1.75 per section). Section 6.4 was skipped
(physics application, no new mathematical entities).

| Section | Defs | Props | Thms | Cors | Proofs | Density |
|---------|------|-------|------|------|--------|---------|
| 6.1     | 1    | 0     | 0    | 0    | 0      | low     |
| 6.2     | 2    | 0     | 0    | 0    | 0      | low     |
| 6.3     | 1    | 0     | 0    | 0    | 0      | low     |
| 6.5     | 1    | 0     | 1    | 0    | 1      | medium  |

This is the lightest chapter so far. Most sections introduce
application formulas (definitions) without new theorems. The only
theorem is the Mean Value Theorem for Integrals in section 6.5.

## 2. Dependency Growth

| Metric              | After Ch5 | After Ch6 | Change    |
|---------------------|-----------|-----------|-----------|
| Total nodes         | 205       | 212       | +3%       |
| Total edges         | 226       | 233       | +3%       |
| Largest component   | 165       | 168       | +2%       |
| Isolated nodes      | 37        | 41        | +4        |
| Isolation ratio     | 18%       | 19%       | +1pp      |
| Graph density       | 0.0054    | 0.0052    | -4%       |

Growth is minimal. Four of the five new definitions are isolated
nodes (area-between-curves, volume-by-cross-sections,
volume-of-revolution, volume-by-cylindrical-shells) — they are
application formulas not referenced by any proof. Only the MVT
for Integrals and its proof joined the main component.

## 3. Type Distribution

| Type       | Ch5 cumul | Ch6 cumul | Shift              |
|------------|-----------|-----------|---------------------|
| definition | 53%       | 54%       | slight increase     |
| proposition| 12%       | 12%       | stable              |
| theorem    | 32%       | 31%       | slight decrease     |
| corollary  | 4%        | 3%        | stable              |

Definition proportion increased slightly due to 5 new definitions
with only 1 new theorem.

## 4. Hub Nodes

| Node                                       | Degree | Role                       |
|--------------------------------------------|--------|----------------------------|
| theorem.limit-laws                         | 17     | Central theorem (Ch2)      |
| definition.derivative-function             | 10     | Foundational def (Ch2)     |
| theorem.chain-rule                         | 9      | Differentiation key        |
| proof.mean-value-theorem-integrals.stewart | 7      | New hub (Ch6)              |
| proof.ftc-part1.stewart                    | 6      | FTC proof (Ch5)            |
| definition.continuity-on-interval          | 6      | Continuity key             |
| proof.mean-value-theorem.stewart           | 6      | MVT proof (Ch4)            |

The MVT for Integrals proof is a new hub node with degree 7 — it
draws on 6 prior entities (definite-integral, continuity-on-interval,
average-value-of-function, extreme-value-theorem,
intermediate-value-theorem, integral-comparison).

This is notable because the IVT (previously unused by any proof)
now has its first downstream consumer.

## 5. Key Dependency Chains

### Chain A — MVT for Integrals (new)

```
definition.definite-integral
  + definition.continuity-on-interval
  + theorem.extreme-value-theorem
  + theorem.intermediate-value-theorem
  + proposition.integral-comparison
  + definition.average-value-of-function
    → theorem.mean-value-theorem-integrals
```

This is the first theorem to use both the EVT and the IVT in its
proof, connecting two previously independent weak dependencies.

## 6. Cross-Chapter Dependencies

Chapter 6 proofs reference 6 entities from Chapters 2-5:

| Earlier entity                         | Used by Ch6 proofs             |
|----------------------------------------|--------------------------------|
| definition.definite-integral           | MVT for Integrals proof        |
| definition.continuity-on-interval      | MVT for Integrals proof        |
| theorem.extreme-value-theorem          | MVT for Integrals proof        |
| theorem.intermediate-value-theorem     | MVT for Integrals proof        |
| proposition.integral-comparison        | MVT for Integrals proof        |
| definition.average-value-of-function   | MVT for Integrals proof (Ch6)  |

## 7. Growth Expectations

### Chapter 7 — Techniques of Integration

Expected impact:

- **Integration techniques.** Integration by parts, trigonometric
  integrals, trigonometric substitution, partial fractions, improper
  integrals.
- **Key new entities.** Integration by parts formula (theorem),
  improper integral definitions (two types), comparison theorem for
  improper integrals.
- **Estimated: ~8-15 new nodes, ~10-20 new edges.**
- **Most sections are methodology** (trig integrals, trig substitution,
  partial fractions) with few new graph-worthy entities.
