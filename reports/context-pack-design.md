# Context Pack System — Design Report

## Architecture

```
YAML → SQLite (build_db.py) → Context Pack Generator (make_context_pack.py) → Markdown
```

The context pack generator reads from the SQLite database (readonly) and produces
a targeted markdown document for each `(source, chapter)` pair.

## Usage

```bash
# Ensure DB is up to date
uv run python -m scripts.build_db

# Generate a context pack
uv run python -m scripts.make_context_pack --source rudin --chapter 6
```

Output: `generated/context-packs/rudin-chapter-06.md`

## Sections

| # | Section | Purpose |
|---|---------|---------|
| 1 | Extraction Target | Identifies the source, chapter, and work |
| 2 | Previous-Chapter Frontier | Top-15 most-reused nodes from earlier chapters of same source |
| 3 | Related Existing Nodes | Dependencies of previous chapter + same-chapter nodes from other sources |
| 4 | Multi-Source Collision Candidates | Already-merged nodes + potential overlaps from other sources |
| 5 | Naming Conventions | ID patterns, examples, and rules inferred from existing graph |
| 6 | Nearby Weak Dependencies | Low/medium confidence proofs and unproved statements |
| 7 | Known Ontology Warnings | Curated list of semantic pitfalls from project audits |
| 8 | Local Graph Snapshot | Global stats, source stats, and highest-degree nodes |

## Selection Heuristics

### Previous-Chapter Frontier (Section 2)
- Query: all statements from same source with chapter < target chapter
- Ranking: by `proof_uses` fan-in (how often each node is used by proofs)
- Limit: top 15
- Rationale: high-reuse nodes are most likely to be referenced by the new chapter

### Related Existing Nodes (Section 3)
- Sub-section A: What the immediately previous chapter's proofs depended on
  - Useful because new proofs often build on the same foundations
- Sub-section B: Same chapter number from other sources
  - Useful because topics often align across textbooks by chapter

### Collision Candidates (Section 4)
- Shows all already-merged multi-source nodes (full list)
- Shows nodes from other sources in chapters ±1 that are NOT yet merged
- Helps extraction agents identify potential duplicates before creating new nodes

### Naming Conventions (Section 5)
- Extracts type distribution and example IDs from the database
- Shows proof ID format with examples
- Includes static rules from AGENTS.md

### Weak Dependencies (Section 6)
- Lists all proofs with confidence < high
- Lists provable statements that lack any proof node
- Helps agents avoid depending on unreliable nodes

### Ontology Warnings (Section 7)
- Static curated list derived from audit findings
- Will be updated as new audits discover patterns

### Local Graph Snapshot (Section 8)
- Global node/edge counts
- Source-specific contribution stats
- Top-10 highest-degree statement nodes

## Future Extensibility

The architecture is designed to accommodate:

1. **Embedding-based retrieval** — Add a `_section_semantic_neighbors()` function
   that queries a vector index for nodes semantically similar to the chapter topic.

2. **Topic clustering** — Add a `_section_topic_cluster()` function that identifies
   mathematical topic clusters (e.g., "integration", "convergence") and retrieves
   relevant nodes regardless of source/chapter.

3. **Confidence-weighted retrieval** — Weight node relevance by proof confidence
   and dependency completeness scores.

4. **Dynamic ontology warnings** — Generate warnings automatically from graph
   patterns (e.g., high fan-in on bundled definitions, proofs with many implicit
   imports mentioned in notes but not in uses).

5. **Chapter-topic inference** — If chapter titles are stored in metadata,
   use them for better semantic matching across sources.

6. **Incremental generation** — Cache context packs and regenerate only when
   the database changes (compare DB mtime vs pack mtime).

## Design Principles

- **Minimal context, maximal value** — Each section is limited (top-10/15/20)
- **Query-based, not dump-based** — All content is derived from SQL queries
- **Readonly** — Never modifies the database or YAML
- **Idempotent** — Running twice produces the same output
- **Source-aware** — Understands multi-source architecture
- **Audit-informed** — Incorporates lessons from graph audits
