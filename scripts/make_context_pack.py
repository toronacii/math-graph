"""Generate targeted context packs for extraction and reconciliation agents.

A context pack is a compact markdown document containing the minimal,
high-value context needed to extract a specific chapter from a specific source.

Usage::

    python -m scripts.make_context_pack --source rudin --chapter 6
    python -m scripts.make_context_pack --source stewart --chapter 5

Output::

    generated/context-packs/<source>-chapter-<NN>.md
"""

from __future__ import annotations

import argparse
import sqlite3
import textwrap
from collections import Counter
from pathlib import Path

from scripts.build_db import DB_PATH, get_connection
from scripts.loader import REPO_ROOT

OUT_DIR = REPO_ROOT / "generated" / "context-packs"

# Source work names as stored in the sources table
SOURCE_WORKS = {
    "rudin": "Principles of Mathematical Analysis",
    "stewart": "Cálculo de una variable — Trascendentes tempranas",
}

SOURCE_AUTHORS = {
    "rudin": "Walter Rudin",
    "stewart": "James Stewart",
}


def _get_con() -> sqlite3.Connection:
    """Get a readonly connection to the graph database."""
    if not DB_PATH.exists():
        raise SystemExit(
            f"Database not found at {DB_PATH}.\n"
            "Run `python -m scripts.build_db` first."
        )
    return get_connection(readonly=True)


# ---- Section generators ----------------------------------------------------


def _section_extraction_target(source: str, chapter: str) -> str:
    """Section 1: Extraction Target."""
    work = SOURCE_WORKS.get(source, source)
    author = SOURCE_AUTHORS.get(source, "Unknown")
    lines = [
        "## 1. Extraction Target\n",
        f"- **Source**: {author} — *{work}*",
        f"- **Chapter**: {chapter}",
        f"- **Source key**: `{source}`",
        "",
    ]
    return "\n".join(lines)


def _section_previous_frontier(con: sqlite3.Connection, source: str, chapter: str) -> str:
    """Section 2: Previous-Chapter Frontier.

    Find the most reused/central nodes from the source's previous chapters.
    """
    work = SOURCE_WORKS.get(source, source)
    prev_chapter = str(int(chapter) - 1) if chapter.isdigit() and int(chapter) > 1 else None

    lines = ["## 2. Previous-Chapter Frontier\n"]

    if not prev_chapter:
        lines.append("_First chapter — no previous frontier._\n")
        return "\n".join(lines)

    # Find statements from this source in previous chapters
    cur = con.cursor()
    # Get all statements from this source's previous chapters (all chapters < target)
    prev_stmts = cur.execute(
        """
        SELECT DISTINCT s.entity_id
        FROM sources s
        WHERE s.work = ? AND CAST(s.chapter AS INTEGER) < CAST(? AS INTEGER)
          AND s.entity_kind = 'statement'
        """,
        (work, chapter),
    ).fetchall()
    prev_ids = {r[0] for r in prev_stmts}

    if not prev_ids:
        lines.append("_No previous chapter nodes found for this source._\n")
        return "\n".join(lines)

    # Count how often each previous-chapter statement is used in proofs
    usage_counts: Counter[str] = Counter()
    for (stmt_id,) in prev_stmts:
        count = cur.execute(
            "SELECT COUNT(*) FROM proof_uses WHERE statement_id = ?",
            (stmt_id,),
        ).fetchone()[0]
        usage_counts[stmt_id] = count

    # Top 15 by usage
    top_nodes = usage_counts.most_common(15)

    lines.append("Nodes from previous chapters most reused across the graph:\n")
    lines.append("| Node | Type | Uses | Title |")
    lines.append("|------|------|------|-------|")
    for node_id, count in top_nodes:
        row = cur.execute(
            "SELECT type, title_en FROM statements WHERE id = ?",
            (node_id,),
        ).fetchone()
        if row:
            ntype, title = row
            lines.append(f"| `{node_id}` | {ntype} | {count} | {title or ''} |")

    lines.append("")
    return "\n".join(lines)


def _section_related_nodes(con: sqlite3.Connection, source: str, chapter: str) -> str:
    """Section 3: Related Existing Nodes.

    Find nodes from OTHER sources that share the same chapter's topic domain.
    Also find nodes this source's proofs already depend on.
    """
    work = SOURCE_WORKS.get(source, source)
    cur = con.cursor()

    lines = ["## 3. Related Existing Nodes\n"]

    # Find what this source's PREVIOUS chapter's proofs used (dependency hubs)
    # These are the nodes the next chapter is most likely to build upon
    prev_chapter = str(int(chapter) - 1) if chapter.isdigit() and int(chapter) > 1 else None

    if prev_chapter:
        # Proofs from the immediately previous chapter
        prev_proofs = cur.execute(
            """
            SELECT DISTINCT s.entity_id
            FROM sources s
            WHERE s.work = ? AND s.chapter = ? AND s.entity_kind = 'proof'
            """,
            (work, prev_chapter),
        ).fetchall()

        # What did those proofs use?
        dep_counts: Counter[str] = Counter()
        for (pid,) in prev_proofs:
            deps = cur.execute(
                "SELECT statement_id FROM proof_uses WHERE proof_id = ?",
                (pid,),
            ).fetchall()
            for (dep_id,) in deps:
                dep_counts[dep_id] += 1

        if dep_counts:
            lines.append(f"### Dependencies used by Chapter {prev_chapter} proofs\n")
            lines.append("| Node | Count | Type |")
            lines.append("|------|-------|------|")
            for dep_id, cnt in dep_counts.most_common(10):
                row = cur.execute(
                    "SELECT type FROM statements WHERE id = ?", (dep_id,)
                ).fetchone()
                dtype = row[0] if row else "?"
                lines.append(f"| `{dep_id}` | {cnt} | {dtype} |")
            lines.append("")

    # Also show nodes from the same chapter in other sources (potential overlap)
    other_works = [w for w in SOURCE_WORKS.values() if w != work]
    for ow in other_works:
        same_ch = cur.execute(
            """
            SELECT DISTINCT s.entity_id
            FROM sources s
            JOIN statements st ON s.entity_id = st.id
            WHERE s.work = ? AND s.chapter = ? AND s.entity_kind = 'statement'
            ORDER BY st.type, s.entity_id
            """,
            (ow, chapter),
        ).fetchall()
        if same_ch:
            lines.append(f"### Same chapter number in other sources ({ow[:20]}...)\n")
            for (sid,) in same_ch[:15]:
                row = cur.execute(
                    "SELECT type, title_en FROM statements WHERE id = ?", (sid,)
                ).fetchone()
                if row:
                    lines.append(f"- `{sid}` ({row[0]}): {row[1] or ''}")
            if len(same_ch) > 15:
                lines.append(f"- ... and {len(same_ch) - 15} more")
            lines.append("")

    return "\n".join(lines)


def _section_collision_candidates(con: sqlite3.Connection, source: str, chapter: str) -> str:
    """Section 4: Multi-Source Collision Candidates.

    Find nodes that already have multiple sources, and nodes from OTHER sources
    in nearby chapters that might overlap with the target.
    """
    work = SOURCE_WORKS.get(source, source)
    cur = con.cursor()

    lines = ["## 4. Multi-Source Collision Candidates\n"]

    # Nodes already merged from multiple sources
    multi_source = cur.execute(
        """
        SELECT entity_id, COUNT(DISTINCT work) as src_count
        FROM sources
        WHERE entity_kind = 'statement'
        GROUP BY entity_id
        HAVING src_count > 1
        ORDER BY entity_id
        """
    ).fetchall()

    if multi_source:
        lines.append(f"### Already-merged nodes ({len(multi_source)} total)\n")
        lines.append("| Node | Type | Sources |")
        lines.append("|------|------|---------|")
        for sid, cnt in multi_source:
            row = cur.execute(
                "SELECT type, title_en FROM statements WHERE id = ?", (sid,)
            ).fetchone()
            works = cur.execute(
                "SELECT DISTINCT work FROM sources WHERE entity_id = ?", (sid,)
            ).fetchall()
            work_short = ", ".join(w[0][:20] for w in works)
            if row:
                lines.append(f"| `{sid}` | {row[0]} | {work_short} |")
        lines.append("")

    # Nodes from other sources in same/nearby chapters that DON'T yet have this source
    lines.append("### Potential overlaps (other-source nodes not yet merged)\n")
    lines.append(
        "Nodes from other sources in nearby chapters that may overlap "
        "with the target extraction:\n"
    )
    ch_int = int(chapter) if chapter.isdigit() else 0
    nearby_range = [str(c) for c in range(max(1, ch_int - 1), ch_int + 2)]

    candidates = cur.execute(
        f"""
        SELECT DISTINCT s.entity_id, st.type, st.title_en
        FROM sources s
        JOIN statements st ON s.entity_id = st.id
        WHERE s.work != ?
          AND s.chapter IN ({','.join('?' * len(nearby_range))})
          AND s.entity_kind = 'statement'
          AND s.entity_id NOT IN (
            SELECT entity_id FROM sources WHERE work = ?
          )
        ORDER BY st.type, s.entity_id
        """,
        (work, *nearby_range, work),
    ).fetchall()

    if candidates:
        for sid, stype, title in candidates[:20]:
            lines.append(f"- `{sid}` ({stype}): {title or ''}")
        if len(candidates) > 20:
            lines.append(f"- ... and {len(candidates) - 20} more")
    else:
        lines.append("_No obvious collision candidates found._")
    lines.append("")

    return "\n".join(lines)


def _section_naming_conventions(con: sqlite3.Connection) -> str:
    """Section 5: Existing Naming Conventions.

    Infer patterns from existing IDs.
    """
    cur = con.cursor()
    lines = ["## 5. Naming Conventions\n"]

    # Count ID prefixes
    type_counts = cur.execute(
        "SELECT type, COUNT(*) FROM statements GROUP BY type ORDER BY COUNT(*) DESC"
    ).fetchall()

    lines.append("### ID format: `<type>.<normalized-name>`\n")
    lines.append("| Type | Count | Example IDs |")
    lines.append("|------|-------|-------------|")
    for stype, cnt in type_counts:
        examples = cur.execute(
            "SELECT id FROM statements WHERE type = ? ORDER BY id LIMIT 3",
            (stype,),
        ).fetchall()
        ex_str = ", ".join(f"`{r[0]}`" for r in examples)
        lines.append(f"| {stype} | {cnt} | {ex_str} |")

    lines.append("")
    lines.append("### Proof ID format: `proof.<statement-name>.<source>`\n")
    lines.append("Examples:")

    proof_examples = cur.execute(
        "SELECT id FROM proofs ORDER BY id LIMIT 5"
    ).fetchall()
    for (pid,) in proof_examples:
        lines.append(f"- `{pid}`")
    lines.append("")

    lines.append("### Rules")
    lines.append("- IDs: lowercase ASCII, dots and hyphens only")
    lines.append("- No spaces, underscores, or special characters")
    lines.append("- Use mathematical name, not author's label")
    lines.append("- Prefer standard names over source-specific names")
    lines.append("")

    return "\n".join(lines)


def _section_weak_dependencies(con: sqlite3.Connection, source: str, chapter: str) -> str:
    """Section 6: Nearby Weak Dependencies."""
    cur = con.cursor()
    lines = ["## 6. Nearby Weak Dependencies\n"]

    # Find low/medium confidence proofs
    weak_proofs = cur.execute(
        """
        SELECT p.id, p.proves, p.confidence, p.notes
        FROM proofs p
        WHERE p.confidence IN ('low', 'medium')
        ORDER BY p.confidence, p.id
        """
    ).fetchall()

    if weak_proofs:
        lines.append(f"### Proofs with non-high confidence ({len(weak_proofs)} total)\n")
        lines.append("| Proof | Proves | Confidence |")
        lines.append("|-------|--------|------------|")
        for pid, proves, conf, _notes in weak_proofs[:15]:
            lines.append(f"| `{pid}` | `{proves}` | {conf} |")
        if len(weak_proofs) > 15:
            lines.append(f"\n... and {len(weak_proofs) - 15} more.")
    else:
        lines.append("_No weak-confidence proofs in the current graph._")

    lines.append("")

    # Statements with sources but no proofs (potential semantic debt)
    unproved = cur.execute(
        """
        SELECT s.id, s.type, s.title_en
        FROM statements s
        WHERE s.type NOT IN ('definition', 'axiom', 'conjecture')
          AND s.id NOT IN (SELECT statement_id FROM statement_proved_by)
        ORDER BY s.type, s.id
        """
    ).fetchall()

    if unproved:
        lines.append(f"### Statements without proofs ({len(unproved)} total)\n")
        for sid, stype, title in unproved[:10]:
            lines.append(f"- `{sid}` ({stype}): {title or ''}")
        if len(unproved) > 10:
            lines.append(f"- ... and {len(unproved) - 10} more")
    lines.append("")

    return "\n".join(lines)


def _section_ontology_warnings() -> str:
    """Section 7: Known Ontology Warnings."""
    lines = ["## 7. Known Ontology Warnings\n"]
    lines.append(textwrap.dedent("""\
        Active warnings from project audits:

        1. **Do not merge stronger and weaker formulations.**
           If one source's theorem is strictly more general (e.g., metric space
           vs real line), create SEPARATE nodes. Only merge if logically equivalent
           in full generality.

        2. **Do not treat `definition.supremum` as an existence theorem.**
           The definition of supremum is not a guarantee that one exists.
           Proofs that use existence of supremum for bounded sets of reals
           should depend on `definition.least-upper-bound-property` or an
           equivalent completeness axiom.

        3. **Bundled definitions inflate hub centrality.**
           Nodes like `definition.neighborhood-limit-point-open-closed` bundle
           multiple concepts. When a proof uses only "open set", the edge still
           goes to the bundled node. Be aware of this when assessing centrality.

        4. **Confidence means extraction confidence, not dependency completeness.**
           `confidence: high` means the extraction is reliable, NOT that the
           `uses` list is semantically complete.

        5. **Stewart uses strict inequalities; Rudin uses non-strict.**
           For increasing/decreasing tests: Stewart says f'>0 implies increasing;
           Rudin says f'>=0 implies monotonically increasing. These are NOT
           equivalent — Rudin's subsumes Stewart's.
    """))
    return "\n".join(lines)


def _section_local_graph(con: sqlite3.Connection, source: str, chapter: str) -> str:
    """Section 8: Local Graph Snapshot."""
    cur = con.cursor()
    work = SOURCE_WORKS.get(source, source)
    lines = ["## 8. Local Graph Snapshot\n"]

    # Global stats
    n_stmts = cur.execute("SELECT COUNT(*) FROM statements").fetchone()[0]
    n_proofs = cur.execute("SELECT COUNT(*) FROM proofs").fetchone()[0]
    n_edges = cur.execute("SELECT COUNT(*) FROM proof_uses").fetchone()[0]
    n_proved = cur.execute("SELECT COUNT(*) FROM statement_proved_by").fetchone()[0]

    lines.append("### Global graph state\n")
    lines.append(f"- Total statements: {n_stmts}")
    lines.append(f"- Total proofs: {n_proofs}")
    lines.append(f"- Total nodes: {n_stmts + n_proofs}")
    lines.append(f"- Uses edges: {n_edges}")
    lines.append(f"- Proved-by edges: {n_proved}")
    lines.append(f"- Total edges: {n_edges + n_proved}")
    lines.append("")

    # Source-specific stats
    source_stmts = cur.execute(
        "SELECT COUNT(DISTINCT entity_id) FROM sources WHERE work = ? AND entity_kind = 'statement'",
        (work,),
    ).fetchone()[0]
    source_proofs = cur.execute(
        "SELECT COUNT(DISTINCT entity_id) FROM sources WHERE work = ? AND entity_kind = 'proof'",
        (work,),
    ).fetchone()[0]
    chapters_done = cur.execute(
        "SELECT DISTINCT chapter FROM sources WHERE work = ? AND entity_kind = 'statement' ORDER BY CAST(chapter AS INTEGER)",
        (work,),
    ).fetchall()
    ch_list = [r[0] for r in chapters_done if r[0]]

    lines.append(f"### Source: {source}\n")
    lines.append(f"- Statements contributed: {source_stmts}")
    lines.append(f"- Proofs contributed: {source_proofs}")
    lines.append(f"- Chapters extracted: {', '.join(ch_list)}")
    lines.append("")

    # Top-degree nodes overall
    lines.append("### Highest-degree statement nodes (by proof_uses fan-in)\n")
    top_degree = cur.execute(
        """
        SELECT statement_id, COUNT(*) as cnt
        FROM proof_uses
        GROUP BY statement_id
        ORDER BY cnt DESC
        LIMIT 10
        """
    ).fetchall()
    lines.append("| Node | Uses-count | Type |")
    lines.append("|------|-----------|------|")
    for sid, cnt in top_degree:
        row = cur.execute("SELECT type FROM statements WHERE id = ?", (sid,)).fetchone()
        lines.append(f"| `{sid}` | {cnt} | {row[0] if row else '?'} |")
    lines.append("")

    return "\n".join(lines)


# ---- Main generator ---------------------------------------------------------


def generate_context_pack(source: str, chapter: str) -> Path:
    """Generate a context pack for the given source and chapter."""
    con = _get_con()

    sections = [
        f"# Context Pack: {source} Chapter {chapter}\n",
        f"> Auto-generated. Do not edit manually.\n",
        _section_extraction_target(source, chapter),
        _section_previous_frontier(con, source, chapter),
        _section_related_nodes(con, source, chapter),
        _section_collision_candidates(con, source, chapter),
        _section_naming_conventions(con),
        _section_weak_dependencies(con, source, chapter),
        _section_ontology_warnings(),
        _section_local_graph(con, source, chapter),
    ]

    con.close()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ch_padded = chapter.zfill(2)
    out_path = OUT_DIR / f"{source}-chapter-{ch_padded}.md"
    out_path.write_text("\n".join(sections), encoding="utf-8")
    return out_path


# ---- CLI --------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate a context pack for MKG extraction."
    )
    parser.add_argument(
        "--source",
        required=True,
        help="Source key (e.g., 'rudin', 'stewart')",
    )
    parser.add_argument(
        "--chapter",
        required=True,
        help="Chapter number to generate context for",
    )
    args = parser.parse_args()

    source = args.source.lower()
    chapter = args.chapter

    out_path = generate_context_pack(source, chapter)
    print(f"wrote {out_path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
