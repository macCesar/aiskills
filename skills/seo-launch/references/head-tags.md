# The `<head>` tags

Everything that goes in the head, what each tag does, and the mistakes that produce a tag that is present and useless.

---

## Basics

```html
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Freight and warehousing in Reynosa | Acme Logistics</title>
<meta name="description" content="Freight, storage and crossdock from any state to the northeast border. Quotes the same day.">
```

**`<title>` — the searched words go first, under ~60 characters.** Google truncates around 60 and cuts the tail, which is where the brand usually sits. One title per page: repeating the same one across the site makes every page compete for the same query. The pattern that survives truncation is `Specific thing | Brand`.

**`description` — 120 to 160 characters.** It does not influence ranking; it is the text the user reads in the results and it is what decides the click. Under 70 characters wastes the space; past 165 it gets cut. Write it per page. When it is auto-generated from a template, check what it produces: a description built from the site name alone says nothing about the page.

**`keywords` — Google stopped using it in 2009**, and Bing does not read it either. Not harmful; just do not let anyone believe it is doing work. If the client asks for it, add it and say what it is worth.

## Canonical

```html
<link rel="canonical" href="https://example.com/">
```

Tells search engines which address is the official one when several serve the same content. **Absolute URL, always** — a relative canonical is either ignored or resolved against the wrong base.

It is a hint. The 301 redirects in the server config (`references/server-files.md`) are the enforcement. Ship both: the canonical for the crawler that follows hints, the 301 for everything else.

The canonical of a page points at itself, not at the home page. A site-wide canonical pointing at `/` tells Google that every page is a duplicate of the home page, and they drop out of the index.

## Robots and theme-color

```html
<meta name="robots" content="index, follow">
<meta name="theme-color" content="#0f2d52">
```

`index, follow` is the default behaviour anyway; declaring it is a statement of intent that makes a stray `noindex` obvious in a diff. **Check production for a leftover `noindex`** — it is the single most effective way to be invisible, and it usually arrives from a staging template.

`theme-color` paints the browser bar on mobile with the site's colour. Small, and it shows.

## Open Graph — WhatsApp, Facebook, LinkedIn

This block is what produces the card with image, title and description when someone pastes the link.

```html
<meta property="og:type"             content="website">
<meta property="og:locale"           content="es_MX">
<meta property="og:site_name"        content="Acme Logistics">
<meta property="og:url"              content="https://example.com/">
<meta property="og:title"            content="Freight, warehousing and crossdock">
<meta property="og:description"      content="…">
<meta property="og:image"            content="https://example.com/images/og-image.jpg">
<meta property="og:image:secure_url" content="https://example.com/images/og-image.jpg">
<meta property="og:image:type"       content="image/jpeg">
<meta property="og:image:width"      content="1200">
<meta property="og:image:height"     content="630">
<meta property="og:image:alt"        content="…">
```

- **`og:title` is not the `<title>`.** The browser title carries the brand at the end for the search engine; the card title goes without it, because `og:site_name` already prints it right below. Repeating it wastes the width.
- **`og:type`**: `website` for the home page and static pages, `article` for a post or a news item. With `article` you can add `article:published_time` and `article:author`.
- **`width` and `height` explicit.** Without them WhatsApp sometimes shows a small thumbnail on first load while it downloads the image to measure it. They must match the real file — see the hard rules.
- **`og:image:secure_url`** is the HTTPS variant some older clients ask for. Same value; costs one line.
- **`og:image:alt`** is the alt text of the thumbnail, for screen readers.
- **`og:locale`** in the `xx_XX` form (`es_MX`, `en_US`), not the bare language code.

## Twitter / X

```html
<meta name="twitter:card"        content="summary_large_image">
<meta name="twitter:title"       content="…">
<meta name="twitter:description" content="…">
<meta name="twitter:image"       content="https://example.com/images/og-image.jpg">
<meta name="twitter:image:alt"   content="…">
```

`summary_large_image` shows the photo full width. The other value, `summary`, leaves it as a small square next to the text. X falls back to the Open Graph tags when the Twitter ones are missing, so the minimum that changes anything is `twitter:card`; the rest is worth writing when the copy should differ, because X truncates earlier than Facebook.

`twitter:site` is the site's `@handle`. Skip it rather than invent it.

## Icons

```html
<link rel="icon" type="image/svg+xml" href="/images/logo-symbol.svg">
<link rel="apple-touch-icon" sizes="180x180" href="/images/apple-touch-icon.png">
<meta name="apple-mobile-web-app-title" content="Acme">
```

Why an SVG, and why iOS still needs the PNG: `references/images.md`.

`apple-mobile-web-app-title` is the name under the icon on the iOS home screen. Without it, iOS takes the full `<title>` and cuts it wherever it fits, which for a keyword-first title is unreadable.

## Absolute URLs, on purpose

Every URL in this block is written in full, with the scheme and the domain.

**Facebook, WhatsApp and X discard images with a relative path.** If `og:image` were `images/og-image.jpg`, there would be no thumbnail — no error, no warning, just a grey rectangle. The same applies to `canonical` and `og:url`.

The places the domain appears: `canonical`, `og:url`, `og:image`, `og:image:secure_url`, `twitter:image`, and `url` / `logo` / `image` inside the JSON-LD. That is a lot of repetition of one string, which is exactly why the head belongs in a parameterized include with the domain defined once (`assets/head.php`, `assets/social-meta.blade.php`).

## Per-page values

The tags that must change per page: `<title>`, `description`, `canonical`, `og:url`, `og:title`, `og:description`. The ones that can stay site-wide: `og:site_name`, `og:locale`, `og:image` (with a per-page override where it is worth it), the icons, `theme-color`.

In Laravel, that split is `@props` with defaults on the component. In a static site, variables set before the include. Either way, a page that only needs a title and a description should be able to say just that.
