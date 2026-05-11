"""Build the MKG dependency graph and emit JSON + GraphML.

Also generates ``node-details.json`` — a lightweight per-node metadata
artifact for the visualization details panel.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import networkx as nx

from scripts.loader import REPO_ROOT, Dataset, load_dataset
from scripts.validate import validate

GRAPH_DIR = REPO_ROOT / "generated" / "graph"
EXPORT_DIR = REPO_ROOT / "generated" / "exports"


def build_graph(ds: Dataset) -> nx.MultiDiGraph:
    g: nx.MultiDiGraph = nx.MultiDiGraph()

    for sid, stmt in ds.statements.items():
        g.add_node(
            sid,
            kind="statement",
            type=stmt.type,
            status=stmt.status,
            title_en=stmt.title.get("en", ""),
            title_es=stmt.title.get("es", ""),
        )

    for pid, proof in ds.proofs.items():
        g.add_node(
            pid,
            kind="proof",
            type="proof",
            status=proof.status,
            style=proof.style or "",
        )
        for ref in proof.uses:
            g.add_edge(ref, pid, relation="uses")
        g.add_edge(pid, proof.proves, relation="proves")

    return g


def _source_to_dict(src: Any) -> dict[str, str]:
    """Convert a Source model to a compact dict, omitting None fields."""
    out: dict[str, str] = {}
    for key in ("work", "author", "edition", "chapter", "section", "page", "locator", "url"):
        val = getattr(src, key, None)
        if val is not None:
            out[key] = val
    return out


def build_node_details(ds: Dataset) -> dict[str, dict]:
    """Build the node-details lookup keyed by node id."""
    details: dict[str, dict] = {}

    for sid, stmt in ds.statements.items():
        entry: dict[str, Any] = {
            "id": sid,
            "kind": "statement",
            "type": stmt.type,
            "status": stmt.status,
            "title": dict(stmt.title),
        }

        # Natural-language statement text (multilingual).
        if stmt.statement.natural:
            entry["natural"] = dict(stmt.statement.natural)

        # LaTeX representation.
        if stmt.statement.latex:
            entry["latex"] = stmt.statement.latex

        # Sources.
        if stmt.sources:
            entry["sources"] = [_source_to_dict(s) for s in stmt.sources]

        # Confidence.
        if stmt.confidence:
            entry["confidence"] = stmt.confidence

        # Notes (brief author/extractor commentary).
        if stmt.notes:
            entry["notes"] = stmt.notes

        details[sid] = entry

    for pid, proof in ds.proofs.items():
        entry = {
            "id": pid,
            "kind": "proof",
            "type": "proof",
            "status": proof.status,
        }

        if proof.style:
            entry["style"] = proof.style

        entry["proves"] = proof.proves

        if proof.uses:
            entry["uses"] = list(proof.uses)

        if proof.sources:
            entry["sources"] = [_source_to_dict(s) for s in proof.sources]

        if proof.confidence:
            entry["confidence"] = proof.confidence

        if proof.notes:
            entry["notes"] = proof.notes

        details[pid] = entry

    return details


def to_node_link(g: nx.MultiDiGraph) -> dict:
    # Stable ordering for deterministic diffs.
    nodes = sorted(
        ({"id": n, **g.nodes[n]} for n in g.nodes),
        key=lambda d: d["id"],
    )
    links = sorted(
        (
            {"source": u, "target": v, **data}
            for u, v, data in g.edges(data=True)
        ),
        key=lambda d: (d["source"], d["target"], d.get("relation", "")),
    )
    return {"directed": True, "multigraph": True, "nodes": nodes, "links": links}


def main() -> int:
    errors = validate()
    if errors:
        print("Refusing to build graph: validation failed.", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    GRAPH_DIR.mkdir(parents=True, exist_ok=True)
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    ds = load_dataset()
    g = build_graph(ds)

    # --- graph.json (unchanged contract) ---
    json_path = GRAPH_DIR / "graph.json"
    json_path.write_text(
        json.dumps(to_node_link(g), indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    # --- node-details.json (rich per-node metadata for details panel) ---
    details = build_node_details(ds)
    details_path = GRAPH_DIR / "node-details.json"
    details_path.write_text(
        json.dumps(details, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    # --- GraphML export ---
    graphml_path = EXPORT_DIR / "graph.graphml"
    nx.write_graphml(g, graphml_path)

    print(f"wrote {json_path.relative_to(REPO_ROOT)} ({g.number_of_nodes()} nodes, {g.number_of_edges()} edges)")
    print(f"wrote {details_path.relative_to(REPO_ROOT)} ({len(details)} entries)")
    print(f"wrote {graphml_path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
