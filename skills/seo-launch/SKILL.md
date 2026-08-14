---
name: seo-launch
description: 'Audit and then install everything a site needs to be indexed and to render a proper card when its link is shared: head tags, Open Graph and Twitter card, the 1200x630 og:image, favicon and apple-touch-icon, robots.txt, sitemap.xml, an .htaccess with one canonical domain, JSON-LD, and the Search Console handover. Works on static sites and on Laravel or plain PHP projects. Use when the user says the link shows a grey box with no preview in WhatsApp, asks why Google cannot find the site, is putting a new domain live, or asks for an SEO review, meta tags, og:image, sitemap or robots.txt — even when they never say "SEO". Not for: keyword research, writing the content itself, backlinks, paid ads, or analytics dashboards.'
allowed-tools: Read, Grep, Glob, Bash, Edit, Write, AskUserQuestion
compatibility: Requires Python 3 (standard library only) and network access to audit a live site. Stage 2 uses ImageMagick to generate the images.
---

# SEO Launch

Get a site indexable and shareable: the `<head>` tags, the images the platforms actually fetch, the server files, the structured data, and the handover to Search Console.

The work has two stages separated by an explicit authorization. The separation exists because the report is the deliverable: an audit that edits while it looks produces a list of things you already changed, which is not a diagnosis and takes the decision away from the owner. Stage 1 writes nothing.

Respond in the user's language. This skill is written in English for portability; the report should match whatever language the user is writing in.

## Read the terrain first

Three questions, answered before anything else, because each one changes what you apply and where:

1. **What kind of project is this?** `artisan` in the root means Laravel — the tags belong in a Blade component or the layout's `<head>`, not in each view. A tree of `.html` files means a static site; look for a `partials/` directory or an SSI/PHP include before writing the same block into every page. Anything else (Astro, Next, Hugo, WordPress), find the one template that owns the `<head>` and edit that.
2. **Is the site live?** A reachable URL means the audit can be measured instead of guessed — run the script. A domain that does not resolve yet means the audit is a read of local files only, and the verification step moves to after the deploy.
3. **Where is the document root?** The `.htaccess`, `robots.txt` and `sitemap.xml` go where Apache serves from, which in a Laravel project is `public/` and in a static project is often `public/` too. Writing them one level up is the most common way this work silently does nothing.

Ask only what you cannot read from the repo. The domain, the business name and the phone number are the user's to give; the framework is yours to detect.

## Stage 1 — Audit, no modifications

Do not create or edit files in this stage, including images.

1. **Measure the live site**, if there is one:

   ```bash
   python3 <SKILL_DIR>/scripts/auditar_seo.py https://example.com
   python3 <SKILL_DIR>/scripts/auditar_seo.py https://mysite.test --local   # self-signed Herd cert
   ```

   Replace `<SKILL_DIR>` with the absolute "Base directory for this skill" from the system message that loaded this skill — the working directory here is the user's project, not this one, so a relative `scripts/…` resolves to nothing. The path also differs by install type (`~/.claude/plugins/cache/<plugin>/<version>/skills/seo-launch` for a plugin install, `~/.claude/skills/seo-launch` standalone), so read it rather than assuming it.

   It reads the page once and checks the `<head>` tags, `robots.txt`, `sitemap.xml`, the `http→https` and `www→apex` redirects, the response headers, and whether the `og:image` exists — including its **real dimensions**, read from the file header, which is how you catch an image declared as 1200×630 that is not.

   `--no-network` limits it to the markup. `--local` relaxes certificate verification and exists only for local `.test` domains; never point it at a site on the public internet, since an unverified response is not evidence of anything.

2. **Read the local files** that own what the script found missing: the template holding the `<head>`, the document root, `.htaccess`, `robots.txt`, `sitemap.xml`.

3. **Report findings as a table** — item, severity, what breaks because of it:

   | Finding | Severity | Consequence |
   | --- | --- | --- |
   | No `og:image` | High | Every shared link renders as a grey rectangle |
   | `<title>` is 74 characters | Medium | Google truncates it at ~60 and the tail is lost |

   Severity is what breaks, not how hard it is to fix. Anything that makes the site invisible (no `sitemap.xml`, `noindex` in production, two domains serving 200) or unshareable (no `og:image`, relative image URLs) is High. Nice-to-haves (`twitter:site`, `theme-color`) are Low, and say so rather than padding the list.

4. **Stop.** Present the table and what you would do about it. Do not start fixing.

If the user asked up front to "audit and fix", still show the table first — approving it takes seconds, and the content decisions inside it (the description text, which pages go in the sitemap, whether keywords are wanted) are not yours to invent.

## Stage 2 — Authorized implementation

Start only once the user approves. Work in this order, because each step depends on the previous one being real:

1. **Tags.** Install the `<head>` block from the right template in `assets/`, parameterized — one place holds the domain, one place holds the fallback image. Never paste the same literal block into five pages.
2. **Images.** Generate the `og:image`, the favicon and the `apple-touch-icon` per `references/images.md`. Verify each file exists and measures what the tags declare.
3. **Server files.** `robots.txt` with the `Sitemap:` line, `sitemap.xml` with the real pages, `.htaccess` with the canonical domain, caching and security headers.
4. **Structured data.** The JSON-LD block, with confirmed data only.
5. **Verify against the live site**, not against the repo. Re-run the script and expect the findings you fixed to be gone. If the site deploys by SFTP-on-save, the files may already be up; if it deploys by git, they are not until it ships — check, do not infer.
6. **Search engines.** The Search Console steps in `references/search-engines.md` need a browser and the domain's DNS. Hand the user the exact sequence; you cannot do this part for them.

## Where to look

| What the work touches | Read |
| --- | --- |
| `<title>`, description, canonical, Open Graph, Twitter card | `references/head-tags.md` |
| `og:image`, favicon, `apple-touch-icon`, ImageMagick commands | `references/images.md` |
| `robots.txt`, `sitemap.xml`, `.htaccess`, caching, headers | `references/server-files.md` |
| JSON-LD: `LocalBusiness`, `Organization`, `Article`, breadcrumbs | `references/structured-data.md` |
| Search Console, Bing, submitting the sitemap, validators | `references/search-engines.md` |

Templates in `assets/`: `head.php` (static site, parameterized include), `social-meta.blade.php` (Laravel component), `htaccess-static`, `robots.txt`.

## Hard rules

These are the ones that break on their own, each with the reason it matters:

- **`og:image` and `canonical` carry absolute URLs.** Facebook, WhatsApp and X discard an image with a relative path — the tag is present, valid, and produces no thumbnail at all.
- **The `og:image` is a JPEG, not WebP.** Several preview clients still cannot decode WebP and fall back to no image; the 30 KB you save are not worth an invisible link.
- **The `apple-touch-icon` is a flat PNG with a white background and no alpha.** iOS does not honour the alpha channel here, it fills transparency with black, and a dark logo disappears into it.
- **The `<title>` stays under ~60 characters.** Past that Google truncates it in the results, and what gets cut is the tail — which is where the brand usually sits.
- **`og:image:width` and `og:image:height` must match the file.** They exist so the client can lay out the card before downloading; wrong values render a cropped or stretched card and nothing reports an error.
- **The canonical redirects go in the server config, not only in the tag.** `rel=canonical` is a hint Google may ignore; the 301 is the one that settles it.
- **JSON-LD carries confirmed data only.** Google cross-checks it against other sources — an invented address or opening hours costs you trust in the whole block, and there is no warning when that happens.
- **Changing the `og:image` requires busting Facebook's cache.** It caches the card for days; without the debugger refresh, the "fixed" preview keeps showing the old image and it looks like the fix failed.
