# Component Catalog

## Problem

Stitch HTML exports contain reusable UI components (buttons, cards, inputs) that users want to extract for Blade templates, design system documentation, or consistency audits. Manually finding and extracting these from 10-20 screen files is tedious.

## Solution

Every build automatically extracts all atomic and composite components, deduplicates them, clusters variants by similarity, and generates a visual catalog (`catalog.html`) alongside a machine-readable JSON (`component_catalog.json`).

## Atomic Components

| Type | Detection |
|------|-----------|
| Buttons | `<button>`, `<a.btn>`, `<input type="submit">` — variant detected by CSS class |
| Headings | `<h1>` through `<h6>` with associated styles |
| Inputs | `<input>`, `<select>`, `<textarea>` with placeholders/labels |
| Badges | `<span>` with classes badge/tag/pill/chip |
| Links | Standalone `<a>` (excludes nav links and button-like links) |
| Icons | Material Symbols spans, SVGs with icon class |

## Composite Components

| Type | Detection |
|------|-----------|
| Cards | `<div>` with card/shadow classes containing image + text |
| Price tables | Sections containing `$`, `€`, `plan`, `price` keywords |
| CTAs | Heading + text + prominent button combo in a section |
| Testimonials | Blocks with quote/testimonial/review classes or `<blockquote>` |
| Hero sections | First large section with h1/h2 + text + optional button |

## Deduplication

Components are deduplicated by hashing normalized HTML (whitespace removed, text content stripped, structure only). Same hash = same component, found_in lists are merged.

## Design Tokens

Extracted from all HTML/CSS across screens:
- **Colors**: hex values from `color`, `background-color`, CSS variables (sorted by frequency)
- **Fonts**: from `font-family` declarations and Google Fonts links
- **Border radius**: from `border-radius` declarations

## Similarity Clustering

Atomic components are clustered by similarity (85% threshold) within semantic context:
- **Context detection**: each component is tagged with its nearest ancestor semantic element (`<form>`, `<nav>`, `<header>`, `<section>`, etc.)
- **Context-aware clustering**: form buttons are grouped separately from CTA buttons
- **Canonical selection**: priority is home-like slug → most screens → most DOM nodes → first found
- **Cluster output**: JSON includes `clusters` key with canonical, variants, similarity scores, and context per cluster

## Visual Catalog

`catalog.html` features:
- **Comparison view**: component variants displayed side-by-side in cluster groups
- **Canonical badge (★)**: auto-detected best version highlighted with accent border
- **Similarity scores**: percentage bars showing how close each variant is to canonical
- **Styled previews**: components render with original Tailwind CSS (CDN + config extracted from screens)
- **Already Unified section**: collapsed list of components with only one variant
- Tabs for Structural, Atomic types, Composite, Already Unified, Design Tokens
- Dark/light mode toggle, search by component name
- Copyable code snippet per component

## Standardization Workflow

1. Build the showcase (catalog is generated automatically)
2. Open `catalog.html` and review component variants
3. Tell the AI which variant to use: "use the navbar from home"
4. AI runs `apply_canonical.py` to replace variants in screen HTMLs
5. Rebuild — catalog shows fewer variants, more items in "Already Unified"
6. Repeat until satisfied
