# Component Standardization

## Problem

Google Stitch generates slight variations of shared components (navbar, footer, tabbar) across screens within the same session. Navigation might have a different link order, footer might use different spacing, tabbar icons might differ.

## Solution

The `--components` flag detects these shared components, groups variants by similarity, and recommends a canonical version for the user to replicate across all screens.

## Detection Strategy

1. **Semantic tags**: `<nav>`, `<header>`, `<footer>`, `<aside>`
2. **ARIA roles**: `role="navigation"`, `role="contentinfo"`, `role="tablist"`
3. **CSS class patterns**: classes containing `nav`, `footer`, `sidebar`, `tabbar`, `bottom-nav`
4. **Position fallback**: `position: fixed/sticky` with `top: 0` (navbar) or `bottom: 0` (tabbar)

## Similarity Scoring

Components are compared using a weighted score:
- **DOM structure (50%)**: Tag-only tree signature comparison via `SequenceMatcher`
- **CSS classes (30%)**: Jaccard similarity of class name sets
- **Visible text (20%)**: Text content similarity via `SequenceMatcher`

Default grouping threshold: **85% similarity**.

## Canonical Selection

Priority for choosing the canonical (best) version:
1. Screens with "home", "main", "dashboard", "landing" in the slug
2. Most DOM nodes (most complete version)
3. First encountered

## Output

`shared_components.json` in the showcase directory, containing per component type:
- `found_in`: number of screens containing this component
- `total_screens`: total screens analyzed
- `canonical`: the recommended version with slug and HTML snippet
- `variants`: list of other versions with similarity scores and difference descriptions
