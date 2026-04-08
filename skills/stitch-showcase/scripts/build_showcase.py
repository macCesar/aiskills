"""
build_showcase.py — Main orchestrator for stitch-showcase.

Generates a navigable showcase from Google Stitch exports.

Default mode (--context): extracts data and writes showcase_context.json
for AI-driven HTML generation.

Legacy mode (--legacy): generates index.html + viewer.html from fixed
HTML templates (deprecated).

Usage:
    python build_showcase.py /path/to/folder-with-zips                  # → context JSON
    python build_showcase.py /path/to/folder-with-zips --context        # same (explicit)
    python build_showcase.py /path/to/folder-with-zips --legacy         # old template mode
    python build_showcase.py /path/to/folder-with-zips --type mobile
    python build_showcase.py /path/to/folder-with-zips --name "My App"
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

SKILL_VERSION = "1.5.0"

# Locate sibling scripts and references
SCRIPTS_DIR = Path(__file__).parent
REFERENCES_DIR = SCRIPTS_DIR.parent / "references"

sys.path.insert(0, str(SCRIPTS_DIR))
import extract_zips
import parse_design_md
import extract_text
import detect_components
import extract_catalog


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
    Build the complete showcase (index.html + viewer.html) from templates.

    Args:
        source_dir: Folder containing Stitch zips
        project_type: 'mobile' or 'web' (auto-detected if None)
        project_name: Project name (extracted from DESIGN.md if None)

    Returns:
        Path to the generated output directory.
    """
    source, metadata, ptype, output_dir, assets_dir = _prepare_source(
        source_dir, project_type, project_name
    )

    # Extract zips and copy assets
    print("\n🗜 Extracting screens...")
    screens_raw = extract_zips.extract_all(str(source), str(assets_dir))

    if not screens_raw:
        print("Error: no screens found (no zips or folders with code.html).", file=sys.stderr)
        sys.exit(1)

    # Enrich with DESIGN.md metadata
    screens = _enrich_screens(screens_raw, metadata, source)

    # If no font_family from DESIGN.md, try to extract from screen HTML files
    if not metadata.get("font_family"):
        extracted_font = _extract_font_from_html_screens(screens_raw)
        if extracted_font:
            metadata["font_family"] = extracted_font
            print(f"  ℹ Font extracted from screens: {extracted_font}")

    # Resolve pending type from screen HTML analysis (majority vote)
    if metadata.pop("_type_pending", False):
        ptype = _detect_type_from_screens(screens, assets_dir)
        metadata["type"] = ptype
        print(f"📱 Type: {ptype} (detected from screens) | Project: {metadata['project_name']}")

    print(f"\n✅ {len(screens)} screens processed")

    # Copy DESIGN.md if present
    design_md = source / "DESIGN.md"
    if design_md.exists():
        shutil.copy2(design_md, output_dir / "DESIGN.md")

    # Generate viewer.html
    _generate_viewer(output_dir, ptype, metadata, screens)

    # Generate index.html (with catalog link)
    _generate_index(output_dir, ptype, metadata, screens)

    # Generate catalog.html (always included)
    _generate_catalog(output_dir, assets_dir, metadata)

    print(f"\n🎉 Showcase ready: {output_dir}/index.html\n")
    return output_dir


def build_context(source_dir: str, project_type: str = None, project_name: str = None) -> Path:
    """
    Generate showcase_context.json for AI-driven HTML generation.

    Use with --context flag. Extracts data but does NOT generate HTML.
    """
    source, metadata, ptype, output_dir, assets_dir = _prepare_source(
        source_dir, project_type, project_name
    )

    # Extract zips and copy assets
    print("\n🗜 Extracting screens...")
    screens_raw = extract_zips.extract_all(str(source), str(assets_dir))

    if not screens_raw:
        print("Error: no screens found (no zips or folders with code.html).", file=sys.stderr)
        sys.exit(1)

    # Enrich with DESIGN.md metadata
    screens = _enrich_screens(screens_raw, metadata, source)

    # If no font_family from DESIGN.md, try to extract from screen HTML files
    if not metadata.get("font_family"):
        extracted_font = _extract_font_from_html_screens(screens_raw)
        if extracted_font:
            metadata["font_family"] = extracted_font
            print(f"  ℹ Font extracted from screens: {extracted_font}")

    # Detect per-screen type (web vs mobile)
    for screen in screens:
        html_path = assets_dir / f"{screen['slug']}.html"
        screen["detected_type"] = _detect_screen_type(html_path)

    # Resolve pending type from screen HTML analysis (majority vote)
    if metadata.pop("_type_pending", False):
        ptype = _detect_type_from_screens(screens, assets_dir)
        metadata["type"] = ptype
        print(f"📱 Type: {ptype} (detected from screens) | Project: {metadata['project_name']}")

    print(f"\n✅ {len(screens)} screens processed")

    # Copy DESIGN.md if present
    design_md = source / "DESIGN.md"
    if design_md.exists():
        shutil.copy2(design_md, output_dir / "DESIGN.md")

    # Read raw DESIGN.md text for AI context
    design_md_raw = _read_design_md_raw(source)

    # Generate context JSON
    _generate_context(output_dir, metadata, screens, ptype, design_md_raw)

    print(f"\n🎉 Context ready: {output_dir}/showcase_context.json")
    print(f"   Assets in: {output_dir}/assets/")
    print(f"   AI should now read reference MDs and generate index.html + viewer.html\n")
    return output_dir


def _dir_has_screens(path: Path) -> bool:
    """Check if a directory contains Stitch screens (zips or folders with code.html)."""
    if any(path.glob("*.zip")):
        return True
    return any(d.is_dir() and (d / "code.html").exists() for d in path.iterdir()
               if not d.name.startswith("."))


def _load_showcase_json(start: Path) -> dict | None:
    """
    Search for showcase.json in start and its parent. Returns parsed dict or None.
    """
    for candidate in (start, start.parent):
        config_path = candidate / "showcase.json"
        if config_path.exists():
            try:
                config = json.loads(config_path.read_text(encoding="utf-8"))
                config["_config_dir"] = str(candidate)
                print(f"  ℹ showcase.json found in {candidate}")
                return config
            except (json.JSONDecodeError, OSError) as e:
                print(f"  ⚠ showcase.json found but invalid: {e}", file=sys.stderr)
    return None


def _discover_source(given: Path) -> Path:
    """
    Resolve the actual source directory containing Stitch screens.

    Discovery order:
    1. If the given path itself has screens → use it
    2. If showcase.json exists (in given or parent) with a "source" key → use it
    3. Auto-discover: scan subdirectories for screens (one level deep)
    4. Fail with a helpful error
    """
    # 1. Direct match
    if _dir_has_screens(given):
        return given

    # 2. showcase.json
    config = _load_showcase_json(given)
    if config:
        config_dir = Path(config["_config_dir"])
        source_rel = config.get("source")
        if source_rel:
            resolved = (config_dir / source_rel).resolve()
            if resolved.exists() and _dir_has_screens(resolved):
                print(f"  ℹ Source resolved from showcase.json → {resolved}")
                return resolved
            else:
                print(f"  ⚠ showcase.json source '{source_rel}' has no screens at {resolved}",
                      file=sys.stderr)

    # 3. Auto-discover subdirectories
    candidates = []
    for child in sorted(given.iterdir()):
        if child.is_dir() and not child.name.startswith(".") and child.name not in ("showcase", "showcase-mobile", "showcase-web"):
            if _dir_has_screens(child):
                candidates.append(child)

    if len(candidates) == 1:
        print(f"  ℹ Auto-discovered source → {candidates[0]}")
        return candidates[0]
    elif len(candidates) > 1:
        names = ", ".join(c.name for c in candidates)
        print(f"Error: multiple subdirectories with screens found: {names}", file=sys.stderr)
        print(f"  Create a showcase.json with {{\"source\": \"<folder>\"}} to specify which one.",
              file=sys.stderr)
        sys.exit(1)

    # 4. Nothing found — helpful error
    print(f"Error: no screens found (no zips or folders with code.html).", file=sys.stderr)
    print(f"\n  Searched: {given}", file=sys.stderr)
    print(f"  Tip: create a showcase.json in your project root:", file=sys.stderr)
    print(f'  {{"source": "stitch", "type": "mobile", "name": "My App"}}', file=sys.stderr)
    sys.exit(1)


def _prepare_source(source_dir: str, project_type: str, project_name: str) -> tuple:
    """
    Common setup for both build modes: resolve source, parse metadata, create output dir.

    Returns (source, metadata, ptype, output_dir, assets_dir).
    """
    source = Path(source_dir).resolve()
    if not source.exists():
        print(f"Error: '{source}' does not exist.", file=sys.stderr)
        sys.exit(1)

    if source.suffix == ".zip":
        source = _extract_source_zip(source)

    # Discover actual source if given path has no screens
    source = _discover_source(source)

    # Load showcase.json config for type/name defaults
    config = _load_showcase_json(source) or _load_showcase_json(source.parent) or {}

    print(f"\n📁 Source: {source}")

    # Parse DESIGN.md
    design_md = source / "DESIGN.md"
    metadata = parse_design_md.parse(str(design_md)) if design_md.exists() else {}

    # Priority: CLI args > showcase.json > DESIGN.md > defaults
    if project_name:
        metadata["project_name"] = project_name
    elif not metadata.get("project_name") and config.get("name"):
        metadata["project_name"] = config["name"]
    if not metadata.get("project_name"):
        metadata["project_name"] = source.name.replace("_", " ").replace("-", " ").title()

    if project_type:
        metadata["type"] = project_type
    elif metadata.get("type", "unknown") == "unknown" and config.get("type"):
        metadata["type"] = config["type"]
    if metadata.get("type", "unknown") == "unknown":
        # Defer type detection — will resolve after screen extraction via _detect_type_from_screens()
        metadata["_type_pending"] = True

    ptype = metadata.get("type", "unknown")
    if ptype != "unknown":
        print(f"📱 Type: {ptype} | Project: {metadata['project_name']}")

    # Create output directory — next to the project root, not inside source
    # Use the config dir (showcase.json location) or source parent as the project root
    project_root = Path(config["_config_dir"]) if "_config_dir" in config else source.parent
    output_dir = project_root / "showcase"
    output_dir.mkdir(exist_ok=True)
    assets_dir = output_dir / "assets"
    assets_dir.mkdir(exist_ok=True)

    print(f"📂 Output: {output_dir}")

    return source, metadata, ptype, output_dir, assets_dir


def _generate_context(output_dir: Path, metadata: dict, screens: list, ptype: str, design_md_raw: str) -> None:
    """
    Write showcase_context.json with all data the AI needs to generate HTML.
    """
    sections = metadata.get("sections", [])

    # Extract design system screen
    ds_screen, filtered_screens = _extract_design_system_screen(screens)

    # Build sections with their screens
    section_data = []
    covered_slugs = set()
    slug_to_screen = {s["slug"]: s for s in filtered_screens}

    for sec in sections:
        sec_screens = [slug_to_screen[sl] for sl in sec["slugs"] if sl in slug_to_screen]
        covered_slugs.update(sec["slugs"])
        if sec_screens:
            key = re.sub(r"[^a-z0-9]+", "-", sec["name"].lower()).strip("-")
            section_data.append({
                "name": sec["name"],
                "key": key,
                "screens": sec_screens,
            })

    # Remaining screens not in any section
    remaining = [s for s in filtered_screens if s["slug"] not in covered_slugs]
    if remaining:
        section_data.append({
            "name": "Other screens",
            "key": "other",
            "screens": remaining,
        })

    # Build flat screen list for viewer prev/next
    all_screens_flat = []
    for sec in section_data:
        all_screens_flat.extend(sec["screens"])
    # Add any screens only in the flat list
    flat_slugs = {s["slug"] for s in all_screens_flat}
    for s in filtered_screens:
        if s["slug"] not in flat_slugs:
            all_screens_flat.append(s)

    context = {
        "skill_version": SKILL_VERSION,
        "project_name": metadata["project_name"],
        "type": ptype,
        "screen_count": len(filtered_screens),
        "font_family": metadata.get("font_family"),
        "colors": metadata.get("colors", {}),
        "color_tokens": metadata.get("color_tokens", {}),
        "default_theme": metadata.get("default_theme", "light"),
        "design_system_screen": ds_screen,
        "design_md_raw": design_md_raw,
        "sections": section_data,
        "all_screens": all_screens_flat,
    }

    context_path = output_dir / "showcase_context.json"
    context_path.write_text(
        json.dumps(context, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"  ✓ showcase_context.json generated ({len(all_screens_flat)} screens)")


def _detect_screen_type(html_path: Path) -> str:
    """
    Analyze a single screen HTML to detect if it's a mobile or web design.

    Returns 'mobile', 'web', or 'unknown'.

    Heuristics:
    - viewport user-scalable=no or maximum-scale=1 → mobile
    - Fixed widths 375-430px in CSS → mobile
    - Media queries with desktop breakpoints, sidebars → web
    - Wide fixed widths (>900px) → web
    """
    if not html_path.exists():
        return "unknown"

    try:
        text = html_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return "unknown"

    mobile_score = 0
    web_score = 0

    # Viewport hints
    if re.search(r'user-scalable\s*=\s*no', text, re.IGNORECASE):
        mobile_score += 2
    if re.search(r'maximum-scale\s*=\s*1', text, re.IGNORECASE):
        mobile_score += 1

    # Fixed mobile widths (375, 390, 393, 412, 414, 428, 430)
    if re.search(r'(?:width|max-width)\s*:\s*(375|390|393|412|414|428|430)px', text):
        mobile_score += 2

    # Desktop breakpoints in media queries
    if re.search(r'@media[^{]*min-width\s*:\s*(768|1024|1200|1280|1440)px', text):
        web_score += 2

    # Sidebar patterns (common in web dashboards)
    if re.search(r'(?:sidebar|side-bar|nav-rail|drawer)', text, re.IGNORECASE):
        web_score += 1

    # Wide fixed widths
    if re.search(r'(?:width|max-width)\s*:\s*(?:9\d\d|1[0-9]\d\d|1[4-9]\d\d)px', text):
        web_score += 1

    if mobile_score > web_score:
        return "mobile"
    if web_score > mobile_score:
        return "web"
    return "unknown"


def _detect_type_from_screens(screens: list, assets_dir: Path) -> str:
    """Majority vote from per-screen type detection. Falls back to 'mobile'."""
    votes = {"mobile": 0, "web": 0}
    for screen in screens:
        dt = screen.get("detected_type")
        if not dt or dt == "unknown":
            html_path = assets_dir / f"{screen['slug']}.html"
            dt = _detect_screen_type(html_path)
        if dt in votes:
            votes[dt] += 1
    if votes["web"] > votes["mobile"]:
        return "web"
    if votes["mobile"] > votes["web"]:
        return "mobile"
    # Tie or all unknown — default to mobile
    print("⚠ Could not detect type (mobile/web). Defaulting to mobile.", file=sys.stderr)
    return "mobile"


def _read_design_md_raw(source: Path) -> str:
    """Read the full DESIGN.md text, or return empty string if absent."""
    design_md = source / "DESIGN.md"
    if design_md.exists():
        try:
            return design_md.read_text(encoding="utf-8")
        except Exception:
            return ""
    return ""


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


def _extract_font_from_html_screens(screens_raw: list) -> str | None:
    """
    Scan screen HTML files for font-family declarations or Google Fonts links.

    Returns the most common font family name, or None.
    """
    GENERIC_FONTS = {
        "sans-serif", "serif", "monospace", "cursive", "fantasy", "system-ui",
        "ui-sans-serif", "ui-serif", "ui-monospace", "ui-rounded",
        "arial", "helvetica", "verdana", "tahoma", "times", "times new roman",
        "courier", "courier new", "georgia", "trebuchet ms", "segoe ui",
    }
    ICON_FONTS = {
        "material symbols", "material symbols outlined", "material symbols rounded",
        "material symbols sharp", "material icons", "material icons outlined",
        "material icons round", "material icons sharp", "font awesome",
        "fontawesome", "ionicons", "feather", "remix icon", "bootstrap icons",
    }
    font_counts: dict[str, int] = {}

    for raw in screens_raw[:8]:  # sample up to 8 screens
        html_path = raw.get("html_path", "")
        if not html_path:
            continue
        try:
            text = Path(html_path).read_text(encoding="utf-8", errors="ignore")

            # Google Fonts link: family=Font+Name or family=Font+Name:wght@...
            for m in re.finditer(r"family=([A-Z][a-zA-Z+]+?)(?::|&|[\"'])", text):
                name = m.group(1).replace("+", " ").strip()
                nl = name.lower()
                if nl not in GENERIC_FONTS and nl not in ICON_FONTS and len(name) > 1:
                    font_counts[name] = font_counts.get(name, 0) + 1

            # CSS font-family declarations
            for m in re.finditer(r"font-family:\s*['\"]?([A-Z][a-zA-Z\s]+)['\"]?", text):
                name = m.group(1).strip().rstrip(",;")
                nl = name.lower()
                if nl not in GENERIC_FONTS and nl not in ICON_FONTS and len(name) > 1:
                    font_counts[name] = font_counts.get(name, 0) + 1

        except Exception:
            continue

    if not font_counts:
        return None

    # Return the most common font
    return max(font_counts, key=font_counts.get)


def _generate_viewer(output_dir: Path, ptype: str, metadata: dict, screens: list) -> None:
    """Generate viewer.html from the unified reference template."""
    template_path = REFERENCES_DIR / "viewer.html"

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
    html = html.replace("{{DEFAULT_VIEW}}", ptype)
    html = html.replace("{{PROJECT_SLUG}}", _project_slug(metadata["project_name"]))
    html = html.replace("{{FONT_LINK}}", font_link)
    html = html.replace("{{FONT_FAMILY}}", font_family)

    (output_dir / "viewer.html").write_text(html, encoding="utf-8")
    print("  ✓ viewer.html generated")


def _generate_index(output_dir: Path, ptype: str, metadata: dict, screens: list) -> None:
    """Generate index.html from the unified reference template."""
    template_path = REFERENCES_DIR / "index.html"

    if not template_path.exists():
        print(f"  ⚠ Template not found: {template_path}", file=sys.stderr)
        _generate_index_fallback(output_dir, ptype, metadata, screens)
        return

    template = template_path.read_text(encoding="utf-8")

    # Extract design system screen before building sections
    ds_screen, filtered_screens = _extract_design_system_screen(screens)

    # Show DS section if there's a dedicated screen OR if metadata has colors/font
    has_ds_info = bool(metadata.get("color_tokens") or metadata.get("colors") or metadata.get("font_family"))
    if ds_screen or has_ds_info:
        ds_html = _design_system_html(ds_screen, metadata)
    else:
        ds_html = ""

    sections_html, groups = _build_sections_html(filtered_screens, metadata, ptype)
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

    # New template variables
    type_labels = {"mobile": "Mobile App", "web": "Web App"}
    type_label = type_labels.get(metadata.get("type", ""), "Showcase")
    project_desc = _project_description_html(metadata, filtered_screens)
    screens_intro = _screens_intro_text(metadata)

    html = template
    html = html.replace("{{PROJECT_NAME}}", escape(metadata["project_name"]))
    html = html.replace("{{SCREEN_COUNT}}", str(len(filtered_screens)))
    html = html.replace("{{SCREENS_HTML}}", sections_html)
    html = html.replace("{{PRIMARY_COLOR}}", accent)
    html = html.replace("{{SECTION_TABS_HTML}}", tabs_html)
    html = html.replace("{{DEFAULT_THEME}}", metadata.get("default_theme", "light"))
    html = html.replace("{{FONT_LINK}}", font_link)
    html = html.replace("{{FONT_FAMILY}}", font_family)
    html = html.replace("{{PROJECT_TYPE_LABEL}}", escape(type_label))
    html = html.replace("{{PROJECT_DESCRIPTION}}", project_desc)
    html = html.replace("{{DEFAULT_VIEW}}", ptype)
    html = html.replace("{{PROJECT_SLUG}}", _project_slug(metadata["project_name"]))
    html = html.replace("{{DESIGN_SYSTEM_HTML}}", ds_html)
    html = html.replace("{{SCREENS_INTRO}}", escape(screens_intro))

    (output_dir / "index.html").write_text(html, encoding="utf-8")
    print("  ✓ index.html generated")


def _generate_catalog(output_dir: Path, assets_dir: Path, metadata: dict) -> None:
    """Run component detection + extraction and generate catalog.html."""
    # Detect shared structural components
    print("\n🔍 Detecting shared components...")
    shared_components = detect_components.detect_shared_components(assets_dir)
    if shared_components:
        shared_json_path = output_dir / "shared_components.json"
        shared_json_path.write_text(
            json.dumps(shared_components, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"  ✅ {len(shared_components)} shared component type(s) detected")
    else:
        print("  ℹ No shared components detected across screens.")

    # Extract atomic + composite component catalog
    print("\n📦 Extracting component catalog...")
    catalog = extract_catalog.extract_component_catalog(assets_dir)
    if not catalog:
        catalog = {}

    # Attach shared components for unified display
    catalog["shared"] = shared_components or {}

    # Write catalog JSON
    json_path = output_dir / "component_catalog.json"
    json_path.write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    atomic_count = sum(len(v) for v in catalog.get("atomic", {}).values())
    composite_count = sum(len(v) for v in catalog.get("composite", {}).values())
    shared_count = len(catalog.get("shared", {}))
    print(f"  ✅ {atomic_count} atomic + {composite_count} composite + {shared_count} shared component types")

    # Generate visual catalog HTML
    _generate_catalog_html(output_dir, metadata, catalog)


DS_SLUG_PATTERNS = ("design_system", "muestrario", "style_guide", "ui_kit", "design_tokens")


def _extract_design_system_screen(screens: list) -> tuple[dict | None, list]:
    """
    Find and remove the design system screen from the screens list.

    Returns (ds_screen_or_None, remaining_screens).
    """
    ds_screen = None
    remaining = []
    for s in screens:
        slug = s["slug"]
        if not ds_screen and any(pat in slug for pat in DS_SLUG_PATTERNS):
            ds_screen = s
        else:
            remaining.append(s)
    return ds_screen, remaining


def _design_system_html(ds_screen: dict | None, metadata: dict) -> str:
    """
    Render the Manual de Identidad section.

    Two variants:
    - With ds_screen: clickable card with thumbnail + tokens
    - Without ds_screen: inline display of color palette + typography
    """
    import urllib.parse

    color_tokens = metadata.get("color_tokens", {})
    colors = metadata.get("colors", {})
    swatches = _collect_swatches(color_tokens, colors)
    font = metadata.get("font_family")

    # ── Color palette strip ──
    palette_html = ""
    if swatches:
        # Large color blocks in a horizontal strip
        blocks = []
        for name, hex_val in swatches:
            text_color = _swatch_text_color(hex_val)
            blocks.append(
                f'<div class="flex-1 min-w-[80px] h-20 flex flex-col items-start justify-end p-2.5" '
                f'style="background:{hex_val}">'
                f'<span class="text-[10px] font-medium leading-none opacity-80" style="color:{text_color}">{escape(name)}</span>'
                f'<span class="text-[10px] font-mono leading-none mt-0.5 opacity-60" style="color:{text_color}">{escape(hex_val)}</span>'
                f'</div>'
            )
        palette_html = (
            '<div class="flex rounded-lg overflow-hidden border border-gray-200 dark:border-white/10">'
            + "\n".join(blocks)
            + '</div>'
        )

    # ── Typography block ──
    typo_html = ""
    if font:
        typo_html = (
            f'<div class="flex items-baseline gap-4 mt-6">'
            f'<span class="text-3xl font-bold text-gray-900 dark:text-gray-100" '
            f'style="font-family:\'{escape(font)}\',sans-serif">Aa</span>'
            f'<div>'
            f'<span class="text-sm font-medium text-gray-700 dark:text-gray-200">{escape(font)}</span>'
            f'<span class="text-xs text-gray-400 dark:text-gray-500 ml-2">Primary typeface</span>'
            f'</div>'
            f'</div>'
        )

    # ── Viewer link (if dedicated screen exists) ──
    link_html = ""
    thumb_col_html = ""
    if ds_screen:
        title = escape(ds_screen.get("title") or "Muestrario de Estilo")
        png_file = ds_screen.get("png_file") or ""
        params = urllib.parse.urlencode({
            "screen": ds_screen.get("html_file", ""),
            "title": ds_screen.get("title", "Design System"),
            "desc": ds_screen.get("description", ""),
        })
        viewer_url = f"viewer.html?{params}"

        link_html = (
            f'<a href="{viewer_url}" rel="noopener" '
            f'class="inline-flex items-center gap-1.5 mt-6 text-sm font-medium text-accent '
            f'hover:underline underline-offset-2">'
            f'Ver muestrario completo'
            f'<svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">'
            f'<path d="M7 17L17 7M17 7H7M17 7V17"/></svg>'
            f'</a>'
        )

        if png_file:
            thumb_col_html = (
                f'<div class="hidden sm:block sm:w-56 shrink-0 rounded-lg overflow-hidden '
                f'border border-gray-200 dark:border-white/10">'
                f'<a href="{viewer_url}" rel="noopener" class="block">'
                f'<img src="{png_file}" alt="{title}" loading="lazy" '
                f'class="w-full h-full object-cover object-top transition-transform duration-200 hover:scale-[1.02]">'
                f'</a></div>'
            )

    # ── Assemble section ──
    has_content = palette_html or typo_html
    if not has_content:
        return ""

    return f"""
  <section class="mx-auto max-w-[1280px] px-6 pb-12">
    <h2 class="text-xl sm:text-2xl font-bold tracking-tight mb-6 text-gray-900 dark:text-gray-100">
      Manual de Identidad
    </h2>
    <div class="flex gap-6 items-start">
      <div class="flex-1 min-w-0">
        {palette_html}
        {typo_html}
        {link_html}
      </div>
      {thumb_col_html}
    </div>
  </section>
"""


def _collect_swatches(color_tokens: dict, colors: dict) -> list[tuple[str, str]]:
    """Collect up to 6 named color swatches, prioritizing semantic tokens."""
    SEMANTIC_ORDER = ["primary", "secondary", "accent", "surface", "background", "error"]
    SKIP_KEYS = {"accent", "surface"}  # these are derived aliases in color_tokens

    swatches = []
    seen_vals = set()

    # First pass: semantic order from color_tokens
    for key in SEMANTIC_ORDER:
        val = color_tokens.get(key)
        if val and val not in seen_vals:
            swatches.append((key.replace("-", " ").title(), val))
            seen_vals.add(val)

    # Second pass: remaining color_tokens
    for key, val in color_tokens.items():
        if key in SKIP_KEYS or val in seen_vals or key.startswith("on-"):
            continue
        swatches.append((key.replace("-", " ").title(), val))
        seen_vals.add(val)
        if len(swatches) >= 6:
            break

    # If we still have room, add from colors dict
    if len(swatches) < 6:
        for key, val in colors.items():
            if val in seen_vals:
                continue
            swatches.append((key.replace("-", " ").title(), val))
            seen_vals.add(val)
            if len(swatches) >= 6:
                break

    return swatches[:6]


def _swatch_text_color(hex_val: str) -> str:
    """Return white or black text color for readable contrast on a background."""
    hex_clean = hex_val.lstrip("#")
    if len(hex_clean) != 6:
        return "#fff"
    try:
        r = int(hex_clean[0:2], 16)
        g = int(hex_clean[2:4], 16)
        b = int(hex_clean[4:6], 16)
    except ValueError:
        return "#fff"
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    return "#000" if luminance > 140 else "#fff"


def _project_description_html(metadata: dict, screens: list) -> str:
    """Generate 2 short paragraphs of project description from metadata."""
    name = escape(metadata.get("project_name", "this project"))
    sections = metadata.get("sections", [])
    section_names = [s["name"] for s in sections if s.get("name")]
    screen_count = len(screens)

    # Paragraph 1
    if section_names:
        top_sections = section_names[:4]
        sections_str = ", ".join(top_sections)
        if len(section_names) > 4:
            sections_str += f" y {len(section_names) - 4} más"
        p1 = (
            f"Propuesta de diseño UI/UX para {name}. "
            f"{screen_count} pantallas organizadas en {len(section_names)} secciones "
            f"que cubren {sections_str}."
        )
    else:
        p1 = f"Propuesta de diseño UI/UX para {name} con {screen_count} pantallas."

    # Paragraph 2
    p2 = (
        "Cada diseño incluye el prototipo interactivo en HTML exportado desde Google Stitch, "
        "con las descripciones originales del prompt de diseño."
    )

    return f"<p>{p1}</p>\n      <p>{p2}</p>"


def _screens_intro_text(metadata: dict) -> str:
    """Short intro paragraph for the screens browsing section."""
    name = metadata.get("project_name", "la aplicación")
    return (
        f"Explora las pantallas de {name}. "
        f"Haz clic en cualquier tarjeta para ver el prototipo interactivo a tamaño completo."
    )


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

    return "\n      ".join(tabs)


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
    cards = "\n".join(_card_html(s, ptype) for s in screens)
    count = len(screens)

    if section_name:
        label = (
            f'<h3 class="section-label text-lg font-semibold tracking-tight '
            f'text-gray-800 dark:text-gray-200 mb-4 pb-2.5 '
            f'border-b border-gray-200 dark:border-white/10">'
            f'{escape(section_name)} <span class="text-sm font-normal text-gray-400 dark:text-gray-500">({count})</span></h3>'
        )
    else:
        label = ""

    data_attr = f' data-section="{escape(section_key)}"' if section_key else ""

    return f"""
    <section class="screen-section mb-10"{data_attr}>
      {label}
      <div class="screens-grid grid gap-4">
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
        f'<p class="card-desc text-xs text-gray-600 dark:text-gray-300 mt-1 leading-snug">'
        f'{desc}</p>'
    ) if desc else ""

    return f"""
        <a class="screen-card group block no-underline transition-all duration-200 cursor-pointer"
           href="{viewer_url}"
           data-title="{title}" data-desc="{desc}">
          <div class="card-thumb relative rounded-xl overflow-hidden ring-1 ring-gray-200 dark:ring-white/10 transition-all duration-200 group-hover:ring-accent">
            {thumb}
            {badge}
          </div>
          <div class="card-info pt-2.5 px-0.5">
            <p class="text-sm font-semibold text-gray-900 dark:text-gray-100">{title}</p>
            {desc_html}
          </div>
        </a>"""


def _slug_to_title(slug: str) -> str:
    """01_splash_screen → 'Splash Screen' (strips numeric prefix)."""
    s = re.sub(r"^[\d_]+", "", slug)
    return s.replace("_", " ").replace("-", " ").title().strip() or slug.title()


def _project_slug(name: str) -> str:
    """'SNAP Gym Web' → 'snap-gym-web' — for scoping localStorage keys per project."""
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "showcase"


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


# ─── Update mode ──────────────────────────────────────────────────────────────

def _update(source_dir: str, project_type: str, project_name: str) -> None:
    """Detect new screens not yet in DESIGN.md and append them under '### Por Clasificar'."""
    source = Path(source_dir).resolve()
    if not source.exists():
        print(f"Error: '{source}' does not exist.", file=sys.stderr)
        sys.exit(1)

    if source.suffix == ".zip":
        source = _extract_source_zip(source)

    # Use discovery to find actual screens
    source = _discover_source(source)

    import extract_zips as _ez
    zips = sorted(source.glob("*.zip"))
    dirs = [d for d in sorted(source.iterdir()) if d.is_dir() and (d / "code.html").exists()]

    all_slugs = [_ez._slug_from_name(z.stem) for z in zips]
    all_slugs += [_ez._slug_from_name(d.name) for d in dirs if _ez._slug_from_name(d.name) not in all_slugs]

    if not all_slugs:
        print("Error: no screens found in source folder.", file=sys.stderr)
        sys.exit(1)

    import parse_design_md as _pd
    design_md = source / "DESIGN.md"
    if not design_md.exists():
        print("  ℹ No DESIGN.md found. Run --init first.")
        return

    metadata = _pd.parse(str(design_md))
    classified = {slug for sec in metadata["sections"] for slug in sec["slugs"]}

    new_slugs = [s for s in all_slugs if s not in classified]

    if not new_slugs:
        print("✅ No new screens detected. All slugs are already in DESIGN.md.")
        print("   Run without --update to rebuild the showcase.")
        return

    print(f"📦 {len(new_slugs)} new screen(s) detected:")
    for s in new_slugs:
        print(f"   + {s}")

    content = design_md.read_text(encoding="utf-8")
    staging = "\n### Por Clasificar\n" + "\n".join(f"- {s}" for s in new_slugs) + "\n"
    if "\n## Colors" in content:
        content = content.replace("\n## Colors", staging + "\n## Colors", 1)
    elif "\n## Typography" in content:
        content = content.replace("\n## Typography", staging + "\n## Typography", 1)
    else:
        content += staging
    design_md.write_text(content, encoding="utf-8")

    print(f"\n✏️  New slugs added to DESIGN.md under '### Por Clasificar'.")
    print("   Move them to the correct sections, add descriptions, then run without flags to rebuild.")


# ─── Init mode ────────────────────────────────────────────────────────────────

def _init(source_dir: str, project_type: str, project_name: str) -> None:
    """Generate a DESIGN.md skeleton and showcase.json with auto-detected slugs."""
    source = Path(source_dir).resolve()
    if not source.exists():
        print(f"Error: '{source}' does not exist.", file=sys.stderr)
        sys.exit(1)

    # If a zip was passed directly, extract it first (same as build())
    if source.suffix == ".zip":
        source = _extract_source_zip(source)

    # Use discovery to find actual screens
    resolved = _discover_source(source)

    # Collect slugs (without extracting content)
    import extract_zips as _ez
    zips = sorted(resolved.glob("*.zip"))
    dirs = [d for d in sorted(resolved.iterdir()) if d.is_dir() and (d / "code.html").exists()]

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

    design_md = resolved / "DESIGN.md"
    if design_md.exists():
        backup = resolved / "DESIGN.md.bak"
        shutil.copy2(design_md, backup)
        print(f"  ℹ Existing DESIGN.md backed up to DESIGN.md.bak")

    design_md.write_text("\n".join(lines), encoding="utf-8")
    print(f"✅ DESIGN.md created at {design_md}")

    # Generate showcase.json in the project root (parent of source if source != given path)
    project_root = source if source != resolved else resolved.parent
    _generate_showcase_json(project_root, resolved, pname, ptype)

    print("   Edit sections and run without --init to build the showcase.")


def _generate_showcase_json(project_root: Path, source: Path, name: str, ptype: str) -> None:
    """Generate showcase.json in the project root pointing to the source directory."""
    config_path = project_root / "showcase.json"
    if config_path.exists():
        print(f"  ℹ showcase.json already exists at {config_path}, skipping")
        return

    # Compute relative path from project root to source
    try:
        source_rel = source.relative_to(project_root)
    except ValueError:
        source_rel = source.name

    config = {
        "source": str(source_rel),
        "type": ptype,
        "name": name,
    }
    config_path.write_text(
        json.dumps(config, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"✅ showcase.json created at {config_path}")


# ─── Text extraction mode ─────────────────────────────────────────────────────

def _extract_text_summaries(source_dir: str, project_type: str = None, project_name: str = None) -> None:
    """
    Extract visible text from all screen HTMLs and write screen_summaries.txt.

    This runs extract_zips first (to ensure assets/ exists), then uses
    extract_text.py to produce compact summaries for LLM consumption.
    """
    source = Path(source_dir).resolve()
    if not source.exists():
        print(f"Error: '{source}' does not exist.", file=sys.stderr)
        sys.exit(1)

    if source.suffix == ".zip":
        source = _extract_source_zip(source)

    # Use discovery to find actual screens
    source = _discover_source(source)

    # Load config for output dir placement
    config = _load_showcase_json(source) or _load_showcase_json(source.parent) or {}

    # Determine output dir
    metadata = {}
    design_md = source / "DESIGN.md"
    if design_md.exists():
        metadata = parse_design_md.parse(str(design_md))

    if project_type:
        metadata["type"] = project_type

    project_root = Path(config["_config_dir"]) if "_config_dir" in config else source.parent
    output_dir = project_root / "showcase"
    output_dir.mkdir(exist_ok=True)
    assets_dir = output_dir / "assets"
    assets_dir.mkdir(exist_ok=True)

    # Extract zips to assets
    print("\n🗜 Extracting screens...")
    screens_raw = extract_zips.extract_all(str(source), str(assets_dir))
    if not screens_raw:
        print("Error: no screens found.", file=sys.stderr)
        sys.exit(1)

    print(f"\n✅ {len(screens_raw)} screens extracted")

    # Extract text from all HTMLs
    print("\n📝 Extracting visible text from HTML files...")
    screen_texts = extract_text.extract_all_screens_text(assets_dir)

    if not screen_texts:
        print("Error: no text extracted.", file=sys.stderr)
        sys.exit(1)

    # Write summaries
    summaries = extract_text.format_all_summaries(screen_texts)
    summary_path = output_dir / "screen_summaries.txt"
    summary_path.write_text(summaries, encoding="utf-8")

    print(f"\n✅ Text summaries written to: {summary_path}")
    print(f"   {len(screen_texts)} screens summarized")
    print(f"   LLM should read this file instead of individual HTMLs")


def _generate_catalog_html(output_dir: Path, metadata: dict, catalog: dict) -> None:
    """Generate the visual component catalog HTML from template."""
    template_path = REFERENCES_DIR / "catalog-template.html"
    if not template_path.exists():
        print(f"  ⚠ Template not found: {template_path}", file=sys.stderr)
        return

    template = template_path.read_text(encoding="utf-8")

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

    # Accent color
    color_tokens = metadata.get("color_tokens", {})
    accent = (
        color_tokens.get("accent")
        or metadata.get("colors", {}).get("primary")
        or "#6366f1"
    )

    # Extract Tailwind head (CDN + config + fonts) for faithful previews
    assets_dir = output_dir / "assets"
    tailwind_head = ""
    if assets_dir.is_dir():
        tailwind_head = extract_catalog.extract_tailwind_head(assets_dir)

    # Build tabs HTML
    tabs_html = _catalog_tabs_html(catalog)

    # Build catalog sections HTML (pass tailwind_head for iframe srcdoc previews)
    default_theme = metadata.get("default_theme", "light")
    catalog_html = _catalog_sections_html(catalog, dark_mode=(default_theme == "dark"), tailwind_head=tailwind_head)

    html = template
    html = html.replace("{{PROJECT_NAME}}", escape(metadata["project_name"]))
    html = html.replace("{{PRIMARY_COLOR}}", accent)
    html = html.replace("{{DEFAULT_THEME}}", default_theme)
    html = html.replace("{{FONT_LINK}}", font_link)
    html = html.replace("{{FONT_FAMILY}}", font_family)
    html = html.replace("{{TABS_HTML}}", tabs_html)
    html = html.replace("{{CATALOG_HTML}}", catalog_html)
    html = html.replace("{{SKILL_VERSION}}", SKILL_VERSION)

    (output_dir / "catalog.html").write_text(html, encoding="utf-8")
    print(f"  ✓ catalog.html generated")


def _catalog_tabs_html(catalog: dict) -> str:
    """Generate tab pills for the comparison-oriented catalog layout."""
    tabs = ['<button class="tab active" data-category="all">All</button>']

    # Structural components tab (shared navbars, footers, etc.)
    shared = catalog.get("shared", {})
    if shared:
        structural_count = sum(1 + len(v.get("variants", [])) for v in shared.values())
        tabs.append(
            f'<button class="tab" data-category="structural">'
            f'Structural <span class="count">({structural_count})</span></button>'
        )

    # Atomic type tabs (from clusters)
    clusters = catalog.get("clusters", {})
    for comp_type in sorted(clusters.keys()):
        type_clusters = clusters[comp_type]
        variant_count = sum(1 + len(c.get("variants", [])) for c in type_clusters)
        label = comp_type.replace("_", " ").title()
        tabs.append(
            f'<button class="tab" data-category="{escape(comp_type)}">'
            f'{escape(label)} <span class="count">({variant_count})</span></button>'
        )

    # Composite components tab
    composite = catalog.get("composite", {})
    if composite:
        composite_count = sum(len(v) for v in composite.values())
        tabs.append(
            f'<button class="tab" data-category="composite">'
            f'Composite <span class="count">({composite_count})</span></button>'
        )

    # Already Unified tab
    tabs.append(
        '<button class="tab" data-category="unified">Already Unified</button>'
    )

    # Design tokens tab
    tokens = catalog.get("design_tokens", {})
    if tokens and (tokens.get("colors") or tokens.get("fonts")):
        tabs.append('<button class="tab" data-category="design-tokens">Design Tokens</button>')

    return "\n    ".join(tabs)


def _iframe_srcdoc(html_content: str, tailwind_head: str) -> str:
    """Build an HTML-attribute-safe srcdoc string for isolated preview iframes."""
    body = html_content[:2000]
    doc = (
        f"<!DOCTYPE html><html><head>{tailwind_head}</head>"
        f"<body style='margin:0;overflow:hidden;display:flex;align-items:center;"
        f"justify-content:center;min-height:100vh'>"
        f"<div>{body}</div></body></html>"
    )
    # Escape for use inside a double-quoted HTML attribute
    return doc.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")


def _catalog_sections_html(catalog: dict, dark_mode: bool = False, tailwind_head: str = "") -> str:
    """Generate comparison-oriented catalog sections."""
    sections = []
    unified_items = []  # Components with only 1 variant (already standardized)
    dark_cls = ' class="dark"' if dark_mode else ""

    # ── Structural components (shared navbars, footers, etc.) ──
    shared = catalog.get("shared", {})
    if shared:
        structural_parts = []
        for comp_type, data in shared.items():
            canonical = data.get("canonical", {})
            variants = data.get("variants", [])
            found_in = data.get("found_in", 0)
            total_screens = data.get("total_screens", 0)
            label = comp_type.replace("_", " ").title()

            if not variants:
                # Already unified — collect for collapsed section
                unified_items.append((label, found_in, total_screens, "structural"))
                continue

            # Build cluster group with side-by-side cards
            cards = []

            # Canonical card — iframe preview for structural components
            canon_slug = escape(canonical.get("slug", ""))
            canon_html = canonical.get("html_snippet", "")
            canon_srcdoc = _iframe_srcdoc(canon_html, tailwind_head)
            canon_code = escape(canon_html[:500])
            cards.append(
                f'<div class="comp-card canonical" data-name="{escape(label)} (canonical)" data-variant="canonical">\n'
                f'  <iframe data-srcdoc="{canon_srcdoc}" style="width:100%;height:120px;border:none;pointer-events:none;background:var(--surface-2);"></iframe>\n'
                f'  <div class="comp-info">\n'
                f'    <div class="comp-name">{escape(label)}<span class="canonical-badge">★ Canonical</span></div>\n'
                f'    <div class="comp-meta"><span class="pill">{canon_slug}</span>'
                f'<span>{found_in}/{total_screens} screens</span></div>\n'
                f'    <div class="comp-code"><button class="copy-btn">Copy</button><pre>{canon_code}</pre></div>\n'
                f'  </div>\n</div>'
            )

            # Variant cards
            for variant in variants:
                v_slug = escape(variant.get("slug", ""))
                v_sim = variant.get("similarity", 0)
                v_pct = int(v_sim * 100)
                v_diffs = escape(variant.get("differences", ""))
                cards.append(
                    f'<div class="comp-card" data-name="{escape(label)} ({v_slug})" data-variant="{v_slug}">\n'
                    f'  <div class="comp-info">\n'
                    f'    <div class="comp-name">{escape(label)} — {v_slug}</div>\n'
                    f'    <div class="comp-meta"><span class="pill">{v_slug}</span>'
                    f'<span>{v_pct}% similarity</span></div>\n'
                    f'    <div class="similarity-bar"><div class="similarity-fill" style="width:{v_pct}%"></div></div>\n'
                    f'    <div class="diff-text">{v_diffs}</div>\n'
                    f'  </div>\n</div>'
                )

            variant_count = 1 + len(variants)
            structural_parts.append(
                f'<div class="cluster-group">\n'
                f'  <div class="cluster-header">\n'
                f'    <h3 class="comp-name" style="margin:0">{escape(label)}</h3>\n'
                f'    <span class="variant-badge">{variant_count} variant{"s" if variant_count != 1 else ""}</span>\n'
                f'  </div>\n'
                f'  <div class="cluster-grid">\n{"".join(cards)}\n  </div>\n'
                f'</div>'
            )

        if structural_parts:
            sections.append(
                f'<section class="section" data-category="structural">\n'
                f'  <h2 class="section-title">Structural Components</h2>\n'
                f'  {"".join(structural_parts)}\n'
                f'</section>'
            )

    # ── Atomic component clusters ──
    clusters = catalog.get("clusters", {})
    for comp_type in sorted(clusters.keys()):
        type_clusters = clusters[comp_type]
        label = comp_type.replace("_", " ").title()
        standalone_cards = []  # Single-variant clusters (no wrapper needed)
        cluster_parts = []    # Multi-variant clusters (with cluster-group wrapper)

        for cluster in type_clusters:
            canonical = cluster.get("canonical", {})
            variants = cluster.get("variants", [])
            context = cluster.get("context", "content")

            # Build canonical card (shown for all clusters)
            c_html = canonical.get("html", "")
            c_preview = c_html[:2000] if len(c_html) < 2000 else c_html[:2000] + "..."
            c_text = escape(canonical.get("text", "")[:60])
            c_variant = escape(canonical.get("variant", ""))
            c_name = f"{c_variant}: {c_text}" if c_variant and c_text else c_variant or c_text
            c_screens = canonical.get("found_in", [])
            c_screen_links = ", ".join(f'<a href="viewer.html?screen=assets/{escape(s)}.html&title={escape(s)}" target="_blank">{escape(s)}</a>' for s in c_screens[:5])

            if not variants:
                # Single-variant (standalone) — render as a simple card, no cluster wrapper
                c_srcdoc = _iframe_srcdoc(c_html, tailwind_head)
                standalone_cards.append(
                    f'<div class="comp-card" data-name="{escape(c_name)}" data-variant="{c_variant}">\n'
                    f'  <iframe data-srcdoc="{c_srcdoc}" style="width:100%;height:80px;border:none;pointer-events:none;"></iframe>\n'
                    f'  <div class="comp-info">\n'
                    f'    <div class="comp-name">{escape(c_name)}</div>\n'
                    f'    <div class="comp-meta"><span class="pill">{c_variant or comp_type}</span>'
                    f'<span>{len(c_screens)} screen{"s" if len(c_screens) != 1 else ""}</span></div>\n'
                    f'    <div class="comp-screens">{c_screen_links}</div>\n'
                    f'    <div class="comp-code"><button class="copy-btn">Copy</button><pre>{escape(c_html[:500])}</pre></div>\n'
                    f'  </div>\n</div>'
                )
                continue

            cards = []
            # Canonical card for multi-variant cluster
            c_srcdoc = _iframe_srcdoc(c_html, tailwind_head)
            cards.append(
                f'<div class="comp-card canonical" data-name="{escape(c_name)} (canonical)" data-variant="canonical">\n'
                f'  <iframe data-srcdoc="{c_srcdoc}" style="width:100%;height:80px;border:none;pointer-events:none;"></iframe>\n'
                f'  <div class="comp-info">\n'
                f'    <div class="comp-name">{escape(c_name)}<span class="canonical-badge">★ Canonical</span></div>\n'
                f'    <div class="comp-meta"><span class="pill">{c_variant or comp_type}</span>'
                f'<span>{len(c_screens)} screen{"s" if len(c_screens) != 1 else ""}</span></div>\n'
                f'    <div class="comp-screens">{c_screen_links}</div>\n'
                f'    <div class="comp-code"><button class="copy-btn">Copy</button><pre>{escape(c_html[:500])}</pre></div>\n'
                f'  </div>\n</div>'
            )

            # Variant cards
            for v in variants:
                v_html = v.get("html", "")
                v_preview = v_html[:2000] if len(v_html) < 2000 else v_html[:2000] + "..."
                v_text = escape(v.get("text", "")[:60])
                v_variant = escape(v.get("variant", ""))
                v_name = f"{v_variant}: {v_text}" if v_variant and v_text else v_variant or v_text
                v_sim = v.get("similarity", 0)
                v_pct = int(v_sim * 100)
                v_screens = v.get("found_in", [])
                v_screen_links = ", ".join(f'<a href="viewer.html?screen=assets/{escape(s)}.html&title={escape(s)}" target="_blank">{escape(s)}</a>' for s in v_screens[:5])

                v_srcdoc = _iframe_srcdoc(v_html, tailwind_head)
                cards.append(
                    f'<div class="comp-card" data-name="{escape(v_name)}" data-variant="{v_variant}">\n'
                    f'  <iframe data-srcdoc="{v_srcdoc}" style="width:100%;height:80px;border:none;pointer-events:none;"></iframe>\n'
                    f'  <div class="comp-info">\n'
                    f'    <div class="comp-name">{escape(v_name)}</div>\n'
                    f'    <div class="comp-meta"><span class="pill">{v_variant or comp_type}</span>'
                    f'<span>{v_pct}% similarity</span>'
                    f'<span>{len(v_screens)} screen{"s" if len(v_screens) != 1 else ""}</span></div>\n'
                    f'    <div class="similarity-bar"><div class="similarity-fill" style="width:{v_pct}%"></div></div>\n'
                    f'    <div class="comp-screens">{v_screen_links}</div>\n'
                    f'  </div>\n</div>'
                )

            context_label = context if context != "content" else "general"
            variant_count = 1 + len(variants)
            cluster_parts.append(
                f'<div class="cluster-group">\n'
                f'  <div class="cluster-header">\n'
                f'    <span class="cluster-context">{escape(context_label)}</span>\n'
                f'    <span class="cluster-count">{variant_count} variant{"s" if variant_count != 1 else ""}</span>\n'
                f'  </div>\n'
                f'  <div class="cluster-grid">\n{"".join(cards)}\n  </div>\n'
                f'</div>'
            )

        if standalone_cards or cluster_parts:
            inner = ""
            if standalone_cards:
                inner += f'<div class="grid">{"".join(standalone_cards)}</div>\n'
            inner += "".join(cluster_parts)
            sections.append(
                f'<section class="section" data-category="{escape(comp_type)}">\n'
                f'  <h2 class="section-title">{escape(label)}</h2>\n'
                f'  {inner}\n'
                f'</section>'
            )

    # ── Composite components (non-clustered, legacy display) ──
    composite = catalog.get("composite", {})
    if composite:
        composite_cards = []
        for comp_type_key, components in composite.items():
            for comp in components:
                composite_cards.append(_catalog_card_html(comp, comp_type_key, dark_mode=dark_mode, tailwind_head=tailwind_head))
        if composite_cards:
            sections.append(
                f'<section class="section" data-category="composite">\n'
                f'  <h2 class="section-title">Composite Components'
                f'<span class="badge">({len(composite_cards)})</span></h2>\n'
                f'  <div class="grid">\n{"".join(composite_cards)}\n  </div>\n'
                f'</section>'
            )

    # ── Already Unified section (collapsed) ──
    if unified_items:
        items_html = ""
        for name, found_in, total, category in unified_items:
            items_html += (
                f'<div class="unified-item">'
                f'<span class="unified-check">✓</span>'
                f'<span>{escape(name)}</span>'
                f'<span class="screen-count-badge">{found_in} screen{"s" if found_in != 1 else ""}</span>'
                f'</div>\n'
            )
        sections.append(
            f'<section class="section unified-section" data-category="unified">\n'
            f'  <h2 class="section-title">Already Unified<span class="badge">({len(unified_items)})</span></h2>\n'
            f'  <button class="unified-toggle">'
            f'<span class="arrow">▸</span> {len(unified_items)} components already standardized across screens</button>\n'
            f'  <div class="unified-content">\n{items_html}  </div>\n'
            f'</section>'
        )

    # ── Design tokens section ──
    tokens = catalog.get("design_tokens", {})
    if tokens:
        sections.append(_design_tokens_section_html(tokens))

    return "\n\n".join(sections)


def _catalog_card_html(comp: dict, comp_type: str, dark_mode: bool = False, tailwind_head: str = "") -> str:
    """Generate a single component card for the catalog."""
    variant = escape(comp.get("variant", ""))
    text = escape(comp.get("text", "")[:80])
    html_code = comp.get("html", "")
    found_in = comp.get("found_in", [])
    count = comp.get("count", len(found_in))
    styles = comp.get("styles", {})

    # Name: variant + truncated text
    name = f"{variant}: {text}" if variant and text else variant or text or comp_type

    # Style properties pills
    style_pills = ""
    if styles:
        pills = []
        for k, v in list(styles.items())[:4]:
            pills.append(f'<span class="style-prop">{escape(k)}: {escape(v)}</span>')
        if pills:
            style_pills = f'<div class="style-props">{"".join(pills)}</div>'

    # Screen links
    screen_links = ", ".join(
        f'<a href="viewer.html?screen=assets/{escape(s)}.html&title={escape(s)}" target="_blank">{escape(s)}</a>'
        for s in found_in[:5]
    )
    if len(found_in) > 5:
        screen_links += f" +{len(found_in) - 5} more"

    # Escaped HTML for code snippet
    code_escaped = escape(html_code[:500])

    # Preview: render in iframe to isolate from page CSS
    srcdoc = _iframe_srcdoc(html_code, tailwind_head)

    return f"""    <div class="comp-card" data-name="{escape(name)}" data-variant="{variant}">
      <iframe data-srcdoc="{srcdoc}" style="width:100%;height:120px;border:none;pointer-events:none;"></iframe>
      <div class="comp-info">
        <div class="comp-name">{escape(name)}</div>
        <div class="comp-meta">
          <span class="pill">{variant or comp_type}</span>
          <span>Found in {count} screen{"s" if count != 1 else ""}</span>
        </div>
        {style_pills}
        <div class="comp-screens">{screen_links}</div>
        <div class="comp-code">
          <button class="copy-btn">Copy</button>
          <pre>{code_escaped}</pre>
        </div>
      </div>
    </div>"""


def _design_tokens_section_html(tokens: dict) -> str:
    """Generate the design tokens section."""
    groups = []

    # Colors
    colors = tokens.get("colors", {})
    if colors:
        swatches = []
        for color, count in list(colors.items())[:12]:
            swatches.append(
                f'<div class="color-swatch">'
                f'<div class="swatch-circle" style="background:{escape(color)}"></div>'
                f'<span class="swatch-label">{escape(color)} <span style="opacity:0.5">({count}×)</span></span>'
                f'</div>'
            )
        groups.append(
            f'<div class="token-group"><h3>Colors</h3>{"".join(swatches)}</div>'
        )

    # Fonts
    fonts = tokens.get("fonts", [])
    if fonts:
        items = "".join(f"<li>{escape(f)}</li>" for f in fonts)
        groups.append(
            f'<div class="token-group"><h3>Fonts</h3><ul class="token-list">{items}</ul></div>'
        )

    # Border radius
    radii = tokens.get("border_radius", [])
    if radii:
        items = "".join(f"<li>{escape(r)}</li>" for r in radii)
        groups.append(
            f'<div class="token-group"><h3>Border Radius</h3><ul class="token-list">{items}</ul></div>'
        )

    if not groups:
        return ""

    return (
        f'<section class="section" data-category="design-tokens">\n'
        f'  <h2 class="section-title">Design Tokens</h2>\n'
        f'  <div class="tokens-grid">\n{"".join(groups)}\n  </div>\n'
        f'</section>'
    )


# ─── Fallbacks (when reference templates are missing) ─────────────────────────

def _generate_viewer_fallback(output_dir: Path, ptype: str, metadata: dict) -> None:
    """Minimal functional viewer HTML (fallback when template missing)."""
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
  #screen-desc {{ font-size: 12px; color: #888; }}
  main {{ flex: 1; display: flex; align-items: center; justify-content: center;
         overflow: hidden; padding: 20px; }}
  iframe {{ width: 100%; height: 100%; border: none; }}
</style>
</head><body>
<header>
  <button id="btn-back" onclick="location.href='index.html'">← Back</button>
  <span id="screen-title">—</span>
  <span id="screen-desc"></span>
</header>
<main>
  <div style="flex:1;height:100%">
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
    """Minimal functional index HTML (Tailwind CDN, view mode toggle, dark toggle)."""
    cards = "\n".join(_card_html(s, ptype) for s in screens)
    name = escape(metadata["project_name"])
    count = len(screens)

    html = f"""<!DOCTYPE html>
<html lang="en" class="view-{ptype}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name} — Showcase</title>
<script src="https://cdn.tailwindcss.com"></script>
<script>tailwind.config = {{ darkMode: 'class', theme: {{ extend: {{ colors: {{ accent: '#6366f1' }} }} }} }}</script>
<style>
  .view-mobile .card-thumb {{ aspect-ratio: 9/19.5; background: #000; }}
  .view-web .card-thumb {{ aspect-ratio: 16/10; background: #fff; }}
  .view-mobile .screens-grid {{ grid-template-columns: repeat(4, 1fr) !important; }}
  .view-web .screens-grid {{ grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)) !important; }}
</style>
</head>
<body class="bg-gray-100 dark:bg-[#0d0d0d] text-gray-900 dark:text-gray-100 transition-colors duration-200 min-h-screen">
<header class="sticky top-0 z-50 bg-white dark:bg-[#111] border-b border-gray-200 dark:border-white/10 shadow-sm">
  <div class="max-w-[1280px] mx-auto px-6 h-16 flex items-center justify-between gap-4">
    <div class="flex items-baseline gap-3">
      <h1 class="text-lg font-bold">{name}</h1>
      <span class="text-sm text-gray-400">{count} screens</span>
    </div>
    <div class="flex items-center gap-3">
      <button id="theme-toggle" class="w-8 h-8 flex items-center justify-center rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-white/10 transition-colors">
        <svg class="w-4 h-4 block dark:hidden" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
        <svg class="w-4 h-4 hidden dark:block" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/></svg>
      </button>
    </div>
  </div>
</header>
<div class="max-w-[1280px] mx-auto px-6 pt-6 pb-16">
  <div class="screens-grid grid gap-4">
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
    parser.add_argument("--context", action="store_true", help="Generate showcase_context.json only (for AI-driven HTML generation)")
    parser.add_argument("--watch", action="store_true", help="Watch for changes and rebuild automatically")
    parser.add_argument("--init", action="store_true", help="Generate DESIGN.md skeleton and exit")
    parser.add_argument("--update", action="store_true", help="Detect new screens not yet in DESIGN.md and append them under '### Por Clasificar'")
    parser.add_argument("--extract-text", action="store_true", help="Extract visible text from screen HTMLs and write screen_summaries.txt")
    args = parser.parse_args()

    if args.extract_text:
        _extract_text_summaries(args.source, project_type=args.type, project_name=args.name)
    elif args.init:
        _init(args.source, project_type=args.type, project_name=args.name)
    elif args.update:
        _update(args.source, project_type=args.type, project_name=args.name)
    elif args.watch:
        _watch(args.source, project_type=args.type, project_name=args.name)
    elif args.context:
        output = build_context(args.source, project_type=args.type, project_name=args.name)
        print(f"Context: file://{output}/showcase_context.json")
    else:
        output = build(args.source, project_type=args.type, project_name=args.name)
        print(f"Open: file://{output}/index.html")
