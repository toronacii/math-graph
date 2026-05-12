# Chapter 4 — Applications of the Derivative — Structural Analysis

**Rerun:** `v0.3.1-stewart-full`
**Snapshot:** `v0.3.1-stewart-full-ch04`
**Generated:** 2026-05-11
**Cumulative graph (Ch1+Ch2+Ch3+Ch4):** 209 nodes, 636 edges, 1
connected component, density 0.0146

---

## 1. What Chapter 4 Adds to the Graph

Chapter 4 is the first *applied* chapter of Stewart Calculus: the
derivative machinery built in Ch3 is turned outward to study
extrema, monotonicity, concavity, indeterminate forms, root finding
and antidifferentiation. The chapter contributes 27 new statements
and 9 new proofs across 9 sections, expanding the cumulative graph
from 173 → 209 nodes (+21%) and 495 → 636 edges (+28%). The
node:edge ratio continues to favor edges, confirming the expected
pattern of an applied chapter: most new content *consumes* prior
infrastructure (Ch2 limits/continuity, Ch3 derivative rules) instead
of introducing new primitives.

Three sections add no formal entities at all (§4.6 graphing with
calculators; §4.7 optimization word-problems; §4.5 contributes only
`definition.slant-asymptote`) — these are pedagogical/methodological
sections whose content is procedural, not propositional. The bulk of
Ch4's mathematical mass concentrates in §4.1 (10 stmts), §4.2
(4 stmts + 4 proofs), §4.3 (7 stmts + 3 proofs) and §4.9 (3 stmts +
1 proof).

The chapter's *spine* is the chain Fermat → Rolle → MVT → zero-
derivative-implies-constant → corollary → first/second-derivative
tests → general-antiderivative. Every theorem in this spine is
either proved in-chapter or already had its dependencies in place.
The sole exception — the Extreme Value Theorem — is stated without
proof and explicitly deferred to Apéndice F.

## 2. Per-Section Topology

| Section | New stmts | New proofs | Local hub | Notes |
|---------|-----------|-----------|-----------|-------|
| 4.1     | 10        | 1         | `theorem.fermat`, `theorem.extreme-value-theorem` | Defines absolute/local extrema, critical numbers; EVT stated without proof |
| 4.2     | 4         | 4         | `theorem.mean-value-theorem` | MVT proved from Rolle; corollary chain to "+ C" |
| 4.3     | 7         | 3         | `proposition.increasing-decreasing-test` | Concavity split into two atomic siblings; first/second-derivative tests |
| 4.4     | 1         | 0         | `theorem.l-hospital-rule` | Stated, not proved (Apéndice F) |
| 4.5     | 1         | 0         | `definition.slant-asymptote` | Rest of section is procedural curve-sketching guide |
| 4.6     | 0         | 0         | — | Graphing methodology only |
| 4.7     | 0         | 0         | — | Optimization word-problems — no new entities |
| 4.8     | 1         | 0         | `definition.newton-iteration` | Modeled as constructive scheme; convergence deferred to §11.11 Ex 39 |
| 4.9     | 3         | 1         | `definition.antiderivative`, `theorem.general-antiderivative` | Foundation for Ch5 (FTC) and Ch9 (ODEs); table-of-formulas as bundled proposition |

## 3. New Hubs Introduced in Ch4

Three Ch4 nodes immediately enter the working-hub tier (combined
in-degree ≥ 3) and will continue to grow in Ch5–Ch9:

1. **`definition.local-maximum`** (combined score 10). Used by
   Fermat's theorem, the EVT corollary chain, the closed-interval
   method, and both first- and second-derivative tests. Its sibling
   `definition.local-minimum` has score 9. Together they form the
   single most-referenced sibling pair introduced in Ch4.

2. **`theorem.mean-value-theorem`** (combined score 3, but every
   inbound edge is `essential` in a proof). MVT is the *fulcrum*
   of Ch4: Rolle proves it; it then proves zero-derivative-implies-
   constant, which proves the integration-constant corollary, which
   proves the general-antiderivative theorem. It also drives the
   increasing-decreasing test. Score will rise sharply when Ch5 FTC
   proofs land.

3. **`definition.antiderivative`** (combined score 3, NEW §4.9).
   Despite its low current score, this node is the structural
   bridge to Ch5 — every indefinite integral and every solution to
   a first-order ODE in Ch9 will depend on it.

The pre-existing super-hubs (`definition.function`,
`definition.derivative-function`, `definition.limit-of-function`)
continue to dominate the chart. Notably, `theorem.chain-rule`
(score 17) does NOT gain new edges in Ch4 — Ch4 proofs lean on
algebraic derivative rules and MVT, not on chain rule.

## 4. Layering and the Two-Layer Dependency Pattern

Of the 636 edges in the cumulative graph:

- **360 `depends_on`** edges (conceptual layer): 95.6% are
  `uses_concept` (344), with 7 `specializes`, 6 `extends`, 3
  `instance_of`. The Ch4 increment was clean — the only new
  `specializes` edge is the corollary → theorem chain in
  `corollary.derivatives-equal-implies-differ-by-constant →
  theorem.derivative-zero-implies-constant`.
- **225 `proof_uses`** edges (inferential layer): role distribution
  remains healthy — `essential` (129) > `definition` (85) >
  `notation` (7) > `background` (3) > `existence` (1). No flat
  `uses` lists; every Ch4 proof uses the structured `parts[].uses`
  form with explicit roles.
- **51 `proves`** edges (proof → statement): one per proof file;
  no statement has multiple competing proofs in this rerun (Stewart
  is single-source).
- **34 `generality`** edges: unchanged from Ch3 except for the new
  corollary→theorem `specializes` edge mentioned above.

The two-layer separation continues to pay off: theorem-on-theorem
dependencies are encoded in `Proof.uses`, not in
`Statement.depends_on`, so a statement's conceptual dependencies
remain stable even as proofs are revised.

## 5. Architectural Decisions and Audit Discipline

The 2026-05-11 audit policies were respected throughout Ch4:

- **Atomic definitions enforced.** `concave-up` and `concave-down`
  were extracted as two separate sibling definitions, not a single
  bundled `concavity` definition. Same for `absolute-maximum` /
  `absolute-minimum` and `local-maximum` / `local-minimum`.
- **Honest dependency_confidence.** 6 statement-level dependency
  edges and 13 proof-level use edges are at `medium`, almost all
  reflecting the carried Ch3 trig-bundle debt or the new §4.9
  power-rule-general dependency in the antiderivative table.
- **Informal proofs flagged.** The first- and second-derivative-
  test proofs are marked `style: informal` and `semantic_confidence:
  medium` — Stewart's §4.3 presentation is geometric/intuitive, not
  rigorous (rigorous versions need uniform continuity arguments).
- **No status auto-promotion.** Every Ch4 entity is `extracted`;
  none has been promoted to `reviewed` or higher.
- **Multi-source guards retained.** Notes on `theorem.extreme-value-
  theorem`, `theorem.mean-value-theorem`, and `definition.newton-
  iteration` flag where Rudin's formulation differs (compactness;
  Cauchy MVT; quadratic convergence theorem) for any future merge.

## 6. Epistemic Debt — What Ch4 Owes Future Chapters

Ch4 closes 10 proof obligations (Fermat, Rolle, MVT, zero-derivative
chain, increasing-decreasing test, both derivative tests, general-
antiderivative — see `closed_in_ch4` in the statistics report) but
opens 3 new debts:

1. **EVT proof** — deferred to Apéndice F. The full proof requires
   sequential compactness; in this rerun's scope, EVT is an axiom-
   like theorem.
2. **L'Hôpital's rule** — deferred to Apéndice F. Stewart's §4.4
   gives only the proof for the simplest case (0/0 with continuous
   derivatives at the limit point); the general statement requires
   Cauchy MVT.
3. **Concavity test proof** — deferred to Apéndice F. Stewart's
   §4.3 derivation is geometric.

Carried forward unchanged from Ch3: trig/inv-trig/hyperbolic
derivative bundles, exponential-growth-decay uniqueness (→ §9.4),
linear-approximation (→ §11.10 Taylor).

NEW in Ch4: the bundled `proposition.antiderivative-formulas-table`
(13 inverse-derivative formulas in one node, mirroring the Ch3
trig-bundle precedent) and the partial-domain-of-validity gap on
the `1/x → ln|x|` row (Stewart's text notes the disconnected-
domain caveat; the bundled node does not encode it).

## 7. Growth Expectations for Ch5–Ch6

Ch5 (Integrals) will land on a graph that is already structurally
ready for it:

- `definition.antiderivative` and `theorem.general-antiderivative`
  are in place.
- `corollary.derivatives-equal-implies-differ-by-constant` provides
  the formal "+ C".
- `theorem.mean-value-theorem` is positioned to power the Mean
  Value Theorem for Integrals and the proof of the FTC.
- The `proposition.antiderivative-formulas-table` bundle gives
  immediate access to the standard integration formulas without
  re-proving each one.

Anticipated Ch5 growth: ~25–30 new statements, ~12–18 new proofs.
Edge growth will be dominated by FTC proofs and the bidirectional
linkage between Riemann sums (new) and antiderivatives (existing).
The hub `theorem.mean-value-theorem` is expected to roughly double
its inbound count.
