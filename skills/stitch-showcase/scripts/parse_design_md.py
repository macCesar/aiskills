"""
parse_design_md.py — Extracts metadata from DESIGN.md for stitch-showcase.

Usage:
    python parse_design_md.py /path/to/DESIGN.md
    → prints JSON with project_name, type, lang, colors, color_tokens, default_theme, font_family, screens, sections
"""
import re
import sys
import json
from pathlib import Path

# Ensure sibling modules resolve when this file is invoked directly.
sys.path.insert(0, str(Path(__file__).parent))
from slug_demangle import slug_to_title


SPANISH_STOPWORDS = {
    "de", "el", "la", "los", "las", "para", "con", "por", "una", "uno",
    "del", "que", "es", "se", "su", "sus", "como", "más", "muy", "este",
    "esta", "estos", "estas", "pantalla", "pantallas", "aplicación",
    "aplicacion", "usuario", "usuarios", "diseño", "diseno", "móvil",
    "movil", "perfil", "configuración", "configuracion",
}


def parse(design_md_path: str) -> dict:
    path = Path(design_md_path)
    if not path.exists():
        return {
            "project_name": "",
            "type": "unknown",
            "lang": "en",
            "colors": {},
            "color_tokens": {},
            "default_theme": "light",
            "font_family": None,
            "screens": [],
            "sections": [],
        }

    text = path.read_text(encoding="utf-8")
    frontmatter = _parse_yaml_frontmatter(text)
    lang = _extract_lang_override(text) or _detect_lang(text)
    colors = _extract_colors(text)
    color_tokens = _extract_color_tokens(text)

    # Frontmatter fills in fields the Markdown body doesn't define.
    if not colors and frontmatter.get("colors"):
        colors = dict(frontmatter["colors"])
    if not color_tokens and frontmatter.get("colors"):
        color_tokens = _semantic_tokens_from_dict(frontmatter["colors"])

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

    # Merge inline titles and descriptions from sections into the screens list.
    # Sections can contain "- slug: Title | Description" or "- slug: description"
    # entries that _extract_screens misses when slugs are only listed under ### headers.
    section_titles = {}
    section_descs = {}
    for sec in sections:
        for slug, title in sec.get("titles", {}).items():
            section_titles[slug] = title
        for slug, desc in sec.get("descriptions", {}).items():
            section_descs[slug] = desc

    if section_titles or section_descs:
        existing_slugs = {s["slug"] for s in screens}
        # Apply titles/descriptions to screens already in the list
        for s in screens:
            slug = s["slug"]
            if not s.get("title") or s["title"] == slug_to_title(slug):
                if slug in section_titles:
                    s["title"] = section_titles[slug]
            if not s.get("description") and slug in section_descs:
                s["description"] = section_descs[slug]
        # Add slugs that only appear inside sections (not in the flat screen list)
        for sec in sections:
            for slug in sec["slugs"]:
                if slug not in existing_slugs:
                    screens.append({
                        "slug": slug,
                        "title": section_titles.get(slug) or slug_to_title(slug),
                        "description": section_descs.get(slug, ""),
                    })
                    existing_slugs.add(slug)

    project_name = _extract_project_name(text) or frontmatter.get("name", "")
    font_family = _extract_typography(text) or frontmatter.get("font_family")

    return {
        "project_name": project_name,
        "type": _detect_type(text),
        "lang": lang,
        "colors": colors,
        "color_tokens": color_tokens,
        "default_theme": default_theme,
        "font_family": font_family,
        "screens": screens,
        "sections": sections,
    }


def _parse_yaml_frontmatter(text: str) -> dict:
    """
    Parse a Stitch-style YAML frontmatter at the top of DESIGN.md.

    Recognizes (everything else is ignored):
      - top-level ``name:`` → ``"name"``
      - ``colors:`` block with hex values → ``"colors"`` dict
      - ``typography:`` block — returns the first ``fontFamily`` → ``"font_family"``

    Returns an empty dict if no frontmatter delimiter is present.
    """
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not m:
        return {}
    fm = m.group(1)
    result: dict = {}

    # name: <value>
    name_m = re.search(r"^name:\s*(.+?)\s*$", fm, re.MULTILINE)
    if name_m:
        val = name_m.group(1).strip().strip("'\"")
        if val:
            result["name"] = val

    # colors: block — collect indented "key: '#hex'" pairs until indentation drops.
    colors_m = re.search(r"^colors:\s*\n((?:[ \t]+\S.*\n?)+)", fm, re.MULTILINE)
    if colors_m:
        colors: dict = {}
        for line in colors_m.group(1).splitlines():
            cm = re.match(
                r"^\s+([a-z][a-z0-9\-]*):\s*['\"]?(#[0-9A-Fa-f]{3,8})['\"]?\s*$",
                line,
            )
            if cm:
                colors[cm.group(1).lower()] = "#" + cm.group(2).lstrip("#").upper()
        if colors:
            result["colors"] = colors

    # typography: pick the first fontFamily declared anywhere in the block.
    typo_m = re.search(r"fontFamily:\s*['\"]?([^'\"\n,]+)['\"]?", fm)
    if typo_m:
        font = typo_m.group(1).strip().rstrip(",;")
        if font:
            result["font_family"] = font

    return result


def _semantic_tokens_from_dict(colors: dict) -> dict:
    """
    Compute `accent` / `surface` semantic tokens from a flat color dict.

    Mirrors the rules used by :func:`_extract_color_tokens`:
      - ``accent``  → first key containing ``primary`` (not ``on-primary``)
      - ``surface`` → first key named ``surface`` or containing ``background``/``bg``
    """
    tokens = dict(colors)
    for name, val in colors.items():
        if "primary" in name and not name.startswith("on-"):
            tokens["accent"] = val
            break
    for name, val in colors.items():
        if name == "surface" or "background" in name or name == "bg":
            tokens["surface"] = val
            break
    return tokens


def _extract_project_name(text: str) -> str:
    """First H1 heading in the document."""
    m = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    return m.group(1).strip() if m else ""


def _extract_lang_override(text: str) -> str | None:
    """
    Explicit override via ``## Lang`` (or ``## Language``) section in DESIGN.md.

    Expected format:
        ## Lang
        es

    Returns a BCP-47-ish code (``es``, ``en``, ``pt-BR``…) or None if absent.
    """
    m = re.search(
        r"^##\s+Lang(?:uage)?\s*\n\s*([A-Za-z]{2}(?:-[A-Za-z]{2,4})?)\s*$",
        text, re.IGNORECASE | re.MULTILINE
    )
    if not m:
        return None
    raw = m.group(1)
    # Normalize: language subtag lowercase, region subtag uppercase (BCP-47).
    if "-" in raw:
        lang, region = raw.split("-", 1)
        return f"{lang.lower()}-{region.upper()}"
    return raw.lower()


def _detect_lang(text: str) -> str:
    """
    Heuristic language detection. Distinguishes Spanish from everything else.

    Signals:
      - Spanish-only accented characters (á é í ó ú ñ ü).
      - Common Spanish stop words from SPANISH_STOPWORDS.

    Returns 'es' when either signal is present, else 'en'.
    """
    if not text:
        return "en"
    lower = text.lower()
    if re.search(r"[áéíóúñü]", lower):
        return "es"
    words = re.findall(r"[a-záéíóúñü]+", lower)
    stop_hits = sum(1 for w in words if w in SPANISH_STOPWORDS)
    return "es" if stop_hits >= 3 else "en"


def _detect_type(text: str) -> str:
    """Returns 'mobile', 'web', or 'unknown'.

    Priority:
    1. Explicit ``## Type`` section with 'mobile' or 'web' on the next line
    2. Keyword scoring across the full document
    """
    # 1. Explicit ## Type section — authoritative if present
    m = re.search(r"^##\s+Type\s*\n\s*(\S+)", text, re.MULTILINE | re.IGNORECASE)
    if m:
        val = m.group(1).strip().lower()
        if val in ("mobile", "web"):
            return val

    # 2. Keyword scoring fallback
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
        # Table rows must START with | (not bullet lines with "Title | Desc" format)
        if not re.match(r"^\s*\|", line) or re.match(r"^\s*\|[-\s|]+\|\s*$", line):
            continue
        cols = [c.strip() for c in line.split("|") if c.strip()]
        if len(cols) >= 2:
            slug = _to_slug(cols[0])
            title = cols[1] if len(cols) > 1 else slug_to_title(slug)
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
        # "1. slug_name - Description" or "- slug_name — Description" or "- slug: Title | Description"
        m = re.match(r"^\s*(?:\d+\.|[-*])\s+([a-zA-Z0-9_\-]+)\s*[-—:]\s*(.+)$", line)
        if m:
            slug = _to_slug(m.group(1))
            raw = m.group(2).strip()
            if " | " in raw:
                title_part, desc_part = raw.split(" | ", 1)
                title = title_part.strip()
                desc = desc_part.strip()
            else:
                title = slug_to_title(slug)
                desc = raw
            screens.append({"slug": slug, "title": title, "description": desc})

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
                    raw = m.group(2).strip()
                    # Support "Title | Description" format for mangled slugs
                    if " | " in raw:
                        title_part, desc_part = raw.split(" | ", 1)
                        current_section.setdefault("titles", {})[slug] = title_part.strip()
                        current_section.setdefault("descriptions", {})[slug] = desc_part.strip()
                    else:
                        current_section.setdefault("descriptions", {})[slug] = raw

    return sections


def _to_slug(s: str) -> str:
    """Normalize to snake_case slug."""
    s = s.strip().lower()
    s = re.sub(r"[\s\-]+", "_", s)
    s = re.sub(r"[^a-z0-9_]", "", s)
    return s


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python parse_design_md.py /path/to/DESIGN.md", file=sys.stderr)
        sys.exit(1)
    result = parse(sys.argv[1])
    print(json.dumps(result, ensure_ascii=False, indent=2))
