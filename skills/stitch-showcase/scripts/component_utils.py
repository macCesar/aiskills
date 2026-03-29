"""
component_utils.py — Shared HTML parsing helpers for component detection and catalog.

Uses only stdlib (html.parser, re, difflib). No external dependencies.

Usage:
    from component_utils import (
        parse_dom_tree, extract_semantic_blocks, dom_signature,
        normalize_html, text_similarity, strip_tags, extract_inline_styles,
    )
"""
import re
import hashlib
from html.parser import HTMLParser
from difflib import SequenceMatcher


# ─── DOM Tree Parser ──────────────────────────────────────────────────────────

class _DOMNode:
    """Lightweight DOM node for tree comparison."""
    __slots__ = ("tag", "attrs", "children", "text", "classes")

    def __init__(self, tag: str, attrs: dict = None):
        self.tag = tag
        self.attrs = attrs or {}
        self.children = []
        self.text = ""
        self.classes = self.attrs.get("class", "").split()

    def node_count(self) -> int:
        return 1 + sum(c.node_count() for c in self.children)

    def to_signature(self) -> str:
        """Tag-only tree string for structural comparison."""
        if not self.children:
            return self.tag
        child_sigs = " ".join(c.to_signature() for c in self.children)
        return f"{self.tag}({child_sigs})"

    def to_dict(self) -> dict:
        return {
            "tag": self.tag,
            "classes": self.classes,
            "text": self.text.strip()[:200] if self.text else "",
            "children": [c.to_dict() for c in self.children],
        }


class _TreeBuilder(HTMLParser):
    """Build a simplified DOM tree from HTML."""

    VOID_TAGS = frozenset([
        "area", "base", "br", "col", "embed", "hr", "img", "input",
        "link", "meta", "param", "source", "track", "wbr",
    ])
    SKIP_TAGS = frozenset(["script", "style", "svg", "noscript"])

    def __init__(self):
        super().__init__()
        self.root = _DOMNode("root")
        self._stack = [self.root]
        self._skip_depth = 0

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if self._skip_depth > 0:
            if tag not in self.VOID_TAGS:
                self._skip_depth += 1
            return
        if tag in self.SKIP_TAGS:
            self._skip_depth = 1
            return

        attr_dict = {k: v for k, v in attrs if k and v}
        node = _DOMNode(tag, attr_dict)
        self._stack[-1].children.append(node)
        if tag not in self.VOID_TAGS:
            self._stack.append(node)

    def handle_endtag(self, tag):
        tag = tag.lower()
        if self._skip_depth > 0:
            self._skip_depth -= 1
            return
        if tag in self.VOID_TAGS or tag in self.SKIP_TAGS:
            return
        if len(self._stack) > 1 and self._stack[-1].tag == tag:
            self._stack.pop()

    def handle_data(self, data):
        if self._skip_depth > 0:
            return
        text = data.strip()
        if text and self._stack:
            self._stack[-1].text += " " + text


def parse_dom_tree(html: str) -> _DOMNode:
    """Parse HTML into a simplified DOM tree."""
    builder = _TreeBuilder()
    try:
        builder.feed(html)
    except Exception:
        pass
    return builder.root


# ─── Semantic Block Extraction ────────────────────────────────────────────────

# Tags and patterns that identify shared components
SEMANTIC_SELECTORS = {
    "navbar": {
        "tags": ["nav"],
        "roles": ["navigation"],
        "classes": ["nav", "navbar", "navigation", "top-bar", "topbar", "app-bar", "appbar", "header-nav"],
    },
    "header": {
        "tags": ["header"],
        "roles": ["banner"],
        "classes": ["header", "site-header", "page-header", "app-header"],
    },
    "footer": {
        "tags": ["footer"],
        "roles": ["contentinfo"],
        "classes": ["footer", "site-footer", "page-footer", "app-footer"],
    },
    "sidebar": {
        "tags": ["aside"],
        "roles": ["complementary"],
        "classes": ["sidebar", "side-bar", "side-nav", "sidenav", "drawer", "nav-rail"],
    },
    "tabbar": {
        "tags": [],
        "roles": ["tablist"],
        "classes": ["tabbar", "tab-bar", "bottom-nav", "bottom-navigation", "bottom-bar", "bottombar"],
    },
}

# CSS position patterns for fallback detection
POSITION_PATTERNS = {
    "navbar": re.compile(
        r"position\s*:\s*(?:fixed|sticky)[^;]*;[^}]*top\s*:\s*0",
        re.IGNORECASE | re.DOTALL,
    ),
    "tabbar": re.compile(
        r"position\s*:\s*(?:fixed|sticky)[^;]*;[^}]*bottom\s*:\s*0",
        re.IGNORECASE | re.DOTALL,
    ),
}


def extract_semantic_blocks(html: str) -> dict:
    """
    Extract semantic component blocks from HTML.

    Returns dict mapping component type to list of HTML snippets:
    {"navbar": ["<nav>...</nav>"], "footer": ["<footer>...</footer>"], ...}
    """
    results = {}

    for comp_type, selectors in SEMANTIC_SELECTORS.items():
        blocks = []

        # 1. Semantic tags
        for tag in selectors["tags"]:
            blocks.extend(_extract_tag_blocks(html, tag))

        # 2. ARIA roles
        for role in selectors["roles"]:
            blocks.extend(_extract_by_role(html, role))

        # 3. CSS class patterns
        for cls in selectors["classes"]:
            blocks.extend(_extract_by_class(html, cls))

        # Deduplicate by content overlap
        unique = _deduplicate_blocks(blocks)
        if unique:
            results[comp_type] = unique

    # 4. Fallback: position-based detection
    for comp_type, pattern in POSITION_PATTERNS.items():
        if comp_type not in results:
            blocks = _extract_by_position_pattern(html, pattern)
            if blocks:
                results[comp_type] = blocks

    return results


def _extract_tag_blocks(html: str, tag: str) -> list:
    """Extract all blocks of a given HTML tag."""
    pattern = re.compile(
        rf"<{tag}[\s>].*?</{tag}>",
        re.IGNORECASE | re.DOTALL,
    )
    return pattern.findall(html)


def _extract_by_role(html: str, role: str) -> list:
    """Extract elements with a specific ARIA role."""
    pattern = re.compile(
        rf'<(\w+)[^>]*\brole\s*=\s*["\']?{re.escape(role)}["\']?[^>]*>.*?</\1>',
        re.IGNORECASE | re.DOTALL,
    )
    return [m.group(0) for m in pattern.finditer(html)]


def _extract_by_class(html: str, cls: str) -> list:
    """Extract elements whose class attribute contains the given class name."""
    pattern = re.compile(
        rf'<(\w+)[^>]*\bclass\s*=\s*"[^"]*\b{re.escape(cls)}\b[^"]*"[^>]*>.*?</\1>',
        re.IGNORECASE | re.DOTALL,
    )
    return [m.group(0) for m in pattern.finditer(html)]


def _extract_by_position_pattern(html: str, pattern: re.Pattern) -> list:
    """
    Extract elements whose inline style matches a CSS position pattern.

    Looks for the pattern in <style> blocks, then tries to find the associated
    element by class name.
    """
    blocks = []
    # Check inline styles on elements
    for m in re.finditer(r'<(\w+)[^>]*style="([^"]*)"[^>]*>.*?</\1>', html, re.DOTALL | re.IGNORECASE):
        if pattern.search(m.group(2)):
            blocks.append(m.group(0))
    return blocks


def _deduplicate_blocks(blocks: list) -> list:
    """Remove blocks that are substrings of other blocks."""
    if len(blocks) <= 1:
        return blocks
    sorted_blocks = sorted(blocks, key=len, reverse=True)
    unique = []
    for b in sorted_blocks:
        if not any(b in u for u in unique if u != b):
            unique.append(b)
    return unique


# ─── Comparison Utilities ─────────────────────────────────────────────────────

def dom_signature(html: str) -> str:
    """Generate a tag-only tree signature for structural comparison."""
    tree = parse_dom_tree(html)
    if tree.children:
        return " ".join(c.to_signature() for c in tree.children)
    return ""


def normalize_html(html: str) -> str:
    """
    Normalize HTML for deduplication hashing.

    Strips whitespace, removes variable content (text nodes), keeps structure.
    """
    # Remove all text content between tags
    normalized = re.sub(r">\s+<", "><", html)
    # Remove whitespace
    normalized = re.sub(r"\s+", " ", normalized).strip()
    # Remove text between tags (keep only structure)
    normalized = re.sub(r">([^<]+)<", "><", normalized)
    return normalized


def html_hash(html: str) -> str:
    """Hash of normalized HTML for deduplication."""
    return hashlib.md5(normalize_html(html).encode("utf-8")).hexdigest()


def text_similarity(a: str, b: str) -> float:
    """Text similarity ratio using SequenceMatcher (0.0 to 1.0)."""
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


def tree_similarity(sig_a: str, sig_b: str) -> float:
    """Structural similarity between two DOM signatures."""
    return text_similarity(sig_a, sig_b)


def class_overlap(classes_a: list, classes_b: list) -> float:
    """Jaccard similarity of CSS class lists."""
    set_a = set(classes_a)
    set_b = set(classes_b)
    if not set_a and not set_b:
        return 1.0
    if not set_a or not set_b:
        return 0.0
    intersection = set_a & set_b
    union = set_a | set_b
    return len(intersection) / len(union)


def component_similarity(html_a: str, html_b: str) -> float:
    """
    Weighted similarity score between two component HTML snippets.

    Weights: tree structure 50% + CSS classes 30% + visible text 20%
    """
    sig_a = dom_signature(html_a)
    sig_b = dom_signature(html_b)
    tree_score = tree_similarity(sig_a, sig_b)

    classes_a = _extract_all_classes(html_a)
    classes_b = _extract_all_classes(html_b)
    class_score = class_overlap(classes_a, classes_b)

    text_a = strip_tags(html_a)
    text_b = strip_tags(html_b)
    text_score = text_similarity(text_a, text_b)

    return tree_score * 0.5 + class_score * 0.3 + text_score * 0.2


def _extract_all_classes(html: str) -> list:
    """Extract all CSS class names from HTML."""
    classes = []
    for m in re.finditer(r'class="([^"]*)"', html, re.IGNORECASE):
        classes.extend(m.group(1).split())
    return classes


# ─── Text & Style Extraction ─────────────────────────────────────────────────

def strip_tags(html: str) -> str:
    """Remove all HTML tags, decode entities, normalize whitespace."""
    from html import unescape
    text = re.sub(r"<(script|style|svg|noscript)[^>]*>.*?</\1>", " ", html, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_inline_styles(html: str) -> dict:
    """
    Extract common CSS properties from inline styles in the outermost element.

    Returns dict with keys like 'background-color', 'color', 'border-radius', etc.
    """
    m = re.search(r'style="([^"]*)"', html, re.IGNORECASE)
    if not m:
        return {}

    style_str = m.group(1)
    props = {}
    for prop in style_str.split(";"):
        prop = prop.strip()
        if ":" in prop:
            key, val = prop.split(":", 1)
            props[key.strip().lower()] = val.strip()
    return props


def extract_css_classes_from_block(html: str) -> list:
    """Extract CSS classes from the outermost element of an HTML block."""
    m = re.match(r'<\w+[^>]*class="([^"]*)"', html, re.IGNORECASE)
    if m:
        return m.group(1).split()
    return []


def detect_button_variant(html: str, classes: list) -> str:
    """Detect button variant (primary/secondary/danger/outline/ghost) from classes and styles."""
    cls_str = " ".join(classes).lower()
    if any(k in cls_str for k in ("primary", "btn-primary", "cta")):
        return "primary"
    if any(k in cls_str for k in ("secondary", "btn-secondary")):
        return "secondary"
    if any(k in cls_str for k in ("danger", "destructive", "btn-danger", "btn-red", "error")):
        return "danger"
    if any(k in cls_str for k in ("outline", "bordered", "btn-outline")):
        return "outline"
    if any(k in cls_str for k in ("ghost", "text", "link", "btn-ghost", "btn-text")):
        return "ghost"

    # Check inline styles for background color hints
    styles = extract_inline_styles(html)
    bg = styles.get("background-color", "") + styles.get("background", "")
    if any(c in bg.lower() for c in ("red", "#e", "#f44", "#ef4", "rgb(239", "rgb(244")):
        return "danger"

    return "default"


def count_dom_nodes(html: str) -> int:
    """Count DOM nodes in an HTML snippet."""
    tree = parse_dom_tree(html)
    return tree.node_count()
