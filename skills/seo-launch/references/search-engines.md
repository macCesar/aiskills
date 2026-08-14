# Registering the site and getting it indexed

The tags and files make the site indexable. This is the part that tells the engines it exists. It needs a browser, a Google account and access to the domain's DNS — **the user has to do it**; hand them the sequence rather than pretending you can.

---

## Google Search Console

<https://search.google.com/search-console>

### Choosing the property type

Google offers two, and they are not equivalent:

| Type | What it covers | How it is verified |
| --- | --- | --- |
| **Domain** | `example.com`, `www.`, http, https, and every subdomain | DNS only |
| URL prefix | exactly the address you type, and nothing else | HTML file, `<meta>` tag, DNS, Analytics… |

**Prefer Domain.** With URL prefix you would have to register each variant separately, which contradicts the whole point of having redirected them to one. Use URL prefix only when there is no access to the DNS zone.

Verification is a `TXT` record Google gives you, pasted into the domain's DNS zone at the registrar. Search Console calls this "Domain name provider". Propagation is usually minutes.

> **Never delete that TXT record.** If it disappears from the DNS, the verification is lost and the reports go with it. From *Settings → Ownership verification* you can add a second method as a backup.

### Submitting the sitemap

Left menu → **Sitemaps**, under *Indexing*. On a Domain property the field wants the full URL:

```
https://example.com/sitemap.xml
```

It should land in **Success** state with the page count discovered. For the first few minutes it may say "Couldn't fetch"; that usually resolves itself.

This does not replace the `Sitemap:` line in `robots.txt` — they complement each other. Search Console tells Google directly; `robots.txt` serves every other crawler that comes by.

### Requesting indexing

Top bar → **URL Inspection** → paste the home page URL.

It will say **"URL is not on Google"**, which is expected for a domain that just went live. Press **Request indexing**. That puts the page in the crawl queue instead of waiting for Google to arrive on its own. Do it for the home page and the two or three pages that matter most; the quota is limited and the sitemap covers the rest.

### What to expect

The *Performance* and *Indexing* panels will show **"Processing data, please check back tomorrow"**. That is normal — first data takes between **3 days and 2 weeks**. It is not a configuration error, and re-submitting does not speed it up.

## Bing Webmaster Tools

<https://www.bing.com/webmasters>

Worth ten minutes: it also feeds DuckDuckGo and, increasingly, the AI assistants that use Bing's index. It offers **import from Google Search Console**, which carries over the property and the verification in a couple of clicks — do that instead of repeating the DNS dance.

Then submit the same sitemap URL. Its **IndexNow** feature accepts an explicit ping when a page changes, which is useful for a site publishing several times a day.

## Validators, once it is live

| Tool | What it tells you |
| --- | --- |
| <https://validator.schema.org/> | the JSON-LD is well-formed and its properties exist |
| <https://search.google.com/test/rich-results> | whether the page qualifies for a rich result (a different question — see `structured-data.md`) |
| <https://developers.facebook.com/tools/debug/> | how the card renders, and the button that busts the cache |
| <https://cards-dev.twitter.com/validator> | the X card, when it is reachable |
| <https://pagespeed.web.dev/> | Core Web Vitals and performance |
| <https://securityheaders.com/> | the headers from the `.htaccess` |

## Facebook's cache

Facebook and WhatsApp cache the card for days. After changing an `og:` tag or the image, paste the URL into the **Sharing Debugger** and press *Scrape Again*. Without it, the link keeps showing the old card and it reads exactly like the change never deployed.

WhatsApp uses Facebook's crawler, so refreshing there fixes both. A trick that works when the cache will not budge: append a harmless query string (`?v=2`) to the URL you are testing to force a fresh scrape.

## What none of this buys

Registering a site does not rank it. What Search Console gives you is visibility into what Google sees — which pages it indexed, which queries reach you, which URLs it refused and why. Indexing itself is a matter of days to weeks for a new domain, and no button shortens it.

If after two weeks the pages are still not indexed, the *Pages* report says why in plain language: `noindex` detected, crawl blocked by `robots.txt`, redirect, duplicate without a canonical, or "discovered but not indexed" — which usually means the content is too thin to be worth a slot.
