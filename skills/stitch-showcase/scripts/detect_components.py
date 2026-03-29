"""
detect_components.py — Detect shared components across Stitch screen HTMLs.

Finds navbars, footers, tabbars, sidebars, and headers that appear across
multiple screens. Compares variants and recommends a canonical version.

Uses only stdlib (html.parser, difflib, re, json). No external dependencies.

Usage:
    # As a module (from build_showcase.py):
    from detect_components import detect_shared_components

    # Standalone:
    python detect_components.py /path/to/assets/
"""
import re
import sys
import json
from pathlib import Path

# Sibling import
sys.path.insert(0, str(Path(__file__).parent))
import component_utils as cu


# Screens containing these slugs get priority when choosing canonical version
HOME_PRIORITY_SLUGS = frozenset([
    "home", "main", "dashboard", "inicio", "principal", "landing",
    "index", "home_screen", "pantalla_principal",
])

# Minimum screens a component must appear in to be considered "shared"
MIN_SHARED_SCREENS = 2

# Default similarity threshold for grouping variants
DEFAULT_SIMILARITY_THRESHOLD = 0.85


def detect_shared_components(
    assets_dir: Path,
    threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
) -> dict:
    """
    Detect shared components across all screen HTMLs in assets_dir.

    Args:
        assets_dir: Directory containing screen .html files
        threshold: Minimum similarity score to group as same component (0.0-1.0)

    Returns:
        Dict with component types as keys, each containing:
        - found_in: number of screens with this component
        - total_screens: total screens analyzed
        - canonical: recommended version with slug, html_snippet, score
        - variants: list of variant diffs
    """
    html_files = sorted(assets_dir.glob("*.html"))
    if not html_files:
        return {}

    total_screens = len(html_files)

    # Step 1: Extract semantic blocks from each screen
    screen_components = {}
    for html_path in html_files:
        slug = html_path.stem
        try:
            html = html_path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue

        blocks = cu.extract_semantic_blocks(html)
        if blocks:
            screen_components[slug] = blocks

    if not screen_components:
        return {}

    # Step 2: For each component type, collect across screens and group variants
    results = {}
    component_types = set()
    for blocks in screen_components.values():
        component_types.update(blocks.keys())

    for comp_type in sorted(component_types):
        # Collect all instances of this component type
        instances = []
        for slug, blocks in screen_components.items():
            if comp_type in blocks:
                for block_html in blocks[comp_type]:
                    instances.append({
                        "slug": slug,
                        "html": block_html,
                        "signature": cu.dom_signature(block_html),
                        "node_count": cu.count_dom_nodes(block_html),
                        "text": cu.strip_tags(block_html),
                    })

        if len(instances) < MIN_SHARED_SCREENS:
            continue

        # Step 3: Group similar instances
        groups = _group_by_similarity(instances, threshold)

        # Only keep groups that span multiple screens
        for group in groups:
            screen_slugs = list(dict.fromkeys(inst["slug"] for inst in group))
            if len(screen_slugs) < MIN_SHARED_SCREENS:
                continue

            # Step 4: Choose canonical version
            canonical = _choose_canonical(group)

            # Step 5: Build variant list with differences
            variants = _build_variants(group, canonical)

            results[f"{comp_type}s"] = {
                "found_in": len(screen_slugs),
                "total_screens": total_screens,
                "canonical": {
                    "slug": canonical["slug"],
                    "html_snippet": _truncate_html(canonical["html"], 2000),
                    "node_count": canonical["node_count"],
                    "score": 1.0,
                },
                "variants": variants,
            }

    return results


def _group_by_similarity(instances: list, threshold: float) -> list:
    """
    Group component instances by similarity score.

    Uses greedy clustering: assign each instance to the first group
    whose representative it matches above threshold.
    """
    groups = []

    for inst in instances:
        placed = False
        for group in groups:
            rep = group[0]
            score = cu.component_similarity(rep["html"], inst["html"])
            if score >= threshold:
                group.append(inst)
                placed = True
                break

        if not placed:
            groups.append([inst])

    return groups


def _choose_canonical(group: list) -> dict:
    """
    Choose the canonical (best) version of a component.

    Priority:
    1. From a "home" or "main" screen
    2. Most DOM nodes (most complete version)
    3. First encountered
    """
    # Sort by: home priority (desc), node count (desc)
    def sort_key(inst):
        is_home = any(h in inst["slug"] for h in HOME_PRIORITY_SLUGS)
        return (-int(is_home), -inst["node_count"])

    sorted_group = sorted(group, key=sort_key)
    return sorted_group[0]


def _build_variants(group: list, canonical: dict) -> list:
    """Build variant entries comparing each screen's version to canonical."""
    seen_slugs = set()
    variants = []

    for inst in group:
        if inst["slug"] == canonical["slug"]:
            continue
        if inst["slug"] in seen_slugs:
            continue
        seen_slugs.add(inst["slug"])

        similarity = cu.component_similarity(canonical["html"], inst["html"])
        differences = _describe_differences(canonical, inst)

        variants.append({
            "slug": inst["slug"],
            "similarity": round(similarity, 3),
            "differences": differences,
            "node_count": inst["node_count"],
        })

    # Sort by similarity descending
    variants.sort(key=lambda v: -v["similarity"])
    return variants


def _describe_differences(canonical: dict, variant: dict) -> str:
    """Generate a human-readable description of differences between two component versions."""
    diffs = []

    # Node count difference
    node_diff = variant["node_count"] - canonical["node_count"]
    if node_diff < -2:
        diffs.append(f"{abs(node_diff)} fewer DOM nodes")
    elif node_diff > 2:
        diffs.append(f"{node_diff} more DOM nodes")

    # Text content differences
    canon_text = canonical["text"]
    var_text = variant["text"]
    if canon_text != var_text:
        # Find missing/added text fragments
        canon_words = set(canon_text.lower().split())
        var_words = set(var_text.lower().split())
        missing = canon_words - var_words
        added = var_words - canon_words

        # Filter noise (single chars, numbers)
        missing = {w for w in missing if len(w) > 2 and not w.isdigit()}
        added = {w for w in added if len(w) > 2 and not w.isdigit()}

        if missing and len(missing) <= 5:
            diffs.append(f"Missing text: {', '.join(sorted(missing)[:3])}")
        if added and len(added) <= 5:
            diffs.append(f"Added text: {', '.join(sorted(added)[:3])}")

    # Class differences
    canon_classes = set(cu._extract_all_classes(canonical["html"]))
    var_classes = set(cu._extract_all_classes(variant["html"]))
    class_diff = canon_classes.symmetric_difference(var_classes)
    if class_diff and len(class_diff) <= 8:
        diffs.append(f"Different classes: {len(class_diff)} changed")

    if not diffs:
        # Structure check
        if canonical["signature"] != variant.get("signature", ""):
            diffs.append("Different DOM structure")
        else:
            diffs.append("Minor text/style differences")

    return "; ".join(diffs)


def _truncate_html(html: str, max_len: int) -> str:
    """Truncate HTML to max_len chars, trying to close at a tag boundary."""
    if len(html) <= max_len:
        return html

    truncated = html[:max_len]
    # Try to close at the last complete tag
    last_close = truncated.rfind(">")
    if last_close > max_len * 0.7:
        truncated = truncated[:last_close + 1]

    return truncated + "<!-- truncated -->"


# ─── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python detect_components.py /path/to/assets/", file=sys.stderr)
        sys.exit(1)

    assets = Path(sys.argv[1]).resolve()
    if not assets.is_dir():
        print(f"Error: '{assets}' is not a directory.", file=sys.stderr)
        sys.exit(1)

    threshold = float(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_SIMILARITY_THRESHOLD

    result = detect_shared_components(assets, threshold)
    if not result:
        print("No shared components detected.", file=sys.stderr)
        sys.exit(0)

    print(json.dumps(result, ensure_ascii=False, indent=2))
    comp_count = sum(1 for v in result.values() if v["found_in"] >= MIN_SHARED_SCREENS)
    print(f"\n--- {comp_count} shared component type(s) detected ---", file=sys.stderr)
