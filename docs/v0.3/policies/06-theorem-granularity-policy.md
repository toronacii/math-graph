# 06 — Theorem Granularity Policy

> When does a multi-part theorem become one node, two nodes, or one
> node with proof-level `parts[]`? When do we extract corollaries as
> their own nodes? This policy answers both.

---

## Core principle

Granularity follows **independent citability**, not textbook layout.

A theorem-shaped fragment becomes its own node when **another statement
or proof can usefully cite it on its own**. If no realistic future node
will ever cite a fragment in isolation, do not extract it.

The graph is for dependency analysis. Sub-units that never appear as
dependencies are noise.

---

## A. Three available granularity tools

v0.3 provides three independent mechanisms; they are NOT alternatives
to one another, they answer different questions.

| Mechanism | Lives on | Answers |
|---|---|---|
| Separate `Statement` nodes | one file each | "Are these independently citable mathematical truths?" |
| `Proof.parts[]` | inside one `Proof` file | "Is this proof internally case-split (direction / case / subclaim)?" |
| `Statement.generality[]` edges | on `Statement` | "How are these independent statements logically related?" |

Use the smallest mechanism that captures the intent. In particular:

- **Do NOT** introduce a separate node merely to record a proof
  case-split. Use `Proof.parts[]`.
- **Do NOT** stuff multiple independently-citable truths into one
  statement to "save files". Use separate nodes.

There is no `Statement.parts[]`. A statement is atomic by design.

---

## B. The decision tree

For a candidate fragment `F` of a textbook theorem `T`:

```text
1. Is F independently citable? (Will any future proof or theorem
   reasonably cite F without citing the rest of T?)
   - no  -> NOT a separate node. Either fold into T's statement,
            or record as a Proof.parts[] entry on the proof of T.
   - yes -> step 2.

2. Is F mathematically self-contained? (Can it be stated without
   referencing the other parts of T?)
   - no  -> NOT a separate node. Keep inside T; if proof-internal,
            use Proof.parts[]. If statement-shaped, this is a smell:
            reword T so the parts ARE self-contained, then split.
   - yes -> step 3.

3. Does F have its own proof or its own use-site?
   - one of the two -> SEPARATE NODE. Add generality edge to T (or
                       to siblings) per §D.
   - neither yet     -> Defer. Extract only T for now; revisit when
                        the use-site appears.
```

---

## C. Patterns

### C.1 Multi-part theorems that SPLIT (FTC pattern)

The Fundamental Theorem of Calculus has two classically separable
parts; both are cited independently throughout calculus and analysis.

```text
theorem.fundamental-theorem-of-calculus-part-1
  - "If f continuous on [a,b], then F(x) = ∫_a^x f is differentiable
     and F' = f."

theorem.fundamental-theorem-of-calculus-part-2
  - "If f continuous on [a,b] and F any antiderivative,
     then ∫_a^b f = F(b) - F(a)."
```

Each is a separate node, with its own proof file. They are linked:

```yaml
# part-1
generality:
  - target: theorem.fundamental-theorem-of-calculus-part-2
    relation: incomparable
    notes: >
      Part 2 follows from Part 1 + MVT, but neither subsumes the other
      as stated. Treat as siblings.
```

A textbook may call the umbrella "the Fundamental Theorem of
Calculus". Do NOT create a third node for the umbrella; it would have
no independent content. If you need a navigation entry point, that is
what the `generality` cluster provides.

Other classic split-cases: Rolle / MVT / Cauchy MVT (three nodes,
generality chain), L'Hôpital 0/0 vs ∞/∞ (two nodes), Heine–Borel "↔"
(two implications, often one node — see C.4).

### C.2 Theorems with cases inside one PROOF (`parts[]` pattern)

Many proofs are case-splits where the cases are not independently
citable. Example: "for ε > 0, choose δ ... case 1: x ≥ a; case 2:
x < a." These belong inside `Proof.parts[]`:

```yaml
# proof.absolute-value-continuous.direct
parts:
  - name: case-positive
    kind: case
    description: x ≥ 0
    uses:
      - id: definition.absolute-value
        role: definition
  - name: case-negative
    kind: case
    description: x < 0
    uses:
      - id: definition.absolute-value
        role: definition
      - id: theorem.limit-of-negation
        role: essential
```

Top-level `Proof.uses` may be left empty in this case (parts carry
the dependencies) or may list the union; the loader does not enforce
a particular convention but per-part is preferred when used.

### C.3 If-and-only-if statements

Default: ONE node, one statement, with both directions in the formal
content. The proof typically uses `Proof.parts[]` with two entries
of `kind: direction`:

```yaml
parts:
  - name: forward
    kind: direction
    description: "(⇒)"
    uses: [...]
  - name: backward
    kind: direction
    description: "(⇐)"
    uses: [...]
```

SPLIT into two nodes ONLY when one direction is independently cited
elsewhere with materially different hypotheses (rare). In that case
keep the iff node AND the directional node and link via
`special_case_of` / `stronger_than`.

### C.4 Corollaries

Default: ONE node, of type `corollary`, with `proved_by` pointing to
its own short proof file. A corollary is by definition independently
citable.

Do NOT extract a corollary if:

- the textbook only calls it a corollary as a remark and never uses
  the name elsewhere in the book, AND
- no other node will plausibly depend on it.

Do extract it (even speculatively) if it is a named result
(Heine–Borel, Bolzano–Weierstrass-as-corollary-in-some-texts, etc.).
Named results pay for themselves in retrieval.

### C.5 Lemmas internal to one proof

If a "lemma" appears only to support one specific proof and the
textbook does not cite it elsewhere:

- Prefer `Proof.parts[]` with `kind: subclaim`.
- Only create a `lemma.*` node if the lemma is named, restated, or
  reused.

This avoids inflating the lemma count with single-use scaffolding.

### C.6 Definition packages

Already covered by `01-bundled-definitions-audit.md`: a single
textbook definition introducing K independent concepts becomes K
atomic `definition.*` nodes. The umbrella id is retired (no
`redirected_to`); each atom records `provenance.derived_from`.

---

## D. Linking siblings produced by a split

When a textbook unit `T` is split into siblings `T1, T2, ..., Tn`:

1. Add `generality` edges among siblings expressing how they relate
   (`incomparable`, `stronger_than`, `equivalent`, `special_case_of`).
   Recorded once per pair per the conventions in
   `04-edge-role-taxonomy.md`.
2. Do NOT create an "umbrella" node unless `T` has its own
   independent mathematical content beyond "the conjunction of
   `T1..Tn`".
3. Each sibling carries `sources` for the umbrella (e.g., "Stewart
   §5.4 'Fundamental Theorem of Calculus, Part 1'") so traceability
   to the textbook is preserved.

---

## E. Anti-patterns

Stop and reconsider if you are about to:

- **Create one node per case of a finite case-split inside a single
  proof.** → Use `Proof.parts[]`.
- **Create one node per direction of an iff that is never cited
  directionally elsewhere.** → Keep one node; use `parts[]` in the
  proof.
- **Create an "umbrella" node whose content is only "T1 and T2".** →
  No node; rely on `generality` edges and shared sources.
- **Refuse to split a textbook theorem because the textbook calls it
  one theorem.** → Independent citability wins over textbook layout.
- **Hide a named corollary inside its parent theorem to "keep things
  tidy".** → Named ⇒ extract.
- **Promote a one-use scaffolding lemma to a `lemma.*` node.** →
  Use `Proof.parts[].kind: subclaim`.

---

## F. Worked examples

### F.1 FTC (split, two nodes)

Per §C.1: two nodes + sibling `generality` edges + two proof files.

### F.2 Continuity on an interval

Stewart-style "f is continuous on [a,b] iff continuous from the right
at a, from the left at b, and continuous at every interior point."

This is one statement of one fact. ONE node:
`theorem.continuity-on-closed-interval-characterisation` (or stays as
`definition.continuity-on-interval` per existing v0.2 convention).
The "iff" is the statement; the proof has two `direction` parts.

### F.3 EVT (one node, internal case-split in proof)

EVT has a proof with cases (sup attained vs. sup not attained →
contradiction). One statement node, `Proof.parts[]` with `case`
entries.

### F.4 Squeeze theorem two-sided + one-sided

`theorem.squeeze-theorem` (two-sided) and `theorem.squeeze-theorem-one-sided`
(one-sided variant) are SEPARATE nodes if the textbook (or a future
proof) cites the one-sided version independently. Otherwise keep
only the two-sided version.

### F.5 Heine–Borel "↔"

"A subset of R^n is compact iff closed and bounded." One node. Proof
uses two `direction` parts. Do NOT split into "compact ⇒ closed and
bounded" and "closed and bounded ⇒ compact" — neither direction is
typically cited in isolation.

(If a downstream proof IS found to need only one direction with a
materially different setup, revisit and split per §C.3.)

---

## G. Operator checklist (per candidate fragment)

- [ ] Did I run the §B decision tree?
- [ ] If I am splitting: are the siblings linked by `generality`?
- [ ] If I am NOT splitting an iff / case / direction: is the proof
      using `Proof.parts[]` to localise dependencies?
- [ ] Am I extracting a named result that is currently unreferenced?
      (acceptable — name it and keep)
- [ ] Am I extracting an unnamed scaffolding lemma? (reject — use
      `parts[].kind: subclaim`)

If any answer is wrong, fix granularity BEFORE writing edges. Edges
are the expensive part to redo.
