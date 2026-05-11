"""Best-effort, lossy migration of a v0.2 YAML entity to a v0.3 skeleton.

Migration philosophy
--------------------
The project decided that the v0.2 graph is a disposable prototype baseline.
A *full re-extraction* is the intended path to v0.3. This script is NOT a
substitute for that — it produces v0.3 SKELETONS pre-populated from v0.2
data so a reviewer can fill the new fields (domains, ambient, ontology,
LaTeX status, decomposed quality) without retyping the existing content.

The output is written to a parallel directory (`migrated/`) by default and
NEVER overwrites `data/` automatically.

Mapping
-------
- `confidence` (single)            → quality.extraction_confidence
- `latex` (string or absent)       → latex.body + latex.status (present|missing)
- title / natural (i18n strings)   → MultilingualBlock; original_language
                                     defaults to 'en' for Rudin works,
                                     'es' for Stewart works (override with --original-lang)
- `uses` (list[str])               → list[ProofDependency] role=essential, conf=high
- `proved_by` / `proves`           → unchanged
- `sources`                        → unchanged + theorem_label inferred from `section`
                                     when the form 'NN.NN' is present
- new fields                       → empty / sensible defaults
- provenance                       → derived_from = [old_id]

Run::

    python -m scripts.migrate_v02_to_v03 --in data --out migrated
"""

from __future__ import annotations

import argparse
import re
from datetime import UTC, datetime
from pathlib import Path

import yaml

from scripts.loader import REPO_ROOT
from scripts.loader import load_dataset as load_v02

THEOREM_LIKE_LABEL = re.compile(r"^\d+\.\d+[a-z]?$")

WORK_LANG_DEFAULT = {
    "Principles of Mathematical Analysis": "en",
    "Cálculo de una variable — Trascendentes tempranas": "es",
}


def _infer_original_lang(work_names: list[str], fallback: str) -> str:
    for w in work_names:
        if w in WORK_LANG_DEFAULT:
            return WORK_LANG_DEFAULT[w]
    return fallback


def _multilingual(d: dict[str, str], original: str) -> dict:
    out = {}
    for lang, text in d.items():
        out[lang] = {
            "text": text,
            "is_original": lang == original,
            "origin": "human" if lang == original else "llm",
            "review_status": "unreviewed",
        }
    if original not in out and out:
        # mark first-seen language as original to satisfy invariant
        first = next(iter(out))
        out[first]["is_original"] = True
        original = first
    return out


def _sources(srcs: list) -> list[dict]:
    out = []
    for s in srcs:
        d = s.model_dump(exclude_none=True)
        sec = d.get("section")
        if sec and THEOREM_LIKE_LABEL.match(sec):
            d.setdefault("theorem_label", sec)
        out.append(d)
    return out


def _migrate_statement(stmt) -> dict:
    work_names = [s.work for s in stmt.sources]
    original = _infer_original_lang(work_names, fallback="en")
    out = {
        "schema_version": "0.3.0",
        "id": stmt.id,
        "type": stmt.type,
        "status": "extracted",
        "language": {"original": original, "available": list(stmt.title.keys())},
        "title": _multilingual(stmt.title, original),
        "statement": {
            "natural": _multilingual(stmt.statement.natural, original),
            "latex": {
                "body": stmt.statement.latex,
                "status": "present" if stmt.statement.latex else (
                    "not_applicable" if stmt.type in ("definition", "axiom") else "missing"
                ),
                "review_status": "unreviewed",
            },
        },
        "proved_by": list(stmt.proved_by),
        "depends_on": [],
        "sources": _sources(stmt.sources),
        "domains": {"primary": [], "secondary": []},
        "ambient": {"structures": []},
        "ontology": {"semantic_kind": [], "keywords": []},
        "generality": [],
        "quality": {
            "extraction_confidence": stmt.confidence,
            "dependency_confidence": None,
            "semantic_confidence": None,
            "translation_confidence": None,
            "latex_confidence": None,
            "source_alignment_confidence": None,
        },
        "provenance": {
            "schema_version": "0.3.0",
            "rerun_id": "v0.3-migration",
            "extracted_by": "scripts.migrate_v02_to_v03",
            "extracted_at": datetime.now(UTC).date().isoformat(),
            "derived_from": [stmt.id],
            "rerun_notes": "auto-migrated from v0.2; needs human review",
        },
        "notes": stmt.notes,
    }
    return {k: v for k, v in out.items() if v is not None}


def _migrate_proof(proof) -> dict:
    out = {
        "schema_version": "0.3.0",
        "id": proof.id,
        "type": "proof",
        "status": "extracted",
        "proves": proof.proves,
        "style": proof.style,
        "uses": [
            {
                "id": ref,
                "role": "essential",
                "confidence": "high",
                "implicit": False,
            }
            for ref in proof.uses
        ],
        "parts": [],
        "sources": _sources(proof.sources),
        "quality": {
            "extraction_confidence": proof.confidence,
            "dependency_confidence": None,
            "semantic_confidence": None,
        },
        "provenance": {
            "schema_version": "0.3.0",
            "rerun_id": "v0.3-migration",
            "extracted_by": "scripts.migrate_v02_to_v03",
            "extracted_at": datetime.now(UTC).date().isoformat(),
            "derived_from": [proof.id],
            "rerun_notes": "auto-migrated from v0.2; dependency roles need review",
        },
        "notes": proof.notes,
    }
    return {k: v for k, v in out.items() if v is not None}


def migrate(in_dir: Path, out_dir: Path) -> tuple[int, int]:
    ds = load_v02(in_dir)
    stmts_out = out_dir / "statements"
    proofs_out = out_dir / "proofs"
    stmts_out.mkdir(parents=True, exist_ok=True)
    proofs_out.mkdir(parents=True, exist_ok=True)

    for sid, stmt in ds.statements.items():
        data = _migrate_statement(stmt)
        (stmts_out / f"{sid}.yml").write_text(
            yaml.dump(data, sort_keys=False, allow_unicode=True, default_flow_style=False),
            encoding="utf-8",
        )
    for pid, pr in ds.proofs.items():
        data = _migrate_proof(pr)
        (proofs_out / f"{pid}.yml").write_text(
            yaml.dump(data, sort_keys=False, allow_unicode=True, default_flow_style=False),
            encoding="utf-8",
        )
    return len(ds.statements), len(ds.proofs)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--in", dest="in_dir", type=Path, default=REPO_ROOT / "data")
    parser.add_argument("--out", dest="out_dir", type=Path, default=REPO_ROOT / "migrated")
    args = parser.parse_args()
    n_s, n_p = migrate(args.in_dir, args.out_dir)
    print(f"migrated {n_s} statements + {n_p} proofs to {args.out_dir.relative_to(REPO_ROOT)}")
    print("NB: skeletons require human review before promotion to status > extracted.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
