"""
extract_catalog.py — Extract atomic and composite UI components from Stitch HTMLs.

Produces a component catalog with deduplication, variant detection, and
design token extraction. Output is a JSON suitable for visual catalog generation.

Uses only stdlib (html.parser, re, json, hashlib). No external dependencies.

Usage:
    # As a module (from build_showcase.py):
    from extract_catalog import extract_component_catalog

    # Standalone:
    python extract_catalog.py /path/to/assets/
"""
import re
import sys
import json
from pathlib import Path
from html import unescape

# Sibling import
sys.path.insert(0, str(Path(__file__).parent))
import component_utils as cu


# ─── Tailwind / Head Extraction ──────────────────────────────────────────────

def extract_tailwind_head(assets_dir: Path) -> str:
    """
    Extract Tailwind CDN script, config block, and Google Fonts links
    from the first screen HTML.

    All Stitch screens share the same Tailwind config, so reading one is enough.

    Returns an HTML string safe to inject into a <head> section.
    """
    html_files = sorted(assets_dir.glob("*.html"))
    if not html_files:
        return ""

    try:
        html = html_files[0].read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""

    parts = []

    # 1. Google Fonts <link> tags
    for m in re.finditer(
        r'<link[^>]*href="[^"]*fonts\.googleapis\.com[^"]*"[^>]*/?\s*>',
        html, re.IGNORECASE,
    ):
        parts.append(m.group(0))

    # Also grab preconnect links for fonts
    for m in re.finditer(
        r'<link[^>]*rel="preconnect"[^>]*href="[^"]*(?:fonts\.googleapis|fonts\.gstatic)[^"]*"[^>]*/?\s*>',
        html, re.IGNORECASE,
    ):
        tag = m.group(0)
        if tag not in parts:
            parts.append(tag)

    # 2. Tailwind CDN <script src="...tailwindcss..."> tag
    for m in re.finditer(
        r'<script[^>]*src="[^"]*tailwindcss[^"]*"[^>]*>\s*</script>',
        html, re.IGNORECASE,
    ):
        parts.append(m.group(0))

    # 3. Tailwind config <script> block (may have id="tailwind-config" or inline)
    #    Match script blocks containing "tailwind.config"
    for m in re.finditer(
        r'<script[^>]*>([^<]*tailwind\.config\s*=\s*\{.*?)</script>',
        html, re.DOTALL | re.IGNORECASE,
    ):
        parts.append(f"<script>{m.group(1)}</script>")

    return "\n  ".join(parts)


# ─── Atomic Component Extractors ──────────────────────────────────────────────

def _extract_buttons(html: str, slug: str) -> list:
    """Extract button components: <button>, <a.btn>, <input type=submit>."""
    buttons = []

    patterns = [
        (r"<button[^>]*>.*?</button>", "button"),
        (r'<a[^>]*class="[^"]*\bbtn\b[^"]*"[^>]*>.*?</a>', "link-button"),
        (r'<a[^>]*role="button"[^>]*>.*?</a>', "link-button"),
        (r'<input[^>]*type="submit"[^>]*/?\s*>', "submit"),
    ]

    for pattern, btn_type in patterns:
        for m in re.finditer(pattern, html, re.DOTALL | re.IGNORECASE):
            block = m.group(0)
            text = cu.strip_tags(block).strip()
            if not text or len(text) > 100:
                continue

            classes = cu.extract_css_classes_from_block(block)
            variant = cu.detect_button_variant(block, classes)
            styles = cu.extract_inline_styles(block)

            buttons.append({
                "type": "button",
                "subtype": btn_type,
                "variant": variant,
                "text": text,
                "html": block,
                "hash": cu.html_hash(block),
                "classes": classes,
                "styles": _pick_style_props(styles, ["background-color", "background", "color",
                                                      "border-radius", "padding", "font-size"]),
                "found_in": [slug],
            })

    return buttons


def _extract_headings(html: str, slug: str) -> list:
    """Extract heading components: h1-h6."""
    headings = []

    for m in re.finditer(r"<(h[1-6])[^>]*>(.*?)</\1>", html, re.DOTALL | re.IGNORECASE):
        tag = m.group(1).lower()
        block = m.group(0)
        text = cu.strip_tags(m.group(2)).strip()
        if not text or len(text) > 200:
            continue

        # Get the full tag with attributes
        classes = cu.extract_css_classes_from_block(block)
        styles = cu.extract_inline_styles(block)

        headings.append({
            "type": "heading",
            "subtype": tag,
            "text": text,
            "html": block,
            "hash": cu.html_hash(block),
            "classes": classes,
            "styles": _pick_style_props(styles, ["font-size", "font-weight", "color",
                                                  "font-family", "line-height"]),
            "found_in": [slug],
        })

    return headings


def _extract_inputs(html: str, slug: str) -> list:
    """Extract form input components: input, select, textarea."""
    inputs = []

    # Input fields
    for m in re.finditer(r"<input[^>]*/?\s*>", html, re.IGNORECASE):
        block = m.group(0)
        input_type = re.search(r'type="([^"]*)"', block, re.IGNORECASE)
        input_type = input_type.group(1).lower() if input_type else "text"

        # Skip hidden, submit (captured as buttons), and checkbox/radio (too simple)
        if input_type in ("hidden", "submit"):
            continue

        placeholder = re.search(r'placeholder="([^"]*)"', block, re.IGNORECASE)
        label_text = placeholder.group(1) if placeholder else input_type

        classes = cu.extract_css_classes_from_block(block)
        styles = cu.extract_inline_styles(block)

        inputs.append({
            "type": "input",
            "subtype": input_type,
            "text": label_text,
            "html": block,
            "hash": cu.html_hash(block),
            "classes": classes,
            "styles": _pick_style_props(styles, ["border", "border-radius", "padding",
                                                  "background-color", "color", "font-size"]),
            "found_in": [slug],
        })

    # Textareas
    for m in re.finditer(r"<textarea[^>]*>.*?</textarea>", html, re.DOTALL | re.IGNORECASE):
        block = m.group(0)
        placeholder = re.search(r'placeholder="([^"]*)"', block, re.IGNORECASE)
        label_text = placeholder.group(1) if placeholder else "textarea"

        inputs.append({
            "type": "input",
            "subtype": "textarea",
            "text": label_text,
            "html": block,
            "hash": cu.html_hash(block),
            "classes": cu.extract_css_classes_from_block(block),
            "styles": cu.extract_inline_styles(block),
            "found_in": [slug],
        })

    # Selects
    for m in re.finditer(r"<select[^>]*>.*?</select>", html, re.DOTALL | re.IGNORECASE):
        block = m.group(0)
        # Get first option text
        opt = re.search(r"<option[^>]*>(.*?)</option>", block, re.DOTALL | re.IGNORECASE)
        label_text = cu.strip_tags(opt.group(1)).strip() if opt else "select"

        inputs.append({
            "type": "input",
            "subtype": "select",
            "text": label_text,
            "html": block,
            "hash": cu.html_hash(block),
            "classes": cu.extract_css_classes_from_block(block),
            "styles": cu.extract_inline_styles(block),
            "found_in": [slug],
        })

    return inputs


def _extract_badges(html: str, slug: str) -> list:
    """Extract badge/tag/pill components."""
    badges = []

    patterns = [
        r'<span[^>]*class="[^"]*\b(?:badge|tag|pill|chip|label)\b[^"]*"[^>]*>.*?</span>',
        r'<div[^>]*class="[^"]*\b(?:badge|tag|pill|chip)\b[^"]*"[^>]*>.*?</div>',
    ]

    for pattern in patterns:
        for m in re.finditer(pattern, html, re.DOTALL | re.IGNORECASE):
            block = m.group(0)
            text = cu.strip_tags(block).strip()
            if not text or len(text) > 50:
                continue

            badges.append({
                "type": "badge",
                "subtype": "badge",
                "text": text,
                "html": block,
                "hash": cu.html_hash(block),
                "classes": cu.extract_css_classes_from_block(block),
                "styles": cu.extract_inline_styles(block),
                "found_in": [slug],
            })

    return badges


def _extract_links(html: str, slug: str) -> list:
    """Extract standalone link components (not inside nav or buttons)."""
    links = []

    # Remove nav blocks to avoid capturing navigation links
    clean_html = re.sub(r"<nav[^>]*>.*?</nav>", "", html, flags=re.DOTALL | re.IGNORECASE)
    # Remove button-like links (already captured)
    clean_html = re.sub(r'<a[^>]*class="[^"]*\bbtn\b[^"]*"[^>]*>.*?</a>', "", clean_html, flags=re.DOTALL | re.IGNORECASE)
    clean_html = re.sub(r'<a[^>]*role="button"[^>]*>.*?</a>', "", clean_html, flags=re.DOTALL | re.IGNORECASE)

    for m in re.finditer(r"<a[^>]*>.*?</a>", clean_html, re.DOTALL | re.IGNORECASE):
        block = m.group(0)
        text = cu.strip_tags(block).strip()
        if not text or len(text) > 80 or len(text) < 2:
            continue

        # Skip if it's just an image link
        if re.search(r"<img[^>]*>", block, re.IGNORECASE) and not text.replace(" ", ""):
            continue

        links.append({
            "type": "link",
            "subtype": "link",
            "text": text,
            "html": block,
            "hash": cu.html_hash(block),
            "classes": cu.extract_css_classes_from_block(block),
            "styles": cu.extract_inline_styles(block),
            "found_in": [slug],
        })

    return links


def _extract_icons(html: str, slug: str) -> list:
    """Extract icon components: Material Symbols spans, icon SVGs."""
    icons = []

    # Material Symbols
    for m in re.finditer(
        r'<span[^>]*class="[^"]*\bmaterial[_-]symbols?[^"]*"[^>]*>(.*?)</span>',
        html, re.DOTALL | re.IGNORECASE,
    ):
        block = m.group(0)
        name = cu.strip_tags(m.group(1)).strip()
        if not name:
            continue

        icons.append({
            "type": "icon",
            "subtype": "material-symbols",
            "text": name,
            "html": block,
            "hash": cu.html_hash(block),
            "classes": cu.extract_css_classes_from_block(block),
            "styles": {},
            "found_in": [slug],
        })

    # SVG icons with icon class
    for m in re.finditer(
        r'<svg[^>]*class="[^"]*\bicon\b[^"]*"[^>]*>.*?</svg>',
        html, re.DOTALL | re.IGNORECASE,
    ):
        block = m.group(0)
        icons.append({
            "type": "icon",
            "subtype": "svg",
            "text": "svg-icon",
            "html": block,
            "hash": cu.html_hash(block),
            "classes": [],
            "styles": {},
            "found_in": [slug],
        })

    return icons


# ─── Composite Component Extractors ──────────────────────────────────────────

def _extract_cards(html: str, slug: str) -> list:
    """Extract card components: divs with card/shadow classes containing image + text."""
    cards = []

    patterns = [
        r'<div[^>]*class="[^"]*\b(?:card|shadow)\b[^"]*"[^>]*>.*?</div>\s*</div>',
        r'<article[^>]*class="[^"]*\b(?:card)\b[^"]*"[^>]*>.*?</article>',
        r'<div[^>]*class="[^"]*\bcard\b[^"]*"[^>]*>(?:(?!<div[^>]*class="[^"]*\bcard\b).)*?</div>',
    ]

    for pattern in patterns:
        for m in re.finditer(pattern, html, re.DOTALL | re.IGNORECASE):
            block = m.group(0)
            text = cu.strip_tags(block).strip()

            # Cards should have some substance (text + possibly image)
            if len(text) < 10:
                continue
            # Skip if too large (probably a wrapper, not a card)
            if len(block) > 5000:
                continue

            has_image = bool(re.search(r"<img[^>]*>", block, re.IGNORECASE))
            has_heading = bool(re.search(r"<h[1-6][^>]*>", block, re.IGNORECASE))

            cards.append({
                "type": "card",
                "subtype": "card",
                "text": text[:150],
                "html": block,
                "hash": cu.html_hash(block),
                "classes": cu.extract_css_classes_from_block(block),
                "styles": cu.extract_inline_styles(block),
                "has_image": has_image,
                "has_heading": has_heading,
                "found_in": [slug],
            })

    return cards


def _extract_price_tables(html: str, slug: str) -> list:
    """Extract price table/pricing card components."""
    tables = []

    # Look for sections containing price indicators
    price_pattern = re.compile(
        r'<(?:div|section|article)[^>]*>(?=.*?(?:\$|€|£|price|plan|pricing|mes|month|year|año))'
        r'.*?</(?:div|section|article)>',
        re.DOTALL | re.IGNORECASE,
    )

    for m in price_pattern.finditer(html):
        block = m.group(0)
        text = cu.strip_tags(block).strip()

        # Must have actual price content
        if not re.search(r"[\$€£]\s*\d+|(?:free|gratis)", text, re.IGNORECASE):
            continue
        if len(block) > 8000:
            continue

        tables.append({
            "type": "price_table",
            "subtype": "pricing",
            "text": text[:200],
            "html": block,
            "hash": cu.html_hash(block),
            "classes": cu.extract_css_classes_from_block(block),
            "styles": cu.extract_inline_styles(block),
            "found_in": [slug],
        })

    return tables


def _extract_ctas(html: str, slug: str) -> list:
    """Extract CTA (call-to-action) sections: heading + text + prominent button."""
    ctas = []

    # Look for sections with heading + button combo
    section_pattern = re.compile(
        r'<(?:section|div)[^>]*>((?:(?!<(?:section|footer|header|nav)\b).)*?'
        r'<h[1-3][^>]*>.*?</h[1-3]>'
        r'(?:(?!<(?:section|footer|header|nav)\b).)*?'
        r'<(?:button|a[^>]*class="[^"]*btn)[^>]*>.*?</(?:button|a)>'
        r'(?:(?!<(?:section|footer|header|nav)\b).)*?'
        r')</(?:section|div)>',
        re.DOTALL | re.IGNORECASE,
    )

    for m in section_pattern.finditer(html):
        block = m.group(0)
        text = cu.strip_tags(block).strip()

        if len(text) < 20 or len(block) > 5000:
            continue

        ctas.append({
            "type": "cta",
            "subtype": "cta",
            "text": text[:200],
            "html": block,
            "hash": cu.html_hash(block),
            "classes": cu.extract_css_classes_from_block(block),
            "styles": cu.extract_inline_styles(block),
            "found_in": [slug],
        })

    return ctas


def _extract_testimonials(html: str, slug: str) -> list:
    """Extract testimonial/quote blocks."""
    testimonials = []

    patterns = [
        r'<(?:div|blockquote)[^>]*class="[^"]*\b(?:testimonial|quote|review)\b[^"]*"[^>]*>.*?</(?:div|blockquote)>',
        r'<blockquote[^>]*>.*?</blockquote>',
    ]

    for pattern in patterns:
        for m in re.finditer(pattern, html, re.DOTALL | re.IGNORECASE):
            block = m.group(0)
            text = cu.strip_tags(block).strip()
            if len(text) < 15 or len(block) > 5000:
                continue

            testimonials.append({
                "type": "testimonial",
                "subtype": "testimonial",
                "text": text[:200],
                "html": block,
                "hash": cu.html_hash(block),
                "classes": cu.extract_css_classes_from_block(block),
                "styles": cu.extract_inline_styles(block),
                "found_in": [slug],
            })

    return testimonials


def _extract_hero_sections(html: str, slug: str) -> list:
    """Extract hero sections: first large section with heading + text + button."""
    heroes = []

    # First section or large div at the top of body
    body_match = re.search(r"<body[^>]*>(.*)", html, re.DOTALL | re.IGNORECASE)
    if not body_match:
        return []

    body = body_match.group(1)

    # Remove nav/header from consideration
    body_clean = re.sub(r"<(?:nav|header)[^>]*>.*?</(?:nav|header)>", "", body, flags=re.DOTALL | re.IGNORECASE)

    # Find first section/div with a heading
    hero_pattern = re.compile(
        r'<(?:section|div)[^>]*>(?:(?!<(?:section)\b).)*?<h[12][^>]*>.*?</h[12]>.*?</(?:section|div)>',
        re.DOTALL | re.IGNORECASE,
    )

    m = hero_pattern.search(body_clean)
    if m:
        block = m.group(0)
        text = cu.strip_tags(block).strip()
        if 20 < len(text) < 1000 and len(block) < 8000:
            has_button = bool(re.search(r"<(?:button|a[^>]*btn)", block, re.IGNORECASE))
            heroes.append({
                "type": "hero",
                "subtype": "hero",
                "text": text[:250],
                "html": block,
                "hash": cu.html_hash(block),
                "classes": cu.extract_css_classes_from_block(block),
                "styles": cu.extract_inline_styles(block),
                "has_button": has_button,
                "found_in": [slug],
            })

    return heroes


# ─── Design Token Extraction ─────────────────────────────────────────────────

def _extract_design_tokens(html_files: list) -> dict:
    """
    Extract design tokens (colors, fonts, border-radius) from all HTML files.

    Returns aggregated tokens with usage frequency.
    """
    colors = {}
    fonts = {}
    radii = {}

    for html_path in html_files:
        try:
            html = html_path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue

        # Colors
        for m in re.finditer(r"(?:color|background(?:-color)?)\s*:\s*(#[0-9a-fA-F]{3,8})\b", html):
            c = m.group(1).upper()
            if len(c) == 4:
                c = f"#{c[1]*2}{c[2]*2}{c[3]*2}"
            if c not in ("#000000", "#FFFFFF"):
                colors[c] = colors.get(c, 0) + 1

        # Also from CSS variables
        for m in re.finditer(r"--[a-z\-]+\s*:\s*(#[0-9a-fA-F]{6})\b", html, re.IGNORECASE):
            c = m.group(1).upper()
            if c not in ("#000000", "#FFFFFF"):
                colors[c] = colors.get(c, 0) + 1

        # Fonts
        for m in re.finditer(r"font-family:\s*['\"]?([A-Z][a-zA-Z\s]+)", html):
            f = m.group(1).strip().rstrip(",")
            if f.lower() not in ("sans-serif", "serif", "monospace", "system-ui", "inherit"):
                fonts[f] = fonts.get(f, 0) + 1

        for m in re.finditer(r"fonts\.googleapis\.com/css2?\?family=([^&\"' ]+)", html):
            f = m.group(1).replace("+", " ").split(":")[0]
            fonts[f] = fonts.get(f, 0) + 1

        # Border radius
        for m in re.finditer(r"border-radius\s*:\s*([^;}{\"]+)", html, re.IGNORECASE):
            r_val = m.group(1).strip()
            if r_val and r_val != "0":
                radii[r_val] = radii.get(r_val, 0) + 1

    # Sort by frequency, take top values
    top_colors = sorted(colors.items(), key=lambda x: -x[1])[:12]
    top_fonts = sorted(fonts.items(), key=lambda x: -x[1])[:5]
    top_radii = sorted(radii.items(), key=lambda x: -x[1])[:6]

    # Try to identify primary color (most used non-gray)
    primary = None
    for c, _ in top_colors:
        hex_clean = c.lstrip("#")
        try:
            r, g, b = int(hex_clean[0:2], 16), int(hex_clean[2:4], 16), int(hex_clean[4:6], 16)
        except (ValueError, IndexError):
            continue
        # Skip near-grays
        if max(abs(r-g), abs(g-b), abs(r-b)) > 30:
            primary = c
            break

    return {
        "colors": {c: count for c, count in top_colors},
        "primary": primary,
        "fonts": [f for f, _ in top_fonts],
        "border_radius": [r for r, _ in top_radii],
    }


# ─── Context Detection ──────────────────────────────────────────────────────

_CONTEXT_TAGS = {"form", "section", "header", "footer", "nav", "aside", "main", "article"}


def _detect_context(html: str, match_start: int) -> str:
    """
    Determine the semantic context of an extracted component by finding
    its nearest ancestor semantic tag.

    Returns a context string like 'form', 'header', 'nav', or 'content' (default).
    """
    # Search backwards from match position for the nearest opening semantic tag
    preceding = html[:match_start]

    best_tag = "content"
    best_pos = -1

    for tag in _CONTEXT_TAGS:
        # Find the last opening tag of this type before the match
        pos = preceding.rfind(f"<{tag}")
        if pos == -1:
            pos = preceding.rfind(f"<{tag.upper()}")
        if pos > best_pos:
            # Make sure it hasn't been closed before our position
            close_pos = preceding.rfind(f"</{tag}>", pos)
            if close_pos == -1:
                close_pos = preceding.rfind(f"</{tag.upper()}>", pos)
            if close_pos == -1:  # tag is still open at our position
                best_tag = tag
                best_pos = pos

    return best_tag


def _extract_with_context(html: str, pattern: str, flags: int = re.DOTALL | re.IGNORECASE):
    """Yield (match, context) tuples for each regex match with its semantic context."""
    for m in re.finditer(pattern, html, flags):
        context = _detect_context(html, m.start())
        yield m, context


# ─── Similarity Clustering for Atomics ──────────────────────────────────────

ATOMIC_SIMILARITY_THRESHOLD = 0.85


def _cluster_atomic_components(components: list) -> list:
    """
    Cluster similar atomic components using weighted similarity scoring.

    Groups components that are similar in structure (>= 85% threshold) and
    share the same context (form buttons separate from CTA buttons).

    Returns list of cluster dicts:
    {
        "canonical": <component>,
        "variants": [<component>, ...],
        "similarity": <float>,
        "context": <str>,
    }
    """
    if not components:
        return []

    # Group by context first
    by_context = {}
    for comp in components:
        ctx = comp.get("context", "content")
        by_context.setdefault(ctx, []).append(comp)

    clusters = []
    for context, group in by_context.items():
        # Greedy clustering within this context
        context_clusters = []
        for comp in group:
            placed = False
            for cluster in context_clusters:
                rep = cluster[0]
                score = cu.component_similarity(rep["html"], comp["html"])
                if score >= ATOMIC_SIMILARITY_THRESHOLD:
                    cluster.append(comp)
                    placed = True
                    break
            if not placed:
                context_clusters.append([comp])

        # Convert to cluster dicts with canonical selection
        for group_members in context_clusters:
            if len(group_members) < 1:
                continue

            canonical = _choose_atomic_canonical(group_members)
            variants = [c for c in group_members if c is not canonical]

            # Compute similarity scores for variants
            variant_data = []
            for v in variants:
                sim = cu.component_similarity(canonical["html"], v["html"])
                variant_data.append({**v, "_similarity": round(sim, 3)})

            clusters.append({
                "canonical": canonical,
                "variants": variant_data,
                "context": context,
            })

    return clusters


def _choose_atomic_canonical(group: list) -> dict:
    """
    Choose the canonical version of an atomic component.

    Priority: home-like slug → most found_in screens → most DOM nodes → first.
    """
    HOME_SLUGS = {"home", "main", "dashboard", "inicio", "principal", "landing", "index"}

    def sort_key(comp):
        slugs = comp.get("found_in", [])
        is_home = any(any(h in s for h in HOME_SLUGS) for s in slugs)
        node_count = cu.count_dom_nodes(comp.get("html", ""))
        return (-int(is_home), -len(slugs), -node_count)

    return sorted(group, key=sort_key)[0]


# ─── Main Catalog Builder ────────────────────────────────────────────────────

def extract_component_catalog(assets_dir: Path) -> dict:
    """
    Extract all atomic and composite components from screen HTMLs.

    Args:
        assets_dir: Directory containing screen .html files

    Returns:
        Complete catalog dict with 'atomic', 'composite', 'design_tokens', and 'clusters' keys.
    """
    html_files = sorted(assets_dir.glob("*.html"))
    if not html_files:
        return {}

    # Collect all components across screens
    all_components = []

    for html_path in html_files:
        slug = html_path.stem
        try:
            html = html_path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue

        # Strip invisible content for component extraction
        clean = _strip_invisible(html)

        # Atomic components (with context detection)
        for extractor in (_extract_buttons, _extract_headings, _extract_inputs,
                          _extract_badges, _extract_links, _extract_icons):
            components = extractor(clean, slug)
            # Add context to each atomic component
            for comp in components:
                comp["context"] = _detect_context(clean, clean.find(comp["html"][:50])) if comp["html"] else "content"
            all_components.extend(components)

        # Composite components
        all_components.extend(_extract_cards(clean, slug))
        all_components.extend(_extract_price_tables(html, slug))
        all_components.extend(_extract_ctas(clean, slug))
        all_components.extend(_extract_testimonials(clean, slug))
        all_components.extend(_extract_hero_sections(html, slug))

    # Deduplicate by normalized HTML hash
    deduped = _deduplicate_components(all_components)

    # Organize into catalog structure
    catalog = _organize_catalog(deduped)

    # Build similarity clusters for atomic components
    atomic_types = {"button", "heading", "input", "badge", "link", "icon"}
    clusters_by_type = {}
    for comp in deduped:
        if comp["type"] in atomic_types:
            clusters_by_type.setdefault(comp["type"], []).append(comp)

    catalog["clusters"] = {}
    for comp_type, components in clusters_by_type.items():
        type_clusters = _cluster_atomic_components(components)
        if type_clusters:
            catalog["clusters"][f"{comp_type}s"] = [
                {
                    "canonical": {
                        "text": c["canonical"].get("text", ""),
                        "variant": c["canonical"].get("variant", c["canonical"].get("subtype", "")),
                        "found_in": c["canonical"].get("found_in", []),
                        "html": c["canonical"].get("html", ""),
                    },
                    "variants": [
                        {
                            "text": v.get("text", ""),
                            "variant": v.get("variant", v.get("subtype", "")),
                            "found_in": v.get("found_in", []),
                            "similarity": v.get("_similarity", 0),
                            "html": v.get("html", ""),
                        }
                        for v in c["variants"]
                    ],
                    "context": c["context"],
                }
                for c in type_clusters
            ]

    # Extract design tokens
    catalog["design_tokens"] = _extract_design_tokens(html_files)

    return catalog


def _strip_invisible(html: str) -> str:
    """Remove script, style, and noscript blocks (keep SVG for icon detection)."""
    html = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<noscript[^>]*>.*?</noscript>", "", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<!--.*?-->", "", html, flags=re.DOTALL)
    return html


def _deduplicate_components(components: list) -> list:
    """
    Deduplicate components by normalized HTML hash.

    Same hash = same component structure, just merge found_in lists and increment count.
    """
    seen = {}
    for comp in components:
        h = comp["hash"]
        if h in seen:
            # Merge found_in
            existing = seen[h]
            for slug in comp["found_in"]:
                if slug not in existing["found_in"]:
                    existing["found_in"].append(slug)
        else:
            seen[h] = comp

    return list(seen.values())


def _organize_catalog(components: list) -> dict:
    """Organize flat component list into atomic/composite categories."""
    atomic_types = {"button", "heading", "input", "badge", "link", "icon"}
    composite_types = {"card", "price_table", "cta", "testimonial", "hero"}

    atomic = {}
    composite = {}

    for comp in components:
        comp_type = comp["type"]
        # Build output entry
        entry = {
            "variant": comp.get("variant", comp.get("subtype", "")),
            "text": comp.get("text", ""),
            "html": comp["html"],
            "styles": comp.get("styles", {}),
            "found_in": comp["found_in"],
            "count": len(comp["found_in"]),
        }

        if comp_type in atomic_types:
            key = f"{comp_type}s"
            atomic.setdefault(key, []).append(entry)
        elif comp_type in composite_types:
            key = f"{comp_type}s"
            composite.setdefault(key, []).append(entry)

    # Sort each category: most frequent first
    for key in atomic:
        atomic[key].sort(key=lambda x: -x["count"])
    for key in composite:
        composite[key].sort(key=lambda x: -x["count"])

    return {"atomic": atomic, "composite": composite}


# ─── Utility ──────────────────────────────────────────────────────────────────

def _pick_style_props(styles: dict, keys: list) -> dict:
    """Pick only the specified CSS property keys from a styles dict."""
    return {k: v for k, v in styles.items() if k in keys}


# ─── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_catalog.py /path/to/assets/", file=sys.stderr)
        sys.exit(1)

    assets = Path(sys.argv[1]).resolve()
    if not assets.is_dir():
        print(f"Error: '{assets}' is not a directory.", file=sys.stderr)
        sys.exit(1)

    result = extract_component_catalog(assets)
    if not result:
        print("No components found.", file=sys.stderr)
        sys.exit(0)

    # Print without html field (too verbose for CLI)
    def _strip_html_field(obj):
        if isinstance(obj, dict):
            return {k: _strip_html_field(v) for k, v in obj.items() if k != "html"}
        if isinstance(obj, list):
            return [_strip_html_field(i) for i in obj]
        return obj

    summary = _strip_html_field(result)
    print(json.dumps(summary, ensure_ascii=False, indent=2))

    # Stats
    atomic_count = sum(len(v) for v in result.get("atomic", {}).values())
    composite_count = sum(len(v) for v in result.get("composite", {}).values())
    print(f"\n--- {atomic_count} atomic + {composite_count} composite components ---", file=sys.stderr)
