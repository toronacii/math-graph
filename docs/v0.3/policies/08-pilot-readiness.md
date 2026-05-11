# 08 — Pilot Readiness (Stewart Ch1)

> Gap analysis and go / no-go assessment for the first v0.3 pilot
> rerun: **Stewart Calculus, Chapter 1 — Functions and Models**.
>
> This document is the last gate before extraction. If anything here
> is incomplete, do NOT begin the pilot; close the gap and update
> this file.

---

## A. Pilot scope

- **Source.** James Stewart, *Cálculo de una variable: Trascendentes
  tempranas*, 7th ed., Chapter 1 (Functions and Models).
- **Goal.** Reproduce the v0.2 Ch1 coverage under v0.3 schema +
  policies, then compare via `mkg-diff` against the frozen v0.2
  baseline at `generated/snapshots/v0.2/`.
- **Out of scope for the pilot.** Rudin Ch1, multi-source merging,
  cross-chapter generality edges, quality-axis scoring beyond
  `extracted` status. These come AFTER the pilot validates the
  pipeline.

The pilot is a methodology test, not a content release.

---

## B. Readiness matrix

Each row is a precondition. Pilot starts only when every row is
**Ready** (or explicitly **Deferred** with a tracking note).

| # | Area | Artefact / Tool | Status | Notes |
|---|---|---|---|---|
| 1 | Schema | `schema/v03.py` (v0.3.1) | Ready | 17/17 tests passing |
| 2 | Schema export | `mkg-export-schema` | Ready | 4 JSON Schemas emitted |
| 3 | Loader | `scripts/v03/loader.py` | Ready | Skips non-v0.3 files |
| 4 | Validator | `mkg-validate` | Ready | Hits Pydantic + custom rules |
| 5 | Graph builder | `mkg-build` | Ready | Disjoint v0.3 output dir |
| 6 | Snapshot tool | `mkg-snapshot` | Ready | `--hashes-only` mode added |
| 7 | Diff tool | `mkg-diff` | Ready | v0.2 ↔ v0.3 comparable |
| 8 | Migration tool | `mkg-migrate` | Ready | Path A / Path B selectable |
| 9 | Context-pack tool | `scripts/v03/make_context_pack.py` | Ready | Smoke-tested on Rudin Ch1 |
| 10 | Statement template | `schema/v03/templates/statement.template.yml` | Ready | Inline rule comments |
| 11 | Proof template | `schema/v03/templates/proof.template.yml` | Ready | Inline rule comments |
| 12 | Extraction prompt | `schema/v03/templates/EXTRACTION_PROMPT.md` | Ready | 11 sections |
| 13 | Policy 01 — bundles | `policies/01-bundled-definitions-audit.md` | Ready | 12 bundles → 48 atoms |
| 14 | Policy 02 — domains | `policies/02-domain-vocabulary.md` | Ready | 21 + 10 tags |
| 15 | Policy 03 — ontology | `policies/03-ontology-vocabulary.md` | Ready | 8 kinds frozen |
| 16 | Policy 04 — edges | `policies/04-edge-role-taxonomy.md` | Ready | 3 layers frozen |
| 17 | Policy 05 — IDs | `policies/05-id-equivalence-policy.md` | Ready | Decision tree + procedures |
| 18 | Policy 06 — granularity | `policies/06-theorem-granularity-policy.md` | Ready | Decision tree + patterns |
| 19 | Policy 07 — freeze | `policies/07-semantic-freeze.md` | Ready | Change-control procedure |
| 20 | Rerun checklist | `docs/v0.3/13-rerun-checklist.md` | Ready | Step-by-step |
| 21 | v0.2 baseline | `generated/snapshots/v0.2/` | Ready | 655 files + hashes |
| 22 | v0.3 output dir | `generated/v0.3/` | Ready | Empty, awaiting extraction |
| 23 | Console aliases | `pyproject.toml` | Ready | All `mkg-*` resolve |
| 24 | Test suite | `tests/v03/` | Ready | 35/35 passing |
| 25 | Linter | `ruff` clean on `schema/v03.py` + new files | Ready | — |

---

## C. Open questions to close BEFORE extraction

These are not blockers per se but should each have an explicit answer
before the first node is written.

### C.1 Bundled-definition pre-split or on-demand?

Two options for the 12 bundles in policy 01:

- **Pre-split.** Author all 48 atomic v0.3 definitions before Stewart
  Ch1 starts.
- **On-demand.** Split each bundle the first time Stewart Ch1
  references it; leave unreferenced bundles untouched.

**Recommendation:** on-demand for the pilot. Stewart Ch1 references
maybe 4–6 of the 12 bundles. Pre-splitting all 12 risks producing
atoms that drift before they are exercised by a real use-site.

**Status.** Decide before pilot. Default to on-demand unless reviewer
overrides.

### C.2 Pilot extractor

Who or what writes Ch1?

- LLM (`llm:claude-opus-4.7`) following `EXTRACTION_PROMPT.md` and
  policies, with human review.
- Human-led with LLM assist.

**Recommendation:** LLM-led with human spot-review at every 10
nodes. The pilot's purpose is to stress-test the policies, which
requires the policies to be applied verbatim — an LLM does this more
predictably than a human.

**Status.** Decide before pilot. Provenance fields (`extracted_by`,
`extracted_at`, `rerun_id`) capture the choice.

### C.3 Cross-chapter / cross-source links

Stewart Ch1 will plausibly reference future chapters (limits
preview) and may share concepts with the frozen Rudin Ch1 v0.2 nodes.

- Forward references to future Stewart chapters: STUB. Create the
  target id with `status: extracted` and minimal metadata
  (`title`, `language`, `statement.natural`, source page); fill in
  later.
- References to Rudin v0.2 concepts: do NOT cross the schema
  boundary. v0.3 nodes do not depend on v0.2 nodes. If conceptual
  overlap exists, note it in `notes` for later v0.3 extraction of
  Rudin.

**Status.** Documented here; reflect in the pilot rerun notes.

### C.4 Quality scoring during pilot

Quality axes default to `null` (unassessed) per the schema. Do not
score during pilot extraction; scoring is a separate review pass
(`status: extracted → reviewed`).

**Status.** Decided.

### C.5 Snapshot cadence

Default: one snapshot at the end of pilot extraction (rerun id
`v0.3-YYYY-MM-DD`). If the pilot takes more than one calendar day,
take an interim snapshot at the end of each day with a `-N` suffix.

**Status.** Decided.

---

## D. Success criteria

The pilot is **complete** when:

1. Every Stewart Ch1 statement and proof identifiable in the v0.2
   baseline has a corresponding v0.3 node (or an explicit
   `notes`-documented intentional omission).
2. `mkg-validate` returns clean on the entire v0.3 corpus.
3. `mkg-build` produces a graph in `generated/v0.3/`.
4. `mkg-diff generated/snapshots/v0.2 generated/v0.3` produces a
   report whose differences are all EXPECTED (atomic split of
   bundles, addition of v0.3-only fields, structured edges) and
   none UNEXPECTED (missing nodes, dropped edges without rationale,
   spurious renames).
5. A snapshot is taken at `generated/snapshots/<rerun_id>/`.
6. A pilot retrospective is written at
   `docs/v0.3/policies/proposals/00-pilot-retrospective-<rerun_id>.md`
   listing every policy item that needed clarification and proposing
   updates (or confirming none needed).

The pilot is **a failure** if:

- Any policy required mid-flight reinterpretation that was not
  anchored in §C of policy 07. (→ policies underspecified.)
- The LLM systematically violated a policy without the validator
  catching it. (→ tooling gap.)
- The diff against v0.2 surfaces UNEXPECTED differences whose root
  cause is policy ambiguity rather than v0.3-by-design changes.

A failed pilot is followed by policy/tool updates and a re-run, NOT
by accepting the corpus.

---

## E. Go / no-go

**Recommended state to enter pilot:** all rows in §B Ready, §C.1 and
§C.2 explicitly answered.

**Current state (as of this document):** all 25 rows of §B Ready.
§C.1 and §C.2 require an explicit decision from the operator.

**Verdict.** Pilot is **READY pending §C.1 and §C.2 decisions**.

When those are recorded (in a short addendum to this file or in the
pilot's rerun notes), proceed to `docs/v0.3/13-rerun-checklist.md`
and begin extraction.

---

## F. Post-pilot scope

After a successful Stewart Ch1 pilot:

1. Stewart Ch2 (Limits and Derivatives) — first real test of the
   forward-reference strategy from §C.3.
2. Quality-scoring pass on Stewart Ch1 + Ch2 (`extracted → reviewed`).
3. Rudin Ch1 v0.3 re-extraction — first real test of the multi-source
   ID-equivalence policy.
4. Multi-source diff: how many merges, how many splits, how many
   `generality` edges did the pilot policies actually require?
   Update policy 05 if the empirical numbers diverge from the
   anticipated ones.

The pilot is a feedback loop, not an endpoint.
