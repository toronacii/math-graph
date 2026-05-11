"""Build the SQLite index from YAML sources and generate all graph outputs.

This is the single entry point for the MKG build pipeline:

1. Load all YAML files via Pydantic (schema validation).
2. Populate/replace the SQLite database.
3. Run integrity checks (ref integrity, symmetry, acyclicity) via SQL.
4. Generate graph.json, node-details.json, graph.graphml.

Usage::

    python -m scripts.build_db            # full build
    python -m scripts.build_db --db-only  # only rebuild the database, skip graph outputs
"""

from __future__ import annotations

import json
import sqlite3
import sys
from typing import Any

import networkx as nx

from scripts.loader import REPO_ROOT, Dataset, load_dataset

DB_PATH = REPO_ROOT / "generated" / "graph" / "math_graph.db"
GRAPH_DIR = REPO_ROOT / "generated" / "graph"
EXPORT_DIR = REPO_ROOT / "generated" / "exports"

# ---- schema ----------------------------------------------------------------

SCHEMA_SQL = """\
CREATE TABLE statements (
    id            TEXT PRIMARY KEY,
    type          TEXT NOT NULL,
    status        TEXT NOT NULL DEFAULT 'draft',
    title_en      TEXT,
    title_es      TEXT,
    natural_en    TEXT,
    natural_es    TEXT,
    latex         TEXT,
    confidence    TEXT,
    notes         TEXT
);

CREATE TABLE proofs (
    id            TEXT PRIMARY KEY,
    proves        TEXT NOT NULL REFERENCES statements(id),
    status        TEXT NOT NULL DEFAULT 'draft',
    style         TEXT,
    confidence    TEXT,
    notes         TEXT
);

CREATE TABLE proof_uses (
    proof_id      TEXT NOT NULL REFERENCES proofs(id),
    statement_id  TEXT NOT NULL REFERENCES statements(id),
    PRIMARY KEY (proof_id, statement_id)
);

CREATE TABLE statement_proved_by (
    statement_id  TEXT NOT NULL REFERENCES statements(id),
    proof_id      TEXT NOT NULL REFERENCES proofs(id),
    PRIMARY KEY (statement_id, proof_id)
);

CREATE TABLE sources (
    entity_id     TEXT NOT NULL,
    entity_kind   TEXT NOT NULL,
    work          TEXT NOT NULL,
    author        TEXT,
    edition       TEXT,
    chapter       TEXT,
    section       TEXT,
    page          TEXT,
    locator       TEXT,
    url           TEXT
);

CREATE INDEX idx_sources_entity ON sources(entity_id);
CREATE INDEX idx_sources_work ON sources(work);
CREATE INDEX idx_sources_chapter ON sources(chapter);
CREATE INDEX idx_proof_uses_stmt ON proof_uses(statement_id);
CREATE INDEX idx_proofs_proves ON proofs(proves);
CREATE INDEX idx_statements_type ON statements(type);
"""

# ---- populate --------------------------------------------------------------


def _populate(con: sqlite3.Connection, ds: Dataset) -> None:
    """Insert all loaded entities into the database."""
    cur = con.cursor()

    for sid, stmt in ds.statements.items():
        cur.execute(
            "INSERT INTO statements (id, type, status, title_en, title_es,"
            " natural_en, natural_es, latex, confidence, notes)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                sid,
                stmt.type,
                stmt.status,
                stmt.title.get("en"),
                stmt.title.get("es"),
                stmt.statement.natural.get("en") if stmt.statement.natural else None,
                stmt.statement.natural.get("es") if stmt.statement.natural else None,
                stmt.statement.latex,
                stmt.confidence,
                stmt.notes,
            ),
        )

        for ref in stmt.proved_by:
            cur.execute(
                "INSERT INTO statement_proved_by (statement_id, proof_id) VALUES (?, ?)",
                (sid, ref),
            )

        for src in stmt.sources:
            cur.execute(
                "INSERT INTO sources (entity_id, entity_kind, work, author, edition,"
                " chapter, section, page, locator, url)"
                " VALUES (?, 'statement', ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    sid,
                    src.work,
                    src.author,
                    src.edition,
                    src.chapter,
                    src.section,
                    src.page,
                    src.locator,
                    src.url,
                ),
            )

    for pid, proof in ds.proofs.items():
        cur.execute(
            "INSERT INTO proofs (id, proves, status, style, confidence, notes)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (pid, proof.proves, proof.status, proof.style, proof.confidence, proof.notes),
        )

        for ref in proof.uses:
            cur.execute(
                "INSERT INTO proof_uses (proof_id, statement_id) VALUES (?, ?)",
                (pid, ref),
            )

        for src in proof.sources:
            cur.execute(
                "INSERT INTO sources (entity_id, entity_kind, work, author, edition,"
                " chapter, section, page, locator, url)"
                " VALUES (?, 'proof', ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    pid,
                    src.work,
                    src.author,
                    src.edition,
                    src.chapter,
                    src.section,
                    src.page,
                    src.locator,
                    src.url,
                ),
            )

    con.commit()


# ---- integrity checks via SQL -----------------------------------------------


def _check_references_sql(con: sqlite3.Connection) -> list[str]:
    errors: list[str] = []
    cur = con.cursor()

    # proof.proves must reference an existing statement
    cur.execute(
        "SELECT p.id, p.proves FROM proofs p"
        " WHERE p.proves NOT IN (SELECT id FROM statements)"
    )
    for row in cur.fetchall():
        errors.append(f"{row[0]}: proves references unknown statement {row[1]!r}")

    # proof_uses must reference existing statements
    cur.execute(
        "SELECT pu.proof_id, pu.statement_id FROM proof_uses pu"
        " WHERE pu.statement_id NOT IN (SELECT id FROM statements)"
    )
    for row in cur.fetchall():
        errors.append(f"{row[0]}: uses references unknown statement {row[1]!r}")

    # statement_proved_by must reference existing proofs
    cur.execute(
        "SELECT spb.statement_id, spb.proof_id FROM statement_proved_by spb"
        " WHERE spb.proof_id NOT IN (SELECT id FROM proofs)"
    )
    for row in cur.fetchall():
        errors.append(f"{row[0]}: proved_by references unknown proof {row[1]!r}")

    return errors


def _check_symmetry_sql(con: sqlite3.Connection) -> list[str]:
    errors: list[str] = []
    cur = con.cursor()

    # Every proof.proves should be mirrored in statement_proved_by
    cur.execute(
        "SELECT p.id, p.proves FROM proofs p"
        " WHERE NOT EXISTS ("
        "   SELECT 1 FROM statement_proved_by spb"
        "   WHERE spb.statement_id = p.proves AND spb.proof_id = p.id"
        " )"
    )
    for row in cur.fetchall():
        errors.append(
            f"{row[0]}: proves {row[1]!r} but that statement does not list it in proved_by"
        )

    # Every statement_proved_by should have a matching proof.proves
    cur.execute(
        "SELECT spb.statement_id, spb.proof_id FROM statement_proved_by spb"
        " WHERE NOT EXISTS ("
        "   SELECT 1 FROM proofs p"
        "   WHERE p.id = spb.proof_id AND p.proves = spb.statement_id"
        " )"
    )
    for row in cur.fetchall():
        errors.append(
            f"{row[0]}: proved_by lists {row[1]!r} but that proof does not prove it"
        )

    return errors


def _check_acyclic_sql(con: sqlite3.Connection) -> list[str]:
    """Build a DiGraph from SQL and check for cycles."""
    g: nx.DiGraph = nx.DiGraph()
    cur = con.cursor()

    # All statement nodes
    for (sid,) in cur.execute("SELECT id FROM statements"):
        g.add_node(sid, kind="statement")

    # All proof nodes + edges
    for pid, proves in cur.execute("SELECT id, proves FROM proofs"):
        g.add_node(pid, kind="proof")
        g.add_edge(pid, proves)  # proof -> statement it establishes

    for proof_id, stmt_id in cur.execute("SELECT proof_id, statement_id FROM proof_uses"):
        g.add_edge(stmt_id, proof_id)  # statement used -> proof

    try:
        cycle = nx.find_cycle(g, orientation="original")
    except nx.NetworkXNoCycle:
        return []

    chain = " -> ".join(edge[0] for edge in cycle) + " -> " + cycle[-1][1]
    return [f"cyclic dependency detected: {chain}"]


def validate_db(con: sqlite3.Connection) -> list[str]:
    """Run all integrity checks against the populated database."""
    errors: list[str] = []
    errors.extend(_check_references_sql(con))
    errors.extend(_check_symmetry_sql(con))
    errors.extend(_check_acyclic_sql(con))
    return errors


# ---- graph outputs from SQL -------------------------------------------------


def _build_graph_from_db(con: sqlite3.Connection) -> nx.MultiDiGraph:
    g: nx.MultiDiGraph = nx.MultiDiGraph()
    cur = con.cursor()

    for row in cur.execute("SELECT id, type, status, title_en, title_es FROM statements"):
        g.add_node(
            row[0],
            kind="statement",
            type=row[1],
            status=row[2],
            title_en=row[3] or "",
            title_es=row[4] or "",
        )

    for row in cur.execute("SELECT id, proves, status, style FROM proofs"):
        g.add_node(
            row[0],
            kind="proof",
            type="proof",
            status=row[2],
            style=row[3] or "",
        )
        g.add_edge(row[0], row[1], relation="proves")

    for proof_id, stmt_id in cur.execute("SELECT proof_id, statement_id FROM proof_uses"):
        g.add_edge(stmt_id, proof_id, relation="uses")

    return g


def _build_node_details_from_db(con: sqlite3.Connection) -> dict[str, dict]:
    details: dict[str, dict] = {}
    cur = con.cursor()
    # Separate cursor for nested queries to avoid disrupting outer iteration.
    sub = con.cursor()

    # Statements — fetchall() so the cursor is free for sub-queries.
    stmt_rows = cur.execute(
        "SELECT id, type, status, title_en, title_es,"
        " natural_en, natural_es, latex, confidence, notes"
        " FROM statements"
    ).fetchall()

    for row in stmt_rows:
        sid = row[0]
        entry: dict[str, Any] = {
            "id": sid,
            "kind": "statement",
            "type": row[1],
            "status": row[2],
            "title": {},
        }
        if row[3]:
            entry["title"]["en"] = row[3]
        if row[4]:
            entry["title"]["es"] = row[4]

        natural: dict[str, str] = {}
        if row[5]:
            natural["en"] = row[5]
        if row[6]:
            natural["es"] = row[6]
        if natural:
            entry["natural"] = natural

        if row[7]:
            entry["latex"] = row[7]

        # Sources
        sources = _get_sources(sub, sid)
        if sources:
            entry["sources"] = sources

        if row[8]:
            entry["confidence"] = row[8]
        if row[9]:
            entry["notes"] = row[9]

        details[sid] = entry

    # Proofs
    proof_rows = cur.execute(
        "SELECT id, proves, status, style, confidence, notes FROM proofs"
    ).fetchall()

    for row in proof_rows:
        pid = row[0]
        entry = {
            "id": pid,
            "kind": "proof",
            "type": "proof",
            "status": row[2],
            "proves": row[1],
        }
        if row[3]:
            entry["style"] = row[3]

        # uses
        uses = [
            r[0]
            for r in sub.execute(
                "SELECT statement_id FROM proof_uses WHERE proof_id = ? ORDER BY statement_id",
                (pid,),
            ).fetchall()
        ]
        if uses:
            entry["uses"] = uses

        sources = _get_sources(sub, pid)
        if sources:
            entry["sources"] = sources

        if row[4]:
            entry["confidence"] = row[4]
        if row[5]:
            entry["notes"] = row[5]

        details[pid] = entry

    return details


def _get_sources(cur: sqlite3.Cursor, entity_id: str) -> list[dict[str, str]]:
    rows = cur.execute(
        "SELECT work, author, edition, chapter, section, page, locator, url"
        " FROM sources WHERE entity_id = ?",
        (entity_id,),
    ).fetchall()
    result = []
    for row in rows:
        src: dict[str, str] = {}
        keys = ("work", "author", "edition", "chapter", "section", "page", "locator", "url")
        for key, val in zip(keys, row, strict=False):
            if val is not None:
                src[key] = val
        result.append(src)
    return result


def _to_node_link(g: nx.MultiDiGraph) -> dict:
    nodes = sorted(
        ({"id": n, **g.nodes[n]} for n in g.nodes),
        key=lambda d: d["id"],
    )
    links = sorted(
        ({"source": u, "target": v, **data} for u, v, data in g.edges(data=True)),
        key=lambda d: (d["source"], d["target"], d.get("relation", "")),
    )
    return {"directed": True, "multigraph": True, "nodes": nodes, "links": links}


def _write_outputs(con: sqlite3.Connection) -> tuple[int, int]:
    """Generate graph.json, node-details.json, graph.graphml. Return (nodes, edges)."""
    GRAPH_DIR.mkdir(parents=True, exist_ok=True)
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    g = _build_graph_from_db(con)

    # graph.json
    json_path = GRAPH_DIR / "graph.json"
    json_path.write_text(
        json.dumps(_to_node_link(g), indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    # node-details.json
    details = _build_node_details_from_db(con)
    details_path = GRAPH_DIR / "node-details.json"
    details_path.write_text(
        json.dumps(details, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    # GraphML
    graphml_path = EXPORT_DIR / "graph.graphml"
    nx.write_graphml(g, graphml_path)

    n_nodes = g.number_of_nodes()
    n_edges = g.number_of_edges()
    print(f"wrote {json_path.relative_to(REPO_ROOT)} ({n_nodes} nodes, {n_edges} edges)")
    print(f"wrote {details_path.relative_to(REPO_ROOT)} ({len(details)} entries)")
    print(f"wrote {graphml_path.relative_to(REPO_ROOT)}")
    return n_nodes, n_edges


# ---- public API -------------------------------------------------------------


def build_db(ds: Dataset | None = None) -> sqlite3.Connection:
    """Build (or rebuild) the SQLite database from YAML sources.

    Returns the open connection so callers can run queries.
    """
    if ds is None:
        ds = load_dataset()

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Always recreate from scratch — YAML is the source of truth.
    if DB_PATH.exists():
        DB_PATH.unlink()

    con = sqlite3.connect(str(DB_PATH))
    con.executescript(SCHEMA_SQL)
    _populate(con, ds)
    return con


def get_connection(readonly: bool = True) -> sqlite3.Connection:
    """Open an existing database for querying.

    Raises FileNotFoundError if the DB doesn't exist yet.
    """
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"{DB_PATH} not found. Run `python -m scripts.build_db` first."
        )
    uri = f"file:{DB_PATH}"
    if readonly:
        uri += "?mode=ro"
    return sqlite3.connect(uri, uri=True)


# ---- CLI --------------------------------------------------------------------


def main() -> int:
    db_only = "--db-only" in sys.argv

    # Phase 1: load YAML + schema validation
    print("loading YAML sources …")
    ds = load_dataset()
    if ds.errors:
        print(f"FAIL — {len(ds.errors)} schema error(s):", file=sys.stderr)
        for err in ds.errors:
            print(f"  - {err.path}: {err.message}", file=sys.stderr)
        return 1
    n_stmts = len(ds.statements)
    n_proofs = len(ds.proofs)
    print(f"  {n_stmts} statements, {n_proofs} proofs loaded")

    # Phase 2: build SQLite
    print("building SQLite database …")
    con = build_db(ds)
    print(f"  wrote {DB_PATH.relative_to(REPO_ROOT)}")

    # Phase 3: integrity checks
    print("running integrity checks …")
    errors = validate_db(con)
    if errors:
        print(f"FAIL — {len(errors)} integrity error(s):", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        con.close()
        return 1
    print("  all checks passed")

    # Phase 4: graph outputs
    if not db_only:
        print("generating graph outputs …")
        _write_outputs(con)

    con.close()
    print("done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
