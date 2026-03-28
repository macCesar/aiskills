"""
build_showcase.py — Main orchestrator for stitch-showcase.

Generates a navigable showcase (index.html + viewer.html) from
Google Stitch exports (zips containing code.html + screen.png).

Usage:
    python build_showcase.py /path/to/folder-with-zips
    python build_showcase.py /path/to/folder-with-zips --type mobile
    python build_showcase.py /path/to/folder-with-zips --type web
    python build_showcase.py /path/to/folder-with-zips --name "My App" --type mobile
    python build_showcase.py /path/to/folder-with-zips --watch
    python build_showcase.py /path/to/folder-with-zips --init
"""
import sys
import re
import json
import time
import shutil
import hashlib
import argparse
from pathlib import Path
from html import escape

# Locate sibling scripts and references
SCRIPTS_DIR = Path(__file__).parent
REFERENCES_DIR = SCRIPTS_DIR.parent / "references"

sys.path.insert(0, str(SCRIPTS_DIR))
import extract_zips
import parse_design_md


def _extract_source_zip(zip_path: Path) -> Path:
    """
    Extract a Stitch mega-zip and return the path to use as source.

    Handles two layouts:
      A) zip contains individual screen folders at the root
         → extract next to the zip, use extraction root
      B) zip contains a single parent folder (stitch/) with screen subfolders inside
         → return that single parent folder
      C) zip contains a flat code.html + screen.png (single screen)
         → return the extraction folder as-is
    """
    import zipfile

    dest = zip_path.parent / zip_path.stem
    dest.mkdir(exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(dest)

    # If extraction produced a single subdirectory, descend into it
    children = [c for c in dest.iterdir() if not c.name.startswith(".")]
    if len(children) == 1 and children[0].is_dir():
        inner = children[0]
        # Check if DESIGN.md is nested one level deeper (e.g. stitch/snap_kinetic/DESIGN.md)
        nested_design = [d for d in inner.rglob("DESIGN.md") if d.parent != inner]
        if nested_design:
            # Promote the first nested DESIGN.md to the inner folder level
            promoted = inner / "DESIGN.md"
            if not promoted.exists():
                import shutil as _shutil
                _shutil.copy2(nested_design[0], promoted)
                print(f"  ℹ DESIGN.md promoted from {nested_design[0].parent.name}/")
        print(f"  ℹ Mega-zip extracted → using {inner}")
        return inner

    print(f"  ℹ Zip extracted → using {dest}")
    return dest


def build(source_dir: str, project_type: str = None, project_name: str = None) -> Path:
    """
    Build the complete showcase.

    Args:
        source_dir: Folder containing Stitch zips
        project_type: 'mobile' or 'web' (auto-detected if None)
        project_name: Project name (extracted from DESIGN.md if None)

    Returns:
        Path to the generated output directory.
    """
    source = Path(source_dir).resolve()
    if not source.exists():
        print(f"Error: '{source}' does not exist.", file=sys.stderr)
        sys.exit(1)

    # If a zip file was passed directly, auto-extract it
    if source.suffix == ".zip":
        source = _extract_source_zip(source)

    print(f"\n📁 Source: {source}")

    # 1. Parse DESIGN.md
    design_md = source / "DESIGN.md"
    metadata = parse_design_md.parse(str(design_md)) if design_md.exists() else {}

    if project_name:
        metadata["project_name"] = project_name
    if not metadata.get("project_name"):
        metadata["project_name"] = source.name.replace("_", " ").replace("-", " ").title()

    if project_type:
        metadata["type"] = project_type
    if metadata.get("type", "unknown") == "unknown":
        print("⚠ Could not detect type (mobile/web). Defaulting to mobile.", file=sys.stderr)
        metadata["type"] = "mobile"

    ptype = metadata["type"]  # 'mobile' or 'web'
    print(f"📱 Type: {ptype} | Project: {metadata['project_name']}")

    # 2. Create output directory
    output_name = "showcase-mobile" if ptype == "mobile" else "showcase-web"
    output_dir = source.parent / output_name
    output_dir.mkdir(exist_ok=True)
    assets_dir = output_dir / "assets"
    assets_dir.mkdir(exist_ok=True)

    print(f"📂 Output: {output_dir}")

    # 3. Extract zips and copy assets
    print("\n🗜 Extracting screens...")
    screens_raw = extract_zips.extract_all(str(source), str(assets_dir))

    if not screens_raw:
        print("Error: no screens found (no zips or folders with code.html).", file=sys.stderr)
        sys.exit(1)

    # 4. Enrich with DESIGN.md metadata
    screens = _enrich_screens(screens_raw, metadata, source)

    print(f"\n✅ {len(screens)} screens processed")

    # 5. Copy DESIGN.md if present
    if design_md.exists():
        shutil.copy2(design_md, output_dir / "DESIGN.md")

    # 6. Generate viewer.html
    _generate_viewer(output_dir, ptype, metadata, screens)

    # 7. Generate index.html
    _generate_index(output_dir, ptype, metadata, screens)

    print(f"\n🎉 Showcase ready: {output_dir}/index.html\n")
    return output_dir


def _enrich_screens(screens_raw: list, metadata: dict, source: Path) -> list:
    """Add title and description to each screen from DESIGN.md or inferred."""
    design_screens = {s["slug"]: s for s in metadata.get("screens", [])}

    enriched = []
    for raw in screens_raw:
        slug = raw["slug"]
        design = design_screens.get(slug, {})

        # Title
        title = design.get("title") or _slug_to_title(slug)

        # Description priority: DESIGN.md → individual .md → meta/h1/title/visible body text → ""
        desc = design.get("description") or ""
        if not desc:
            desc = _read_md_desc(slug, source)
        if not desc:
            desc = _read_html_title(raw.get("html_path", ""))

        enriched.append({
            "slug": slug,
            "title": title,
            "description": desc,
            "html_file": f"assets/{slug}.html",
            "png_file": f"assets/{slug}.png" if raw.get("png_path") else None,
        })

    return enriched


def _read_md_desc(slug: str, source: Path) -> str:
    """Look for an individual .md file with the screen description."""
    for md_file in source.glob("*.md"):
        if md_file.name == "DESIGN.md":
            continue
        name_slug = re.sub(r"^[\d\-_]+", "", md_file.stem.lower())
        name_slug = re.sub(r"[\s\-]+", "_", name_slug)
        if name_slug == slug or md_file.stem.lower().replace("-", "_") == slug:
            text = md_file.read_text(encoding="utf-8").strip()
            # First non-empty line that is not a heading
            for line in text.splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    return line
    return ""


def _read_html_title(html_path: str) -> str:
    """
    Extract a description from a Stitch HTML file.

    Priority:
    1. <meta name="description"> or <meta property="og:description">
    2. First visible <h1> or <h2> text
    3. <title> tag (skipped if generic/filename-like)
    4. First meaningful visible text found in the body
       (strips <script>, <style>, <svg>; colects short readable phrases)
    """
    if not html_path:
        return ""
    try:
        text = Path(html_path).read_text(encoding="utf-8", errors="ignore")

        # 1. <meta name="description" content="...">
        m = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']', text, re.IGNORECASE)
        if not m:
            m = re.search(r'<meta[^>]+content=["\'](.*?)["\'][^>]+name=["\']description["\']', text, re.IGNORECASE)
        if m:
            val = m.group(1).strip()
            if val:
                return val

        # 2. <meta property="og:description" content="...">
        m = re.search(r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\'](.*?)["\']', text, re.IGNORECASE)
        if not m:
            m = re.search(r'<meta[^>]+content=["\'](.*?)["\'][^>]+property=["\']og:description["\']', text, re.IGNORECASE)
        if m:
            val = m.group(1).strip()
            if val:
                return val

        # Isolate <body> for remaining checks
        body_m = re.search(r"<body[^>]*>(.*)", text, re.IGNORECASE | re.DOTALL)
        body = body_m.group(1) if body_m else text

        # 3. First visible <h1> or <h2>
        m = re.search(r"<h[12][^>]*>(.*?)</h[12]>", body, re.IGNORECASE | re.DOTALL)
        if m:
            val = re.sub(r"<[^>]+>", "", m.group(1)).strip()
            if val and len(val) < 120:
                return val

        # 4. <title> tag — only accept non-generic values
        m = re.search(r"<title[^>]*>(.+?)</title>", text, re.IGNORECASE | re.DOTALL)
        if m:
            val = re.sub(r"<[^>]+>", "", m.group(1)).strip()
            # Skip if it looks like a filename, generic placeholder, or "Untitled"
            if val and not re.match(r"^(untitled|index|screen|page|document|\d+)$", val, re.IGNORECASE):
                return val

        # 5. First meaningful visible text in body (Stitch HTML often has no title/h1)
        visible = _extract_body_text(body)
        if visible:
            return visible

    except Exception:
        pass
    return ""


def _extract_body_text(body_html: str) -> str:
    """
    Extract the first short, readable phrase from Stitch HTML body content.

    Strips <script>, <style>, <svg>, <noscript> blocks entirely, then
    collects text nodes and returns the first phrase that looks like
    real UI text (3–100 chars, not pure numbers/punctuation).
    """
    # Remove non-visible blocks
    cleaned = re.sub(
        r"<(script|style|svg|noscript|defs|symbol)[^>]*>.*?</\1>",
        " ", body_html, flags=re.IGNORECASE | re.DOTALL
    )
    # Strip remaining tags
    cleaned = re.sub(r"<[^>]+>", " ", cleaned)
    # Decode common HTML entities
    for entity, char in [("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"),
                          ("&nbsp;", " "), ("&#39;", "'"), ("&quot;", '"')]:
        cleaned = cleaned.replace(entity, char)
    # Normalize whitespace
    cleaned = re.sub(r"[ \t]+", " ", cleaned)

    # Split into candidate phrases on common delimiters or line breaks
    candidates = re.split(r"[\n\r|•·/\\]+", cleaned)
    for phrase in candidates:
        phrase = phrase.strip()
        # Accept phrases that are 3–100 chars and contain at least one letter
        if 3 <= len(phrase) <= 100 and re.search(r"[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ]", phrase):
            # Skip if it's all caps single word (likely a CSS class leak or constant)
            if re.match(r"^[A-Z_]{2,}$", phrase):
                continue
            return phrase

    return ""


def _generate_viewer(output_dir: Path, ptype: str, metadata: dict, screens: list) -> None:
    """Generate viewer.html from the matching reference template."""
    template_name = "viewer-mobile.html" if ptype == "mobile" else "viewer-web.html"
    template_path = REFERENCES_DIR / template_name

    if not template_path.exists():
        print(f"  ⚠ Template not found: {template_path}", file=sys.stderr)
        _generate_viewer_fallback(output_dir, ptype, metadata)
        return

    template = template_path.read_text(encoding="utf-8")

    # Build screens JSON for prev/next navigation
    screens_data = [
        {"title": s["title"], "desc": s["description"], "html_file": s["html_file"]}
        for s in screens
    ]

    # Typography
    font = metadata.get("font_family")
    if font:
        font_link = (
            f'<link rel="preconnect" href="https://fonts.googleapis.com">\n'
            f'  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
            f'  <link href="https://fonts.googleapis.com/css2?family='
            f'{font.replace(" ", "+")}:wght@400;500;600;700&display=swap" rel="stylesheet">'
        )
    else:
        font_link = ""
    font_family = font or "system-ui"

    html = template
    html = html.replace("{{PROJECT_NAME}}", escape(metadata["project_name"]))
    html = html.replace("{{SCREENS_JSON}}", json.dumps(screens_data, ensure_ascii=False))
    html = html.replace("{{DEFAULT_THEME}}", metadata.get("default_theme", "light"))
    html = html.replace("{{FONT_LINK}}", font_link)
    html = html.replace("{{FONT_FAMILY}}", font_family)

    (output_dir / "viewer.html").write_text(html, encoding="utf-8")
    print("  ✓ viewer.html generated")


def _generate_index(output_dir: Path, ptype: str, metadata: dict, screens: list) -> None:
    """Generate index.html from the matching reference template."""
    template_name = "index-mobile.html" if ptype == "mobile" else "index-web.html"
    template_path = REFERENCES_DIR / template_name

    if not template_path.exists():
        print(f"  ⚠ Template not found: {template_path}", file=sys.stderr)
        _generate_index_fallback(output_dir, ptype, metadata, screens)
        return

    template = template_path.read_text(encoding="utf-8")

    sections_html, groups = _build_sections_html(screens, metadata, ptype)
    tabs_html = _section_tabs_html(groups)

    # Typography
    font = metadata.get("font_family")
    if font:
        font_link = (
            f'<link rel="preconnect" href="https://fonts.googleapis.com">\n'
            f'  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
            f'  <link href="https://fonts.googleapis.com/css2?family='
            f'{font.replace(" ", "+")}:wght@400;500;600;700&display=swap" rel="stylesheet">'
        )
    else:
        font_link = ""
    font_family = font or "system-ui"

    # Accent color: prefer color_tokens accent, fall back to colors primary
    color_tokens = metadata.get("color_tokens", {})
    accent = (
        color_tokens.get("accent")
        or metadata.get("colors", {}).get("primary")
        or "#6366f1"
    )

    html = template
    html = html.replace("{{PROJECT_NAME}}", escape(metadata["project_name"]))
    html = html.replace("{{SCREEN_COUNT}}", str(len(screens)))
    html = html.replace("{{SCREENS_HTML}}", sections_html)
    html = html.replace("{{PRIMARY_COLOR}}", accent)
    html = html.replace("{{SECTION_TABS_HTML}}", tabs_html)
    html = html.replace("{{DEFAULT_THEME}}", metadata.get("default_theme", "light"))
    html = html.replace("{{FONT_LINK}}", font_link)
    html = html.replace("{{FONT_FAMILY}}", font_family)

    (output_dir / "index.html").write_text(html, encoding="utf-8")
    print("  ✓ index.html generated")


def _build_sections_html(screens: list, metadata: dict, ptype: str) -> tuple[str, list[dict]]:
    """
    Generate screen cards HTML, grouped by sections if defined in DESIGN.md.

    Returns (html_string, groups) where groups is a list of
    {"name": str, "key": str, "screens": list} dicts.
    """
    sections = metadata.get("sections", [])

    if sections:
        slug_to_screen = {s["slug"]: s for s in screens}
        html_parts = []
        covered = set()
        groups = []

        for section in sections:
            section_screens = [slug_to_screen[sl] for sl in section["slugs"] if sl in slug_to_screen]
            covered.update(section["slugs"])
            if section_screens:
                key = re.sub(r"[^a-z0-9]+", "-", section["name"].lower()).strip("-")
                groups.append({"name": section["name"], "key": key, "screens": section_screens})
                html_parts.append(_section_html(section["name"], key, section_screens, ptype))

        # Screens not belonging to any section
        remaining = [s for s in screens if s["slug"] not in covered]
        if remaining:
            key = "other"
            groups.append({"name": "Other screens", "key": key, "screens": remaining})
            html_parts.append(_section_html("Other screens", key, remaining, ptype))

        return "\n".join(html_parts), groups
    else:
        # Auto-group by keyword overlap when DESIGN.md has no sections
        raw_groups = _auto_group_screens(screens)
        groups = []
        html_parts = []
        for g in raw_groups:
            key = re.sub(r"[^a-z0-9]+", "-", g["name"].lower()).strip("-") or "ungrouped"
            groups.append({"name": g["name"], "key": key, "screens": g["screens"]})
            html_parts.append(_section_html(g["name"], key, g["screens"], ptype))
        return "\n".join(html_parts), groups


def _section_tabs_html(groups: list[dict]) -> str:
    """
    Generate filter tab pills for section navigation.

    Only generates tabs when there are 2+ named sections.
    Returns empty string otherwise.
    """
    named = [g for g in groups if g["name"]]
    if len(named) < 2:
        return ""

    tabs = []
    # Base classes shared by all tabs — JS controls active state via inline style
    base = 'filter-tab text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-white/10 rounded-full px-4 py-1.5 text-[12px] font-medium transition-colors'
    tabs.append(f'<button class="{base}" data-section="all">All</button>')
    for g in groups:
        if not g["name"]:
            continue
        count = len(g["screens"])
        tabs.append(
            f'<button class="{base}" '
            f'data-section="{escape(g["key"])}">'
            f'{escape(g["name"])} <span class="opacity-50">({count})</span></button>'
        )

    inner = "\n    ".join(tabs)
    return (
        f'\n  <!-- ── Section filter tabs ──────────────────────────────── -->\n'
        f'  <div class="mx-auto max-w-[1280px] px-6 pt-4">\n'
        f'    <div class="flex flex-wrap gap-2">\n'
        f'    {inner}\n'
        f'    </div>\n'
        f'  </div>\n'
    )


def _auto_group_screens(screens: list) -> list[dict]:
    """
    Infer logical groups from slug keyword overlap when DESIGN.md has no sections.

    Strategy:
      1. Strip theme suffixes (_oscuro, _claro, _dark, _light) and trailing numbers.
      2. Find words shared by 2+ slugs (excluding stop words).
      3. Greedily assign screens to the largest keyword clusters.
      4. Remaining singletons go into an ungrouped bucket.
    """
    THEME_SUFFIXES = {"oscuro", "claro", "dark", "light"}
    STOP_WORDS = {
        "de", "del", "la", "el", "los", "las", "un", "una", "y", "en",
        "con", "a", "al", "lo", "the", "and", "of", "for", "to", "in",
    }

    def keywords(slug: str) -> list[str]:
        s = re.sub(r"_\d+$", "", slug)
        return [
            w for w in s.split("_")
            if w and w not in STOP_WORDS and w not in THEME_SUFFIXES and len(w) > 1
        ]

    screen_kws = {s["slug"]: keywords(s["slug"]) for s in screens}
    slug_to_screen = {s["slug"]: s for s in screens}

    # Count how many slugs each keyword appears in
    word_to_slugs: dict[str, list[str]] = {}
    for slug, kws in screen_kws.items():
        for w in kws:
            word_to_slugs.setdefault(w, []).append(slug)

    # Only words shared by 2+ screens are useful for clustering
    cluster_words = {w: slugs for w, slugs in word_to_slugs.items() if len(slugs) >= 2}

    if not cluster_words:
        return [{"name": "", "screens": screens}]

    # Greedy: biggest clusters first; each screen assigned to its first cluster
    assigned: set[str] = set()
    groups: list[dict] = []

    for word, slugs in sorted(cluster_words.items(), key=lambda x: -len(x[1])):
        unassigned = [s for s in slugs if s not in assigned]
        if len(unassigned) < 2:
            continue
        group_screens = [slug_to_screen[s] for s in unassigned if s in slug_to_screen]
        if len(group_screens) >= 2:
            name = word.replace("_", " ").title()
            groups.append({"name": name, "screens": group_screens})
            assigned.update(s["slug"] for s in group_screens)

    remaining = [s for s in screens if s["slug"] not in assigned]
    if remaining:
        label = "Other" if groups else ""
        groups.append({"name": label, "screens": remaining})

    return groups


def _section_html(section_name: str, section_key: str, screens: list, ptype: str) -> str:
    """HTML for a section containing screen cards (Tailwind classes)."""
    # Grid columns differ by type: narrower for mobile phones, wider for web screens
    col_min = "160px" if ptype == "mobile" else "240px"
    cards = "\n".join(_card_html(s, ptype) for s in screens)
    count = len(screens)

    if section_name:
        label = (
            f'<h2 class="section-label text-[11px] font-semibold tracking-wider uppercase '
            f'text-gray-400 dark:text-gray-500 mb-4 pb-2.5 '
            f'border-b border-gray-200 dark:border-white/10">'
            f'{escape(section_name)} <span class="font-normal normal-case tracking-normal opacity-60">({count})</span></h2>'
        )
    else:
        label = ""

    data_attr = f' data-section="{escape(section_key)}"' if section_key else ""

    return f"""
    <section class="screen-section mb-10"{data_attr}>
      {label}
      <div class="screens-grid grid gap-4" style="grid-template-columns: repeat(auto-fill, minmax({col_min}, 1fr))">
        {cards}
      </div>
    </section>"""


DARK_SUFFIXES = ('_oscuro', '_dark', '_dark_mode', '_oscura')
LIGHT_SUFFIXES = ('_claro', '_light', '_light_mode', '_clara')


def _card_html(screen: dict, ptype: str) -> str:
    """HTML for a single screen card using Tailwind classes."""
    import urllib.parse
    slug = screen["slug"]
    title = escape(screen["title"])
    desc = escape(screen["description"])
    html_file = screen["html_file"]
    png_file = screen.get("png_file") or ""

    params = urllib.parse.urlencode({
        "screen": html_file,
        "title": screen["title"],
        "desc": screen["description"],
    })
    viewer_url = f"viewer.html?{params}"

    aspect = "aspect-[9/19.5]" if ptype == "mobile" else "aspect-[16/10]"

    # Dark/light variant badge
    badge = ""
    if any(slug.endswith(s) for s in DARK_SUFFIXES):
        badge = '<span class="absolute top-2 right-2 text-[9px] px-1.5 py-0.5 rounded-full bg-black/60 text-white/80 font-medium">dark</span>'
    elif any(slug.endswith(s) for s in LIGHT_SUFFIXES):
        badge = '<span class="absolute top-2 right-2 text-[9px] px-1.5 py-0.5 rounded-full bg-white/70 text-black/60 font-medium">light</span>'

    if png_file:
        thumb = (
            f'<img src="{png_file}" alt="{title}" loading="lazy" '
            f'class="w-full h-full object-cover object-top transition-transform duration-300 group-hover:scale-[1.03]">'
        )
    else:
        thumb = (
            f'<div class="w-full h-full flex items-center justify-center '
            f'text-4xl font-bold text-gray-300 dark:text-white/10">'
            f'{title[0].upper()}</div>'
        )

    desc_html = (
        f'<p class="card-desc text-[10px] text-gray-400 dark:text-gray-500 mt-0.5 line-clamp-2 leading-snug">'
        f'{desc}</p>'
    ) if desc else ""

    return f"""
        <a class="screen-card group block no-underline bg-white dark:bg-[#1a1a1a] border border-gray-200 dark:border-white/10 rounded-2xl overflow-hidden transition-all duration-200 cursor-pointer hover:border-accent hover:ring-1 hover:ring-accent hover:shadow-lg dark:hover:shadow-[0_8px_24px_rgba(0,0,0,.5)]"
           href="{viewer_url}" target="_blank" rel="noopener">
          <div class="card-thumb relative {aspect} bg-black dark:bg-black overflow-hidden">
            {thumb}
            {badge}
          </div>
          <div class="card-info px-3 py-2.5 border-t border-gray-200 dark:border-white/10">
            <p class="text-xs font-semibold truncate text-gray-900 dark:text-gray-100">{title}</p>
            {desc_html}
          </div>
        </a>"""


def _slug_to_title(slug: str) -> str:
    """01_splash_screen → 'Splash Screen' (strips numeric prefix)."""
    s = re.sub(r"^[\d_]+", "", slug)
    return s.replace("_", " ").replace("-", " ").title().strip() or slug.title()


# ─── Watch mode ───────────────────────────────────────────────────────────────

def _source_signature(source: Path) -> str:
    """Hash of mtimes of all zips and screen folders in source."""
    parts = []
    for p in sorted(source.iterdir()):
        if p.suffix == ".zip" or (p.is_dir() and (p / "code.html").exists()):
            parts.append(f"{p.name}:{p.stat().st_mtime}")
    return hashlib.md5("\n".join(parts).encode()).hexdigest()


def _watch(source_dir: str, project_type: str, project_name: str) -> None:
    """Watch source folder and rebuild on changes (Ctrl+C to stop)."""
    print("👀 Watching for changes... (Ctrl+C to stop)")
    last_sig = None
    while True:
        try:
            source = Path(source_dir).resolve()
            sig = _source_signature(source)
            if sig != last_sig:
                if last_sig is not None:
                    print("\n🔄 Changes detected, rebuilding...")
                build(source_dir, project_type, project_name)
                last_sig = sig
            time.sleep(2)
        except KeyboardInterrupt:
            print("\n👋 Watch stopped.")
            break


# ─── Init mode ────────────────────────────────────────────────────────────────

def _init(source_dir: str, project_type: str, project_name: str) -> None:
    """Generate a DESIGN.md skeleton in source_dir with auto-detected slugs."""
    source = Path(source_dir).resolve()
    if not source.exists():
        print(f"Error: '{source}' does not exist.", file=sys.stderr)
        sys.exit(1)

    # If a zip was passed directly, extract it first (same as build())
    if source.suffix == ".zip":
        source = _extract_source_zip(source)

    # Collect slugs (without extracting content)
    import extract_zips as _ez
    zips = sorted(source.glob("*.zip"))
    dirs = [d for d in sorted(source.iterdir()) if d.is_dir() and (d / "code.html").exists()]

    slugs = [_ez._slug_from_name(z.stem) for z in zips]
    slugs += [_ez._slug_from_name(d.name) for d in dirs if _ez._slug_from_name(d.name) not in slugs]

    if not slugs:
        print("Error: no screens found. Cannot generate DESIGN.md.", file=sys.stderr)
        sys.exit(1)

    # Auto-group slugs for skeleton
    fake_screens = [{"slug": s, "title": _slug_to_title(s), "description": ""} for s in slugs]
    groups = _auto_group_screens(fake_screens)

    pname = project_name or source.name.replace("_", " ").replace("-", " ").title()
    ptype = project_type or "mobile"

    lines = [
        f"# {pname}",
        "",
        "## Type",
        ptype,
        "",
        "## Screens",
    ]
    for g in groups:
        if g["name"]:
            lines.append(f"### {g['name']}")
        for s in g["screens"]:
            lines.append(f"- {s['slug']}")
        lines.append("")

    lines += [
        "## Colors",
        "- Primary: #6366f1",
        "- Background: #ffffff",
        "",
        "## Typography",
        "- **Inter**",
        "",
    ]

    design_md = source / "DESIGN.md"
    if design_md.exists():
        backup = source / "DESIGN.md.bak"
        shutil.copy2(design_md, backup)
        print(f"  ℹ Existing DESIGN.md backed up to DESIGN.md.bak")

    design_md.write_text("\n".join(lines), encoding="utf-8")
    print(f"✅ DESIGN.md created at {design_md}")
    print("   Edit sections and run without --init to build the showcase.")


# ─── Fallbacks (when reference templates are missing) ─────────────────────────

def _generate_viewer_fallback(output_dir: Path, ptype: str, metadata: dict) -> None:
    """Minimal functional viewer HTML."""
    phone_style = """
      #phone-wrap {
        width: 390px; height: 844px;
        border: 8px solid #333; border-radius: 40px;
        overflow: hidden; margin: 0 auto;
        box-shadow: 0 20px 60px rgba(0,0,0,0.5);
      }
    """ if ptype == "mobile" else ""

    frame_open = '<div id="phone-wrap">' if ptype == "mobile" else '<div id="web-wrap" style="flex:1">'

    html = f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="UTF-8">
<title>Viewer — {escape(metadata['project_name'])}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: #0d0d0d; color: #f0f0f0; font-family: system-ui, sans-serif;
         display: flex; flex-direction: column; height: 100vh; }}
  header {{ display: flex; align-items: center; gap: 16px; padding: 12px 20px;
            background: #141414; border-bottom: 1px solid #222; flex-shrink: 0; }}
  #btn-back {{ color: #aaa; text-decoration: none; font-size: 14px; cursor: pointer;
               background: none; border: none; padding: 0; }}
  #btn-back:hover {{ color: #fff; }}
  #screen-title {{ font-weight: 600; font-size: 15px; }}
  #screen-desc {{ font-size: 12px; color: #888; margin-left: auto; max-width: 400px; text-align: right; }}
  main {{ flex: 1; display: flex; align-items: center; justify-content: center;
         overflow: hidden; padding: 20px; }}
  {phone_style}
  iframe {{ width: 100%; height: 100%; border: none; }}
</style>
</head><body>
<header>
  <button id="btn-back" onclick="window.close()">← Back</button>
  <span id="screen-title">—</span>
  <span id="screen-desc"></span>
</header>
<main>
  {frame_open}
    <iframe id="viewer-frame" src="" title="Screen viewer"></iframe>
  </div>
</main>
<script>
  const p = new URLSearchParams(location.search);
  document.getElementById('screen-title').textContent = p.get('title') || '';
  document.getElementById('screen-desc').textContent = p.get('desc') || '';
  document.getElementById('viewer-frame').src = p.get('screen') || '';
</script>
</body></html>"""
    (output_dir / "viewer.html").write_text(html, encoding="utf-8")


def _generate_index_fallback(output_dir: Path, ptype: str, metadata: dict, screens: list) -> None:
    """Minimal functional index HTML (Tailwind CDN, light default, dark toggle)."""
    cards = "\n".join(_card_html(s, ptype) for s in screens)
    name = escape(metadata["project_name"])
    count = len(screens)
    badge = "Mobile" if ptype == "mobile" else "Web"
    col_min = "160px" if ptype == "mobile" else "240px"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name} — Showcase</title>
<script src="https://cdn.tailwindcss.com"></script>
<script>tailwind.config = {{ darkMode: 'class', theme: {{ extend: {{ colors: {{ accent: '#6366f1' }} }} }} }}</script>
</head>
<body class="bg-gray-100 dark:bg-[#0d0d0d] text-gray-900 dark:text-gray-100 transition-colors duration-200 min-h-screen">
<header class="sticky top-0 z-50 bg-white dark:bg-[#111] border-b border-gray-200 dark:border-white/10 shadow-sm">
  <div class="max-w-[1280px] mx-auto px-6 h-16 flex items-center justify-between gap-4">
    <div class="flex items-baseline gap-3">
      <h1 class="text-lg font-bold">{name}</h1>
      <span class="text-sm text-gray-400">{count} screens</span>
    </div>
    <div class="flex items-center gap-3">
      <span class="text-xs text-gray-400 border border-gray-200 dark:border-white/10 rounded-full px-3 py-1">{badge}</span>
      <button id="theme-toggle" class="w-8 h-8 flex items-center justify-center rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-white/10 transition-colors">
        <svg class="w-4 h-4 block dark:hidden" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
        <svg class="w-4 h-4 hidden dark:block" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/></svg>
      </button>
    </div>
  </div>
</header>
<div class="max-w-[1280px] mx-auto px-6 pt-6 pb-16">
  <div class="screens-grid grid gap-4" style="grid-template-columns: repeat(auto-fill, minmax({col_min}, 1fr))">
    {cards}
  </div>
</div>
<script>
  const html = document.documentElement;
  if (localStorage.getItem('showcase-theme') === 'dark') html.classList.add('dark');
  document.getElementById('theme-toggle').addEventListener('click', () => {{
    html.classList.toggle('dark');
    localStorage.setItem('showcase-theme', html.classList.contains('dark') ? 'dark' : 'light');
  }});
</script>
</body></html>"""
    (output_dir / "index.html").write_text(html, encoding="utf-8")


# ─── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate a navigable showcase from Google Stitch exports."
    )
    parser.add_argument("source", help="Folder containing Stitch zips (or a mega-zip)")
    parser.add_argument("--type", choices=["mobile", "web"], help="Design type")
    parser.add_argument("--name", help="Project name (if no DESIGN.md)")
    parser.add_argument("--watch", action="store_true", help="Watch for changes and rebuild automatically")
    parser.add_argument("--init", action="store_true", help="Generate DESIGN.md skeleton and exit")
    args = parser.parse_args()

    if args.init:
        _init(args.source, project_type=args.type, project_name=args.name)
    elif args.watch:
        _watch(args.source, project_type=args.type, project_name=args.name)
    else:
        output = build(args.source, project_type=args.type, project_name=args.name)
        print(f"Open: file://{output}/index.html")
