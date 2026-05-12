# MKG Graph Explorer

Interactive frontend for the Mathematical Knowledge Graph (MKG) v0.3.1.

A semantic browser for mathematical knowledge — visually explore proof
dependencies, conceptual dependencies, mathematical domains, source
provenance, ontology structure, and learning paths emerging from the graph.

---

## Stack

```
React 19 + TypeScript + Vite + Tailwind CSS v4 + Sigma.js + Graphology + KaTeX
```

- **Graphology** is the in-memory graph model.
- **Sigma.js** is the canvas/WebGL renderer (chosen over React Flow because
  this graph may grow to thousands of nodes).
- **Tailwind v4** for layout (via `@tailwindcss/vite`).
- **KaTeX** for LaTeX rendering.
- **Zustand** for app state.

---

## Data Source

The frontend consumes JSON only. It never reads YAML.

Expected files in `public/`:

```
public/graph.json          ← node-link export of the v0.3 graph
public/node-details.json   ← per-node detail blobs (i18n, LaTeX, sources, ...)
```

These are produced by:

```bash
python -m scripts.v03.build_db
```

which writes them to `generated/v0.3/{graph,node-details}.json`.

A sync script copies them into `public/`:

```bash
npm run sync
```

`sync` runs automatically as a `predev` and `prebuild` hook, so
`npm run dev` always picks up the latest export.

---

## Development

```bash
npm install
npm run dev        # localhost:5173
npm run build
npm run preview
```

Other scripts:

```bash
npm run sync       # copy generated/v0.3/*.json → public/
npm run lint
```

---

## Project Goal

Build the first serious MKG Graph Explorer that allows the user to:

- navigate the graph visually,
- inspect nodes deeply,
- filter by metadata,
- highlight dependency paths,
- distinguish proof edges from conceptual edges,
- understand mathematical structure,
- and explore the latest generated graph data.

---

## Required Features

### 1. Graph Rendering

Sigma.js + Graphology with:

- pan
- zoom
- hover
- click selection
- node labels
- edge highlighting
- responsive canvas

### 2. Node Styling

Color nodes by primary entity type:

```
definition    proposition    theorem    lemma
corollary     axiom          conjecture proof
```

Proof nodes must be visually distinct (size, border ring, and color).

### 3. Edge Styling

Distinguish edge types:

```
proof uses edge          (proof.uses statement)
proof proves edge        (proof → statement)
statement depends_on edge (conceptual)
generality edge
derived_from / redirected_to
```

Use different colors, thickness, and line styles. The visual language
must make obvious that:

```
depends_on  ≠  uses
```

### 4. Details Panel

Right-side panel for the selected node:

- id
- type / kind
- status
- title in available languages (with original-language indicator)
- original language
- natural statement (with language switcher)
- LaTeX rendered (KaTeX) if present
- `latex_status`
- domains
- ambient structures
- ontology `semantic_kind` + keywords
- quality axes
- sources (work, edition, chapter, section, theorem label, page, locator, url)
- proofs (`proved_by` for statements, `proves` for proofs)
- `uses`
- `depends_on`
- incoming / outgoing edges grouped by relation

### 5. Filters

Filters for:

- entity type
- source / work
- chapter
- status
- domains
- ambient structures
- ontology `semantic_kind`
- `latex_status`
- quality levels (per axis)
- proof role
- edge type / confidence

Filters update visibility via Sigma reducers — they NEVER mutate source data.

### 6. Search

Search by:

- id
- title (any language)
- statement text
- source locator
- theorem label

Result click focuses the node in the canvas (camera animation + select).

### 7. Neighborhood Exploration

For the selected node:

- show ancestors
- show descendants
- show immediate neighborhood
- show proof neighborhood (only `uses` / `proves`)
- show conceptual neighborhood (only `depends_on`)
- expand one hop
- reset view

Implemented with `graphology-traversal`. View modes:

- filter-only (dim others)
- subgraph mode (load only neighborhood into a second Sigma instance)

### 8. Path Highlighting

For the selected node:

- highlight incoming dependencies (ancestors closure)
- highlight outgoing dependents (descendants closure)
- dim unrelated graph
- shortest path between two pinned nodes (directed and undirected)

Helps answer:

```
What do I need to know before this?
What depends on this?
How does this theorem connect to the graph?
```

### 9. Graph Statistics

Lightweight stats bar:

- total nodes / edges
- nodes by type
- edges by type
- connected components (when available)
- selected subgraph size
- visible node count after filters

### 10. Layouts

At least:

- ForceAtlas2 (default, web worker)
- hierarchical / DAG-like (dagre, lazily and only on filtered subgraph)
- local neighborhood layout (ForceAtlas2 on subgraph)

DAG layout is size-aware — disabled / warned when the full graph exceeds
a configurable node-count threshold.

---

## UI Layout

```
┌──────── Top bar (dataset version, stats, layout selector) ─────────┐
│ Left           │       Sigma canvas        │ Right                  │
│ Search         │                           │ Details panel          │
│ Filters        │                           │                        │
└────────────────┴───────────────────────────┴────────────────────────┘
```

Tailwind for clean layout. Usability and graph exploration are prioritized
over visual flourish.

---

## Performance Requirements

- Canvas / WebGL rendering only (Sigma) — no per-node DOM.
- Debounce filters and search (~200 ms).
- Memoize reducers; avoid recomputation on every render.
- Subgraph mode auto-engages above a configurable node-count threshold.
- Label density / `labelGridCellSize` tuned for large graphs.

---

## Project Structure

```
visualization/web/
├── public/
│   ├── graph.json                  ← synced from generated/v0.3/
│   ├── node-details.json           ← synced from generated/v0.3/
│   └── favicon.svg
├── scripts/
│   └── sync.mjs                    ← copies generated/v0.3/*.json → public/
├── src/
│   ├── main.tsx
│   ├── App.tsx
│   ├── index.css                   ← @import "tailwindcss";
│   ├── theme.ts                    ← color palettes for nodes/edges
│   ├── i18n.ts
│   ├── data/
│   │   ├── types.ts                ← v0.3.1 export types
│   │   └── loadGraph.ts            ← fetch + Graphology builder
│   ├── state/
│   │   └── store.ts                ← Zustand store
│   └── components/
│       ├── GraphCanvas.tsx         ← Sigma + reducers
│       ├── DetailsPanel.tsx
│       ├── FilterPanel.tsx
│       ├── SearchBox.tsx
│       ├── StatsBar.tsx
│       └── MathBlock.tsx           ← KaTeX wrapper
├── package.json
├── vite.config.ts
└── README.md
```

---

## Build Plan (Phased)

### Phase 0 — Enrich graph exports (BLOCKING, Python side)

The current export at `generated/v0.3/node-details.json` only carries
`id`, `type`, `status`, `title`, `natural`, and (for proofs) `uses`.
The SQLite schema in `scripts/v03/build_db.py` already stores everything
needed; the JSON emit must be extended.

Extend `_node_details()` in `scripts/v03/build_db.py:513` to include,
for statements:

- `latex` body + `latex_status` + `latex_review`
- `domains` (primary + secondary)
- `ambient` structures
- `ontology` `semantic_kind` + `keywords`
- `quality` axes
- `sources` with full locator
- `provenance`
- `proved_by` (reverse of `proofs.proves`)
- `depends_on` (`statement_depends_on`)

For proofs:

- `latex` + `latex_status` / `review`
- `quality`
- `sources`
- `provenance`

Lightly enrich graph node payloads in `_build_graph()` so filters work
without joining: `primary_domain`, `semantic_kinds`, `latex_status`,
`quality_overall`. Full data stays in `node-details.json`.

Add tests in `tests/v03/` for the new fields, then re-run:

```bash
python -m scripts.v03.build_db
```

### Phase 1 — Frontend MVP

1. Tear down the previous Cytoscape app.
2. Add Sigma + Graphology + Tailwind v4 + Zustand + KaTeX.
3. Wire `npm run sync` (predev + prebuild hook).
4. Data layer: types + `loadGraph` + Graphology MultiDirectedGraph,
   neighbor indexing by relation.
5. `GraphCanvas` with node/edge reducers (color by type, distinct proof
   styling, edge styling per `relation` and `confidence`, dashed for
   `implicit:true`).
6. `DetailsPanel` rendering full node-details + adjacency.
7. `SearchBox` (debounced, multi-field).
8. `FilterPanel` (entity type, edge relation, status, source).
9. `StatsBar`.
10. ForceAtlas2 layout (web worker) with re-run button.
11. README (this file).

### Phase 2 — Advanced exploration

1. Neighborhood exploration (ancestors / descendants / proof / conceptual,
   1-hop expand, reset). Subgraph view mode.
2. Path highlighting (incoming / outgoing closures, shortest path between
   two pinned nodes — directed and undirected).
3. Advanced filters (domains, ambient, ontology, latex_status, quality
   levels, proof role, confidence threshold). URL state sync.
4. DAG layout (dagre) — lazy, subgraph-only above threshold. Local
   neighborhood layout.
5. Performance hardening (label density, debounced reducers, auto
   subgraph mode).
6. Polish (keyboard shortcuts, color legend, empty states, loading
   skeleton).

---

## Constraints

Do NOT:

- parse YAML in the browser,
- mutate generated graph data from the UI,
- implement extraction logic in the frontend,
- implement validation logic in the frontend,
- introduce backend requirements unless necessary,
- overfit to the current small graph (currently 144 nodes / 375 edges,
  designed to scale to thousands).

Do:

- build for growth,
- preserve metadata richness,
- keep the data model flexible,
- make graph exploration powerful,
- make future filters easy to add.

---

## Known Limitations

- Phase 0 must land before Phase 1 can render LaTeX, sources, domains,
  ambient structures, ontology, or quality axes — the export currently
  omits these fields.
- Sigma node shape customization is limited; proof vs statement
  distinction is currently encoded via color + size + border ring.
  A custom Sigma node program may be added later if needed.
- DAG layout is expensive; it is restricted to filtered subgraphs above
  a configurable node-count threshold.
- The dataset is bilingual (en / es) with `is_original` flags. The UI
  surfaces both; future sources may add more languages.

---

## Final Goal

Build the first serious MKG Graph Explorer:

```
a semantic browser for mathematical knowledge
```

where the user can visually explore proof dependencies, conceptual
dependencies, mathematical domains, source provenance, ontology
structure, and learning paths emerging from the graph.
