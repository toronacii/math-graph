# Audit: Rudin Connectedness and MKG Graph Integrity

Date: 2026-05-11
Scope: Observational audit of the active node `proof.connected-subsets-of-r.rudin`, its immediate dependency neighborhood, and several global graph-health signals.
Mutation policy: No statement, proof, schema, generated graph, or classification file was modified. This report is the only artifact created.

Validation snapshot:

- `python -m scripts.validate` reports `OK -- all entities valid`.
- Current loaded dataset: 326 statements, 201 proofs, 527 total nodes, 687 directed dependency edges.
- Global weakly connected components: 62. Largest component: 464 nodes. Remaining structure includes one component of size 3 and 60 singleton components.
- Root nodes: 143, all definitions.
- All 527 entities are still `draft`.
- 89 statements lack a `statement.latex` field.
- 550 source records lack `page` or `locator` metadata.

The validation result should not be interpreted as semantic health. The validator currently checks syntax, referential integrity, symmetry, and acyclicity. It does not check whether dependencies are mathematically adequate.

## 1. Critical Issues

### 1.1 Under-specified proof dependencies for `theorem.connected-subsets-of-r`

Description:

`data/proofs/proof.connected-subsets-of-r.rudin.yml:7-10` lists only:

- `definition.separated-connected`
- `definition.supremum`
- `proposition.sup-in-closure`

The proof note at `data/proofs/proof.connected-subsets-of-r.rudin.yml:21-22` invokes a substantially richer argument: separation by cuts at a missing point, existence of `sup(A cap [x,y])`, closure membership, exclusion from separated components, and construction of a point `z_1` between `z` and `y` outside `E`.

Why it matters:

The edge to `definition.supremum` records the meaning of `sup`, not the existence of the supremum of a nonempty bounded subset of `R`. That existence comes from completeness, represented elsewhere as `definition.least-upper-bound-property` and `theorem.existence-of-reals`. The current proof imports completeness semantically but does not expose it structurally.

The proof also appears to use interval/order facts that are not represented in `uses`, including at least:

- interval notation and boundedness, from `definition.segment-interval-cell-ball`
- order trichotomy/transitivity, from `definition.order-relation`
- ordered-field/order-density or midpoint existence to choose a point strictly between two reals
- closure/separation interaction beyond the bare definition of connectedness

Likely future consequences:

The graph will understate the dependence of connectedness and IVT on real completeness. `proof.intermediate-value-theorem.rudin.yml:6-8` depends on `theorem.connected-subsets-of-r` and `theorem.continuous-image-connected`; therefore the hidden completeness import propagates into IVT while remaining invisible in graph queries.

Suggested mitigation:

Mark this proof as semantically under-specified until it records the real-completeness dependency explicitly. Distinguish "uses supremum notation" from "uses existence of supremum." If the project wants to avoid adding many low-level order facts as hard edges, record them as explicit implicit imports with confidence and role metadata.

### 1.2 `definition.supremum` is being used as an existence theorem

Description:

The same pattern appears in multiple high-confidence proofs:

- `proof.connected-subsets-of-r.rudin` uses `definition.supremum`.
- `proof.monotone-convergence.rudin.yml:7-11` uses `definition.supremum` to let `s = sup E`.
- `proof.extreme-value-theorem-compact-metric.rudin.yml:6-8` uses `definition.supremum` after showing an image is closed and bounded.
- `proof.sup-in-closure.rudin.yml:7-9` uses `definition.supremum`, though its statement assumes the supremum already exists.

Why it matters:

A definition of supremum is not a guarantee that a supremum exists. Treating the definition as an existence engine collapses the distinction between order vocabulary and completeness. That distinction is one of the main reasons Rudin Chapter 1 matters.

Likely future consequences:

Completeness-dependent theorems will appear no more foundationally expensive than purely order-theoretic theorems. Queries such as "which theorems depend on completeness of `R`?" will miss key results or return misleadingly short chains.

Suggested mitigation:

Introduce a dependency-role convention for every `definition.supremum` edge:

- `notation/meaning`: the proof assumes a supremum already exists.
- `existence`: the proof uses the least-upper-bound property or existence of `R`.

At minimum, proofs that establish existence of a supremum for a bounded set of reals should also depend on `definition.least-upper-bound-property` or an explicit theorem/axiom representing completeness.

### 1.3 False-equivalence risk in multi-source nodes

Description:

Several merged Stewart/Rudin nodes violate or strain the repository's own identity criterion: same node only if logically equivalent in full generality.

Concrete examples:

- `proposition.increasing-decreasing-test.yml:11-18` states Stewart's strict derivative version: `f'(x) > 0` implies increasing and `f'(x) < 0` implies decreasing. But `data/proofs/proof.increasing-decreasing-test.rudin.yml:20-23` proves Rudin's non-strict version: `f'(x) >= 0` implies monotonically increasing and `f'(x) <= 0` implies monotonically decreasing. The note at `data/statements/proposition.increasing-decreasing-test.yml:42-47` admits Rudin's version subsumes Stewart's. Subsumption is not equivalence.
- `definition.local-maximum.yml:35-38` and `definition.local-minimum.yml:35-38` admit that Rudin defines these concepts on a general metric space, while the stored statement at `definition.local-maximum.yml:15-20` and `definition.local-minimum.yml:15-20` is the real-line interval version. Equivalence "on `R`" is not full-generality equivalence.
- `theorem.power-series-convergence.yml:38-48` lists both Stewart and Rudin as sources, but `proved_by` at `theorem.power-series-convergence.yml:35-36` lists only the Stewart proof. There is no Rudin proof node despite the source being merged.

Why it matters:

These are not merely editorial differences. They affect theorem strength, valid reuse, dependency direction, and future proof search. A stronger theorem can prove a weaker theorem, but it should not be silently identified with it.

Likely future consequences:

As more sources are added, the graph will accumulate nodes that are partly source-merged and partly source-specialized. Eventually, the same ID will mean different things depending on which proof path is followed.

Suggested mitigation:

Audit all 23 multi-source statements before adding another major source. For each merged node, require an explicit equivalence note using the full-generality criterion. When one source is strictly more general, create separate general and special-case nodes with a proof edge from the general result to the special result.

### 1.4 Reports understate semantic debt by equating resolved links with adequate dependencies

Description:

The weak-dependency reports repeatedly declare no debt:

- `reports/rudin-chapter-02-weak-dependencies.yml:1` says `weak_dependencies: []`.
- `reports/rudin-chapter-02-weak-dependencies.yml:47-51` says all Chapter 2 proofs have high confidence and implicit imports are conventional or tracked.
- `reports/rudin-chapter-04-weak-dependencies.yml:3-6` says Chapter 4 proofs are explicit and self-contained.
- `reports/rudin-chapter-05-weak-dependencies.yml:3-7` says all dependency references resolve and shared nodes already have established dependencies.

Why it matters:

Resolved references are not the same as semantically sufficient references. The active connectedness proof is a counterexample: references resolve, the graph is acyclic, and confidence is high, but key assumptions remain hidden.

Likely future consequences:

The reports will create false assurance. Later contributors may treat "no weak dependencies" as an epistemic guarantee when it is currently only a syntactic or extraction-confidence claim.

Suggested mitigation:

Separate at least three notions:

- schema validity
- extraction confidence
- dependency completeness

The last one requires mathematical audit and should not default to high merely because Rudin is rigorous or because references resolve.

## 2. Structural Risks

### 2.1 Packed definition nodes distort dependency granularity

Description:

`definition.neighborhood-limit-point-open-closed.yml:9-11` bundles neighborhood, limit point, isolated point, closed, interior, open, complement, perfect, bounded, and dense into one node. `definition.segment-interval-cell-ball.yml:9-11` bundles segment, interval, k-cell, open ball, closed ball, and convexity.

Why it matters:

These are not interchangeable concepts. A proof that uses "closed" should not be graph-indistinguishable from a proof that uses "dense" or "perfect." The current bundled nodes inflate hub centrality while lowering semantic resolution.

Likely future consequences:

Hub analysis will confuse author packaging with mathematical centrality. Future topology and metric-space chapters will route too many edges through a few omnibus definitions, creating artificial bottlenecks.

Suggested mitigation:

Either split high-degree bundled definitions into atomic concept nodes or add sub-concept anchors that allow a proof to specify which part of a bundled textbook definition it uses.

### 2.2 `uses` edges have no role, polarity, confidence, or locality

Description:

The schema stores `Proof.uses` as a plain list of statement IDs (`schema/models.py:166-168`). There is no place to say how an item is used.

Why it matters:

The graph cannot distinguish:

- essential theorem dependency
- notation import
- background object definition
- existence principle
- local lemma used only in one proof direction
- implicit foundational import
- uncertain dependency

Likely future consequences:

Proof fan-in will remain low but misleading. Complex theorems will look clean because edge semantics are compressed out of existence.

Suggested mitigation:

Allow optional structured dependency entries, for example `id`, `role`, `confidence`, `direction`, and `notes`. Preserve the current simple list as shorthand only for unambiguous essential dependencies.

### 2.3 The schema does not enforce stated mathematical representation rules

Description:

The project rules say human-readable mathematics must use LaTeX, but `StatementBody.latex` is optional in `schema/models.py:107-112`. The audit found 89 statements without `statement.latex`. The active target `theorem.connected-subsets-of-r.yml:8-12` has no LaTeX field.

Why it matters:

Natural-language statements with Unicode mathematical symbols are readable but hard to normalize, compare, search, or disambiguate across sources. This directly weakens the multi-source identity criterion.

Likely future consequences:

Duplicate detection and theorem generality comparison will become increasingly manual. Similar theorems will be merged or split based on prose impressions instead of comparable mathematical form.

Suggested mitigation:

Make missing LaTeX a validation warning immediately and eventually an error for non-definition statements. For definitions, require LaTeX when symbols, equations, or formal conditions appear in natural text.

### 2.4 Source traceability is too coarse

Description:

All 550 source records currently lack `page` or `locator` metadata. Sections are present, but section-level citations are often too coarse for audit and correction.

Why it matters:

When a dependency or merge decision is challenged, a section pointer may be insufficient to reconstruct the exact statement or proof fragment. This is especially dangerous for long sections containing examples, informal remarks, and multiple theorem variants.

Likely future consequences:

Human reviewers will spend increasing time rediscovering extraction context. Disputed nodes will be harder to adjudicate, and later corrections may accidentally alter the wrong formulation.

Suggested mitigation:

Require page, theorem number, exercise number, or stable locator when available. At minimum, distinguish theorem-level locator from section-level source.

## 3. Semantic Ambiguities

### 3.1 `theorem.connected-subsets-of-r` conflates "interval" language with order-convexity

Description:

`theorem.connected-subsets-of-r.yml:10-11` states an order-convexity condition. The note at `theorem.connected-subsets-of-r.yml:24-25` says connected subsets of `R` are precisely intervals.

Why it matters:

"Interval" has multiple conventions: open, closed, half-open, degenerate, empty, rays, and sometimes generalized intervals. The stored theorem avoids the word in the formal statement but uses it in the note, while no LaTeX or explicit interval-family formulation is present.

Likely future consequences:

Future sources may state "connected subsets of `R` are intervals" and be merged without checking whether they include empty sets, singleton sets, rays, or degenerate intervals under the same convention.

Suggested mitigation:

Record the exact order-convex condition in LaTeX. If "interval" is used as an alternate title/formulation, add a note specifying the interval convention.

### 3.2 Definitions mix objects, properties, and bundled axiom systems

Description:

The graph currently stores very different semantic objects under `definition`: objects (`definition.euclidean-k-space`), properties (`definition.compact-set`), relation schemas (`definition.order-relation`), and axiom bundles (`definition.field.yml:11-19`).

Why it matters:

This is acceptable for early extraction, but graph queries over "definitions" will become ontologically coarse. A proof using the field axioms is not just using the word "field"; it may use associativity, inverse existence, or distributivity.

Likely future consequences:

Algebra, topology, logic, and category theory will expose this pressure sharply. Definitions will become miniature theories, but the graph will still treat them as atomic roots.

Suggested mitigation:

Do not prematurely formalize all axioms. But introduce an optional `ontology` or `concept_role` field to distinguish object definition, property definition, relation definition, operation definition, axiom bundle, theorem schema, and proof technique.

### 3.3 Confidence is overloaded

Description:

Most Rudin proofs are marked high confidence. This appears to mean extraction confidence or trust in Rudin, not completeness of the represented dependency list.

Why it matters:

The active connectedness proof is mathematically standard, but the represented dependency list is incomplete. A single scalar `confidence: high` cannot express "source proof is rigorous, extraction is probably correct, but dependency list is incomplete."

Likely future consequences:

Reviewers will need to infer what confidence means from context. That will make weak-dependency reports less reliable over time.

Suggested mitigation:

Split confidence into at least:

- `statement_confidence`
- `source_alignment_confidence`
- `dependency_completeness_confidence`

## 4. Graph-Theoretic Concerns

### 4.1 Root explosion is currently masked by treating all definitions as roots

Description:

The graph has 143 roots, all definitions. This is not automatically wrong, but it is not a stable foundation model.

Why it matters:

Many definitions depend conceptually on prior definitions: compactness depends on open cover, open cover depends on open set, open set depends on metric neighborhood, and so on. Some of these dependencies are represented indirectly through proofs, but definitions themselves cannot depend on other definitions in the current architecture.

Likely future consequences:

The root layer will grow without indicating actual conceptual order. The graph will increasingly confuse "unproved" with "primitive."

Suggested mitigation:

Consider a separate non-proof relation for definitional dependence, or allow definition nodes to have `depends_on` references distinct from theorem-proving edges. This need not violate `Statement -> Proof -> Statement` for asserted mathematical facts.

### 4.2 Chapter-local connectivity can be artificial

Description:

`reports/rudin-chapter-02-structural-analysis.md:27-31` reports a fully connected Chapter 2 subgraph with no isolated nodes. But the same report identifies `definition.neighborhood-limit-point-open-closed` as a packed hub at `reports/rudin-chapter-02-structural-analysis.md:45-49`.

Why it matters:

A chapter can be graph-connected because many proofs touch a bundled definition, not because the dependency topology has high semantic coherence.

Likely future consequences:

Connected-component metrics may reward over-bundling. Extraction choices will change graph health metrics independently of the mathematics.

Suggested mitigation:

Track "semantic atom count" or "bundled concept count" for high-degree definitions. Report both raw graph connectivity and adjusted connectivity after expanding bundled definitions.

### 4.3 Proof fan-in appears suspiciously low for several deep results

Description:

The largest proof fan-in in the current graph is only 6 dependencies. Many substantial results have 2 to 4 dependencies.

Why it matters:

Low fan-in is desirable when dependencies are well-abstracted, but it can also signal dependency under-specification. The active connectedness proof has fan-in 3 while hiding order, interval, closure, and completeness assumptions.

Likely future consequences:

Shortest-path and dependency-depth analyses will systematically undercount conceptual prerequisites.

Suggested mitigation:

Add an audit query for "complex proof note with low fan-in" and "proofs using high-level theorem plus bare definition." These should be reviewed manually before being marked dependency-complete.

## 5. Scalability Concerns

### 5.1 The architecture lacks explicit ambient context

Description:

Statements do not record ambient theory, domain, logic, or structural context. The graph implicitly assumes classical real analysis unless a statement happens to say otherwise.

Why it matters:

The multi-source guide says the graph should eventually represent all of mathematics. That requires distinguishing results in ordered fields, complete ordered fields, metric spaces, topological spaces, normed vector spaces, manifolds, categories, and non-classical foundations.

Likely future consequences:

False merges will accelerate when sources move beyond calculus and real analysis. The same phrase may describe different theorems in different ambient categories.

Suggested mitigation:

Add optional context metadata: `ambient_structure`, `domain`, `logic`, `hypotheses_scope`, and `generality_relation`.

### 5.2 Theorem families and parameterized generality are not represented

Description:

The current node model represents a statement as one fixed assertion. It has no mechanism for theorem schemas, indexed theorem families, or parameterized variants.

Why it matters:

Many future results are not single isolated assertions: compactness preservation across topological spaces, isomorphism theorems across algebraic categories, Yoneda-style schemas, model-theoretic compactness, and duality principles all have parameterized forms.

Likely future consequences:

The graph will either over-merge variants into vague nodes or explode into many near-duplicates with unclear relationships.

Suggested mitigation:

Introduce a way to record generality relations between statements: equivalent, strictly stronger, strictly weaker, special case, overlapping, and incomparable.

### 5.3 Proof nodes will eventually need internal structure, but not full formalization

Description:

The current `Statement -> Proof -> Statement` model is sufficient for coarse dependency topology, but not for proofs with multiple independent directions, cases, reductions, or reusable proof techniques.

Why it matters:

The active connectedness proof has two directions. Different dependencies are used in each direction. The current proof node cannot localize dependencies to the forward direction, converse direction, or a specific construction.

Likely future consequences:

Dependencies will become all-or-nothing at the proof level. Reusable proof techniques, proof transformations, and alternate derivations will be difficult to analyze.

Suggested mitigation:

Add optional lightweight proof sections, such as `parts`, `cases`, or `directions`, each with local `uses`. This preserves the anti-formalization stance while improving graph fidelity.

## 6. Recommendations

1. Re-audit `proof.connected-subsets-of-r.rudin` before using it as a trusted dependency hub for IVT and later real-analysis results.

2. Add a semantic audit rule for any proof that uses `definition.supremum`: determine whether it uses only the definition or also the least-upper-bound property.

3. Audit all multi-source nodes now. Priority targets:

- `proposition.increasing-decreasing-test`
- `definition.local-maximum`
- `definition.local-minimum`
- `theorem.power-series-convergence`

4. Upgrade weak-dependency reports so `weak_dependencies: []` cannot be emitted merely because all references resolve. Add a separate field for `semantic_dependency_audit_status`.

5. Add validation warnings for:

- missing `statement.latex`
- source records without page/locator
- statement sources whose works are not represented by any proof source for non-definition statements
- high-confidence proofs with notes mentioning concepts absent from `uses`

6. Split or sub-index the highest-risk bundled definitions before topology grows further:

- `definition.neighborhood-limit-point-open-closed`
- `definition.segment-interval-cell-ball`
- `definition.field`
- `definition.separated-connected`

7. Introduce edge-level dependency metadata before adding category theory, abstract algebra, or logic. The current flat `uses` list will not scale to theorem schemas, ambient contexts, or non-equivalent generalizations.

## 7. Urgency Level

Overall urgency: High.

Immediate urgency:

- `proof.connected-subsets-of-r.rudin` should not be treated as dependency-complete in its current representation.
- Multi-source nodes with admitted strict generality differences should be resolved before further source integration.
- `theorem.power-series-convergence` has a source/proof mismatch that should be corrected before reports treat source coverage as complete.

Strategic urgency:

The graph is still small enough to repair these patterns. If the same modeling habits continue through abstract algebra, topology beyond metric spaces, logic, or category theory, the cost of separating false equivalences and hidden assumptions will grow nonlinearly.
