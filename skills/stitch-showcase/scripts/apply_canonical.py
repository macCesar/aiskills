"""
apply_canonical.py — Replace component variants with a canonical version across screens.

Reads the canonical component from a source screen HTML and replaces matching
components in target screen HTMLs. Supports both structural (navbar, footer, etc.)
and atomic (buttons, inputs, etc.) components.

Uses only stdlib. No external dependencies.

Usage:
    # As a module (from AI agent):
    from apply_canonical import apply_canonical

    # Standalone:
    python apply_canonical.py /path/to/assets/ navbar home_screen
    python apply_canonical.py /path/to/assets/ button home_screen --targets screen1 screen2
"""
import re
import sys
import json
from pathlib import Path

# Sibling import
sys.path.insert(0, str(Path(__file__).parent))
import component_utils as cu

# Structural component types handled by semantic block extraction
STRUCTURAL_TYPES = {"navbar", "navbars", "header", "headers", "footer", "footers",
                    "sidebar", "sidebars", "tabbar", "tabbars"}

# Map plural type names to singular for semantic block lookup
_TYPE_SINGULAR = {
    "navbars": "navbar", "headers": "header", "footers": "footer",
    "sidebars": "sidebar", "tabbars": "tabbar",
}


def apply_canonical(
    assets_dir: Path,
    component_type: str,
    canonical_slug: str,
    target_slugs: list = None,
) -> dict:
    """
    Replace component variants in target HTMLs with the canonical version.

    Args:
        assets_dir: Directory containing screen .html files
        component_type: Component type (e.g., "navbar", "footer", "button")
        canonical_slug: Screen slug to use as the canonical source
        target_slugs: List of screen slugs to update. If None, updates all
                      screens that have this component (except the canonical).

    Returns:
        Dict mapping slug → status: "replaced", "skipped", "not_found", or "error"
    """
    assets_dir = Path(assets_dir).resolve()
    canonical_path = assets_dir / f"{canonical_slug}.html"

    if not canonical_path.exists():
        return {"_error": f"Canonical screen '{canonical_slug}' not found"}

    canonical_html = canonical_path.read_text(encoding="utf-8", errors="replace")

    # Normalize type name
    comp_type = _TYPE_SINGULAR.get(component_type.lower(), component_type.lower())

    if comp_type in {v for v in _TYPE_SINGULAR.values()}:
        return _apply_structural(assets_dir, comp_type, canonical_html,
                                 canonical_slug, target_slugs)
    else:
        return _apply_atomic(assets_dir, comp_type, canonical_html,
                             canonical_slug, target_slugs)


def _apply_structural(
    assets_dir: Path,
    comp_type: str,
    canonical_html: str,
    canonical_slug: str,
    target_slugs: list = None,
) -> dict:
    """Replace structural components (navbar, footer, etc.) in target screens."""
    # Extract the canonical component block
    canonical_blocks = cu.extract_semantic_blocks(canonical_html)
    if comp_type not in canonical_blocks or not canonical_blocks[comp_type]:
        return {"_error": f"No {comp_type} found in canonical screen '{canonical_slug}'"}

    # Use the first (usually only) block as the canonical version
    canon_block = canonical_blocks[comp_type][0]

    # Determine target files
    html_files = sorted(assets_dir.glob("*.html"))
    results = {}

    for html_path in html_files:
        slug = html_path.stem
        if slug == canonical_slug:
            continue
        if target_slugs and slug not in target_slugs:
            continue

        try:
            html = html_path.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            results[slug] = f"error: {e}"
            continue

        # Find the matching component block in this screen
        target_blocks = cu.extract_semantic_blocks(html)
        if comp_type not in target_blocks or not target_blocks[comp_type]:
            results[slug] = "not_found"
            continue

        # Replace each matching block with the canonical version
        updated = html
        replaced = False
        for target_block in target_blocks[comp_type]:
            if target_block in updated:
                updated = updated.replace(target_block, canon_block, 1)
                replaced = True

        if replaced and updated != html:
            html_path.write_text(updated, encoding="utf-8")
            results[slug] = "replaced"
        else:
            results[slug] = "skipped"

    return results


def _apply_atomic(
    assets_dir: Path,
    comp_type: str,
    canonical_html: str,
    canonical_slug: str,
    target_slugs: list = None,
) -> dict:
    """
    Replace atomic components (buttons, inputs, etc.) in target screens.

    Uses the component catalog JSON to find cluster members, then replaces
    matching snippets in each target screen.
    """
    # Try to load catalog for cluster info
    catalog_path = assets_dir.parent / "component_catalog.json"
    catalog = {}
    if catalog_path.exists():
        try:
            catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        except Exception:
            pass

    # Find the canonical component snippet from catalog clusters
    plural_type = f"{comp_type}s"
    clusters = catalog.get("clusters", {}).get(plural_type, [])

    # Find cluster where canonical_slug is in the canonical's found_in
    target_cluster = None
    canon_snippet = None

    for cluster in clusters:
        canonical = cluster.get("canonical", {})
        if canonical_slug in canonical.get("found_in", []):
            target_cluster = cluster
            canon_snippet = canonical.get("html", "")
            break

    if not canon_snippet:
        return {"_error": f"No {comp_type} cluster found with canonical from '{canonical_slug}'. "
                f"Run build first to generate component_catalog.json."}

    # Collect target slugs from cluster variants
    variant_snippets = {}
    for v in target_cluster.get("variants", []):
        for slug in v.get("found_in", []):
            if slug != canonical_slug:
                variant_snippets[slug] = v.get("html", "")

    html_files = sorted(assets_dir.glob("*.html"))
    results = {}

    for html_path in html_files:
        slug = html_path.stem
        if slug == canonical_slug:
            continue
        if target_slugs and slug not in target_slugs:
            continue
        if slug not in variant_snippets:
            continue

        try:
            html = html_path.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            results[slug] = f"error: {e}"
            continue

        old_snippet = variant_snippets[slug]
        if old_snippet and old_snippet in html:
            updated = html.replace(old_snippet, canon_snippet, 1)
            html_path.write_text(updated, encoding="utf-8")
            results[slug] = "replaced"
        else:
            results[slug] = "not_found"

    return results


# ─── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Replace component variants with a canonical version."
    )
    parser.add_argument("assets_dir", help="Directory containing screen .html files")
    parser.add_argument("component_type", help="Component type (navbar, footer, button, etc.)")
    parser.add_argument("canonical_slug", help="Screen slug to use as canonical source")
    parser.add_argument("--targets", nargs="*", help="Specific screen slugs to update (default: all)")
    args = parser.parse_args()

    assets = Path(args.assets_dir).resolve()
    if not assets.is_dir():
        print(f"Error: '{assets}' is not a directory.", file=sys.stderr)
        sys.exit(1)

    result = apply_canonical(assets, args.component_type, args.canonical_slug, args.targets)

    if "_error" in result:
        print(f"Error: {result['_error']}", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(result, ensure_ascii=False, indent=2))

    replaced = sum(1 for v in result.values() if v == "replaced")
    total = len(result)
    print(f"\n--- {replaced}/{total} screens updated ---", file=sys.stderr)
