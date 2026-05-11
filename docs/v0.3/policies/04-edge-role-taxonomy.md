# 04 — Edge Role Taxonomy

> Frozen role vocabularies for the THREE edge layers in v0.3:
>
> 1. **Proof layer** — `Proof.uses[].role` (`DependencyRole`)
> 2. **Concept layer** — `Statement.depends_on[].role` (`ConceptDependencyRole`)
> 3. **Generality layer** — `Statement.generality[].relation` (`GeneralityRelation`)
>
> All three are `Literal` types in `schema/v03.py`. Adding a role
> requires a schema change. Removing or renaming a role requires a
> migration of every using edge.

## Why three layers?

Each layer answers a different question:

| Layer | Question | Source of truth |
|---|---|---|
| Proof | "What does this DERIVATION step on?" | `Proof.uses` |
| Concept | "What concepts does this STATEMENT presuppose?" | `Statement.depends_on` |
| Generality | "How are these two STATEMENTS RELATED logically?" | `Statement.generality` |

A single mathematical fact may have edges in 1, 2, or 3 of these
layers. They are **independent and additive**. Do not collapse them.

---

## A. Proof layer — `DependencyRole`

Frozen set:

```text
essential | background | notation | existence | definition |
lemma_local | implicit
```

| Role          | Use when…                                                                                | Example                                                              |
|---------------|------------------------------------------------------------------------------------------|----------------------------------------------------------------------|
| `essential`   | Removing this dependency BREAKS the proof.                                               | IVT proof depends on `theorem.continuous-image-connected` (essential). |
| `background`  | Cited for context; the proof can be reframed without it.                                 | A proof citing a related "see also" theorem to justify a remark.     |
| `notation`    | Supplies vocabulary / notation only.                                                     | Limit proof citing `definition.metric` for the symbol `d(x,y)`.       |
| `existence`   | Supplies an EXISTENCE / completeness principle.                                          | EVT proof depending on completeness for sup of bounded set.          |
| `definition`  | Supplies a definitional unfolding (the proof literally rewrites a definition).           | Proof of "f even ⇒ symmetric" using `definition.even-function`.       |
| `lemma_local` | Used in exactly ONE direction / case / sub-claim. Prefer `parts[]` if the proof is split.| Forward direction of an "iff" proof depends on a lemma the converse does not. |
| `implicit`    | Implicit foundational / conventional dependency the author does not cite.                | Most analysis proofs implicitly use `axiom.choice` or excluded middle. |

### `role: implicit` vs `implicit: true` flag

These are independent and frequently confused. The freeze decides:

| Combination | Meaning |
|---|---|
| `role: implicit` + `implicit: false` | The author DOES cite the convention (e.g., "by the axiom of choice"). The mathematical role is foundational/implicit. |
| `role: essential` + `implicit: true` | The proof essentially needs this, but the author did NOT cite it (we inferred). |
| `role: implicit` + `implicit: true` | (Most common.) Foundational and inferred. |
| `role: essential` + `implicit: false` | (Most common.) Cited and essential. |

`implicit: true` is **always** an inference flag. `role: implicit` is
**always** a mathematical-role flag. They are orthogonal.

### When NOT to use a proof-layer edge

- **Concept references** (the theorem mentions a definition but the
  proof does not use it). → put in `Statement.depends_on` of the
  THEOREM, not in `Proof.uses`.
- **Generality relations** (this theorem is a special case of
  another). → put in `Statement.generality`.
- **The statement being proved.** It is referenced via `proves`, never
  via `uses`.

### Confidence rule

Every proof edge gets a `confidence` (default `high`). Use:

- `high` — explicit, unambiguous citation.
- `medium` — strongly implied; the proof clearly needs this but the
  source phrasing is loose.
- `low` — possibly used; reviewer should verify. (If you're unsure
  whether to include the edge, include it with `low`.)

---

## B. Concept layer — `ConceptDependencyRole`

Frozen set:

```text
specializes | uses_concept | extends | instance_of | ambient
```

| Role          | Use when…                                                                       | Example                                                            |
|---------------|---------------------------------------------------------------------------------|--------------------------------------------------------------------|
| `specializes` | This statement IS a special case of the referenced statement.                   | `theorem.evt-stewart` specializes `theorem.continuous-image-compact`. |
| `uses_concept`| The statement REFERENCES the concept by name in its formulation.                | `definition.continuity-metric` uses `definition.metric-space`.      |
| `extends`     | The statement EXTENDS / enriches the referenced concept.                        | `definition.ordered-field` extends `definition.field`.              |
| `instance_of` | This is an instance of an abstract structure.                                   | `definition.real-numbers` is an instance of `definition.complete-ordered-field`. |
| `ambient`     | The statement OPERATES inside the referenced ambient structure.                 | `theorem.heine-borel-rk` lives `ambient` to `definition.metric-space`. |

### When to choose `ambient` vs `uses_concept`

If the structure is named in the statement TYPE / SETTING (a hypothesis
on which the result depends), it is **ambient**. If the concept is
used INSIDE the formulation (a noun referenced by name), it is
**uses_concept**.

A statement may have BOTH:

```yaml
depends_on:
  - id: definition.metric-space
    role: ambient
  - id: definition.cauchy-sequence
    role: uses_concept
```

### When NOT to use a concept-layer edge

- **Proof derivation steps.** → `Proof.uses`.
- **Generality relations.** → `Statement.generality`.
- **Bibliographical / pedagogical references.** Not modeled in v0.3.

### Anti-pattern: definition chains as concept-layer trees

Real definitions form a DAG, but every transitive ancestor is NOT a
direct edge. Record only DIRECT references. Transitive closure is
the graph traversal's job.

---

## C. Generality layer — `GeneralityRelation`

Frozen set (v0.3.1):

```text
equivalent | stronger_than | weaker_than | special_case_of |
incomparable | overlapping | sibling | disjoint
```

| Relation          | Meaning (as `A.generality = [{target: B, relation: R}]`)            |
|-------------------|---------------------------------------------------------------------|
| `equivalent`      | A ⇔ B (logically equivalent in full generality).                    |
| `stronger_than`   | A implies B but B does not imply A.                                 |
| `weaker_than`     | B implies A but A does not imply B.                                 |
| `special_case_of` | A is a strict specialization of B (typical: A specializes B by adding hypotheses). |
| `incomparable`    | Neither A ⇒ B nor B ⇒ A; the statements address overlapping but different content. |
| `overlapping`     | Statements partially coincide but neither subsumes the other; they share context, not implication. |
| `sibling`         | Parallel concepts at the same conceptual level (e.g. even/odd functions, horizontal/vertical shifts). Use when neither subsumes the other AND they are NOT mutually exclusive. (v0.3.1) |
| `disjoint`        | Concepts are mutually exclusive by construction (e.g. algebraic vs transcendental functions). (v0.3.1) |

### Choosing among `incomparable`, `sibling`, `disjoint`, `overlapping`

| Situation                                                | Use                |
|----------------------------------------------------------|--------------------|
| Two concepts share an axis but neither subsumes the other; intersection is non-empty | `incomparable`     |
| Parallel concepts at the same level; both can apply or fail independently            | `sibling`          |
| Concepts are explicitly mutually exclusive by definition                              | `disjoint`         |
| Statements partially coincide on a common subdomain                                   | `overlapping`      |

If unsure, default to `incomparable` and add a `notes` field
explaining why.

### Use SPARINGLY

The generality layer should be used ONLY when the relation is:

- **Mathematically definite** (provable from the statements alone),
  not a reviewer's intuition.
- **Useful for navigation / retrieval** (if no agent will ever care,
  do not record it).

A heavy generality web is a SMELL — it usually indicates that the
authors over-fragmented closely related results, and the right fix is
to MERGE the redundant nodes (per `05-id-equivalence-policy.md`)
rather than wire them with generality edges.

### Symmetry and direction

- `equivalent` is symmetric. Record on EITHER node, not both
  (avoid duplicate edges). Convention: record on the node with the
  alphabetically earlier id.
- `incomparable`, `overlapping`, `sibling`, `disjoint` are symmetric.
  Same alphabetical-earlier-id convention.
- `stronger_than` / `weaker_than` are reciprocal. Record only ONE
  direction. Convention: record `stronger_than` on the stronger node.
- `special_case_of` records on the SPECIAL node. Its inverse
  (`generalization_of`) is NOT in the vocabulary; traversal handles it.

---

## D. Cross-layer rules

1. **Never duplicate.** If A → B is captured in one layer, do not
   re-record it in another layer with different framing.
2. **Proof layer takes precedence over concept layer.** If a proof
   `essential`-uses a definition, the THEOREM may STILL `depends_on`
   that definition with `role: ambient` or `uses_concept` — the
   theorem and its proof are different nodes with different concerns.
3. **Generality layer never replaces a proof.** If A is a corollary
   of B, you still need `proof.A.X` whose `uses: [{id: B}]`. The
   generality edge is a navigation hint, not a derivation.
4. **No self-loops.** A statement cannot depend on itself in any
   layer. The validator does not currently check this; reviewers
   must.

---

## E. Schema-extension policy (all three layers)

Adding any role / relation requires:

1. Schema change to `schema/v03.py` (the relevant Literal).
2. Test in `tests/v03/test_schema.py`.
3. Update to this document with a real-use justification.
4. JSON-Schema re-export.

Removing any role requires:

1. Migration script that re-classifies every existing edge.
2. Snapshot before and after.

The bar is high. A proposal "we need a role for X" must include at
least 5 candidate edges that ONLY the new role describes correctly.
