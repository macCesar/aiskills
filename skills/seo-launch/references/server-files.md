# Server files: `robots.txt`, `sitemap.xml`, `.htaccess`

The three files that live in the document root. Put them one level above it and the work silently does nothing — check where Apache actually serves from before writing.

---

## `robots.txt`

```
User-agent: *
Allow: /
Disallow: /send.php

Sitemap: https://example.com/sitemap.xml
```

Its main job here is the **`Sitemap:` line**: it is the only standard place to point at the sitemap without submitting it by hand to each engine. The `Sitemap:` URL must be absolute.

`Disallow` is for endpoints that are not pages — a form handler, an internal API, a debug route. Do not disallow `/admin` and think it is protected: `robots.txt` is public and reads as a directory of interesting URLs to anyone curious. It keeps polite crawlers out; it is not access control.

**A missing `robots.txt` returns 404**, which crawlers accept as "everything is allowed" — so the site still gets indexed. What you lose is the sitemap pointer.

**Never ship `Disallow: /`** to production. It is the staging default and it removes the whole site from the index.

## `sitemap.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://example.com/</loc>
    <lastmod>2026-08-13</lastmod>
    <changefreq>monthly</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://example.com/faq.html</loc>
    <lastmod>2026-08-13</lastmod>
    <priority>0.6</priority>
  </url>
</urlset>
```

- **URLs, not fragments.** The sections of a single page (`#services`, `#contact`) are anchors in the same document and do not go in. A sitemap indexes documents.
- **Only canonical URLs.** Listing both `www.` and the apex, or both `http` and `https`, contradicts the redirects and the canonical tag.
- **`lastmod` must be truthful.** It is the signal that tells a crawler to come back; a file that stamps today's date on every page every day gets its `lastmod` ignored entirely.
- **`changefreq` and `priority` are advisory** and Google largely disregards them. They are harmless. `priority` is relative *within your site*, so making everything 1.0 says nothing.
- Serve it as `application/xml`. If the server sends `text/plain`, add the MIME type (below).

For a site with dozens of pages, write it by hand or generate it in the build. For a database-driven site (Laravel, WordPress), generate it from a route or a scheduled command — a hand-written sitemap of a news site is stale the day it ships.

## `.htaccess`

For a **static site** served directly by Apache. A Laravel project already has an `.htaccess` with the front-controller rewrite: add these blocks to it, do not replace it. Full commented template in `assets/htaccess-static`.

### One canonical domain

Before this, three URLs typically serve the same content with a 200: `http://example.com/`, `https://www.example.com/`, `https://example.com/`. For a search engine that is duplicate content, and the authority is split across the three.

```apache
RewriteEngine On

RewriteCond %{HTTPS} !=on
RewriteCond %{HTTP:X-Forwarded-Proto} !=https
RewriteRule ^ https://example.com%{REQUEST_URI} [R=301,L]

RewriteCond %{HTTP_HOST} ^www\.example\.com$ [NC]
RewriteRule ^ https://example.com%{REQUEST_URI} [R=301,L]
```

**The double HTTPS condition is not redundant.** Behind a proxy or CDN — which is most shared hosting — `%{HTTPS}` can arrive off even though the request was secure. Testing only that variable produces an infinite redirect loop.

Pick apex or `www` and be consistent with the canonical tag and the sitemap. Which one does not matter; disagreeing about it does.

### Caching

```apache
<IfModule mod_headers.c>
  <FilesMatch "\.(webp|jpe?g|png|svg|ico|woff2)$">
    Header set Cache-Control "public, max-age=31536000, immutable"
  </FilesMatch>

  <FilesMatch "\.(html|css|js)$">
    Header set Cache-Control "public, max-age=0, must-revalidate"
  </FilesMatch>
</IfModule>
```

**Images and fonts: a year, `immutable`** — the browser will not even ask whether they changed. The discipline that makes this safe is renaming a file when its content changes.

**HTML and CSS: revalidate every time.** This is the counter-intuitive half, and it is the one that bites. A CSS file that is always called `app.css` cannot be cached long: recompile it, and every returning visitor keeps the old one until the cache expires — new utility classes silently missing, no console error, the page just looks broken for the people who visited before. A revalidation costs a 304 with an empty body; a month of stale CSS costs a bug you cannot reproduce on your own machine.

That trade only flips when the build fingerprints filenames (`app.4f3a1c.css`) and rewrites the references, which is what Vite and friends do — then the CSS is immutable like the images.

### Compression

```apache
<IfModule mod_deflate.c>
  AddOutputFilterByType DEFLATE text/html text/css text/plain text/xml \
    application/javascript application/json image/svg+xml
</IfModule>
```

`image/svg+xml` is the one usually missing from a default config. An SVG is text and compresses enormously — a 17 KB logo drops to 6 KB.

### Security headers

```apache
<IfModule mod_headers.c>
  Header always set X-Content-Type-Options "nosniff"
  Header always set Referrer-Policy "strict-origin-when-cross-origin"
  Header always set X-Frame-Options "SAMEORIGIN"
  Header always set Permissions-Policy "geolocation=(), microphone=(), camera=()"
</IfModule>
```

| Header | What it prevents |
| --- | --- |
| `nosniff` | the browser guessing a file's type and executing something that is not a script |
| `Referrer-Policy` | leaking the full originating URL when the user follows a link out |
| `X-Frame-Options` | the site being framed for clickjacking |
| `Permissions-Policy` | the page requesting camera, microphone or location |

**`Content-Security-Policy` is deliberately not in the default set.** A miscalibrated CSP strips the site of its styles, and any page with an inline `<script>` or a third-party font needs it tuned per site. Add it once those are self-hosted and you can test it; shipping a broken one is worse than shipping none.

### Hidden files and working files

```apache
RedirectMatch 404 /\.(?!well-known/)

<FilesMatch "\.(md|json|lock|yml|yaml|sh|sql|bak|log)$">
  Require all denied
</FilesMatch>
```

Any path starting with a dot returns 404. This matters more than it sounds: an SFTP watcher that uploads the project directory can put `.vscode/sftp.json` — with the hosting password in plain text — inside the document root, where it is one guessed URL away from anyone.

**The `(?!well-known/)` exception is not optional.** AutoSSL renews the certificate by placing a file in `/.well-known/acme-challenge/`. Without the exception the validation fails silently and you find out when the certificate expires. Test it by serving a real file from that path before calling the rule done.

The real fix for that class of problem is upstream — the document root should be a subdirectory (`public/`) with the repository and its config living above it, and the deploy tool's ignore list should exclude `.vscode`, `.git` and `node_modules`. The `.htaccess` rule is the second barrier, not the first.

### MIME types

```apache
AddType image/svg+xml .svg
AddType image/webp    .webp
AddType application/xml .xml
```

An SVG served as `text/plain` renders **blank**. If the logo and the favicon are SVG, this line is the difference between a site with a logo and a site without one.

## Verifying, from the terminal

```bash
# Redirects: expect 301 and the canonical target
curl -so /dev/null -w '%{http_code} → %{redirect_url}\n' http://example.com/
curl -so /dev/null -w '%{http_code} → %{redirect_url}\n' https://www.example.com/

# Headers on an image (cache) and on the HTML (security, revalidation)
curl -sI https://example.com/images/hero.webp
curl -sI https://example.com/

# Something that must not be reachable
curl -sI https://example.com/CLAUDE.md | head -1

# Real transferred weight, compressed
curl -s --compressed -o /dev/null -w '%{size_download}\n' https://example.com/
```
