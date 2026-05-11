"""Build the MKG dependency graph and emit JSON + GraphML.

This module now delegates to :mod:`scripts.build_db` which maintains
the SQLite index as the single source of derived data.  Running this
module directly (``python -m scripts.build_graph``) is equivalent to
``python -m scripts.build_db`` — kept for backwards compatibility.
"""

from __future__ import annotations

from scripts.build_db import main

if __name__ == "__main__":
    raise SystemExit(main())
