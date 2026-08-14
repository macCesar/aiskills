# Structured data (JSON-LD)

A block that describes the thing on the page in a vocabulary search engines parse. It is what can produce the side panel with phone, location and services, or the breadcrumb trail above a result.

It goes in the `<head>` as `<script type="application/ld+json">`. JSON-LD is the format Google recommends; microdata and RDFa still work but mean editing the markup itself.

---

## The rule that outranks the schemas

**Confirmed data only.** Google cross-checks structured data against other sources — the business listing, the site's own text, directories. An address, opening hours or a rating that does not match makes it distrust the whole block, and nothing tells you that happened.

Leave a field out rather than approximate it. A `LocalBusiness` with name, URL, phone and city is worth more than one with an invented street and guessed hours.

Do not describe what is not on the page. Marking up a product that is not there, or reviews that do not exist, is what Google's spam policies call structured data abuse, and the penalty applies to the site, not the tag.

## `LocalBusiness` — a business with a physical presence

```json
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "Acme Logistics",
  "description": "Freight, storage and crossdock in the northeast.",
  "url": "https://example.com/",
  "logo": "https://example.com/images/logo.svg",
  "image": "https://example.com/images/og-image.jpg",
  "telephone": "+52-899-186-6350",
  "address": {
    "@type": "PostalAddress",
    "addressLocality": "Reynosa",
    "addressRegion": "Tamaulipas",
    "addressCountry": "MX"
  },
  "areaServed": ["Reynosa", "Matamoros", "Monterrey"],
  "sameAs": ["https://www.facebook.com/acmelogistics"],
  "hasOfferCatalog": {
    "@type": "OfferCatalog",
    "name": "Services",
    "itemListElement": [
      { "@type": "Offer", "itemOffered": { "@type": "Service", "name": "Full truckload freight" } },
      { "@type": "Offer", "itemOffered": { "@type": "Service", "name": "Warehousing" } }
    ]
  }
}
```

- **Phone in international format** (`+52-899-186-6350`) — that is what schema.org expects and what a phone link can dial from anywhere.
- **`address` can be partial.** `addressLocality` + `addressRegion` + `addressCountry` is valid and honest for a business without a public street address; `streetAddress` is optional.
- **`sameAs`** holds the real, verified profiles — the actual Facebook page, not the one that ought to exist.
- **`openingHours`** only if they are accurate and maintained. Wrong hours are worse than no hours.
- Use a more specific subtype when one fits: `Restaurant`, `AutoRepair`, `MedicalClinic`, `Store`. The full list is at <https://schema.org/LocalBusiness>.

**Omit the email if the page deliberately obfuscates it.** Publishing it in plain text inside the JSON-LD undoes whatever the visible markup was protecting it from.

## `Organization` — a company without a storefront

For a business whose location is not the point: an agency, a SaaS, a publisher.

```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Acme Software",
  "url": "https://example.com/",
  "logo": "https://example.com/images/logo.svg",
  "sameAs": ["https://github.com/acme", "https://www.linkedin.com/company/acme"],
  "contactPoint": {
    "@type": "ContactPoint",
    "telephone": "+52-899-186-6350",
    "contactType": "customer service",
    "availableLanguage": ["Spanish", "English"]
  }
}
```

The `logo` should be a square-ish, reasonably large image on a plain background — it is a candidate for the knowledge panel.

## `Article` / `NewsArticle` — a post or a news item

```json
{
  "@context": "https://schema.org",
  "@type": "NewsArticle",
  "headline": "Headline, under 110 characters",
  "description": "The same summary as the meta description.",
  "image": ["https://example.com/images/note-1200x630.jpg"],
  "datePublished": "2026-08-13T08:30:00-06:00",
  "dateModified": "2026-08-13T11:00:00-06:00",
  "author": { "@type": "Person", "name": "Author Name" },
  "publisher": {
    "@type": "Organization",
    "name": "Site Name",
    "logo": { "@type": "ImageObject", "url": "https://example.com/images/logo.png" }
  },
  "mainEntityOfPage": { "@type": "WebPage", "@id": "https://example.com/note-slug" }
}
```

- **`headline` under 110 characters** — Google truncates it beyond that.
- **Dates in ISO 8601 with a timezone offset.** A date without an offset is read as UTC, which shifts an evening post to the next day.
- **`dateModified` only when the content really changed.** Bumping it on every deploy is the same lie as a sitemap that stamps today on everything.
- On a database-driven site this block is generated per page from the record — never hand-written per post.

## `BreadcrumbList` — the trail above a result

```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    { "@type": "ListItem", "position": 1, "name": "Home", "item": "https://example.com/" },
    { "@type": "ListItem", "position": 2, "name": "Services", "item": "https://example.com/services" },
    { "@type": "ListItem", "position": 3, "name": "Warehousing" }
  ]
}
```

Positions start at 1 and are contiguous. The last item is the current page and **carries no `item` URL**. It must reflect a trail the user can actually see or follow on the page.

## Several blocks on one page

Two options, both valid: multiple `<script type="application/ld+json">` tags, or one array. Multiple tags are easier to generate from separate templates.

```html
<script type="application/ld+json">{ "@context": "…", "@type": "Organization", … }</script>
<script type="application/ld+json">{ "@context": "…", "@type": "BreadcrumbList", … }</script>
```

A typical article page carries three: `NewsArticle`, `BreadcrumbList`, and the site-wide `Organization`.

## Validating

- **<https://validator.schema.org/>** — checks the markup is well-formed and the properties exist. This is the one that must come back with zero errors.
- **<https://search.google.com/test/rich-results>** — a *different* tool. It checks whether the page qualifies for a rich result: the cards with stars, prices or steps.

`LocalBusiness` on its own does **not** generate a rich result, so the Rich Results Test will likely say no eligible items were detected. **That is not an error.** The JSON-LD still does its job of explaining the business to Google, and it is what feeds the knowledge panel.

Escaping is the other thing to check: a quote or an apostrophe inside a value that is not escaped breaks the JSON, and a broken block is ignored in full. Templating a description straight into JSON without escaping is how that happens — the audit script parses every block it finds and reports the ones that do not parse.
