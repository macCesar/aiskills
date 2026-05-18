#!/usr/bin/env python3
"""
check_ai_patterns.py — Deterministic scanner for AI-writing tics in Spanish.

Reads patterns from sibling `references/lexicon-es-mx.md` and reports every
hit found in the input text with line number, category, matched phrase, and
a replacement suggestion when the lexicon supplies one.

Usage:
    python check_ai_patterns.py <text_file>
    python check_ai_patterns.py < input.txt
    cat input.txt | python check_ai_patterns.py

Stdlib only. Python 3.8+.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Iterator, NamedTuple


SCRIPT_DIR = Path(__file__).resolve().parent
LEXICON_PATH = SCRIPT_DIR.parent / "references" / "lexicon-es-mx.md"


class Hit(NamedTuple):
    line_no: int
    column: int
    category: str
    matched: str
    suggestion: str  # empty string if none


def _parse_section_header(line: str) -> str:
    """Return the header text if line is `## ...`, else empty string."""
    if line.startswith("## "):
        return line[3:].strip().rstrip(":")
    return ""


def _split_phrases(content: str) -> list[str]:
    """
    Split a comma-separated phrase block into individual phrases.
    Strips whitespace and a trailing period.
    """
    cleaned = content.strip().rstrip(".")
    return [p.strip() for p in cleaned.split(",") if p.strip()]


def _parse_replacement_line(line: str) -> tuple[str, str] | None:
    """
    Parse a lexicon line of the form `- phrase -> suggestion` or
    `phrase -> suggestion`. Returns (phrase, suggestion) or None.
    """
    stripped = line.lstrip("-").strip()
    if "->" not in stripped:
        return None
    left, _, right = stripped.partition("->")
    phrase = left.strip()
    suggestion = right.strip()
    # Strip any inline parenthetical hint on the phrase side, e.g. `aplicar a (trabajo)`.
    # We keep the visible form so the user can locate it, but build a search regex
    # that ignores the hint. Here, we keep the phrase as-is and let the search
    # tolerate the parenthetical by stripping it for matching only.
    return phrase, suggestion


def load_lexicon(path: Path) -> dict[str, list[tuple[str, str]]]:
    """
    Parse the lexicon markdown file into a dict of:
        category -> list of (phrase, suggestion) tuples.

    Suggestion is an empty string when the lexicon offers none.
    """
    if not path.exists():
        return {}

    categories: dict[str, list[tuple[str, str]]] = {}
    current_category = ""
    current_inline_block: list[str] = []

    def flush_inline_block() -> None:
        if not current_category or not current_inline_block:
            return
        text = " ".join(current_inline_block)
        phrases = _split_phrases(text)
        for p in phrases:
            categories.setdefault(current_category, []).append((p, ""))
        current_inline_block.clear()

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()

        header = _parse_section_header(line)
        if header:
            flush_inline_block()
            current_category = header
            continue

        if not current_category:
            continue

        if not line.strip():
            flush_inline_block()
            continue

        replacement = _parse_replacement_line(line)
        if replacement is not None:
            phrase, suggestion = replacement
            categories.setdefault(current_category, []).append((phrase, suggestion))
            continue

        if line.startswith("-"):
            # Bullet item without `->`: treat as a plain phrase.
            phrase = line.lstrip("-").strip()
            if phrase:
                categories.setdefault(current_category, []).append((phrase, ""))
            continue

        # Otherwise, this is part of an inline comma-separated block.
        current_inline_block.append(line)

    flush_inline_block()
    return categories


def _compile_pattern(phrase: str) -> re.Pattern[str]:
    """
    Build a case-insensitive regex matching the phrase as a whole-word boundary,
    tolerating an optional parenthetical hint (e.g. `aplicar a (trabajo)` matches
    `aplicar a`).
    """
    bare = re.sub(r"\s*\([^)]*\)\s*", "", phrase).strip()
    escaped = re.escape(bare)
    # Allow optional whitespace inside multi-word phrases.
    escaped = escaped.replace(r"\ ", r"\s+")
    return re.compile(rf"(?<!\w){escaped}(?!\w)", re.IGNORECASE)


def scan_text(
    text: str,
    categories: dict[str, list[tuple[str, str]]],
) -> Iterator[Hit]:
    """Yield a Hit for every phrase match found in the text."""
    compiled = [
        (category, phrase, suggestion, _compile_pattern(phrase))
        for category, items in categories.items()
        for phrase, suggestion in items
    ]

    for line_no, line in enumerate(text.splitlines(), start=1):
        for category, phrase, suggestion, pattern in compiled:
            for match in pattern.finditer(line):
                yield Hit(
                    line_no=line_no,
                    column=match.start() + 1,
                    category=category,
                    matched=match.group(0),
                    suggestion=suggestion,
                )


def read_input() -> str:
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg in ("-h", "--help"):
            print(__doc__)
            sys.exit(0)
        return Path(arg).read_text(encoding="utf-8")
    return sys.stdin.read()


def format_hit(hit: Hit) -> str:
    location = f"line {hit.line_no}:{hit.column}"
    body = f'[{hit.category}] "{hit.matched}"'
    if hit.suggestion:
        body += f"  →  {hit.suggestion}"
    return f"{location}  {body}"


def main() -> int:
    categories = load_lexicon(LEXICON_PATH)
    if not categories:
        print(
            f"WARNING: lexicon not found or empty at {LEXICON_PATH}",
            file=sys.stderr,
        )
        return 2

    text = read_input()
    hits = list(scan_text(text, categories))

    if not hits:
        print("OK: no AI-writing tics detected.")
        return 0

    print(f"Found {len(hits)} potential AI-writing tic(s):\n")
    for hit in hits:
        print(format_hit(hit))

    by_category: dict[str, int] = {}
    for hit in hits:
        by_category[hit.category] = by_category.get(hit.category, 0) + 1

    print("\nSummary by category:")
    for category, count in sorted(by_category.items(), key=lambda x: -x[1]):
        print(f"  {count:>3}  {category}")

    return 1


if __name__ == "__main__":
    sys.exit(main())
