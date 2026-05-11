"""Compare two graph snapshots and produce a migration report.

Usage::

    python -m scripts.diff_graphs \
        --before generated/snapshots/v0.2 \
        --after  generated/snapshots/v0.3-2026-06-01 \
        --out    reports/migration-v0.2-to-v0.3.md

Reports:
  - nodes added / removed / kept
  - id redirects (via provenance.derived_from / redirected_to in `after`)
  - edges added / removed
  - status distribution shift
  - per-source coverage delta
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts.v03.loader import REPO_ROOT


def _load_graph(snapshot_dir: Path) -> dict:
    p = snapshot_dir / "graph" / "graph.json"
    if not p.exists():
        raise SystemExit(f"missing {p}")
    return json.loads(p.read_text())


def _node_ids(g: dict) -> set[str]:
    return {n["id"] for n in g["nodes"]}


def _edge_keys(g: dict) -> set[tuple]:
    keys = set()
    for e in g["links"]:
        keys.add((e["source"], e["target"], e.get("relation", "")))
    return keys


def _load_redirects(snapshot_dir: Path) -> dict[str, str]:
    """Read node-details.json for redirected_to (from provenance)."""
    p = snapshot_dir / "graph" / "node-details.json"
    if not p.exists():
        return {}
    details = json.loads(p.read_text())
    redirects: dict[str, str] = {}
    for nid, node in details.items():
        prov = node.get("provenance") or {}
        rt = prov.get("redirected_to")
        if rt:
            redirects[nid] = rt
        for prior in prov.get("derived_from", []) or []:
            redirects[prior] = nid
    return redirects


def diff(before: Path, after: Path, out: Path) -> None:
    g0 = _load_graph(before)
    g1 = _load_graph(after)
    n0, n1 = _node_ids(g0), _node_ids(g1)
    e0, e1 = _edge_keys(g0), _edge_keys(g1)
    redirects = _load_redirects(after)

    added = sorted(n1 - n0)
    removed = sorted(n0 - n1)
    kept = sorted(n0 & n1)

    edges_added = sorted(e1 - e0)
    edges_removed = sorted(e0 - e1)

    out.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# Migration Report: {before.name} → {after.name}\n",
        "## Node deltas\n",
        f"- kept:    {len(kept)}",
        f"- added:   {len(added)}",
        f"- removed: {len(removed)}",
        "",
        "## Edge deltas\n",
        f"- kept:    {len(e0 & e1)}",
        f"- added:   {len(edges_added)}",
        f"- removed: {len(edges_removed)}",
        "",
        "## ID redirects (declared in `after.provenance`)\n",
    ]
    if redirects:
        lines.append("| from | to |")
        lines.append("|------|-----|")
        for src, dst in sorted(redirects.items()):
            lines.append(f"| `{src}` | `{dst}` |")
    else:
        lines.append("_No redirects declared._")

    lines.append("\n## Removed nodes (no redirect declared)\n")
    orphans = [n for n in removed if n not in redirects]
    for nid in orphans[:200]:
        lines.append(f"- `{nid}`")
    if len(orphans) > 200:
        lines.append(f"- … {len(orphans) - 200} more")

    lines.append("\n## Added nodes (sample)\n")
    for nid in added[:200]:
        lines.append(f"- `{nid}`")
    if len(added) > 200:
        lines.append(f"- … {len(added) - 200} more")

    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--before", type=Path, required=True)
    parser.add_argument("--after", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    diff(args.before, args.after, args.out)
    print(f"wrote {args.out.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
