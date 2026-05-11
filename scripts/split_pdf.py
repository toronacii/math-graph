"""Split a PDF textbook into per-chapter files.

Auto-detects chapter boundaries by looking for pages whose first
non-empty line is a chapter number (digits only) and whose second
non-empty line is an ALL-CAPS title.

Usage:
    python -m scripts.split_pdf [--pdf PATH] [--output-dir DIR]

Defaults are configured for Walter Rudin's *Principles of Mathematical
Analysis* (3rd edition).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import fitz  # PyMuPDF


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_BACK_MATTER_KEYWORDS = frozenset(
    {"BIBLIOGRAPHY", "INDEX", "LISTOFSPECIALSYMBOLS", "REFERENCES"}
)


def _first_non_empty_lines(text: str, n: int = 3) -> list[str]:
    """Return the first *n* non-empty stripped lines from *text*."""
    lines: list[str] = []
    for raw in text.split("\n"):
        stripped = raw.strip()
        if stripped:
            lines.append(stripped)
            if len(lines) == n:
                break
    return lines


def _normalize_ocr_number(s: str) -> int | None:
    """Parse a chapter number, allowing OCR artefacts like '1 1' -> 11."""
    collapsed = s.replace(" ", "")
    if collapsed.isdigit():
        return int(collapsed)
    return None


def _is_upper_title(line: str, min_words: int = 1) -> bool:
    """Return True if *line* looks like an ALL-CAPS chapter title."""
    # Remove common OCR noise (soft-hyphens, punctuation) before checking
    cleaned = re.sub(r"[^A-Za-z\s]", "", line)
    words = cleaned.split()
    if len(words) < min_words:
        return False
    alpha_chars = [c for c in cleaned if c.isalpha()]
    if not alpha_chars:
        return False
    upper_ratio = sum(1 for c in alpha_chars if c.isupper()) / len(alpha_chars)
    return upper_ratio >= 0.75


def _is_back_matter(lines: list[str]) -> bool:
    """Heuristic: does this page start back-matter (bibliography, index)?"""
    for line in lines[:2]:
        # Strip everything except letters, then compare
        normalized = re.sub(r"[^A-Za-z]", "", line).upper()
        if normalized in _BACK_MATTER_KEYWORDS:
            return True
    return False


# ---------------------------------------------------------------------------
# Chapter detection
# ---------------------------------------------------------------------------

def _normalize_title(title: str) -> str:
    """Collapse OCR noise to a canonical form for comparison."""
    return re.sub(r"[^A-Za-z]", "", title).upper()


def _char_similarity(a: str, b: str) -> float:
    """Return the character-level similarity ratio between two strings (0..1).

    Uses the ratio of shared character counts to the length of the longer
    string.  This is intentionally simple — good enough to catch OCR
    variants of the same running header.
    """
    from collections import Counter

    if not a or not b:
        return 0.0
    ca, cb = Counter(a), Counter(b)
    shared = sum((ca & cb).values())
    return shared / max(len(a), len(b))


def _is_running_header(title: str, header_norm: str, threshold: float = 0.80) -> bool:
    """Return True if *title* is likely an OCR variant of *header_norm*."""
    norm = _normalize_title(title)
    if not norm or not header_norm:
        return False
    return _char_similarity(norm, header_norm) >= threshold


def detect_chapters(doc: fitz.Document) -> list[dict]:
    """Return a list of dicts with keys: number, title, start_page (0-indexed)."""
    # --- First pass: collect every candidate --------------------------------
    candidates: list[dict] = []
    for page_idx in range(doc.page_count):
        page = doc[page_idx]
        text = page.get_text()
        lines = _first_non_empty_lines(text, n=3)
        if len(lines) < 2:
            continue

        num = _normalize_ocr_number(lines[0])
        if num is None or num < 1:
            continue

        if not _is_upper_title(lines[1]):
            continue

        candidates.append(
            {
                "number": num,
                "title": lines[1],
                "start_page": page_idx,
            }
        )

    if not candidates:
        return []

    # --- Detect running headers (fuzzy) -------------------------------------
    # Find the most frequent normalized title.  Then use fuzzy matching to
    # also remove OCR variants of the same header.
    from collections import Counter

    title_counts = Counter(_normalize_title(c["title"]) for c in candidates)
    most_common_title, most_common_count = title_counts.most_common(1)[0]

    if most_common_count > 3:
        candidates = [
            c
            for c in candidates
            if not _is_running_header(c["title"], most_common_title)
        ]

    # --- Filter TOC pages ---------------------------------------------------
    # TOC pages mention multiple "Chapter N" lines on the same page.
    filtered: list[dict] = []
    for c in candidates:
        page = doc[c["start_page"]]
        full_text = page.get_text()
        chapter_mentions = re.findall(
            r"Chapter\s+\d", full_text, re.IGNORECASE
        )
        if len(chapter_mentions) >= 2:
            continue  # likely TOC
        filtered.append(c)
    candidates = filtered

    # --- Filter back-matter pages -------------------------------------------
    # Pages starting INDEX, BIBLIOGRAPHY, etc. are not chapters.
    candidates = [
        c
        for c in candidates
        if re.sub(r"[^A-Za-z]", "", c["title"]).upper() not in _BACK_MATTER_KEYWORDS
    ]

    # --- Deduplicate: keep first occurrence of each chapter number ----------
    seen: set[int] = set()
    unique: list[dict] = []
    for ch in candidates:
        if ch["number"] not in seen:
            seen.add(ch["number"])
            unique.append(ch)

    # Sort by chapter number
    unique.sort(key=lambda c: c["number"])

    return unique


def detect_content_end(doc: fitz.Document, last_chapter_start: int) -> int:
    """Return the 0-indexed page number of the last content page (before back-matter)."""
    for page_idx in range(last_chapter_start + 1, doc.page_count):
        page = doc[page_idx]
        text = page.get_text()
        lines = _first_non_empty_lines(text, n=2)
        if _is_back_matter(lines):
            return page_idx - 1
    return doc.page_count - 1


# ---------------------------------------------------------------------------
# Splitting
# ---------------------------------------------------------------------------

def split_pdf(
    pdf_path: Path,
    output_dir: Path,
    chapters: list[dict],
    content_end: int,
) -> list[Path]:
    """Write one PDF per chapter and return the list of output paths."""
    output_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []

    for i, ch in enumerate(chapters):
        start = ch["start_page"]
        end = chapters[i + 1]["start_page"] - 1 if i + 1 < len(chapters) else content_end

        out_name = f"chapter-{ch['number']:02d}.pdf"
        out_path = output_dir / out_name

        sub_doc = fitz.open()  # new empty document
        sub_doc.insert_pdf(fitz.open(pdf_path), from_page=start, to_page=end)
        sub_doc.save(str(out_path))
        sub_doc.close()

        paths.append(out_path)
        page_count = end - start + 1
        print(
            f"  Chapter {ch['number']:>2d}  "
            f"pp {start + 1:>3d}-{end + 1:<3d}  "
            f"({page_count:>3d} pages)  "
            f"{ch['title']}"
        )

    return paths


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> None:
    default_pdf = Path(__file__).resolve().parent.parent / (
        "sources/rudin/Principles of mathematical analysis - Walter Rudin.pdf"
    )
    default_output = Path(__file__).resolve().parent.parent / "sources/rudin/chapters"

    parser = argparse.ArgumentParser(
        description="Split a PDF textbook into per-chapter files.",
    )
    parser.add_argument(
        "--pdf",
        type=Path,
        default=default_pdf,
        help="Path to the source PDF (default: Rudin).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=default_output,
        help="Directory for chapter PDFs (default: sources/rudin/chapters/).",
    )
    args = parser.parse_args(argv)

    if not args.pdf.exists():
        print(f"Error: PDF not found at {args.pdf}", file=sys.stderr)
        sys.exit(1)

    print(f"Opening {args.pdf.name} ...")
    doc = fitz.open(str(args.pdf))
    print(f"  Total pages: {doc.page_count}")

    print("\nDetecting chapters ...")
    chapters = detect_chapters(doc)
    if not chapters:
        print("Error: no chapters detected.", file=sys.stderr)
        sys.exit(1)

    content_end = detect_content_end(doc, chapters[-1]["start_page"])
    print(f"  Found {len(chapters)} chapters (content ends at page {content_end + 1})\n")

    print("Splitting:")
    paths = split_pdf(args.pdf, args.output_dir, chapters, content_end)
    doc.close()

    print(f"\nDone. {len(paths)} chapter files written to {args.output_dir}/")


if __name__ == "__main__":
    main()
