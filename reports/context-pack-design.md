# Context Pack System — Design Report (v2)

## Architecture

```
YAML → SQLite (build_db.py) → Context Pack Generator (make_context_pack.py) → Markdown + Metrics YAML
```

The context pack generator reads from the SQLite database (readonly) and produces
a targeted markdown document plus a `.metrics.yml` sidecar for each `(source, chapter)` pair.

## Usage

```bash
# Ensure DB is up to date
python -m scripts.build_db

# Generate a context pack (extraction mode, default)
python -m scripts.make_context_pack --source rudin --chapter 7

# Generate in audit mode (broader context for reviewing existing entities)
python -m scripts.make_context_pack --source rudin --chapter 6 --mode audit
```

Output:
- `generated/context-packs/rudin-chapter-07.md`
- `generated/context-packs/rudin-chapter-07.metrics.yml`

## Sections

| # | Section | Purpose |
|---|---------|---------|
| 1 | Extraction Target | Identifies the source, chapter, work, and mode |
| 2 | Previous-Chapter Frontier | Top-15 most-reused nodes from earlier chapters of same source |
| 3 | Source Locator Map | Maps textbook locators (e.g., "Theorem 6.4") to MKG node IDs |
| 4 | Related Existing Nodes | Dependencies of previous chapter + topic-relevant nodes from other sources |
| 5 | Multi-Source Collision Candidates | Already-merged nodes + potential overlaps (no truncation) |
| 6 | Naming Conventions | ID patterns, examples, and rules inferred from existing graph |
| 7 | Canonical YAML Templates | Copy-paste templates for statements and proofs |
| 8 | Nearby Weak Dependencies | Low/medium confidence proofs and unproved statements |
| 9 | Known Ontology Warnings | Curated list of semantic pitfalls from project audits |
| 10 | Local Graph Snapshot | Global stats, source stats, and highest-degree nodes |

## v2 Improvements Over v1

1. **Source Locator Map (Section 3)** — Derives `Theorem 6.4 → theorem.refinement-upper-lower-sums`
   from existing `section` field in source metadata. No schema change needed. Covers all
   chapters up to and including target.

2. **Canonical YAML Templates (Section 7)** — Provides ready-to-copy templates for
   statements, proofs, and multi-source shared nodes. Eliminates formatting guesswork.

3. **No truncation of collision candidates** — Section 5 lists ALL potential overlaps,
   grouped by type. This prevents missed merges during extraction.

4. **Topic-based retrieval (Section 4)** — Replaced chapter-number matching with a
   `SOURCE_CHAPTER_TOPICS` dictionary providing topic keywords per source/chapter.
   Nodes from other sources are scored by keyword match against title/natural text.

5. **Metrics sidecar** — Each pack generates a `.metrics.yml` with estimated tokens,
   locator count, collision candidate count, retrieval strategy metadata.

6. **Extraction/audit mode flag** — `--mode extraction` (default) vs `--mode audit`.
   Currently affects header metadata; future versions may adjust section verbosity.

## Selection Heuristics

### Previous-Chapter Frontier (Section 2)
- Query: all statements from same source with chapter < target chapter
- Ranking: by `proof_uses` fan-in (how often each node is used by proofs)
- Limit: top 15
- Rationale: high-reuse nodes are most likely to be referenced by the new chapter

### Source Locator Map (Section 3)
- Query: all statements from same source with chapter ≤ target, having non-empty `section`
- Grouped by chapter, sorted by section number
- Display: `{Type} {section}` → `{node_id}`
- Rationale: agents referencing "Theorem 4.23" can instantly look up the correct node ID

### Related Existing Nodes (Section 4)
- Sub-section A: What the immediately previous chapter's proofs depended on
  - Useful because new proofs often build on the same foundations
- Sub-section B: Topic-keyword retrieval from other sources
  - Keywords from `SOURCE_CHAPTER_TOPICS[source][chapter]`
  - Scored by match count against title + natural language text
  - Top 20 shown, sorted by relevance score
  - Replaces naive "same chapter number" heuristic from v1

### Collision Candidates (Section 5)
- Shows all already-merged multi-source nodes (full list, no truncation)
- Shows nodes from other sources in chapters ±1 that are NOT yet merged
- Also shows topic-matched candidates from ANY chapter of other sources
- All candidates grouped by type for readability
- Helps extraction agents identify potential duplicates before creating new nodes

### Naming Conventions (Section 6)
- Extracts type distribution and example IDs from the database
- Shows proof ID format with examples
- Includes static rules from AGENTS.md

### Canonical YAML Templates (Section 7)
- Three templates: minimal statement, minimal proof, multi-source shared
- Includes field reference (valid types, statuses, styles, confidence levels)

### Weak Dependencies (Section 8)
- Lists all proofs with confidence < high (limited to 15 for readability)
- Lists provable statements that lack any proof node (limited to 10)
- Helps agents avoid depending on unreliable nodes

### Ontology Warnings (Section 9)
- Static curated list derived from audit findings
- Will be updated as new audits discover patterns

### Local Graph Snapshot (Section 10)
- Global node/edge counts
- Source-specific contribution stats and chapters extracted
- Top-10 highest-degree statement nodes

## Metrics Sidecar

Each generated pack produces a `.metrics.yml` file with:

```yaml
source: rudin
chapter: '7'
mode: extraction
estimated_tokens: 8377
estimated_chars: 33508
locator_mappings: 194
collision_candidates_nearby: 13
multi_source_nodes: 23
weak_dependencies: 28
ontology_warnings: 5
topic_keywords: 5
retrieval_strategy: topic-keywords + nearby-chapters + frontier
```

This enables tracking pack growth and retrieval effectiveness over time.

## Future Extensibility

The architecture is designed to accommodate:

1. **Embedding-based retrieval** — Add a `_section_semantic_neighbors()` function
   that queries a vector index for nodes semantically similar to the chapter topic.

2. **Confidence-weighted retrieval** — Weight node relevance by proof confidence
   and dependency completeness scores.

3. **Dynamic ontology warnings** — Generate warnings automatically from graph
   patterns (e.g., high fan-in on bundled definitions, proofs with many implicit
   imports mentioned in notes but not in uses).

4. **Chapter-topic inference** — If chapter titles are stored in metadata,
   use them for better semantic matching across sources.

5. **Incremental generation** — Cache context packs and regenerate only when
   the database changes (compare DB mtime vs pack mtime).

6. **Mode-sensitive sections** — Audit mode could show broader context (more
   candidates, cross-source coverage analysis) while extraction mode stays minimal.

## Design Principles

- **Minimal context, maximal value** — Each section is limited (top-10/15/20)
- **No silent truncation** — Collision candidates show ALL items (critical for correctness)
- **Query-based, not dump-based** — All content is derived from SQL queries
- **Readonly** — Never modifies the database or YAML
- **Idempotent** — Running twice produces the same output
- **Source-aware** — Understands multi-source architecture
- **Audit-informed** — Incorporates lessons from graph audits
- **Token-conscious** — Metrics track estimated token usage (~8-9K tokens typical)
