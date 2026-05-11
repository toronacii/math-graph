# 07 — Semantic Freeze

> Which v0.3 decisions are FROZEN (changing them is a versioned event),
> which are OPEN (extractors may exercise judgement), and how do we
> change a frozen decision when we must.

---

## Why a freeze?

Most extraction errors are recoverable: a wrong title, a missing
source, a misclassified type. Changing schema-level conventions in the
middle of extraction is NOT recoverable cheaply — it invalidates
context packs, retroactively reshapes audits, and forces re-runs.

The freeze names the conventions that must stop changing before
Stewart Ch1 begins. Anything not named here is open by default.

---

## A. What is FROZEN

Each item below is locked. Changing it requires the procedure in §C.

### A.1 Schema (Pydantic)

- The class structure of `schema/v03.py`.
- The `SCHEMA_VERSION = "0.3.1"` constant (the loader accepts both
  `"0.3.0"` and `"0.3.1"` via `SUPPORTED_SCHEMA_VERSIONS`; the v0.3.1
  bump is additive — see §C.5 changelog).
- `StatementType`, `Status`, `Confidence`, `LangCode`,
  `DependencyRole`, `ConceptDependencyRole`, `GeneralityRelation`,
  `SemanticKind` literal sets.
- The `Statement`, `Proof`, `ProofPart`, `ProofDependency`,
  `ConceptDependency`, `GeneralityEdge`, `MultilingualEntry`,
  `LatexBlock`, `QualityBlock`, `ProvenanceBlock`,
  `OntologyBlock`, `DomainsBlock`, `AmbientBlock`, `LanguageBlock`,
  `Source` shapes.
- ID-prefix rule: `<type>.<slug>` with `type ∈ STATEMENT_TYPES ∪ {proof}`.
- `extra = "forbid"` everywhere (no silent extra keys).

### A.2 Vocabularies

- Domain Tier-1 (21) and Tier-2 (10) tags as listed in
  `02-domain-vocabulary.md`.
- `semantic_kind` literal set as listed in `03-ontology-vocabulary.md`
  (8 kinds; `space`, `theorem-schema`, `transformation` rejected).
- Edge-role literals across all three layers (proof / concept /
  generality), per `04-edge-role-taxonomy.md`.
- The forbidden-vocabulary table in policy 03 (banned aliases for
  semantic_kind, banned domain aliases, banned proof-role names).

### A.3 Identity & granularity rules

- §A decision tree of `05-id-equivalence-policy.md` (when two
  formulations share a node).
- Conventions for `derived_from` vs `redirected_to` (policy 05 §E).
- `generality` direction conventions: `equivalent`/`incomparable`
  on alphabetically-earlier id; `stronger_than` on stronger node;
  `special_case_of` on special node, no `generalization_of` inverse.
- §B decision tree of `06-theorem-granularity-policy.md` (when to
  split a textbook unit).
- Bundled-definition split list of
  `01-bundled-definitions-audit.md` (12 bundles → 48 atoms).

### A.4 Provenance rules

- `provenance.schema_version` is REQUIRED on every entity and is the
  loader's gate.
- `rerun_id` follows the `v0.3-YYYY-MM-DD` pattern (one rerun per
  day max; suffix `-N` if multiple in a day).
- Snapshots under `generated/snapshots/<rerun_id>/` are immutable
  once written. Errors are corrected by a NEW snapshot, not an edit.
- v0.2 frozen baseline at `generated/snapshots/v0.2/` is read-only.

### A.5 Pipeline contracts

- The four-phase per-chapter pipeline of v0.2 is RETIRED for new
  work. v0.3 uses the rerun checklist
  (`docs/v0.3/13-rerun-checklist.md`).
- Output directories: v0.2 → `generated/graph/`,
  v0.3 → `generated/v0.3/`. Disjoint, never mixed.
- Console aliases: `mkg-validate`, `mkg-build`, `mkg-snapshot`,
  `mkg-diff`, `mkg-migrate`, `mkg-export-schema`. Existing aliases
  are not renamed; new functionality gets a new alias.

### A.6 Review status lifecycle

`extracted → reviewed → validated → audited → stable → canonical`,
with the promotion gates in `08-status-lifecycle.md`. New states are
not added during the freeze.

---

## B. What is OPEN

Extractors may exercise judgement on these without invoking change
control:

- Choice of `keywords[]` (subject to the conventions in policy 03).
- Free-form `domains.notes`, `ambient.notes`, `notes` on edges and
  entities.
- LaTeX phrasing of `statement.latex.canonical` so long as it remains
  semantically equivalent to the source.
- Translation quality of secondary-language `statement.natural`
  entries (originals are fixed; translations may be improved).
- Choice of proof `style` string (free-form: `direct`,
  `contradiction`, `induction`, `construction`, etc.).
- Whether a particular case-split is recorded as `Proof.parts[]` or
  inlined into `Proof.uses` (per policy 06 guidance, but not gated).
- Quality-block scores and confidence values (these are by design
  reviewable judgements).
- Source page numbers, edition cross-checks, additional `Source`
  entries on a node.

If you are unsure whether a decision is FROZEN or OPEN, treat it as
FROZEN and ask.

---

## C. Change-control procedure for frozen items

When a frozen decision must change:

1. **Write a one-page proposal** at
   `docs/v0.3/policies/proposals/<NN>-<slug>.md` with:
   - the current rule (quote the policy or schema text);
   - the proposed change;
   - the trigger (concrete extraction failure or new requirement);
   - migration impact: which files / edges / scripts / context packs
     are invalidated;
   - rollback plan.
2. **Pause the active rerun** (do not commit any new statement /
   proof files) until the proposal is resolved.
3. **Resolve.** For solo work this is a self-merge after a 24-hour
   sleep on it. For team work, a second reviewer signs off.
4. **Apply the change atomically.** All of:
   - schema edits (with `mkg-export-schema` rerun);
   - policy doc edits;
   - migration script for in-flight files;
   - bumping the rerun id (`v0.3-YYYY-MM-DD-N`) so the change is
     anchored to a snapshot boundary.
5. **Bump `SCHEMA_VERSION`** when the change is structural:
   - adding / removing / renaming a field → MINOR (`0.3.1 → 0.4.0`).
   - changing a literal set in a non-additive way → MINOR.
   - additive literal that does not break old data → PATCH
     (`0.3.0 → 0.3.1`); add the old version to
     `SUPPORTED_SCHEMA_VERSIONS` so existing files continue to load,
     and note in the changelog (§C.5) whether old files need a
     refresh.
6. **Archive the proposal** alongside the snapshot it changed under.

The cost of this procedure is intentional. It is what makes the
freeze meaningful.

### C.5 Version changelog

- **v0.3.1 (2026-05-11).** Additive PATCH bump.
  - `SemanticKind` += `notation`, `pedagogical` (closes audit F1).
  - `GeneralityRelation` += `sibling`, `disjoint` (closes audit F2).
  - `SUPPORTED_SCHEMA_VERSIONS` introduced; loader accepts both
    `"0.3.0"` and `"0.3.1"` so v0.3 pilot files do not need to be
    rewritten.
  - New: `schema/v03/sources.yml` canonical source registry +
    `load_source_registry()` API (closes F4); validator warns on
    unregistered `Source.work`.
  - Validator: locator-missing promoted to **error** when
    `provenance.rerun_id` is set (closes F5).
  - Extraction prompt: enums for `proof.uses[].role`,
    `depends_on.role`, `semantic_kind`, `generality.relation` inlined
    (closes F6 / F7).
  - 8 audit findings: F1, F2, F4, F5, F6, F7 closed; F3, F8 deferred.
  - No file rewrites required for existing v0.3.0 pilot files; new
    files SHOULD declare `schema_version: "0.3.1"`.

- **v0.3.0 (2026-05-04).** Initial frozen schema. See
  `reports/audits/v0.3-pilot-stewart-ch1.md` for the pilot that
  surfaced the v0.3.1 fixes.

---

## D. What the freeze does NOT freeze

- The PILOT chapter scope (Stewart Ch1) is a planning decision, not a
  policy. It can be changed at any time before extraction begins.
- The CONTENT of the graph: every statement, proof, edge, and quality
  score is by design subject to revision via subsequent reruns.
- v0.2 → v0.3 migration scope: which v0.2 files are migrated by
  bridge (Path B) vs re-extracted (Path A) is decided per chapter
  per the matrix in `10-migration-strategy.md`. Not a policy
  decision.
- Documentation outside `docs/v0.3/policies/` and outside
  `schema/v03.py`. Architectural docs (`docs/v0.3/00-..-13-*.md`)
  may be edited freely so long as they do not contradict policy.

---

## E. Sunset of v0.2 conventions

The v0.2 schema (`schema/models.py`) and v0.2 outputs
(`generated/graph/`) are NOT frozen — they are FROZEN-BY-RETIREMENT.
They will not change because they are read-only historical artefacts.
The corresponding policies in `AGENTS.md` ("Per-Chapter Extraction
Pipeline (v0.2 — historical)") describe behaviour that no longer
applies to new work.

When the v0.3 pilot completes and the graph reaches Stewart Ch1
parity, the v0.2 pipeline section in `AGENTS.md` is removed; the
v0.2 snapshot remains.

---

## F. Operator checklist (before authoring a v0.3 file)

- [ ] Have I read policies 02–06?
- [ ] If I want to add a `semantic_kind` / domain / edge role that is
      not in the frozen list, have I followed §C instead of inventing
      one?
- [ ] If I want to change an ID convention, have I followed §C?
- [ ] If I am unsure whether something is FROZEN or OPEN, am I
      treating it as FROZEN?

The freeze is the cheapest insurance the project will buy. Use it.
