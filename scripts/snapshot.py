"""Create a frozen snapshot of the current generated graph + data.

Usage::

    python -m scripts.snapshot --label v0.3-2026-06-01

The snapshot is written under generated/snapshots/<label>/ and contains:
  - data/                 (full YAML at snapshot time)
  - graph/                (graph.json, node-details.json, math_graph.db)
  - exports/              (graph.graphml)
  - reports/              (audits + chapter reports)
  - milestones/
  - context-packs/
  - MANIFEST.yml
  - hashes.txt            (sha256 of every file in the snapshot)

Snapshots are immutable. Never edit them in place.
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
from datetime import UTC, datetime
from pathlib import Path

import yaml

from scripts.v03.loader import REPO_ROOT


def _copy(src: Path, dst: Path) -> None:
    if src.is_dir():
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
    elif src.is_file():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _write_hashes(out: Path) -> int:
    hashes: list[tuple[str, str]] = []
    for p in sorted(out.rglob("*")):
        if p.is_file() and p.name not in {"hashes.txt", "MANIFEST.yml"}:
            rel = p.relative_to(out).as_posix()
            hashes.append((rel, _sha256(p)))
    (out / "hashes.txt").write_text(
        "\n".join(f"{h}  {rel}" for rel, h in hashes) + "\n", encoding="utf-8"
    )
    return len(hashes)


def snapshot(label: str, root: Path = REPO_ROOT) -> Path:
    out = root / "generated" / "snapshots" / label
    out.mkdir(parents=True, exist_ok=True)

    _copy(root / "data", out / "data")
    _copy(root / "generated" / "v0.3", out / "graph")  # v0.3 outputs
    _copy(root / "generated" / "exports", out / "exports")
    _copy(root / "reports", out / "reports")
    _copy(root / "milestones", out / "milestones")
    _copy(root / "generated" / "context-packs", out / "context-packs")

    file_count = _write_hashes(out)

    manifest = {
        "snapshot": {
            "label": label,
            "created": datetime.now(UTC).isoformat(),
            "status": "frozen",
            "policy": "read-only-historical-archive",
        },
        "file_count": file_count,
        "hash_index": "hashes.txt",
    }
    (out / "MANIFEST.yml").write_text(
        yaml.dump(manifest, sort_keys=False, default_flow_style=False), encoding="utf-8"
    )
    return out


def hashes_only(label: str, root: Path = REPO_ROOT) -> Path:
    """Backfill hashes.txt for an existing snapshot directory.

    Does not modify MANIFEST.yml or any other file. Use this for
    snapshots that were created manually (e.g. the v0.2 baseline)
    where MANIFEST.yml already exists with a hand-authored schema.
    """
    out = root / "generated" / "snapshots" / label
    if not out.is_dir():
        raise SystemExit(f"snapshot directory not found: {out}")
    n = _write_hashes(out)
    print(f"wrote {n} file hashes to {out.relative_to(root)}/hashes.txt")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a frozen MKG snapshot.")
    parser.add_argument("--label", required=True, help="snapshot label, e.g. v0.3-2026-06-01")
    parser.add_argument(
        "--hashes-only",
        action="store_true",
        help="Only (re)write hashes.txt for an existing snapshot directory.",
    )
    args = parser.parse_args()
    if args.hashes_only:
        out = hashes_only(args.label)
    else:
        out = snapshot(args.label)
        print(f"wrote snapshot to {out.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
