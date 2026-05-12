# Chapter 3 — Structural Analysis

## 1. Conceptual Density

Chapter 3 produces 27 statements + 24 proofs = 51 nodes across 6
sections (8.5 per section), the highest density so far. The composition
shifted decisively toward theorems:

| Section | Defs | Props | Thms | Cors | Proofs | Density |
|---------|------|-------|------|------|--------|---------|
| 3.1     | 1    | 0     | 5    | 0    | 6      | high    |
| 3.2     | 0    | 0     | 2    | 0    | 2      | high    |
| 3.3     | 0    | 0     | 6    | 0    | 6      | high    |
| 3.4     | 0    | 0     | 1    | 1    | 2      | high    |
| 3.5     | 1    | 0     | 3    | 0    | 3      | high    |
| 3.6     | 1    | 0     | 5    | 1    | 5      | high    |

Every section is proof-dense. Section 3.3 is the most prolific,
generating 6 trig derivative theorems. Section 3.6 closes the
exponential/logarithmic derivative cycle.

## 2. Dependency Growth

| Metric              | After Ch2 | After Ch3 | Change    |
|---------------------|-----------|-----------|-----------|
| Total nodes         | 95        | 146       | +54%      |
| Total edges         | 58        | 146       | +152%     |
| Largest component   | 27        | 100       | +270%     |
| Isolated nodes      | 36        | 35        | -3%       |
| Isolation ratio     | 38%       | 24%       | -14pp     |
| Graph density       | 0.0065    | 0.0069    | +6%       |

Edge growth (+152%) vastly outpaced node growth (+54%), confirming
Chapter 3's role as a connectivity chapter. The largest connected
component exploded from 27 to 100 nodes, absorbing nearly all
Chapter 2 theorem/proof structures. Density increased despite the
quadratic denominator because Chapter 3 proofs reference many
earlier entities.

## 3. Type Distribution Shift

| Type       | Ch2 cumul | Ch3 cumul | Shift                   |
|------------|-----------|-----------|-------------------------|
| definition | 73%       | 57%       | continued thinning      |
| proposition| 12%       | 9%        | relative decrease       |
| theorem    | 11%       | 31%       | major increase          |
| corollary  | 1.3%      | 3%        | growing                 |
| proof      | 27%       | 43%       | approaching parity      |

The graph has crossed a structural inflection point: theorems now
represent 31% of statement nodes, up from 11% after Chapter 2.
This reflects the shift from vocabulary-building to result-proving.

## 4. Hub Nodes

| Node                              | Degree | Role                  |
|-----------------------------------|--------|-----------------------|
| theorem.limit-laws                | 14     | Central theorem       |
| definition.derivative-function    | 10     | Foundational def      |
| theorem.chain-rule                | 8      | Differentiation key   |
| definition.inverse-function       | 6      | Inverse function key  |
| theorem.quotient-rule             | 5      | Derivation tool       |
| theorem.derivative-sin            | 5      | Trig derivative root  |
| theorem.derivative-cos            | 5      | Trig derivative root  |

`theorem.limit-laws` remains the most connected node in the graph,
now feeding 14 edges. `definition.derivative-function` emerged as the
second hub — it feeds directly into 10 proofs (constant, power,
constant-multiple, sum, product, quotient, sin, cos, exponential).

`theorem.chain-rule` is the new structural keystone for Chapter 3:
it feeds implicit differentiation proofs (arcsin, arccos, arctan),
logarithmic derivatives, and the general exponential derivative.

## 5. Proof Topology

| Style          | Count | Change from Ch2 |
|----------------|-------|-----------------|
| direct         | 36    | +25             |
| epsilon-delta  | 4     | +0              |
| assumed        | 2     | +0              |
| algebraic      | 1     | +0              |
| geometric      | 1     | +0              |

All 24 new proofs are style: direct. This is expected for
differentiation rules, which follow from definition + algebraic
manipulation + prior rules. No new assumed or low-confidence proofs.

Confidence shift:

| Confidence | Ch2  | Ch3  | Change |
|------------|------|------|--------|
| high       | 1    | 24   | +23    |
| medium     | 16   | 17   | +1     |
| low        | 3    | 3    | +0     |

Chapter 3 dramatically improved the confidence profile: 23 new
high-confidence proofs vs only 1 new medium-confidence proof
(power rule, where the general case is deferred to 3.6).

## 6. Cross-Chapter Dependencies

Chapter 3 proofs reference 12 distinct entities from Chapters 1-2:

| Ch1/Ch2 entity                         | Used by Ch3 proofs (count) |
|----------------------------------------|---------------------------|
| definition.derivative-function         | 10                        |
| theorem.limit-laws                     | 8                         |
| theorem.differentiable-implies-continuous | 3                      |
| definition.inverse-function            | 4                         |
| theorem.limit-sinx-over-x             | 2                         |
| corollary.limit-cosx-minus-1-over-x   | 2                         |
| definition.absolute-value              | 1                         |
| definition.natural-exponential-function| 1                         |
| definition.natural-logarithm           | 1                         |
| proposition.change-of-base-formula     | 1                         |

This confirms the extraction design: Chapter 1-2 definitions and
theorems serve as reusable foundations. The sinx/x cascade extended
as predicted: epsilon-delta -> squeeze -> sinx/x -> d/dx sin -> d/dx tan -> d/dx arctan.

## 7. Graph Layering

The graph now exhibits five natural layers:

```
Layer 0: Foundational definitions (function, domain, range...)
Layer 1: Structural definitions (limit, continuity, derivative)
Layer 2: Core theorems (limit laws, squeeze, IVT)
Layer 3: Special limits (sinx/x, cosx-1/x) + diff->cont
Layer 4: Differentiation rules (power, product, quotient, chain, trig, log)
Layer 5: Derived derivatives (arcsin, arccos, arctan, general exponential)
```

The longest chain now spans 11 edges (5 statement hops):
epsilon-delta -> squeeze -> sinx/x -> d/dx sin -> d/dx tan -> d/dx arctan.

## 8. Growth Expectations

### Chapter 4 — Applications of Differentiation

Expected impact:

- **Theorem-heavy.** Mean Value Theorem, Rolle's Theorem, L'Hopital's
  Rule, first/second derivative tests, optimization theorems.
- **First lemmas.** Rolle's Theorem is a lemma for MVT; Fermat's
  Theorem (local extrema) is a lemma for both.
- **Deep dependency chains.** MVT proof will reference
  differentiable-implies-continuous + Rolle's; L'Hopital may use
  Cauchy's MVT variant.
- **Estimated: ~15-20 new nodes, ~30-40 new edges.**
- **Fan-in increase.** L'Hopital's Rule proof likely references 4+
  prior results.

### Chapter 5 — Integrals

Expected impact:

- **New definitional layer.** Riemann sums, definite integral,
  antiderivative, indefinite integral.
- **Fundamental Theorem of Calculus.** Two parts, each theorem + proof.
  Will reference continuity, derivative definition, IVT.
- **Estimated: ~20-25 new nodes, ~30-40 new edges.**
