# 05 — ID Equivalence Policy

> When do two statements share a node, and when do they get separate nodes?
> This is the single most expensive decision in the graph: changing an ID
> after extraction means rewriting every edge that references it.
>
> This policy operationalises the **Multi-Source Disambiguation Guide** in
> `AGENTS.md` and adds v0.3-specific provenance rules.

---

## Core principle

A statement node represents a **mathematical truth**, not a textbook entry.

Two formulations share a node **iff** they are **logically equivalent in
their full generality** — same hypotheses, same conclusion, same
mathematical objects, modulo notation and language.

If the question "is X the same statement as Y?" requires more than 60
seconds of thought, default to **separate nodes** and link them via
`generality`. Splitting later is far cheaper than merging.

---

## A. The decision tree

For a candidate node `C` against an existing node `E`:

```text
1. Compare formal content (LaTeX or precise prose), ignoring notation
   and language.
   - identical (modulo notation)            -> SAME NODE  (go to §C)
   - C strictly subsumes E                   -> SEPARATE; link generality
                                                (E special_case_of C)
   - E strictly subsumes C                   -> SEPARATE; link generality
                                                (C special_case_of E)
   - overlapping but neither subsumes        -> SEPARATE; link generality
                                                (overlapping or
                                                 incomparable)
   - equivalent under named correspondence
     (e.g., metric-space d  vs.  |x-y| on R) -> SEPARATE; link generality
                                                (equivalent + notes)
   - same name, different statement          -> SEPARATE; rename one ID
   - genuinely unrelated                     -> SEPARATE; no edge
```

When in doubt: SEPARATE + `generality` edge.

---

## B. Equivalence classes that are NOT a single node

These commonly tempt extractors into over-merging. v0.3 keeps them
SEPARATE.

### B.1 Different ambient settings

A theorem stated on `R` (Stewart) and the analogous theorem stated in
arbitrary metric spaces (Rudin) are **two nodes**, even when the
`R`-version is a special case of the metric-space version.

```yaml
# theorem.continuous-image-compact (Rudin 4.14)
generality:
  - target: theorem.extreme-value-theorem
    relation: stronger_than
    notes: >
      EVT on [a,b] follows by Heine–Borel: [a,b] compact in R, image
      compact ⇒ closed and bounded ⇒ attains sup/inf.
```

```yaml
# theorem.extreme-value-theorem (Stewart §...)
generality:
  - target: theorem.continuous-image-compact
    relation: special_case_of
```

Rationale: the proofs differ, the dependency footprints differ, and the
generalisation is mathematically meaningful. Merging would erase the
relationship.

### B.2 Theorem families with named parts

Multi-part theorems where the parts are independently citable get
SEPARATE nodes. See `06-theorem-granularity-policy.md`.

```text
theorem.fundamental-theorem-of-calculus-part-1
theorem.fundamental-theorem-of-calculus-part-2
```

### B.3 Pedagogical variants of the SAME truth

When a textbook restates a theorem in a "friendlier" form for a
specific audience but the formal content is unchanged, merge.

```text
"For continuous f on [a,b], f attains its max and min on [a,b]."   (Stewart)
"If f is continuous on a closed interval [a,b], then f attains its
 supremum and infimum."                                            (any analysis text)
```

→ SAME node. Add `sources` entries; add a second `statement.natural`
entry under the new language if any; do not branch.

### B.4 Notation variants of the SAME truth

`f(-x) = f(x)` vs `f(-x) - f(x) = 0` vs `∀x: f(-x) = f(x)` are the
same truth. SAME node. Pick the cleanest LaTeX as canonical and put
alternates in `notes` if pedagogically useful.

### B.5 Definition vs. characterisation theorem

`definition.continuity-epsilon-delta` and
`theorem.continuity-sequential-characterisation` describe the same
underlying concept but are NOT the same node:

- the definition INTRODUCES the concept;
- the theorem ASSERTS an equivalent characterisation that requires proof.

→ SEPARATE. Link with a `proved_by` from the theorem and an
`equivalent` generality edge (yes, both layers — they answer different
questions).

---

## C. When merging IS correct: the procedure

Confirmed equivalent (decision-tree branch "same node"):

1. Keep the existing node and its `id`.
2. Append the new `Source` to `sources`.
3. Append the new natural-language formulation under
   `statement.natural[<lang>]` if it adds a new language or improves
   the existing entry. Mark the original-source entry with
   `is_original: true`.
4. Do **not** mutate `title` unless the new source supplies a clearer
   canonical title; if so, prior titles move into `notes`.
5. Add a `notes` entry documenting the merge decision and the
   distinguishing features that were considered (so future reviewers
   do not relitigate it).
6. Append each source's distinct proof as a SEPARATE `proof.*` node
   (e.g., `proof.evt.stewart`, `proof.evt.rudin-via-compactness`).

**Do not** record `derived_from` for source-merge operations. That
field is reserved for v0.2 → v0.3 split/restructure provenance.

---

## D. When splitting IS correct: the procedure

Splitting an existing v0.3 node (e.g., a bundled definition imported
from v0.2 or one mistakenly merged earlier in v0.3) into multiple
atomic nodes:

1. Create N new files, one per atomic concept, each with a fresh ID.
2. On EACH new node, set
   `provenance.derived_from: [<old-id>]`.
3. On the old node:
   - if it remains a meaningful umbrella (rare), keep it and add
     `generality` edges pointing to the children;
   - if it is fully replaced, delete the old file. Do NOT set
     `redirected_to` (see §E for why).
4. Re-target every edge that referenced the old id to the SPECIFIC
   child it actually depended on. (Concept-aware retargeting; do not
   blanket-link every edge to every child.)
5. If the old id existed in `generated/snapshots/v0.2/` only, you do
   NOT need to delete a v0.3 file (there is none); the audit trail is
   purely in `derived_from`.

This is the procedure used in
`01-bundled-definitions-audit.md` for the 12 v0.2 bundles.

---

## E. `redirected_to` vs `derived_from`

These two fields look similar and are routinely confused. The freeze:

| Field | Meaning | Cardinality | Use when |
|---|---|---|---|
| `derived_from` | "This node's content originated as part of these prior IDs." | many → 1 (or many → many in chains) | A v0.2 bundle was split into atomic v0.3 nodes; each new node lists the bundle in `derived_from`. |
| `redirected_to` | "This ID is retired in favour of a single canonical replacement." | 1 → 1 | A v0.3 node turned out to duplicate another v0.3 node and is being merged into it; the loser keeps a stub file with `redirected_to: <winner>`. |

Rules:

- A 1 → N split sets `derived_from` on the children, NEVER
  `redirected_to` on the parent (there is no single successor).
- A N → 1 merge sets `redirected_to` on each loser and (optionally)
  `derived_from: [<loser>...]` on the winner.
- Stubs with `redirected_to` are kept indefinitely; they preserve the
  ability to follow stale references in old snapshots.
- The loader treats a node with `redirected_to` as **non-canonical**:
  it is loaded for traceability but not counted in graph statistics
  and not allowed as the target of new edges.

---

## F. Generality edges as the safety net

Whenever you choose SEPARATE over SAME, **add a `generality` edge**
unless the two statements are genuinely unrelated. The edge is the
mechanism that keeps the graph navigable across legitimate splits.

Conventions (frozen in `04-edge-role-taxonomy.md`):

- `equivalent` and `incomparable` are recorded once on the
  alphabetically-earlier id.
- `stronger_than` is recorded on the stronger node.
- `special_case_of` is recorded on the special node (no inverse
  `generalization_of` edge).

If after extraction a `generality` cluster contains 4+ nodes that
collectively look like one "fact in different costumes", that is a
**merge smell** — flag it for §C review.

---

## G. Anti-patterns

Stop and reconsider if you are about to:

- **Create a new node because a different book uses different
  letters** (`f` vs `φ`). → SAME node.
- **Create a new node because the wording adds "for all x"
  explicitly**. → SAME node.
- **Merge two nodes because "well, on `R` they coincide"**.
  → SEPARATE; this is exactly the metric-vs-real-line trap.
- **Merge a definition with the theorem that characterises it.**
  → SEPARATE.
- **Use `redirected_to` to record a 1 → N split.** → Use
  `derived_from` on the children instead.
- **Re-target a v0.2 edge to ALL children of a split bundle.** → Pick
  the SPECIFIC child that the original edge semantically required.

---

## H. Worked examples

### H.1 EVT (split — different generality)

- `theorem.extreme-value-theorem` (Stewart): continuous `f` on `[a,b]`
  attains max and min.
- `theorem.continuous-image-compact` (Rudin 4.14): the continuous
  image of a compact set is compact.

→ **Two nodes.** Stewart's is `special_case_of` Rudin's. Rudin's is
`stronger_than` Stewart's. Each has its own proof; Stewart's proof may
later cite Rudin's as `essential` (with `derived_from` notes if
historically applicable).

### H.2 Squeeze theorem (merge — same content, two sources)

- Stewart's "Teorema del estrecho/sandwich" and Rudin's squeeze-style
  lemma.

→ **One node.** Add both sources, both natural-language entries, both
proofs as separate `proof.*` files.

### H.3 Continuity (split — definition vs characterisation)

- `definition.continuity-epsilon-delta`
- `theorem.continuity-sequential-characterisation`

→ **Two nodes.** Linked via `proved_by` (the theorem has a proof) and
`generality.equivalent` (the underlying notion is the same).

### H.4 Bundled neighbourhood definitions (split — bundle → atoms)

`definition.neighborhood-limit-point-open-closed` (v0.2) →
`definition.neighborhood`, `definition.limit-point`,
`definition.interior-point`, `definition.open-set`,
`definition.closed-set`, ... (10 v0.3 atoms).

→ See policy 01. Each atom carries
`provenance.derived_from: [definition.neighborhood-limit-point-open-closed]`.
Old id is dropped; v0.2 edges are re-targeted by the migration
script (with human review of ambiguous cases).

---

## I. Operator checklist (per candidate node)

Before writing a new statement file, answer:

- [ ] Did I search existing IDs for the obvious names (and 1–2
      alternates)?
- [ ] Did I compare formal content, not just titles?
- [ ] Did I pick the right branch of the §A decision tree?
- [ ] If SAME: did I add the source, the language entry, and a merge
      note?
- [ ] If SEPARATE: did I add a `generality` edge unless genuinely
      unrelated?
- [ ] If splitting an existing node: did I set `derived_from` on each
      child and re-target edges per §D?

If any answer is "no", stop and resolve before saving.
