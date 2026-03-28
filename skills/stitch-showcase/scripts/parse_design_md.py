"""
parse_design_md.py — Extracts metadata from DESIGN.md for stitch-showcase.

Usage:
    python parse_design_md.py /path/to/DESIGN.md
    → prints JSON with project_name, type, colors, color_tokens, default_theme, font_family, screens, sections
"""
import re
import sys
import json
from pathlib import Path


def parse(design_md_path: str) -> dict:
    path = Path(design_md_path)
    if not path.exists():
        return {
            "project_name": "",
            "type": "unknown",
            "colors": {},
            "color_tokens": {},
            "default_theme": "light",
            "font_family": None,
            "screens": [],
            "sections": [],
        }

    text = path.read_text(encoding="utf-8")
    colors = _extract_colors(text)
    color_tokens = _extract_color_tokens(text)

    # Determine default_theme from surface token
    surface_hex = color_tokens.get("surface") or color_tokens.get("background")
    if not surface_hex:
        # fall back to colors dict
        for key in ("surface", "background", "bg"):
            if key in colors:
                surface_hex = colors[key]
                break
    default_theme = _surface_default_theme(surface_hex) if surface_hex else "light"

    screens = _extract_screens(text)
    sections = _extract_sections(text)

    # Merge inline descriptions from sections into the screens list.
    # Sections can contain "- slug: description" entries that _extract_screens
    # misses when slugs are only listed under ### headers (no flat list).
    section_descs = {}
    for sec in sections:
        for slug, desc in sec.get("descriptions", {}).items():
            section_descs[slug] = desc

    if section_descs:
        existing_slugs = {s["slug"] for s in screens}
        # Apply section descriptions to screens already in the list
        for s in screens:
            if not s.get("description") and s["slug"] in section_descs:
                s["description"] = section_descs[s["slug"]]
        # Add slugs that only appear inside sections (not in the flat screen list)
        for sec in sections:
            for slug in sec["slugs"]:
                if slug not in existing_slugs:
                    screens.append({
                        "slug": slug,
                        "title": _slug_to_title(slug),
                        "description": section_descs.get(slug, ""),
                    })
                    existing_slugs.add(slug)

    return {
        "project_name": _extract_project_name(text),
        "type": _detect_type(text),
        "colors": colors,
        "color_tokens": color_tokens,
        "default_theme": default_theme,
        "font_family": _extract_typography(text),
        "screens": screens,
        "sections": sections,
    }


def _extract_project_name(text: str) -> str:
    """First H1 heading in the document."""
    m = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    return m.group(1).strip() if m else ""


def _detect_type(text: str) -> str:
    """Returns 'mobile', 'web', or 'unknown' based on keywords."""
    lower = text.lower()
    mobile_keywords = ["móvil", "movil", "mobile", "ios", "android", "app móvil", "aplicación móvil"]
    web_keywords = ["web", "dashboard", "escritorio", "desktop", "browser", "navegador"]

    mobile_score = sum(1 for kw in mobile_keywords if kw in lower)
    web_score = sum(1 for kw in web_keywords if kw in lower)

    if mobile_score > web_score:
        return "mobile"
    if web_score > mobile_score:
        return "web"
    return "unknown"


def _extract_colors(text: str) -> dict:
    """Extract name:value pairs from the colors section."""
    colors = {}
    color_section = re.search(
        r"##\s+(?:Colores?|Colors?)\s*\n(.*?)(?=\n##|\Z)",
        text, re.IGNORECASE | re.DOTALL
    )
    if not color_section:
        return colors

    for line in color_section.group(1).splitlines():
        # Formats: "- Primary: #FDD900" or "Primary: #FDD900"
        m = re.search(r"[-*]?\s*(.+?):\s*(#[0-9A-Fa-f]{3,8}|rgb\(.+?\)|[a-z]+)\s*$", line, re.IGNORECASE)
        if m:
            key = m.group(1).strip().lower()
            val = m.group(2).strip()
            colors[key] = val

    return colors


def _extract_color_tokens(text: str) -> dict:
    """
    Extract semantic color tokens in Stitch DESIGN.md format.

    Matches: `token-name` (#XXXXXX) or token-name (#XXXXXX)
    Returns dict with semantic roles:
      accent  → first token containing 'primary' (not 'on-primary')
      surface → first token named 'surface' or containing 'background'/'bg'
      + all raw tokens by name
    """
    tokens = {}

    # Match backtick-wrapped: `token-name` (#XXXXXX)
    for m in re.finditer(r"`([a-z][a-z0-9\-]+)`\s*\(#([0-9A-Fa-f]{6})\)", text, re.IGNORECASE):
        tokens[m.group(1).lower()] = "#" + m.group(2).upper()

    # Match bare: token-name (#XXXXXX)  (only if not already captured)
    for m in re.finditer(r"\b([a-z][a-z0-9\-]+)\s*\(#([0-9A-Fa-f]{6})\)", text, re.IGNORECASE):
        key = m.group(1).lower()
        if key not in tokens:
            tokens[key] = "#" + m.group(2).upper()

    # Build semantic roles
    result = dict(tokens)  # copy all raw tokens

    # accent: first 'primary' token that isn't 'on-primary'
    for name, val in tokens.items():
        if "primary" in name and not name.startswith("on-"):
            result["accent"] = val
            break

    # surface: 'surface' or 'background'/'bg'
    for name, val in tokens.items():
        if name == "surface" or "background" in name or name == "bg":
            result["surface"] = val
            break

    return result


def _surface_default_theme(surface_hex: str) -> str:
    """
    Determine showcase default theme from app surface color luminance.

    Dark app surface → use light showcase (for contrast).
    Light app surface → use dark showcase (for contrast).
    """
    hex_clean = surface_hex.lstrip("#")
    if len(hex_clean) != 6:
        return "light"
    try:
        r = int(hex_clean[0:2], 16)
        g = int(hex_clean[2:4], 16)
        b = int(hex_clean[4:6], 16)
    except ValueError:
        return "light"

    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    if luminance < 100:
        return "light"   # dark app → light showcase
    if luminance > 155:
        return "dark"    # light app → dark showcase
    return "light"


def _extract_typography(text: str) -> str | None:
    """
    Extract primary font family name from the Typography section of DESIGN.md.

    Returns font name (e.g. 'Inter') or None if not found.
    """
    # Look for ## Typography or ## N. Typography section
    typo_section = re.search(
        r"##\s+(?:\d+\.\s+)?Typography\s*\n(.*?)(?=\n##|\Z)",
        text, re.IGNORECASE | re.DOTALL
    )

    UI_LABELS = {"display", "headline", "title", "body", "label", "bold", "regular", "medium", "semibold"}

    if typo_section:
        section_text = typo_section.group(1)
        # Look for bold text **FontName** in first few lines
        for line in section_text.splitlines()[:6]:
            m = re.search(r"\*\*([A-Z][a-zA-Z\s\+]+)\*\*", line)
            if m:
                candidate = m.group(1).strip()
                words = candidate.split()
                # Font names are 1-3 words, not UI labels
                if 1 <= len(words) <= 3 and words[0].lower() not in UI_LABELS:
                    return candidate

        # Broader search in full section
        for m in re.finditer(r"\*\*([A-Z][a-zA-Z\s\+]+)\*\*", section_text):
            candidate = m.group(1).strip()
            words = candidate.split()
            if 1 <= len(words) <= 3 and words[0].lower() not in UI_LABELS:
                return candidate

    # Fallback: search entire doc for font-family
    m = re.search(r"font-family:\s*[\"']?([A-Z][a-zA-Z\s]+)[\"']?", text)
    if m:
        candidate = m.group(1).strip().rstrip(",;")
        if candidate:
            return candidate

    return None


def _extract_screens(text: str) -> list:
    """
    Extract screen list with slug, title, description.

    Supported formats:
    1. Markdown table: | slug | title | description |
    2. Numbered list:  1. splash_screen - Description
    3. Bullet list:    - splash_screen — Description
    4. Simple pair:    splash_screen: Description
    """
    # Attempt 1: markdown table
    table_screens = _parse_table(text)
    if table_screens:
        return table_screens

    # Attempt 2: numbered or bullet list inside a Screens section
    list_screens = _parse_screen_list(text)
    if list_screens:
        return list_screens

    return []


def _parse_table(text: str) -> list:
    """Parse markdown table with slug/title/description columns."""
    section = re.search(
        r"##\s+(?:Pantallas?|Screens?)\s*\n(.*?)(?=\n##|\Z)",
        text, re.IGNORECASE | re.DOTALL
    )
    if not section:
        return []

    section_text = section.group(1)
    rows = []

    for line in section_text.splitlines():
        # Table rows: | col1 | col2 | col3 |
        if "|" not in line or re.match(r"^\s*\|[-\s|]+\|\s*$", line):
            continue
        cols = [c.strip() for c in line.split("|") if c.strip()]
        if len(cols) >= 2:
            slug = _to_slug(cols[0])
            title = cols[1] if len(cols) > 1 else _slug_to_title(slug)
            desc = cols[2] if len(cols) > 2 else ""
            rows.append({"slug": slug, "title": title, "description": desc})

    # Skip header row if it contains "slug", "screen", etc.
    if rows and rows[0]["slug"] in ("slug", "pantalla", "screen", "nombre", "name"):
        rows = rows[1:]

    return rows


def _parse_screen_list(text: str) -> list:
    """Parse numbered or bullet lists of screens."""
    section = re.search(
        r"##\s+(?:Pantallas?|Screens?)\s*\n(.*?)(?=\n##|\Z)",
        text, re.IGNORECASE | re.DOTALL
    )
    if not section:
        return []

    screens = []
    for line in section.group(1).splitlines():
        # "1. slug_name - Description" or "- slug_name — Description"
        m = re.match(r"^\s*(?:\d+\.|[-*])\s+([a-zA-Z0-9_\-]+)\s*[-—:]\s*(.+)$", line)
        if m:
            slug = _to_slug(m.group(1))
            desc = m.group(2).strip()
            screens.append({
                "slug": slug,
                "title": _slug_to_title(slug),
                "description": desc,
            })

    return screens


def _extract_sections(text: str) -> list:
    """
    Extract sections with their screen slugs if defined in DESIGN.md.

    Expected format:
    ### Onboarding
    - splash_screen
    - login
    """
    sections = []
    section_block = re.search(
        r"##\s+(?:Pantallas?|Screens?)\s*\n(.*?)(?=\n##\s+(?!#)|\Z)",
        text, re.IGNORECASE | re.DOTALL
    )
    if not section_block:
        return []

    content = section_block.group(1)
    current_section = None

    for line in content.splitlines():
        h3 = re.match(r"^###\s+(.+)$", line)
        if h3:
            current_section = {"name": h3.group(1).strip(), "slugs": []}
            sections.append(current_section)
            continue

        if current_section:
            m = re.match(r"^\s*[-*\d.]+\s*([a-zA-Z0-9_\-]+)\s*(?:[-—:]\s*(.+))?$", line)
            if m:
                slug = _to_slug(m.group(1))
                current_section["slugs"].append(slug)
                if m.group(2):
                    current_section.setdefault("descriptions", {})[slug] = m.group(2).strip()

    return sections


def _to_slug(s: str) -> str:
    """Normalize to snake_case slug."""
    s = s.strip().lower()
    s = re.sub(r"[\s\-]+", "_", s)
    s = re.sub(r"[^a-z0-9_]", "", s)
    return s


def _slug_to_title(slug: str) -> str:
    """splash_screen → 'Splash Screen'"""
    return slug.replace("_", " ").replace("-", " ").title()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python parse_design_md.py /path/to/DESIGN.md", file=sys.stderr)
        sys.exit(1)
    result = parse(sys.argv[1])
    print(json.dumps(result, ensure_ascii=False, indent=2))
