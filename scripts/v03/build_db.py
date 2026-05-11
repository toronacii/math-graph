"""v0.3 SQLite builder + graph exports.

Schema is wider than v0.2: edges carry role/confidence/locality, sources
carry theorem_label, statements record domains/ambient/ontology/quality.

Outputs (under generated/v0.3/):
  - math_graph.db        SQLite index
  - graph.json           node-link JSON for visualization
  - node-details.json    per-node detail blob
  - graph.graphml        GraphML export
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path
from typing import Any

import networkx as nx

from scripts.v03.loader import REPO_ROOT, Dataset, load_dataset

OUT_DIR = REPO_ROOT / "generated" / "v0.3"
DB_PATH = OUT_DIR / "math_graph.db"
GRAPH_DIR = OUT_DIR
EXPORT_DIR = OUT_DIR

SCHEMA_SQL = """
CREATE TABLE statements (
    id              TEXT PRIMARY KEY,
    type            TEXT NOT NULL,
    status          TEXT NOT NULL,
    schema_version  TEXT NOT NULL,
    original_lang   TEXT NOT NULL,
    latex_body      TEXT,
    latex_status    TEXT NOT NULL,
    latex_review    TEXT NOT NULL,
    notes           TEXT
);

CREATE TABLE statement_titles (
    statement_id   TEXT NOT NULL REFERENCES statements(id),
    lang           TEXT NOT NULL,
    text           TEXT NOT NULL,
    is_original    INTEGER NOT NULL,
    origin         TEXT NOT NULL,
    review_status  TEXT NOT NULL,
    PRIMARY KEY (statement_id, lang)
);

CREATE TABLE statement_natural (
    statement_id   TEXT NOT NULL REFERENCES statements(id),
    lang           TEXT NOT NULL,
    text           TEXT NOT NULL,
    is_original    INTEGER NOT NULL,
    origin         TEXT NOT NULL,
    review_status  TEXT NOT NULL,
    PRIMARY KEY (statement_id, lang)
);

CREATE TABLE statement_quality (
    statement_id   TEXT PRIMARY KEY REFERENCES statements(id),
    extraction     TEXT,
    dependency     TEXT,
    semantic       TEXT,
    translation    TEXT,
    latex_conf     TEXT,
    source_align   TEXT
);

CREATE TABLE statement_provenance (
    statement_id   TEXT PRIMARY KEY REFERENCES statements(id),
    schema_version TEXT NOT NULL,
    rerun_id       TEXT,
    extracted_by   TEXT,
    extracted_at   TEXT,
    redirected_to  TEXT
);

CREATE TABLE statement_derived_from (
    statement_id   TEXT NOT NULL REFERENCES statements(id),
    prior_id       TEXT NOT NULL,
    PRIMARY KEY (statement_id, prior_id)
);

CREATE TABLE statement_domains (
    statement_id   TEXT NOT NULL REFERENCES statements(id),
    kind           TEXT NOT NULL,   -- 'primary' | 'secondary'
    name           TEXT NOT NULL,
    PRIMARY KEY (statement_id, kind, name)
);

CREATE TABLE statement_ambient (
    statement_id   TEXT NOT NULL REFERENCES statements(id),
    structure      TEXT NOT NULL,
    PRIMARY KEY (statement_id, structure)
);

CREATE TABLE statement_ontology (
    statement_id   TEXT NOT NULL REFERENCES statements(id),
    semantic_kind  TEXT,
    keyword        TEXT,
    PRIMARY KEY (statement_id, semantic_kind, keyword)
);

CREATE TABLE statement_proved_by (
    statement_id  TEXT NOT NULL REFERENCES statements(id),
    proof_id      TEXT NOT NULL,
    PRIMARY KEY (statement_id, proof_id)
);

CREATE TABLE statement_depends_on (
    statement_id   TEXT NOT NULL REFERENCES statements(id),
    target_id      TEXT NOT NULL,
    role           TEXT NOT NULL,
    confidence     TEXT,
    notes          TEXT,
    PRIMARY KEY (statement_id, target_id, role)
);

CREATE TABLE statement_generality (
    statement_id   TEXT NOT NULL REFERENCES statements(id),
    target_id      TEXT NOT NULL,
    relation       TEXT NOT NULL,
    PRIMARY KEY (statement_id, target_id, relation)
);

CREATE TABLE proofs (
    id              TEXT PRIMARY KEY,
    proves          TEXT NOT NULL REFERENCES statements(id),
    status          TEXT NOT NULL,
    schema_version  TEXT NOT NULL,
    style           TEXT,
    notes           TEXT
);

CREATE TABLE proof_uses (
    proof_id      TEXT NOT NULL REFERENCES proofs(id),
    statement_id  TEXT NOT NULL REFERENCES statements(id),
    role          TEXT NOT NULL,
    confidence    TEXT NOT NULL,
    implicit      INTEGER NOT NULL,
    locality      TEXT NOT NULL DEFAULT '',
    notes         TEXT,
    PRIMARY KEY (proof_id, statement_id, role, locality)
);

CREATE TABLE proof_parts (
    proof_id   TEXT NOT NULL REFERENCES proofs(id),
    name       TEXT NOT NULL,
    kind       TEXT NOT NULL,
    description TEXT,
    PRIMARY KEY (proof_id, name)
);

CREATE TABLE proof_quality (
    proof_id       TEXT PRIMARY KEY REFERENCES proofs(id),
    extraction     TEXT,
    dependency     TEXT,
    semantic       TEXT,
    translation    TEXT,
    latex_conf     TEXT,
    source_align   TEXT
);

CREATE TABLE proof_provenance (
    proof_id       TEXT PRIMARY KEY REFERENCES proofs(id),
    schema_version TEXT NOT NULL,
    rerun_id       TEXT,
    extracted_by   TEXT,
    extracted_at   TEXT,
    redirected_to  TEXT
);

CREATE TABLE sources (
    entity_id      TEXT NOT NULL,
    entity_kind    TEXT NOT NULL,
    work           TEXT NOT NULL,
    author         TEXT,
    edition        TEXT,
    year           INTEGER,
    chapter        TEXT,
    section        TEXT,
    theorem_label  TEXT,
    page           TEXT,
    locator        TEXT,
    url            TEXT,
    source_language TEXT
);

CREATE INDEX idx_sources_entity   ON sources(entity_id);
CREATE INDEX idx_sources_work     ON sources(work);
CREATE INDEX idx_sources_chapter  ON sources(chapter);
CREATE INDEX idx_proofs_proves    ON proofs(proves);
CREATE INDEX idx_proof_uses_stmt  ON proof_uses(statement_id);
CREATE INDEX idx_stmt_domain      ON statement_domains(name);
CREATE INDEX idx_stmt_ambient     ON statement_ambient(structure);
CREATE INDEX idx_stmt_ontology    ON statement_ontology(semantic_kind);
CREATE INDEX idx_stmt_keyword     ON statement_ontology(keyword);
CREATE INDEX idx_stmt_type        ON statements(type);
CREATE INDEX idx_stmt_status      ON statements(status);
"""


def _populate(con: sqlite3.Connection, ds: Dataset) -> None:
    cur = con.cursor()
    for sid, s in ds.statements.items():
        cur.execute(
            "INSERT INTO statements VALUES (?,?,?,?,?,?,?,?,?)",
            (
                sid,
                s.type,
                s.status,
                s.schema_version,
                s.language.original,
                s.statement.latex.body,
                s.statement.latex.status,
                s.statement.latex.review_status,
                s.notes,
            ),
        )
        for lang, t in s.title.items():
            cur.execute(
                "INSERT INTO statement_titles VALUES (?,?,?,?,?,?)",
                (sid, lang, t.text, int(t.is_original), t.origin, t.review_status),
            )
        for lang, t in s.statement.natural.items():
            cur.execute(
                "INSERT INTO statement_natural VALUES (?,?,?,?,?,?)",
                (sid, lang, t.text, int(t.is_original), t.origin, t.review_status),
            )
        q = s.quality
        cur.execute(
            "INSERT INTO statement_quality VALUES (?,?,?,?,?,?,?)",
            (
                sid,
                q.extraction_confidence,
                q.dependency_confidence,
                q.semantic_confidence,
                q.translation_confidence,
                q.latex_confidence,
                q.source_alignment_confidence,
            ),
        )
        p = s.provenance
        cur.execute(
            "INSERT INTO statement_provenance VALUES (?,?,?,?,?,?)",
            (sid, p.schema_version, p.rerun_id, p.extracted_by, p.extracted_at, p.redirected_to),
        )
        for prior in p.derived_from:
            cur.execute(
                "INSERT INTO statement_derived_from VALUES (?,?)", (sid, prior)
            )
        for d in s.domains.primary:
            cur.execute(
                "INSERT OR IGNORE INTO statement_domains VALUES (?,?,?)",
                (sid, "primary", d),
            )
        for d in s.domains.secondary:
            cur.execute(
                "INSERT OR IGNORE INTO statement_domains VALUES (?,?,?)",
                (sid, "secondary", d),
            )
        for st in s.ambient.structures:
            cur.execute(
                "INSERT OR IGNORE INTO statement_ambient VALUES (?,?)", (sid, st)
            )
        for k in s.ontology.semantic_kind:
            cur.execute(
                "INSERT OR IGNORE INTO statement_ontology VALUES (?,?,?)",
                (sid, k, ""),
            )
        for kw in s.ontology.keywords:
            cur.execute(
                "INSERT OR IGNORE INTO statement_ontology VALUES (?,?,?)",
                (sid, "", kw),
            )
        for ref in s.proved_by:
            cur.execute(
                "INSERT INTO statement_proved_by VALUES (?,?)", (sid, ref)
            )
        for dep in s.depends_on:
            cur.execute(
                "INSERT INTO statement_depends_on VALUES (?,?,?,?,?)",
                (sid, dep.id, dep.role, dep.confidence, dep.notes),
            )
        for gen in s.generality:
            cur.execute(
                "INSERT INTO statement_generality VALUES (?,?,?)",
                (sid, gen.target, gen.relation),
            )
        for src in s.sources:
            cur.execute(
                "INSERT INTO sources VALUES (?,'statement',?,?,?,?,?,?,?,?,?,?,?)",
                (
                    sid, src.work, src.author, src.edition, src.year, src.chapter,
                    src.section, src.theorem_label, src.page, src.locator, src.url,
                    src.source_language,
                ),
            )

    for pid, pr in ds.proofs.items():
        cur.execute(
            "INSERT INTO proofs VALUES (?,?,?,?,?,?)",
            (pid, pr.proves, pr.status, pr.schema_version, pr.style, pr.notes),
        )
        for dep in pr.uses:
            cur.execute(
                "INSERT OR IGNORE INTO proof_uses VALUES (?,?,?,?,?,?,?)",
                (
                    pid, dep.id, dep.role, dep.confidence, int(dep.implicit),
                    dep.locality or "", dep.notes,
                ),
            )
        for part in pr.parts:
            cur.execute(
                "INSERT INTO proof_parts VALUES (?,?,?,?)",
                (pid, part.name, part.kind, part.description),
            )
            for dep in part.uses:
                cur.execute(
                    "INSERT OR IGNORE INTO proof_uses VALUES (?,?,?,?,?,?,?)",
                    (
                        pid, dep.id, dep.role, dep.confidence, int(dep.implicit),
                        dep.locality or part.name, dep.notes,
                    ),
                )
        q = pr.quality
        cur.execute(
            "INSERT INTO proof_quality VALUES (?,?,?,?,?,?,?)",
            (
                pid,
                q.extraction_confidence,
                q.dependency_confidence,
                q.semantic_confidence,
                q.translation_confidence,
                q.latex_confidence,
                q.source_alignment_confidence,
            ),
        )
        p = pr.provenance
        cur.execute(
            "INSERT INTO proof_provenance VALUES (?,?,?,?,?,?)",
            (pid, p.schema_version, p.rerun_id, p.extracted_by, p.extracted_at, p.redirected_to),
        )
        for src in pr.sources:
            cur.execute(
                "INSERT INTO sources VALUES (?,'proof',?,?,?,?,?,?,?,?,?,?,?)",
                (
                    pid, src.work, src.author, src.edition, src.year, src.chapter,
                    src.section, src.theorem_label, src.page, src.locator, src.url,
                    src.source_language,
                ),
            )
    con.commit()


def _build_graph(con: sqlite3.Connection) -> nx.MultiDiGraph:
    g: nx.MultiDiGraph = nx.MultiDiGraph()
    cur = con.cursor()
    for sid, stype, status in cur.execute("SELECT id, type, status FROM statements"):
        g.add_node(sid, kind="statement", type=stype, status=status)
    for pid, proves, status, style in cur.execute(
        "SELECT id, proves, status, style FROM proofs"
    ):
        g.add_node(pid, kind="proof", type="proof", status=status, style=style or "")
        g.add_edge(pid, proves, relation="proves")
    for pid, sid, role, conf, implicit in cur.execute(
        "SELECT proof_id, statement_id, role, confidence, implicit FROM proof_uses"
    ):
        g.add_edge(
            sid, pid,
            relation="uses", role=role, confidence=conf, implicit=bool(implicit),
        )
    for sid, tid, role in cur.execute(
        "SELECT statement_id, target_id, role FROM statement_depends_on"
    ):
        g.add_edge(sid, tid, relation="depends_on", role=role)
    return g


def _to_node_link(g: nx.MultiDiGraph) -> dict:
    nodes = sorted(({"id": n, **g.nodes[n]} for n in g.nodes), key=lambda d: d["id"])
    links = sorted(
        ({"source": u, "target": v, **data} for u, v, data in g.edges(data=True)),
        key=lambda d: (d["source"], d["target"], d.get("relation", "")),
    )
    return {"directed": True, "multigraph": True, "schema_version": "0.3.1",
            "nodes": nodes, "links": links}


def _node_details(con: sqlite3.Connection) -> dict[str, dict[str, Any]]:
    cur = con.cursor()
    sub = con.cursor()
    out: dict[str, dict] = {}
    for row in cur.execute("SELECT id, type, status FROM statements").fetchall():
        sid = row[0]
        entry: dict[str, Any] = {"id": sid, "kind": "statement", "type": row[1], "status": row[2]}
        titles = {}
        for lang, text, is_orig in sub.execute(
            "SELECT lang, text, is_original FROM statement_titles WHERE statement_id=?", (sid,)
        ):
            titles[lang] = {"text": text, "is_original": bool(is_orig)}
        if titles:
            entry["title"] = titles
        natural = {}
        for lang, text, is_orig in sub.execute(
            "SELECT lang, text, is_original FROM statement_natural WHERE statement_id=?", (sid,)
        ):
            natural[lang] = {"text": text, "is_original": bool(is_orig)}
        if natural:
            entry["natural"] = natural
        out[sid] = entry
    for row in cur.execute("SELECT id, proves, status, style FROM proofs").fetchall():
        pid = row[0]
        entry = {"id": pid, "kind": "proof", "type": "proof", "status": row[2],
                 "proves": row[1], "style": row[3] or ""}
        deps = []
        for did, role, conf in sub.execute(
            "SELECT statement_id, role, confidence FROM proof_uses WHERE proof_id=? ORDER BY statement_id",
            (pid,),
        ):
            deps.append({"id": did, "role": role, "confidence": conf})
        if deps:
            entry["uses"] = deps
        out[pid] = entry
    return out


def build_db(ds: Dataset | None = None) -> sqlite3.Connection:
    if ds is None:
        ds = load_dataset()
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()
    con = sqlite3.connect(str(DB_PATH))
    con.executescript(SCHEMA_SQL)
    _populate(con, ds)
    return con


def _write_outputs(con: sqlite3.Connection) -> tuple[int, int]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    g = _build_graph(con)
    (GRAPH_DIR / "graph.json").write_text(
        json.dumps(_to_node_link(g), indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (GRAPH_DIR / "node-details.json").write_text(
        json.dumps(_node_details(con), indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    nx.write_graphml(g, EXPORT_DIR / "graph.graphml")
    return g.number_of_nodes(), g.number_of_edges()


def main() -> int:
    print("loading v0.3 YAML …")
    ds = load_dataset()
    if ds.skipped_legacy:
        print(f"  skipped {len(ds.skipped_legacy)} non-v0.3 file(s)")
    if ds.errors:
        print(f"FAIL — {len(ds.errors)} schema error(s):", file=sys.stderr)
        for e in ds.errors:
            print(f"  - {e.path}: {e.message}", file=sys.stderr)
        return 1
    print(f"  {len(ds.statements)} statements, {len(ds.proofs)} proofs")
    print("building SQLite …")
    con = build_db(ds)
    print(f"  wrote {DB_PATH.relative_to(REPO_ROOT)}")
    print("writing outputs …")
    n, e = _write_outputs(con)
    print(f"  graph: {n} nodes, {e} edges")
    con.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
