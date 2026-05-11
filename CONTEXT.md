# MKG Project Context — Cumulative State

> Document for handoff to another LLM or collaborator.
> Generated: 2026-05-11

---

## 1. What Is This Project?

A **Mathematical Knowledge Graph (MKG)**: a dependency graph of mathematical
knowledge extracted from textbooks. Each node is either a **statement** (axiom,
definition, lemma, proposition, theorem, corollary, conjecture) or a **proof**.
Statements connect to other statements only *through* proofs:

```
Statement → Proof → Statement
```

The graph is stored as YAML files (one per entity), validated with Pydantic
schemas, and built into a SQLite index + JSON graph for visualization.

**NOT a proof assistant.** We track dependency structure, not formal derivations.

---

## 2. Repository Structure

```
data/
  statements/     # 320 YAML files (one per statement)
  proofs/         # 186 YAML files (one per proof)
sources/          # source-book metadata + chapter PDFs
schema/           # Pydantic models
scripts/
  validate.py     # schema + integrity validation
  build_graph.py  # delegates to build_db.py
  build_db.py     # YAML → SQLite → validate → graph outputs
  split_pdf.py    # splits Rudin PDF into chapter files
generated/
  graph/          # graph.json, node-details.json, math_graph.db (gitignored)
  exports/        # graph.graphml
visualization/
  web/public/     # graph.json + node-details.json for web viewer
tests/            # 18 pytest tests
reports/          # per-chapter statistics, structural analysis, weak deps
milestones/       # per-chapter completion records
```

---

## 3. Cumulative Graph State

| Metric | Value |
|--------|-------|
| **Total nodes** | 527 |
| **Total edges** | 687 |
| Statements | 326 |
| Proofs | 201 |
| Definitions | 143 |
| Propositions | 43 |
| Theorems | 123 |
| Lemmas | 2 |
| Corollaries | 15 |
| Uses edges | 486 |
| Proved-by edges | 201 |

---

## 4. Sources Processed

### Stewart — *Calculo de una variable: Trascendentes tempranas* (7th ed.)

All 11 chapters extracted:

| Ch | Title | Entities |
|----|-------|----------|
| 1 | Functions and Models | ~30 |
| 2 | Limits and Derivatives | ~25 |
| 3 | Differentiation Rules | ~30 |
| 4 | Applications of Differentiation | ~20 |
| 5 | Integrals | ~25 |
| 6 | Applications of Integration | ~15 |
| 7 | Techniques of Integration | ~20 |
| 8 | Further Applications of Integration | ~10 |
| 9 | Differential Equations | ~15 |
| 10 | Parametric Equations and Polar Coordinates | ~20 |
| 11 | Infinite Sequences and Series | 31 |

**Total from Stewart**: 266 nodes (182 statements + 84 proofs), 293 edges.

Content language: primarily Spanish (original textbook), with English translations.
Confidence: mixed (56 high, 21 medium, 7 low). 12 weak proofs identified.

### Rudin — *Principles of Mathematical Analysis* (3rd ed., 1976)

Chapters 1-5 extracted:

| Ch | Title | New Entities |
|----|-------|-------------|
| 1 | The Real and Complex Number Systems | 52 (16 def, 5 prop, 12 thm, 1 cor, 18 proofs) |
| 2 | Basic Topology | 72 (12 def, 10 prop, 12 thm, 2 lem, 6 cor, 30 proofs) |
| 3 | Numerical Sequences and Series | 77 (10 def, 9 prop, 25 thm, 33 proofs) |
| 4 | Continuity | 49 (8 def, 1 prop, 16 thm, 3 cor, 21 proofs) |
| 5 | Differentiation | 21 (5 thm, 1 cor, 15 proofs) + 13 shared updated |

**Total from Rudin (Ch1-5)**: 271 entities. All confidence: high.

Content language: English. No weak dependencies.

---

## 5. Multi-Source Architecture

When the same mathematical truth appears in both sources:
- **Same node**: add the second source to `sources` list, add a new proof node.
- **Different generality**: create SEPARATE nodes (e.g., Stewart's EVT on [a,b] vs Rudin's EVT on compact metric spaces).

### Shared Theorems (across Stewart + Rudin)

From Ch3:
- comparison-test-series, geometric-series, divergence-test, root-test, ratio-test,
  absolute-convergence-implies-convergence, alternating-series-test,
  power-series-convergence, monotonic-sequence-theorem

From Ch4:
- intermediate-value-theorem

From Ch5:
- differentiable-implies-continuous, product-rule, quotient-rule, chain-rule,
  fermat-theorem, mean-value-theorem, lhopitals-rule,
  increasing-decreasing-test, zero-derivative-constant

**Total shared**: 19 theorems/propositions/corollaries with dual sources and independent proofs.

---

## 6. Key Reclassifications

During extraction, entity types are reviewed against the Entity Classification Guide
(see AGENTS.md). Notable reclassifications:

### Rudin Ch3 (7 theorem→proposition)
- convergent-sequence-properties, nonnegative-series-bounded,
  cauchy-criterion-series, special-sequence-limits, convergence-in-rk,
  diameter-properties, root-test-stronger-than-ratio

### Rudin Ch4 (1 theorem→proposition)
- continuity-limit-point-equivalence

---

## 7. Pipeline & Tooling

### Per-Chapter Pipeline (4 phases)
1. **Extract**: read chapter, identify statements + proofs, create YAML files
2. **Validate**: `uv run python -m scripts.validate`
3. **Reclassify**: review types against Entity Classification Guide
4. **Reports**: `uv run python -m scripts.build_graph`, generate reports/milestone, sync viz

### CI Pipeline (`.github/workflows/validate.yml`)
```
ruff check → pytest → validate.py → build_graph.py → upload artifact
```

### Build Pipeline (`scripts/build_db.py`)
```
YAML → Pydantic models → SQLite (math_graph.db) → integrity checks → graph.json + node-details.json + graph.graphml
```

### Key Commands
```bash
uv run python -m scripts.validate    # schema + integrity
uv run python -m scripts.build_graph # full build pipeline
uv run ruff check .                  # lint
uv run pytest                        # 18 tests
```

---

## 8. YAML Schema (by example)

### Statement
```yaml
id: theorem.intermediate-value-theorem
type: theorem
status: draft

title:
  en: Intermediate Value Theorem
  es: Teorema del valor intermedio

statement:
  natural:
    en: >
      Suppose that f is continuous on [a, b] and let N be any number
      between f(a) and f(b). Then there exists c in (a,b) such that f(c) = N.
  latex: |
    f \text{ continuous on } [a,b] \implies \exists c \in (a,b): f(c) = N

proved_by:
  - proof.intermediate-value-theorem.stewart
  - proof.intermediate-value-theorem.rudin

sources:
  - work: Calculo de una variable — Trascendentes tempranas
    author: James Stewart
    edition: "7"
    chapter: "2"
    section: "2.5"
  - work: Principles of Mathematical Analysis
    author: Walter Rudin
    edition: "3"
    chapter: "4"
    section: "4.23"

confidence: high
```

### Proof
```yaml
id: proof.intermediate-value-theorem.rudin
type: proof

proves: theorem.intermediate-value-theorem

uses:
  - theorem.continuous-image-connected
  - theorem.connected-subsets-of-r

sources:
  - work: Principles of Mathematical Analysis
    author: Walter Rudin
    edition: "3"
    chapter: "4"
    section: "4.23"

confidence: high
```

---

## 9. ID Conventions

```
<type>.<normalized-name>                    # statements
proof.<statement-name>.<source-or-style>    # proofs
```

Examples:
- `definition.compact-set`
- `theorem.heine-borel`
- `proposition.convergent-sequence-properties`
- `proof.heine-borel.rudin`

IDs: lowercase ASCII, dots and hyphens only.

---

## 10. Hub Nodes (highest degree)

- `definition.neighborhood-limit-point-open-closed` (degree 11)
- `theorem.limit-laws` (degree 17)
- `definition.continuity-metric` (degree ~12)
- `theorem.continuity-open-preimage` (degree ~8)
- `theorem.continuous-image-compact` (degree ~7)
- `definition.compact-set` (degree ~10)

---

## 11. Deferred Items

- `proof.abel-cauchy-product.rudin`: Theorem 3.51 stated in Ch3, proof deferred to Ch8.

---

## 12. Next Steps

1. **Rudin Chapter 6** — The Riemann-Stieltjes Integral
2. **Rudin Chapter 7** — Sequences and Series of Functions
3. Continue through Rudin Chapters 8-11
3. Continue through Rudin Chapters 7-11

---

## 13. Rules Reference

All extraction rules, entity classification guide, multi-source disambiguation
guide, and pipeline details are in **AGENTS.md** (605 lines). That file is the
authoritative reference for how to extend the graph.
