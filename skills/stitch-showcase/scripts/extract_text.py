"""
extract_text.py — Extract visible text from Stitch HTML files.

Produces a compact text summary per screen, suitable for LLM consumption
without reading the full HTML. This dramatically reduces token usage when
generating DESIGN.md descriptions.

Usage:
    # As a module (from build_showcase.py):
    from extract_text import extract_visible_text, extract_all_screens_text

    # Standalone:
    python extract_text.py /path/to/assets/  → prints summaries to stdout
"""
import re
import sys
from pathlib import Path
from html import unescape


def extract_visible_text(html_path: Path) -> dict:
    """
    Extract visible text content from a Stitch HTML file.

    Returns a dict with:
        - headings: list of h1-h6 text
        - paragraphs: list of paragraph text
        - buttons: list of button/link text
        - lists: list of li text
        - inputs: list of placeholder/label text
        - meta_title: <title> text if any
        - meta_desc: <meta description> if any
        - css_colors: list of hex colors found in CSS
        - css_fonts: list of font families found in CSS
    """
    if not html_path.exists():
        return {}

    raw = html_path.read_text(encoding="utf-8", errors="replace")

    # Extract meta info before stripping
    meta_title = _extract_meta_title(raw)
    meta_desc = _extract_meta_desc(raw)
    css_colors = _extract_css_colors(raw)
    css_fonts = _extract_css_fonts(raw)

    # Strip non-visible content
    clean = _strip_invisible(raw)

    # Extract structured text
    headings = _extract_by_tag(clean, r"<h[1-6][^>]*>(.*?)</h[1-6]>")
    paragraphs = _extract_by_tag(clean, r"<p[^>]*>(.*?)</p>")
    buttons = _extract_buttons(clean)
    lists = _extract_by_tag(clean, r"<li[^>]*>(.*?)</li>")
    inputs = _extract_inputs(clean)

    return {
        "headings": headings,
        "paragraphs": paragraphs,
        "buttons": buttons,
        "lists": lists,
        "inputs": inputs,
        "meta_title": meta_title,
        "meta_desc": meta_desc,
        "css_colors": css_colors,
        "css_fonts": css_fonts,
    }


def extract_all_screens_text(assets_dir: Path) -> list[dict]:
    """
    Extract text from all HTML files in an assets directory.

    Returns a list of dicts, each with 'slug' and 'text' keys.
    """
    results = []
    html_files = sorted(assets_dir.glob("*.html"))

    for html_path in html_files:
        slug = html_path.stem
        text_data = extract_visible_text(html_path)
        if text_data:
            results.append({"slug": slug, "text": text_data})

    return results


def format_screen_summary(slug: str, text_data: dict) -> str:
    """
    Format extracted text into a compact summary string for LLM consumption.

    Produces ~10-30 lines per screen instead of 200+ lines of raw HTML.
    """
    lines = [f"## {slug}"]

    if text_data.get("meta_title"):
        lines.append(f"Title: {text_data['meta_title']}")

    if text_data.get("meta_desc"):
        lines.append(f"Description: {text_data['meta_desc']}")

    if text_data.get("headings"):
        lines.append(f"Headings: {' | '.join(text_data['headings'][:10])}")

    if text_data.get("paragraphs"):
        # Truncate long paragraphs
        paras = [p[:150] for p in text_data["paragraphs"][:5]]
        lines.append(f"Text: {' // '.join(paras)}")

    if text_data.get("buttons"):
        lines.append(f"Buttons: {', '.join(text_data['buttons'][:15])}")

    if text_data.get("lists"):
        lines.append(f"List items: {', '.join(text_data['lists'][:15])}")

    if text_data.get("inputs"):
        lines.append(f"Inputs: {', '.join(text_data['inputs'][:10])}")

    if text_data.get("css_colors"):
        lines.append(f"Colors: {', '.join(text_data['css_colors'][:10])}")

    if text_data.get("css_fonts"):
        lines.append(f"Fonts: {', '.join(text_data['css_fonts'][:5])}")

    return "\n".join(lines)


def format_all_summaries(screen_texts: list[dict]) -> str:
    """Format all screen summaries into a single string."""
    parts = []
    for item in screen_texts:
        summary = format_screen_summary(item["slug"], item["text"])
        parts.append(summary)
    return "\n\n".join(parts)


# ─── Internal helpers ──────────────────────────────────────────────────────────


def _strip_invisible(html: str) -> str:
    """Remove script, style, svg, noscript, and HTML comments."""
    # Remove script blocks
    html = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
    # Remove style blocks
    html = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.DOTALL | re.IGNORECASE)
    # Remove SVG blocks
    html = re.sub(r"<svg[^>]*>.*?</svg>", "", html, flags=re.DOTALL | re.IGNORECASE)
    # Remove noscript
    html = re.sub(r"<noscript[^>]*>.*?</noscript>", "", html, flags=re.DOTALL | re.IGNORECASE)
    # Remove HTML comments
    html = re.sub(r"<!--.*?-->", "", html, flags=re.DOTALL)
    return html


def _strip_tags(text: str) -> str:
    """Remove all HTML tags and decode entities."""
    text = re.sub(r"<[^>]+>", " ", text)
    text = unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _extract_by_tag(html: str, pattern: str) -> list[str]:
    """Extract and clean text matching a regex pattern."""
    matches = re.findall(pattern, html, flags=re.DOTALL | re.IGNORECASE)
    results = []
    for m in matches:
        clean = _strip_tags(m).strip()
        if clean and len(clean) > 1:
            results.append(clean)
    return results


def _extract_buttons(html: str) -> list[str]:
    """Extract text from buttons and clickable links."""
    patterns = [
        r"<button[^>]*>(.*?)</button>",
        r'<a[^>]*class="[^"]*btn[^"]*"[^>]*>(.*?)</a>',
        r'<a[^>]*role="button"[^>]*>(.*?)</a>',
        r'<input[^>]*type="submit"[^>]*value="([^"]*)"',
    ]
    results = []
    for pat in patterns:
        for m in re.findall(pat, html, flags=re.DOTALL | re.IGNORECASE):
            clean = _strip_tags(m).strip()
            if clean and len(clean) > 1:
                results.append(clean)
    return results


def _extract_inputs(html: str) -> list[str]:
    """Extract placeholder text and labels from form elements."""
    results = []
    # Placeholders
    for m in re.findall(r'placeholder="([^"]*)"', html, flags=re.IGNORECASE):
        if m.strip():
            results.append(m.strip())
    # Labels
    for m in re.findall(r"<label[^>]*>(.*?)</label>", html, flags=re.DOTALL | re.IGNORECASE):
        clean = _strip_tags(m).strip()
        if clean and len(clean) > 1:
            results.append(clean)
    return results


def _extract_meta_title(html: str) -> str:
    """Extract <title> content."""
    m = re.search(r"<title[^>]*>(.*?)</title>", html, flags=re.DOTALL | re.IGNORECASE)
    if m:
        title = _strip_tags(m.group(1)).strip()
        # Skip generic titles
        if title.lower() not in ("untitled", "index", "screen", "document", ""):
            return title
    return ""


def _extract_meta_desc(html: str) -> str:
    """Extract meta description."""
    m = re.search(r'<meta[^>]*name="description"[^>]*content="([^"]*)"', html, flags=re.IGNORECASE)
    if not m:
        m = re.search(r'<meta[^>]*property="og:description"[^>]*content="([^"]*)"', html, flags=re.IGNORECASE)
    return m.group(1).strip() if m else ""


def _extract_css_colors(html: str) -> list[str]:
    """Extract unique hex colors from inline styles and style blocks."""
    colors = set()
    for m in re.findall(r"#([0-9a-fA-F]{6})\b", html):
        hex_val = f"#{m.upper()}"
        # Skip near-black and near-white (too common/generic)
        if hex_val not in ("#000000", "#FFFFFF", "#000", "#FFF"):
            colors.add(hex_val)
    return sorted(colors)[:10]


def _extract_css_fonts(html: str) -> list[str]:
    """Extract font-family declarations from CSS."""
    fonts = set()
    for m in re.findall(r"font-family:\s*['\"]?([^;'\"}{,]+)", html, flags=re.IGNORECASE):
        font = m.strip().strip("'\"")
        if font.lower() not in ("inherit", "initial", "unset", "sans-serif", "serif", "monospace", "system-ui"):
            fonts.add(font)
    # Also check Google Fonts links
    for m in re.findall(r"fonts\.googleapis\.com/css2?\?family=([^&\"' ]+)", html):
        font = m.replace("+", " ").split(":")[0]
        fonts.add(font)
    return sorted(fonts)


# ─── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_text.py /path/to/assets/", file=sys.stderr)
        sys.exit(1)

    assets = Path(sys.argv[1]).resolve()
    if not assets.is_dir():
        print(f"Error: '{assets}' is not a directory.", file=sys.stderr)
        sys.exit(1)

    screen_texts = extract_all_screens_text(assets)
    if not screen_texts:
        print("No HTML files found.", file=sys.stderr)
        sys.exit(1)

    print(format_all_summaries(screen_texts))
    print(f"\n--- {len(screen_texts)} screens extracted ---", file=sys.stderr)
