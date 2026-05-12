# Chapter 1 — Structural Analysis

- **Rerun:** `v0.3.1-stewart-full`
- **Snapshot label:** `v0.3.1-stewart-full-ch01`
- **Source:** Stewart, *Cálculo de una variable: Trascendentes tempranas*, 7th ed. (Spanish), Ch. 1 §1.1–§1.6 (§1.4 omitted as non-mathematical).
- **Generated:** 2026-05-11
- **Replaces:** `v0.3.1-stewart-full-ch1-partial`
- **Predecessor pilot:** `generated/snapshots/v0.3.1-stewart-ch1/` (kept as historical baseline; do not compare directly — pilot included nodes from later chapters).

## Footprint

| Metric | Value |
|---|---|
| Statements | 39 |
| Proofs | 5 |
| Total graph nodes | 44 |
| Edges | 88 |
| Connected components | 1 |
| Density | ≈ 0.047 |
| Per-section statement count | §1.1 = 13, §1.2 = 7, §1.3 = 7, §1.5 = 3, §1.6 = 9 |

All 44 entities at status `extracted`, schema `0.3.1`,
`provenance.rerun_id: v0.3.1-stewart-full`, language original `es`.
Every entity carries section + locator; PDF page numbers deferred to
a later locator-enrichment pass.

## Layering

The full Ch1 graph forms five clean semantic layers:

1. **Atomic foundations.** `definition.function` — universal hub
   (in-degree 27). Carries no `depends_on` edges.
2. **Function attributes.** `definition.{domain, range,
   independent-variable, dependent-variable, graph-of-function}` —
   atomic splits from Stewart's bundled function box.
3. **Properties, criteria, families, transformations.**
   `definition.{even, odd, increasing, decreasing}-function`,
   `definition.{piecewise, absolute-value}`, the §1.2 family
   (`linear, polynomial, power, rational, algebraic, trigonometric`),
   the §1.3 transformations (`{vertical,horizontal}-{translation,
   stretch}`, `reflection`), `definition.{arithmetic-of,
   composition-of}-functions`, and the
   `proposition.{vertical,horizontal}-line-test` criteria.
4. **Exponentials & inverses.** `definition.{exponential,
   natural-exponential, one-to-one, inverse}-function`,
   `proposition.laws-of-exponents`,
   `proposition.cancellation-equations`.
5. **Logarithms & change of base.** `definition.{logarithmic,
   natural-logarithm, inverse-trigonometric}-function`,
   `proposition.{laws-of-logarithms, change-of-base-formula}`.

The graph is a single connected component. Layer 1 is a single node;
layers 2–5 contain 5, 18, 6, and 5 nodes respectively (plus the 5
proof nodes attached to the propositions in layers 3–5).

## Hubs

| ID | In-degree | Role |
|---|---|---|
| `definition.function` | 27 | Universal foundational atom. |
| `definition.domain` | 11 | Attribute hub for every function-typed concept. |
| `definition.graph-of-function` | 7 | Geometric anchor for transformations + line tests. |
| `definition.one-to-one-function` | 3 | Bridge from §1.6 onward. |
| `definition.inverse-function` | 3 | Bridge into logarithms. |
| `definition.exponential-function` | 3 | Family node; depended on by laws-of-exponents and logarithm. |
| `definition.logarithmic-function` | 3 | Sub-hub for §1.6 derivations. |

The two universal hubs (`function`, `domain`) are real conceptual
primitives, not v0.2-style accidental bundles. The `function` hub
is expected to grow in every subsequent chapter.

## Edge taxonomy

Of the 88 edges:

- **`uses_concept` (`depends_on`)** — 68. Concept-layer edges.
- **`instance_of` (`depends_on`)** — 3. `absolute-value` →
  `piecewise-function`, `natural-exponential-function` →
  `exponential-function`, `natural-logarithm` →
  `logarithmic-function`.
- **`definition` (`Proof.uses`)** — 8. Definitional unfoldings used
  by proofs.
- **`essential` (`Proof.uses`)** — 4. Substantive proof steps:
  `proof.laws-of-logarithms.stewart` cites `laws-of-exponents` and
  `cancellation-equations`; `proof.change-of-base-formula.stewart`
  cites `laws-of-logarithms` and `cancellation-equations`.
- **`proved_by`** — 5. Statement→proof edges.

Five of the eight available `Proof.uses` roles are exercised
(`definition`, `essential`, plus `notation`, `existence`,
`background`, `lemma_local`, `implicit` reserved for later
chapters). Zero flat / role-less `uses` lists — the 2026-05-11
audit's principal warning is upheld throughout Ch1.

## Generality edges

Authored with explicit alphabetical-owner discipline per
`policies/04-edge-role-taxonomy.md`:

- `definition.even-function` ↔ `definition.odd-function` (sibling)
- `definition.decreasing-function` ↔
  `definition.increasing-function` (owned by `decreasing` —
  alphabetically earlier)
- `definition.dependent-variable` ↔
  `definition.independent-variable` (owned by `dependent`)
- `definition.horizontal-translation` ↔
  `definition.vertical-translation` (owned by `horizontal`)
- `definition.horizontal-stretch` ↔ `definition.vertical-stretch`
  (owned by `horizontal`)
- `definition.algebraic-function` `stronger_than`
  `definition.rational-function`
- `definition.natural-exponential-function` `special_case_of`
  `definition.exponential-function`
- `definition.natural-logarithm` `special_case_of`
  `definition.logarithmic-function`
- `proposition.horizontal-line-test` ↔
  `proposition.vertical-line-test` (sibling, owned by `horizontal`)

## Orphans

16 nodes have in-degree 0 within Ch1. Most are leaf concepts whose
upstream dependents will appear in later chapters:

- Transformations (`{vertical,horizontal}-{translation,stretch}`,
  `reflection`) — referenced by Ch2 limit/continuity arguments and
  Ch3 derivative-of-composition examples.
- Function arithmetic (`arithmetic-of-functions`) — referenced by
  Ch2 limit-of-sum/product/quotient and Ch3 differentiation rules.
- Parity (`even-function`, `odd-function`) — referenced by Ch5
  symmetric-integral propositions.
- `absolute-value`, `mathematical-model` — application-side leaves.
- `inverse-trigonometric-function` — referenced by Ch3 inverse-trig
  derivative formulas.

Orphan status here is **informational, not a defect**. No Ch1 hub
suffers from the v0.2-style "definitions as roots" pathology — every
substantive Ch1 statement carries `depends_on` edges into the
foundational layer.

## Audit-recommendation application

| Audit recommendation (2026-05-11) | Application in Ch1 |
|---|---|
| Atomic over bundled definition nodes | Function box split into 5 atoms; transformations split into 5 atoms; composition split from arithmetic. Bundled hubs avoided. |
| `Proof.uses[].role` precision | All 12 `uses[]` entries across 5 proofs carry an explicit role (`definition` or `essential`). |
| Honest `dependency_confidence` | 5 entities at `medium` (trig bundle, inverse-trig bundle, exp, natural-exp, log) reflecting genuine debt. |
| Supremum / completeness `existence` discipline | Not applicable in Ch1 (no completeness invocations). Becomes binding from Ch11 (series). |
| Multi-source merge integrity | Single-source rerun. Future Rudin merge will add `sources[]` per id-equivalence policy. |

## Explicit epistemic debt (carried, not failed)

Per the user directive of 2026-05-11, the following bundles are
preserved as explicit debt and are NOT split for Ch1:

1. `definition.trigonometric-function` (six trig functions).
2. `definition.inverse-trigonometric-function` (six inverses).

These remain at `dependency_confidence: medium` and are blocked from
promotion to `validated` until split. Splitting will be revisited if
later chapters force structural pressure (e.g., individual
derivatives in Ch3 referencing only `sin` and `cos` separately).

The `definition.linear-function` terminology-collision warning (with
the future `definition.linear-map`) is preserved in
`weak-dependencies.yml` for Ch2+ disambiguation.

## Growth expectations into Ch2

Anticipated structural pressure once Ch2 (limits and derivatives)
lands:

- `definition.function`, `definition.domain`, `definition.graph-of-
  function` will gain ~10–15 incoming edges each.
- `definition.composition-of-functions`,
  `definition.arithmetic-of-functions`, the trig and exp/log family
  nodes will all become heavily-cited mid-graph hubs.
- New roles will appear on Proof.uses: `essential` (limit laws),
  `existence` (squeeze, IVT, EVT), and potentially `notation`
  (epsilon-delta machinery).
- Density should stay ≈ 0.04–0.06 as the orphan layer fills in.
