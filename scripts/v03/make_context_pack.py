"""Generate v0.3 context packs for extraction and audit agents.

A v0.3 context pack is a compact markdown document containing the minimal,
high-value context needed to extract (or audit) a specific chapter of a
specific source against the v0.3 schema.

Differences from v0.2 (`scripts.make_context_pack`):

  * Locators include `theorem_label` from `Provenance` / `Source`, not just
    chapter+section.
  * Retrieval uses the `domains`, `ambient` and `ontology` blocks instead
    of hand-curated topic keyword tables.
  * "Weak dependencies" section reports the **6 quality axes**
    (extraction / dependency / semantic / translation / latex /
    source_alignment) independently, including unassessed (`null`) values.
  * Templates point to `schema/v03/templates/`.

Usage::

    uv run python -m scripts.v03.make_context_pack --source rudin --chapter 6
    uv run python -m scripts.v03.make_context_pack --source rudin --chapter 6 --mode audit

Output::

    generated/v0.3/context-packs/<source>-chapter-<NN>.md
    generated/v0.3/context-packs/<source>-chapter-<NN>.metrics.yml
"""

from __future__ import annotations

import argparse
import sqlite3
from collections import Counter
from pathlib import Path

import yaml

from schema.v03 import load_source_registry
from scripts.v03.build_db import DB_PATH
from scripts.v03.loader import REPO_ROOT

OUT_DIR = REPO_ROOT / "generated" / "v0.3" / "context-packs"


def _registry_field(key: str, field: str, default: str = "") -> str:
    entry = load_source_registry().get(key, {})
    return entry.get(field, default)


def _source_work(key: str) -> str:
    return _registry_field(key, "work", key)


def _source_author(key: str) -> str:
    return _registry_field(key, "author", "Unknown")

QUALITY_AXES = [
    ("extraction", "extraction_confidence"),
    ("dependency", "dependency_confidence"),
    ("semantic", "semantic_confidence"),
    ("translation", "translation_confidence"),
    ("latex_conf", "latex_confidence"),
    ("source_align", "source_alignment_confidence"),
]


def _get_con() -> sqlite3.Connection:
    if not DB_PATH.exists():
        raise SystemExit(
            f"v0.3 database not found at {DB_PATH}.\n"
            "Run `uv run python -m scripts.v03.build_db` first."
        )
    con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    return con


# ---- Section generators ----------------------------------------------------


def _section_header(source: str, chapter: str, mode: str) -> str:
    work = _source_work(source)
    author = _source_author(source)
    return "\n".join([
        "## 1. Extraction Target\n",
        "- **Schema**: v0.3",
        f"- **Source**: {author} — *{work}*",
        f"- **Chapter**: {chapter}",
        f"- **Source key**: `{source}`",
        f"- **Mode**: {mode}",
        "",
    ])


def _section_frontier(con: sqlite3.Connection, source: str, chapter: str) -> str:
    work = _source_work(source)
    cur = con.cursor()
    lines = ["## 2. Previous-Chapter Frontier\n"]
    if not chapter.isdigit() or int(chapter) <= 1:
        lines.append("_First chapter — no previous frontier._\n")
        return "\n".join(lines)

    prev = cur.execute(
        """
        SELECT DISTINCT s.entity_id
        FROM sources s
        WHERE s.work = ?
          AND CAST(s.chapter AS INTEGER) < CAST(? AS INTEGER)
          AND s.entity_kind = 'statement'
        """,
        (work, chapter),
    ).fetchall()
    if not prev:
        lines.append("_No previous-chapter nodes for this source._\n")
        return "\n".join(lines)

    counts: Counter[str] = Counter()
    for (sid,) in prev:
        n = cur.execute(
            "SELECT COUNT(*) FROM proof_uses WHERE statement_id = ?", (sid,)
        ).fetchone()[0]
        m = cur.execute(
            "SELECT COUNT(*) FROM statement_depends_on WHERE target_id = ?", (sid,)
        ).fetchone()[0]
        counts[sid] = n + m

    lines.append("Most-reused prior nodes (proof_uses + statement_depends_on):\n")
    lines.append("| Node | Type | Reuse | Title |")
    lines.append("|------|------|-------|-------|")
    for sid, c in counts.most_common(15):
        row = cur.execute(
            "SELECT type FROM statements WHERE id = ?", (sid,)
        ).fetchone()
        title_row = cur.execute(
            "SELECT text FROM statement_titles WHERE statement_id=? "
            "ORDER BY is_original DESC LIMIT 1",
            (sid,),
        ).fetchone()
        ntype = row[0] if row else "?"
        title = title_row[0] if title_row else ""
        lines.append(f"| `{sid}` | {ntype} | {c} | {title} |")
    lines.append("")
    return "\n".join(lines)


def _section_locators(con: sqlite3.Connection, source: str, chapter: str) -> str:
    work = _source_work(source)
    cur = con.cursor()
    lines = [
        "## 3. Source Locator Map\n",
        "Textbook locators (chapter / section / theorem_label) → MKG node IDs:\n",
    ]
    rows = cur.execute(
        """
        SELECT s.entity_id, s.chapter, s.section, s.theorem_label, s.page,
               st.type
        FROM sources s
        JOIN statements st ON s.entity_id = st.id
        WHERE s.work = ?
          AND CAST(s.chapter AS INTEGER) <= CAST(? AS INTEGER)
          AND s.entity_kind = 'statement'
        ORDER BY CAST(s.chapter AS INTEGER), s.section, s.theorem_label
        """,
        (work, chapter),
    ).fetchall()
    if not rows:
        lines.append("_No locator data available._\n")
        return "\n".join(lines)

    current = None
    for sid, ch, section, label, page, etype in rows:
        if ch != current:
            current = ch
            lines.append(f"\n**Chapter {ch}:**\n")
            lines.append("| Locator | Section | Page | Node | Type |")
            lines.append("|---------|---------|------|------|------|")
        loc = label or (etype.capitalize() + " " + (section or ""))
        lines.append(
            f"| {loc} | {section or ''} | {page or ''} | `{sid}` | {etype} |"
        )
    lines.append("")
    return "\n".join(lines)


def _section_domain_neighborhood(
    con: sqlite3.Connection, source: str, chapter: str
) -> str:
    """Use domains/ambient/ontology to surface relevant prior nodes."""
    work = _source_work(source)
    cur = con.cursor()
    lines = ["## 4. Domain-Relevant Neighborhood\n"]

    # Domains/ambient/ontology of statements already extracted from this source
    # (any chapter ≤ target). Use them to fetch related nodes from OTHER works.
    domains = {r[0] for r in cur.execute(
        """
        SELECT DISTINCT d.name FROM statement_domains d
        JOIN sources s ON s.entity_id = d.statement_id
        WHERE s.work = ? AND CAST(s.chapter AS INTEGER) <= CAST(? AS INTEGER)
        """,
        (work, chapter),
    ).fetchall()}
    structures = {r[0] for r in cur.execute(
        """
        SELECT DISTINCT a.structure FROM statement_ambient a
        JOIN sources s ON s.entity_id = a.statement_id
        WHERE s.work = ? AND CAST(s.chapter AS INTEGER) <= CAST(? AS INTEGER)
        """,
        (work, chapter),
    ).fetchall()}

    if not (domains or structures):
        lines.append(
            "_No v0.3 domains / ambient structures recorded for this source yet._\n"
        )
        return "\n".join(lines)

    lines.append(f"Active domains: {sorted(domains) or '—'}")
    lines.append(f"Active ambient structures: {sorted(structures) or '—'}\n")

    # Surface other-work nodes sharing these domains or structures
    if domains:
        placeholders = ",".join("?" * len(domains))
        rows = cur.execute(
            f"""
            SELECT DISTINCT st.id, st.type
            FROM statement_domains d
            JOIN statements st ON d.statement_id = st.id
            JOIN sources s ON s.entity_id = st.id
            WHERE d.name IN ({placeholders}) AND s.work != ?
            ORDER BY st.type, st.id
            LIMIT 40
            """,
            (*sorted(domains), work),
        ).fetchall()
        if rows:
            lines.append("### Other-source nodes in matching domains\n")
            lines.append("| Node | Type |")
            lines.append("|------|------|")
            for sid, etype in rows:
                lines.append(f"| `{sid}` | {etype} |")
            lines.append("")

    return "\n".join(lines)


def _section_collisions(
    con: sqlite3.Connection, source: str, chapter: str
) -> str:
    work = _source_work(source)
    cur = con.cursor()
    lines = ["## 5. Multi-Source Collision Candidates\n"]

    multi = cur.execute(
        """
        SELECT entity_id, COUNT(DISTINCT work)
        FROM sources
        WHERE entity_kind = 'statement'
        GROUP BY entity_id HAVING COUNT(DISTINCT work) > 1
        ORDER BY entity_id
        """
    ).fetchall()
    if multi:
        lines.append(f"### Already-merged nodes ({len(multi)})\n")
        lines.append("| Node | Sources |")
        lines.append("|------|---------|")
        for sid, _ in multi:
            ws = cur.execute(
                "SELECT DISTINCT work FROM sources WHERE entity_id=?", (sid,)
            ).fetchall()
            lines.append(f"| `{sid}` | {', '.join(w[0] for w in ws)} |")
        lines.append("")

    # Other-source statements in nearby chapters not already cited by this work
    if chapter.isdigit():
        ch = int(chapter)
        nearby = [str(c) for c in range(max(1, ch - 1), ch + 2)]
        ph = ",".join("?" * len(nearby))
        rows = cur.execute(
            f"""
            SELECT DISTINCT s.entity_id, st.type
            FROM sources s
            JOIN statements st ON s.entity_id = st.id
            WHERE s.work != ? AND s.chapter IN ({ph}) AND s.entity_kind='statement'
              AND s.entity_id NOT IN (
                  SELECT entity_id FROM sources WHERE work = ?
              )
            ORDER BY st.type, s.entity_id
            """,
            (work, *nearby, work),
        ).fetchall()
        if rows:
            lines.append(
                f"### Other-source nodes in nearby chapters ({len(rows)})\n"
            )
            by_type: dict[str, list[str]] = {}
            for sid, etype in rows:
                by_type.setdefault(etype, []).append(sid)
            for etype in sorted(by_type):
                lines.append(f"\n**{etype}** ({len(by_type[etype])}):")
                for sid in sorted(by_type[etype]):
                    lines.append(f"- `{sid}`")
            lines.append("")
    return "\n".join(lines)


def _section_quality_axes(con: sqlite3.Connection) -> str:
    cur = con.cursor()
    lines = ["## 6. Quality-Axis Backlog (statements + proofs)\n"]
    lines.append(
        "Counts per axis. `low`/`medium` need attention; `null` = unassessed.\n"
    )
    lines.append("| Axis | low | medium | high | null |")
    lines.append("|------|----:|------:|-----:|-----:|")
    for col, _label in QUALITY_AXES:
        s_counts = cur.execute(
            f"SELECT {col}, COUNT(*) FROM statement_quality GROUP BY {col}"
        ).fetchall()
        p_counts = cur.execute(
            f"SELECT {col}, COUNT(*) FROM proof_quality GROUP BY {col}"
        ).fetchall()
        bucket = {"low": 0, "medium": 0, "high": 0, None: 0}
        for v, c in (*s_counts, *p_counts):
            if v in bucket:
                bucket[v] += c
            elif v is None:
                bucket[None] += c
        lines.append(
            f"| {col} | {bucket['low']} | {bucket['medium']} | "
            f"{bucket['high']} | {bucket[None]} |"
        )
    lines.append("")

    # Sample low/medium proofs for the agent to inspect
    rows = cur.execute(
        """
        SELECT proof_id, semantic, dependency
        FROM proof_quality
        WHERE semantic IN ('low','medium') OR dependency IN ('low','medium')
        ORDER BY proof_id
        LIMIT 20
        """
    ).fetchall()
    if rows:
        lines.append("### Sample weak proofs\n")
        lines.append("| Proof | semantic | dependency |")
        lines.append("|-------|----------|------------|")
        for pid, sem, dep in rows:
            lines.append(f"| `{pid}` | {sem or '—'} | {dep or '—'} |")
        lines.append("")
    return "\n".join(lines)


def _section_unproved(con: sqlite3.Connection) -> str:
    cur = con.cursor()
    rows = cur.execute(
        """
        SELECT s.id, s.type
        FROM statements s
        WHERE s.type NOT IN ('definition','axiom','conjecture')
          AND s.id NOT IN (SELECT statement_id FROM statement_proved_by)
        ORDER BY s.type, s.id
        """
    ).fetchall()
    if not rows:
        return ""
    lines = [f"## 7. Statements Without Proofs ({len(rows)})\n"]
    for sid, etype in rows[:30]:
        lines.append(f"- `{sid}` ({etype})")
    if len(rows) > 30:
        lines.append(f"- … and {len(rows) - 30} more")
    lines.append("")
    return "\n".join(lines)


def _section_naming(con: sqlite3.Connection) -> str:
    cur = con.cursor()
    lines = ["## 8. Naming Conventions\n"]
    type_counts = cur.execute(
        "SELECT type, COUNT(*) FROM statements GROUP BY type ORDER BY COUNT(*) DESC"
    ).fetchall()
    if not type_counts:
        lines.append("_No statements indexed yet._\n")
        return "\n".join(lines)
    lines.append("| Type | Count | Example |")
    lines.append("|------|------:|---------|")
    for t, c in type_counts:
        ex = cur.execute(
            "SELECT id FROM statements WHERE type=? ORDER BY id LIMIT 1", (t,)
        ).fetchone()
        lines.append(f"| {t} | {c} | `{ex[0] if ex else ''}` |")
    lines.append(
        "\n- IDs: lowercase ASCII, dots and hyphens only.\n"
        "- Statement id prefix MUST equal `type`.\n"
        "- Proof id format: `proof.<statement-name>.<source>`.\n"
    )
    return "\n".join(lines)


def _section_templates() -> str:
    template_dir = Path("schema/v03/templates")
    return (
        "## 9. Canonical YAML Templates\n\n"
        f"Use the canonical templates in `{template_dir}/`:\n"
        f"- `{template_dir}/statement.template.yml`\n"
        f"- `{template_dir}/proof.template.yml`\n\n"
        "All v0.3 entities MUST set `schema_version: 0.3.1` (loader\n"
        "still accepts `0.3.0`) and include a\n"
        "`language` block with `is_original` flags on every multilingual entry.\n"
    )


def _section_local_graph(con: sqlite3.Connection, source: str) -> str:
    work = _source_work(source)
    cur = con.cursor()
    n_s = cur.execute("SELECT COUNT(*) FROM statements").fetchone()[0]
    n_p = cur.execute("SELECT COUNT(*) FROM proofs").fetchone()[0]
    n_u = cur.execute("SELECT COUNT(*) FROM proof_uses").fetchone()[0]
    n_d = cur.execute("SELECT COUNT(*) FROM statement_depends_on").fetchone()[0]
    n_pb = cur.execute("SELECT COUNT(*) FROM statement_proved_by").fetchone()[0]
    src_s = cur.execute(
        "SELECT COUNT(DISTINCT entity_id) FROM sources WHERE work=? AND entity_kind='statement'",
        (work,),
    ).fetchone()[0]
    chapters = [
        r[0] for r in cur.execute(
            "SELECT DISTINCT chapter FROM sources WHERE work=? AND entity_kind='statement' "
            "ORDER BY CAST(chapter AS INTEGER)",
            (work,),
        ).fetchall() if r[0]
    ]
    return "\n".join([
        "## 10. Local Graph Snapshot\n",
        f"- Statements: {n_s} | Proofs: {n_p}",
        f"- proof_uses edges: {n_u}",
        f"- statement_depends_on edges: {n_d}",
        f"- proved_by edges: {n_pb}",
        f"- This source ({source}): {src_s} statements; chapters: "
        f"{', '.join(chapters) or '—'}",
        "",
    ])


# ---- main ------------------------------------------------------------------


def generate(source: str, chapter: str, mode: str) -> Path:
    con = _get_con()
    sections = [
        f"# v0.3 Context Pack: {source} chapter {chapter}\n",
        "> Auto-generated by `scripts.v03.make_context_pack`. Do not edit by hand.\n",
        _section_header(source, chapter, mode),
        _section_frontier(con, source, chapter),
        _section_locators(con, source, chapter),
        _section_domain_neighborhood(con, source, chapter),
        _section_collisions(con, source, chapter),
        _section_quality_axes(con),
        _section_unproved(con),
        _section_naming(con),
        _section_templates(),
        _section_local_graph(con, source),
    ]
    text = "\n".join(s for s in sections if s)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ch = chapter.zfill(2)
    out = OUT_DIR / f"{source}-chapter-{ch}.md"
    out.write_text(text, encoding="utf-8")

    metrics = {
        "schema_version": "0.3.1",
        "source": source,
        "chapter": chapter,
        "mode": mode,
        "estimated_chars": len(text),
        "estimated_tokens": len(text) // 4,
        "generator": "scripts.v03.make_context_pack",
    }
    (OUT_DIR / f"{source}-chapter-{ch}.metrics.yml").write_text(
        yaml.dump(metrics, sort_keys=False, default_flow_style=False),
        encoding="utf-8",
    )
    con.close()
    return out


def main() -> int:
    p = argparse.ArgumentParser(description="Generate a v0.3 MKG context pack.")
    p.add_argument("--source", required=True, help="Source key, e.g. rudin, stewart.")
    p.add_argument("--chapter", required=True, help="Target chapter number.")
    p.add_argument(
        "--mode",
        default="extraction",
        choices=["extraction", "audit"],
        help="Pack mode.",
    )
    args = p.parse_args()
    out = generate(args.source.lower(), args.chapter, args.mode)
    print(f"wrote {out.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
