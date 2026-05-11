"""Generate targeted context packs for extraction and reconciliation agents.

A context pack is a compact markdown document containing the minimal,
high-value context needed to extract a specific chapter from a specific source.

Usage::

    python -m scripts.make_context_pack --source rudin --chapter 6
    python -m scripts.make_context_pack --source rudin --chapter 6 --mode audit

Output::

    generated/context-packs/<source>-chapter-<NN>.md
    generated/context-packs/<source>-chapter-<NN>.metrics.yml
"""

from __future__ import annotations

import argparse
import re
import sqlite3
import textwrap
from collections import Counter
from pathlib import Path

import yaml

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

# Topic keywords per source chapter (lightweight topic heuristic)
# Used for topic-based retrieval instead of chapter-number matching
SOURCE_CHAPTER_TOPICS: dict[str, dict[str, list[str]]] = {
    "rudin": {
        "1": ["real number", "field", "ordered field", "supremum", "infimum",
              "completeness", "archimedean", "complex number"],
        "2": ["metric space", "topology", "open", "closed", "compact",
              "connected", "countable", "neighborhood", "limit point"],
        "3": ["sequence", "series", "convergence", "cauchy", "subsequence",
              "root test", "ratio test", "absolute convergence", "power series"],
        "4": ["continuity", "limit", "uniform continuity", "connectedness",
              "intermediate value", "extreme value", "compact"],
        "5": ["differentiation", "derivative", "mean value theorem",
              "l'hopital", "taylor", "chain rule"],
        "6": ["integral", "riemann", "stieltjes", "partition", "integrability",
              "fundamental theorem", "integration by parts", "rectifiable", "arc length"],
        "7": ["sequence of functions", "uniform convergence", "equicontinuous",
              "stone-weierstrass", "pointwise"],
        "8": ["power series", "exponential", "logarithm", "trigonometric",
              "fourier", "gamma function"],
        "9": ["several variables", "linear transformation", "contraction",
              "inverse function", "implicit function", "jacobian"],
        "10": ["differential form", "surface", "stokes", "partition of unity",
               "simplex", "chain"],
        "11": ["lebesgue", "measure", "measurable", "dominated convergence",
               "L2", "fourier"],
    },
    "stewart": {
        "1": ["function", "model", "domain", "range", "composition",
              "inverse", "exponential", "logarithm"],
        "2": ["limit", "derivative", "tangent", "rate of change",
              "continuity", "squeeze theorem"],
        "3": ["differentiation", "product rule", "quotient rule",
              "chain rule", "implicit", "related rates"],
        "4": ["maximum", "minimum", "mean value theorem", "optimization",
              "curve sketching", "l'hopital", "antiderivative"],
        "5": ["integral", "area", "definite integral", "fundamental theorem",
              "substitution", "sigma notation"],
        "6": ["area between curves", "volume", "shell", "disk", "washer",
              "work", "average value"],
        "7": ["integration technique", "by parts", "trigonometric",
              "partial fraction", "improper integral"],
        "8": ["sequence", "series", "convergence", "power series",
              "taylor", "maclaurin", "radius"],
    },
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


def _section_extraction_target(source: str, chapter: str, mode: str) -> str:
    """Section 1: Extraction Target."""
    work = SOURCE_WORKS.get(source, source)
    author = SOURCE_AUTHORS.get(source, "Unknown")
    lines = [
        "## 1. Extraction Target\n",
        f"- **Source**: {author} — *{work}*",
        f"- **Chapter**: {chapter}",
        f"- **Source key**: `{source}`",
        f"- **Mode**: {mode}",
        "",
    ]
    return "\n".join(lines)


def _section_previous_frontier(con: sqlite3.Connection, source: str, chapter: str) -> str:
    """Section 2: Previous-Chapter Frontier."""
    work = SOURCE_WORKS.get(source, source)
    prev_chapter = str(int(chapter) - 1) if chapter.isdigit() and int(chapter) > 1 else None

    lines = ["## 2. Previous-Chapter Frontier\n"]

    if not prev_chapter:
        lines.append("_First chapter — no previous frontier._\n")
        return "\n".join(lines)

    cur = con.cursor()
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

    usage_counts: Counter[str] = Counter()
    for (stmt_id,) in prev_stmts:
        count = cur.execute(
            "SELECT COUNT(*) FROM proof_uses WHERE statement_id = ?",
            (stmt_id,),
        ).fetchone()[0]
        usage_counts[stmt_id] = count

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


def _section_source_locator_map(con: sqlite3.Connection, source: str, chapter: str) -> str:
    """Section 3: Source Locator Map.

    Maps textbook locators (e.g., 'Theorem 4.23') to MKG node IDs.
    Includes all chapters up to and including the target chapter.
    """
    work = SOURCE_WORKS.get(source, source)
    cur = con.cursor()
    lines = ["## 3. Source Locator Map\n"]
    lines.append(
        "Textbook locators → MKG node IDs for this source "
        "(all chapters up to target):\n"
    )

    # Get all statements from this source with section info, up to target chapter
    rows = cur.execute(
        """
        SELECT s.entity_id, s.section, s.chapter, st.type, st.title_en
        FROM sources s
        JOIN statements st ON s.entity_id = st.id
        WHERE s.work = ?
          AND CAST(s.chapter AS INTEGER) <= CAST(? AS INTEGER)
          AND s.entity_kind = 'statement'
          AND s.section IS NOT NULL AND s.section != ''
        ORDER BY CAST(s.chapter AS INTEGER), s.section
        """,
        (work, chapter),
    ).fetchall()

    if not rows:
        lines.append("_No locator data available._\n")
        return "\n".join(lines)

    # Group by chapter
    current_ch = None
    for entity_id, section, ch, etype, title in rows:
        if ch != current_ch:
            current_ch = ch
            lines.append(f"\n**Chapter {ch}:**\n")
            lines.append("| Locator | Node ID | Type | Title |")
            lines.append("|---------|---------|------|-------|")

        # Construct display locator like "Theorem 6.4" or "Definition 2.15"
        type_label = etype.capitalize() if etype else "?"
        # Use section as-is if it contains chapter prefix, otherwise prepend
        locator_display = f"{type_label} {section}"
        lines.append(
            f"| {locator_display} | `{entity_id}` | {etype} | {title or ''} |"
        )

    lines.append("")
    return "\n".join(lines)


def _get_topic_keywords(source: str, chapter: str) -> list[str]:
    """Get topic keywords for a source chapter."""
    source_topics = SOURCE_CHAPTER_TOPICS.get(source, {})
    return source_topics.get(chapter, [])


def _section_related_nodes(con: sqlite3.Connection, source: str, chapter: str) -> str:
    """Section 4: Related Existing Nodes.

    Uses topic-based retrieval instead of chapter-number matching.
    """
    work = SOURCE_WORKS.get(source, source)
    cur = con.cursor()
    lines = ["## 4. Related Existing Nodes\n"]

    # Part A: What this source's PREVIOUS chapter's proofs used
    prev_chapter = str(int(chapter) - 1) if chapter.isdigit() and int(chapter) > 1 else None

    if prev_chapter:
        prev_proofs = cur.execute(
            """
            SELECT DISTINCT s.entity_id
            FROM sources s
            WHERE s.work = ? AND s.chapter = ? AND s.entity_kind = 'proof'
            """,
            (work, prev_chapter),
        ).fetchall()

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
            for dep_id, cnt in dep_counts.most_common(15):
                row = cur.execute(
                    "SELECT type FROM statements WHERE id = ?", (dep_id,)
                ).fetchone()
                dtype = row[0] if row else "?"
                lines.append(f"| `{dep_id}` | {cnt} | {dtype} |")
            lines.append("")

    # Part B: Topic-based retrieval from OTHER sources
    # Find nodes from other sources whose titles/content match chapter topics
    target_keywords = _get_topic_keywords(source, chapter)

    if target_keywords:
        lines.append("### Topic-relevant nodes from other sources\n")
        lines.append(
            f"Topic keywords: {', '.join(target_keywords)}\n"
        )

        # Search for nodes from other sources matching these keywords
        other_works = [w for w in SOURCE_WORKS.values() if w != work]
        matches: list[tuple[str, str, str, float]] = []  # (id, type, title, score)

        for ow in other_works:
            candidates = cur.execute(
                """
                SELECT DISTINCT st.id, st.type, st.title_en, st.natural_en
                FROM statements st
                JOIN sources s ON s.entity_id = st.id
                WHERE s.work = ? AND s.entity_kind = 'statement'
                """,
                (ow,),
            ).fetchall()

            for sid, stype, title, natural in candidates:
                # Score by keyword match in title + natural language
                searchable = f"{title or ''} {natural or ''}".lower()
                score = sum(1 for kw in target_keywords if kw in searchable)
                if score > 0:
                    matches.append((sid, stype, title or "", score))

        # Sort by score descending, take top 20
        matches.sort(key=lambda x: -x[3])
        if matches:
            lines.append("| Node | Type | Title | Relevance |")
            lines.append("|------|------|-------|-----------|")
            for sid, stype, title, score in matches[:20]:
                lines.append(f"| `{sid}` | {stype} | {title} | {score} |")
        else:
            lines.append("_No topic-relevant nodes found in other sources._")
        lines.append("")

    return "\n".join(lines)


def _section_collision_candidates(
    con: sqlite3.Connection, source: str, chapter: str
) -> str:
    """Section 5: Multi-Source Collision Candidates.

    Lists ALL candidates without truncation.
    """
    work = SOURCE_WORKS.get(source, source)
    cur = con.cursor()

    lines = ["## 5. Multi-Source Collision Candidates\n"]

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

    # Potential overlaps: use topic-based retrieval + nearby chapters
    # NO TRUNCATION — list all candidates
    lines.append("### Potential overlaps (other-source nodes not yet merged)\n")
    lines.append(
        "Nodes from other sources that may overlap with the target extraction.\n"
        "Based on topic keywords and nearby chapters (no truncation):\n"
    )

    ch_int = int(chapter) if chapter.isdigit() else 0
    nearby_range = [str(c) for c in range(max(1, ch_int - 1), ch_int + 2)]

    # Get candidates from nearby chapters
    chapter_candidates = cur.execute(
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

    # Also get topic-matched candidates from ANY chapter
    target_keywords = _get_topic_keywords(source, chapter)
    topic_candidates: list[tuple[str, str, str]] = []
    if target_keywords:
        all_other = cur.execute(
            """
            SELECT DISTINCT st.id, st.type, st.title_en
            FROM statements st
            JOIN sources s ON s.entity_id = st.id
            WHERE s.work != ?
              AND s.entity_kind = 'statement'
              AND s.entity_id NOT IN (
                SELECT entity_id FROM sources WHERE work = ?
              )
            """,
            (work, work),
        ).fetchall()
        for sid, stype, title in all_other:
            searchable = (title or "").lower()
            if any(kw in searchable for kw in target_keywords):
                if (sid, stype, title) not in chapter_candidates:
                    topic_candidates.append((sid, stype, title))

    # Merge and deduplicate
    all_candidates: dict[str, tuple[str, str, str]] = {}
    for sid, stype, title in chapter_candidates:
        all_candidates[sid] = (sid, stype, title or "")
    for sid, stype, title in topic_candidates:
        all_candidates[sid] = (sid, stype, title or "")

    if all_candidates:
        # Group by type for readability
        by_type: dict[str, list[tuple[str, str]]] = {}
        for sid, stype, title in all_candidates.values():
            by_type.setdefault(stype, []).append((sid, title))

        for stype in sorted(by_type.keys()):
            items = sorted(by_type[stype])
            lines.append(f"\n**{stype}** ({len(items)}):")
            for sid, title in items:
                lines.append(f"- `{sid}`: {title}")
    else:
        lines.append("_No obvious collision candidates found._")
    lines.append("")

    return "\n".join(lines)


def _section_naming_conventions(con: sqlite3.Connection) -> str:
    """Section 6: Existing Naming Conventions."""
    cur = con.cursor()
    lines = ["## 6. Naming Conventions\n"]

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


def _section_canonical_templates() -> str:
    """Section 7: Canonical YAML Templates."""
    lines = ["## 7. Canonical YAML Templates\n"]
    lines.append("### Minimal statement\n")
    lines.append("```yaml")
    lines.append(textwrap.dedent("""\
        id: theorem.example-name
        type: theorem
        status: draft

        title:
          en: Example Theorem Name

        statement:
          natural:
            en: >
              If X then Y.
          latex: |
            X \\implies Y

        proved_by:
          - proof.example-name.rudin

        sources:
          - work: Principles of Mathematical Analysis
            author: Walter Rudin
            edition: "3"
            chapter: "6"
            section: "6.4"

        confidence: high""").rstrip())
    lines.append("```\n")

    lines.append("### Minimal proof\n")
    lines.append("```yaml")
    lines.append(textwrap.dedent("""\
        id: proof.example-name.rudin
        type: proof
        status: draft

        proves: theorem.example-name

        uses:
          - definition.some-definition
          - theorem.some-prerequisite

        style: direct
        sources:
          - work: Principles of Mathematical Analysis
            author: Walter Rudin
            edition: "3"
            chapter: "6"
            section: "6.4"

        confidence: high
        notes: >
          Brief proof sketch for dependency context.""").rstrip())
    lines.append("```\n")

    lines.append("### Multi-source statement (shared node)\n")
    lines.append("```yaml")
    lines.append(textwrap.dedent("""\
        id: theorem.shared-result
        type: theorem
        status: draft

        title:
          en: Shared Result Name
          es: Nombre del resultado

        statement:
          natural:
            en: >
              Statement in English.
            es: >
              Enunciado en espanol.
          latex: |
            f \\in \\mathscr{R}

        proved_by:
          - proof.shared-result.stewart
          - proof.shared-result.rudin

        sources:
          - work: Cálculo de una variable — Trascendentes tempranas
            author: James Stewart
            edition: "7"
            chapter: "5"
            section: "5.3"
          - work: Principles of Mathematical Analysis
            author: Walter Rudin
            edition: "3"
            chapter: "6"
            section: "6.21"

        confidence: high""").rstrip())
    lines.append("```\n")

    lines.append("### Field reference\n")
    lines.append("- `type`: axiom | definition | lemma | proposition | theorem | corollary | conjecture | proof")
    lines.append("- `status`: always `draft`")
    lines.append("- `style` (proofs only): direct | contradiction | induction | construction")
    lines.append("- `confidence`: high | medium | low")
    lines.append("- `proved_by`: list of proof IDs (empty `[]` for definitions/axioms)")
    lines.append("- `uses`: list of statement IDs the proof depends on")
    lines.append("")

    return "\n".join(lines)


def _section_weak_dependencies(con: sqlite3.Connection, source: str, chapter: str) -> str:
    """Section 8: Nearby Weak Dependencies."""
    cur = con.cursor()
    lines = ["## 8. Nearby Weak Dependencies\n"]

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
    """Section 9: Known Ontology Warnings."""
    lines = ["## 9. Known Ontology Warnings\n"]
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
    """Section 10: Local Graph Snapshot."""
    cur = con.cursor()
    work = SOURCE_WORKS.get(source, source)
    lines = ["## 10. Local Graph Snapshot\n"]

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


# ---- Metrics ----------------------------------------------------------------


def _compute_metrics(
    con: sqlite3.Connection,
    source: str,
    chapter: str,
    mode: str,
    pack_text: str,
) -> dict:
    """Compute quality metrics for the generated context pack."""
    work = SOURCE_WORKS.get(source, source)
    cur = con.cursor()

    # Estimate token length (~4 chars per token)
    estimated_tokens = len(pack_text) // 4

    # Count locator mappings
    locator_count = cur.execute(
        """
        SELECT COUNT(*)
        FROM sources s
        WHERE s.work = ?
          AND CAST(s.chapter AS INTEGER) <= CAST(? AS INTEGER)
          AND s.entity_kind = 'statement'
          AND s.section IS NOT NULL AND s.section != ''
        """,
        (work, chapter),
    ).fetchone()[0]

    # Count collision candidates
    ch_int = int(chapter) if chapter.isdigit() else 0
    nearby_range = [str(c) for c in range(max(1, ch_int - 1), ch_int + 2)]
    collision_count = cur.execute(
        f"""
        SELECT COUNT(DISTINCT s.entity_id)
        FROM sources s
        WHERE s.work != ?
          AND s.chapter IN ({','.join('?' * len(nearby_range))})
          AND s.entity_kind = 'statement'
          AND s.entity_id NOT IN (
            SELECT entity_id FROM sources WHERE work = ?
          )
        """,
        (work, *nearby_range, work),
    ).fetchone()[0]

    # Weak dependencies
    weak_count = cur.execute(
        "SELECT COUNT(*) FROM proofs WHERE confidence IN ('low', 'medium')"
    ).fetchone()[0]

    # Multi-source nodes
    multi_source_count = cur.execute(
        """
        SELECT COUNT(*) FROM (
            SELECT entity_id FROM sources
            WHERE entity_kind = 'statement'
            GROUP BY entity_id HAVING COUNT(DISTINCT work) > 1
        )
        """
    ).fetchone()[0]

    # Topic keywords used
    target_keywords = _get_topic_keywords(source, chapter)

    return {
        "source": source,
        "chapter": chapter,
        "mode": mode,
        "estimated_tokens": estimated_tokens,
        "estimated_chars": len(pack_text),
        "locator_mappings": locator_count,
        "collision_candidates_nearby": collision_count,
        "multi_source_nodes": multi_source_count,
        "weak_dependencies": weak_count,
        "ontology_warnings": 5,  # static count
        "topic_keywords": len(target_keywords),
        "retrieval_strategy": "topic-keywords + nearby-chapters + frontier",
    }


# ---- Main generator ---------------------------------------------------------


def generate_context_pack(source: str, chapter: str, mode: str = "extraction") -> Path:
    """Generate a context pack for the given source and chapter."""
    con = _get_con()

    sections = [
        f"# Context Pack: {source} Chapter {chapter}\n",
        f"> Auto-generated. Do not edit manually.\n",
        _section_extraction_target(source, chapter, mode),
        _section_previous_frontier(con, source, chapter),
        _section_source_locator_map(con, source, chapter),
        _section_related_nodes(con, source, chapter),
        _section_collision_candidates(con, source, chapter),
        _section_naming_conventions(con),
        _section_canonical_templates(),
        _section_weak_dependencies(con, source, chapter),
        _section_ontology_warnings(),
        _section_local_graph(con, source, chapter),
    ]

    pack_text = "\n".join(sections)

    # Write context pack
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ch_padded = chapter.zfill(2)
    out_path = OUT_DIR / f"{source}-chapter-{ch_padded}.md"
    out_path.write_text(pack_text, encoding="utf-8")

    # Compute and write metrics sidecar
    metrics = _compute_metrics(con, source, chapter, mode, pack_text)
    metrics_path = OUT_DIR / f"{source}-chapter-{ch_padded}.metrics.yml"
    metrics_path.write_text(
        yaml.dump(metrics, default_flow_style=False, sort_keys=False),
        encoding="utf-8",
    )

    con.close()
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
    parser.add_argument(
        "--mode",
        default="extraction",
        choices=["extraction", "audit"],
        help="Pack mode: 'extraction' (complete overlap lists) or 'audit' (broader context)",
    )
    args = parser.parse_args()

    source = args.source.lower()
    chapter = args.chapter

    out_path = generate_context_pack(source, chapter, args.mode)
    print(f"wrote {out_path.relative_to(REPO_ROOT)}")

    # Also print metrics path
    ch_padded = chapter.zfill(2)
    metrics_path = OUT_DIR / f"{source}-chapter-{ch_padded}.metrics.yml"
    print(f"wrote {metrics_path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
