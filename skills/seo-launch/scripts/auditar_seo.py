#!/usr/bin/env python3
"""Audit the SEO tags and configuration files of a URL.

Downloads the page once, extracts what lives in the <head> and contrasts it
with what the platforms actually need. Also checks robots.txt, sitemap.xml,
the canonical redirects, the response headers and the og:image.

    python3 auditar_seo.py https://example.com
    python3 auditar_seo.py https://example.com --no-network  # markup only
    python3 auditar_seo.py https://mysite.test --local       # self-signed cert

Standard library only: runs on any macOS or Linux with Python 3.
"""

from __future__ import annotations

import argparse
import gzip
import json
import re
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser

# A browser User-Agent keeps some WAFs (Sucuri, Cloudflare) from answering
# with a challenge instead of the page.
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"

OK, FALTA, REVISAR, INFO = "ok", "falta", "revisar", "info"

SIMBOLO = {OK: "  ok  ", FALTA: " MISS ", REVISAR: "CHECK ", INFO: " info "}

# Set from --local. Certificate verification is on by default: a tool that
# never verifies would happily audit a man-in-the-middled response and report
# it as healthy. The flag exists for Herd's .test domains, which are signed by
# a local authority the interpreter does not trust.
VERIFICAR_TLS = True

# Last transport error, so main() can explain a failure instead of printing a
# bare "could not read".
ULTIMO_ERROR = ""

# ---------------------------------------------------------------- utilities


def contexto_ssl() -> ssl.SSLContext:
    """Default verification, unless --local relaxed it for a self-signed cert."""
    ctx = ssl.create_default_context()
    if not VERIFICAR_TLS:
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    return ctx


def pedir(url: str, metodo: str = "GET", seguir: bool = True, tiempo: int = 15):
    """Return (status, headers, body, final_url), or (None, {}, '', url) on failure."""
    global ULTIMO_ERROR

    class SinRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *_args, **_kwargs):
            return None

    handlers = [] if seguir else [SinRedirect()]
    opener = urllib.request.build_opener(
        urllib.request.HTTPSHandler(context=contexto_ssl()), *handlers
    )
    peticion = urllib.request.Request(url, method=metodo, headers={"User-Agent": UA})

    try:
        with opener.open(peticion, timeout=tiempo) as r:
            crudo = r.read() if metodo == "GET" else b""
            cabeceras = {k.lower(): v for k, v in r.headers.items()}
            if cabeceras.get("content-encoding") == "gzip":
                crudo = gzip.decompress(crudo)
            cuerpo = crudo.decode("utf-8", errors="replace")
            return r.status, cabeceras, cuerpo, r.url
    except urllib.error.HTTPError as e:
        cabeceras = {k.lower(): v for k, v in e.headers.items()} if e.headers else {}
        return e.code, cabeceras, "", url
    except Exception as e:
        ULTIMO_ERROR = f"{type(e).__name__}: {e}"
        return None, {}, "", url


def dimensiones(datos: bytes) -> tuple[int, int] | None:
    """Width and height of a PNG, JPEG or WebP, reading only the file header.

    This catches the silent failure of declaring og:image:width 1200 when the
    image measures something else: the card renders cropped and nobody notices.
    """
    if datos[:8] == b"\x89PNG\r\n\x1a\n" and len(datos) >= 24:
        return int.from_bytes(datos[16:20], "big"), int.from_bytes(datos[20:24], "big")

    if datos[:2] == b"\xff\xd8":  # JPEG: walk the segments up to the SOF
        i = 2
        while i + 9 < len(datos):
            if datos[i] != 0xFF:
                i += 1
                continue
            marcador = datos[i + 1]
            if marcador in (0xD8, 0xD9) or 0xD0 <= marcador <= 0xD7:
                i += 2
                continue
            largo = int.from_bytes(datos[i + 2 : i + 4], "big")
            if 0xC0 <= marcador <= 0xCF and marcador not in (0xC4, 0xC8, 0xCC):
                alto = int.from_bytes(datos[i + 5 : i + 7], "big")
                ancho = int.from_bytes(datos[i + 7 : i + 9], "big")
                return ancho, alto
            i += 2 + largo
        return None

    if datos[:4] == b"RIFF" and datos[8:12] == b"WEBP":
        formato = datos[12:16]
        if formato == b"VP8 " and len(datos) >= 30:
            return (
                int.from_bytes(datos[26:28], "little") & 0x3FFF,
                int.from_bytes(datos[28:30], "little") & 0x3FFF,
            )
        if formato == b"VP8L" and len(datos) >= 25:
            bits = int.from_bytes(datos[21:25], "little")
            return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
        if formato == b"VP8X" and len(datos) >= 30:
            return (
                int.from_bytes(datos[24:27], "little") + 1,
                int.from_bytes(datos[27:30], "little") + 1,
            )
    return None


class LectorHead(HTMLParser):
    """Collects from the <head> what matters for SEO and for social cards."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.metas: dict[str, str] = {}
        self.links: list[dict[str, str]] = []
        self.jsonld: list[str] = []
        self.lang = ""
        self._en_title = False
        self._en_jsonld = False

    def handle_starttag(self, tag, attrs):
        a = {k.lower(): (v or "") for k, v in attrs}
        if tag == "html":
            self.lang = a.get("lang", "")
        elif tag == "title":
            self._en_title = True
        elif tag == "meta":
            clave = a.get("name") or a.get("property") or a.get("http-equiv")
            if clave:
                self.metas.setdefault(clave.lower(), a.get("content", ""))
            elif "charset" in a:
                self.metas.setdefault("charset", a["charset"])
        elif tag == "link":
            self.links.append(a)
        elif tag == "script" and a.get("type", "").lower() == "application/ld+json":
            self._en_jsonld = True
            self.jsonld.append("")

    def handle_endtag(self, tag):
        if tag == "title":
            self._en_title = False
        elif tag == "script":
            self._en_jsonld = False

    def handle_data(self, data):
        if self._en_title:
            self.title += data
        elif self._en_jsonld and self.jsonld:
            self.jsonld[-1] += data

    def link(self, rel: str) -> dict[str, str] | None:
        for enlace in self.links:
            if rel in enlace.get("rel", "").lower().split():
                return enlace
        return None


class Reporte:
    def __init__(self) -> None:
        self.filas: list[tuple[str, str, str, str]] = []
        self.seccion = ""

    def abrir(self, titulo: str) -> None:
        self.seccion = titulo

    def add(self, estado: str, etiqueta: str, detalle: str = "") -> None:
        self.filas.append((self.seccion, estado, etiqueta, detalle))

    def imprimir(self) -> int:
        actual = None
        for seccion, estado, etiqueta, detalle in self.filas:
            if seccion != actual:
                print(f"\n{seccion}\n{'─' * len(seccion)}")
                actual = seccion
            linea = f"[{SIMBOLO[estado]}] {etiqueta}"
            if detalle:
                linea += f" — {detalle}"
            print(linea)

        faltan = sum(1 for f in self.filas if f[1] == FALTA)
        revisar = sum(1 for f in self.filas if f[1] == REVISAR)
        bien = sum(1 for f in self.filas if f[1] == OK)

        print(f"\n{'═' * 60}")
        print(f"SUMMARY   {bien} ok · {revisar} to check · {faltan} missing")
        print("═" * 60)
        return faltan


# ------------------------------------------------------------------- checks


def revisar_head(h: LectorHead, r: Reporte) -> None:
    r.abrir("Basics")

    r.add(OK if h.metas.get("charset") else FALTA, "charset", h.metas.get("charset", ""))
    r.add(OK if h.lang else FALTA, "lang on <html>", h.lang or "no lang attribute")

    vp = h.metas.get("viewport", "")
    r.add(OK if vp else FALTA, "viewport", vp)

    t = h.title.strip()
    if not t:
        r.add(FALTA, "<title>", "no title")
    elif len(t) > 60:
        r.add(REVISAR, "<title>", f"{len(t)} characters; Google truncates near 60")
    else:
        r.add(OK, "<title>", f"{len(t)} characters")

    d = h.metas.get("description", "").strip()
    if not d:
        r.add(FALTA, "description", "this is the text people read in the results")
    elif len(d) < 70:
        r.add(REVISAR, "description", f"{len(d)} characters; too short (120-160 works well)")
    elif len(d) > 165:
        r.add(REVISAR, "description", f"{len(d)} characters; gets cut past 160")
    else:
        r.add(OK, "description", f"{len(d)} characters")

    canonical = h.link("canonical")
    if not canonical:
        r.add(FALTA, "canonical", "without it, every URL variant competes with itself")
    else:
        href = canonical.get("href", "")
        estado = OK if href.startswith("http") else REVISAR
        nota = href if estado == OK else f"{href} — must be absolute"
        r.add(estado, "canonical", nota)

    robots = h.metas.get("robots", "")
    if "noindex" in robots.lower():
        r.add(REVISAR, "meta robots", f"{robots} — this page is NOT indexed")
    else:
        r.add(OK if robots else INFO, "meta robots", robots or "absent (indexed by default)")

    tc = h.metas.get("theme-color", "")
    r.add(OK if tc else INFO, "theme-color", tc or "paints the mobile browser bar")

    # --- Open Graph ---------------------------------------------------------
    r.abrir("Open Graph (WhatsApp, Facebook, LinkedIn)")

    for etiqueta, obligatoria in (
        ("og:type", True),
        ("og:site_name", False),
        ("og:locale", False),
        ("og:url", True),
        ("og:title", True),
        ("og:description", True),
    ):
        v = h.metas.get(etiqueta, "").strip()
        if v:
            recorte = v if len(v) <= 70 else v[:67] + "…"
            r.add(OK, etiqueta, recorte)
        else:
            r.add(FALTA if obligatoria else INFO, etiqueta, "")

    og_url = h.metas.get("og:url", "")
    if og_url and not og_url.startswith("http"):
        r.add(REVISAR, "og:url is relative", f"{og_url} — must be absolute")

    og_img = h.metas.get("og:image", "").strip()
    if not og_img:
        r.add(FALTA, "og:image", "without it the link shows up as a grey rectangle")
    elif not og_img.startswith("http"):
        r.add(REVISAR, "og:image", f"{og_img} — relative; WhatsApp and Facebook discard it")
    else:
        r.add(OK, "og:image", og_img)

    for etiqueta in ("og:image:width", "og:image:height", "og:image:alt", "og:image:type"):
        v = h.metas.get(etiqueta, "")
        r.add(OK if v else INFO, etiqueta, v)

    # --- Twitter/X ----------------------------------------------------------
    r.abrir("Twitter / X")

    card = h.metas.get("twitter:card", "")
    if not card:
        r.add(FALTA, "twitter:card", "no card without this")
    elif card != "summary_large_image":
        r.add(REVISAR, "twitter:card", f"{card} — 'summary_large_image' shows the photo full width")
    else:
        r.add(OK, "twitter:card", card)

    for etiqueta in ("twitter:title", "twitter:description", "twitter:image", "twitter:site"):
        v = h.metas.get(etiqueta, "")
        r.add(OK if v else INFO, etiqueta, v[:70] if v else "")

    # --- Icons --------------------------------------------------------------
    r.abrir("Icons")

    icono = h.link("icon")
    if not icono:
        r.add(FALTA, "favicon", "no <link rel=icon>")
    else:
        href = icono.get("href", "")
        if icono.get("type", "") == "image/svg+xml" or href.endswith(".svg"):
            r.add(OK, "favicon SVG", href)
        else:
            r.add(REVISAR, "favicon", f"{href} — an SVG draws sharp at any size")

    touch = h.link("apple-touch-icon")
    if touch:
        r.add(OK, "apple-touch-icon", f"{touch.get('href', '')} ({touch.get('sizes', 'no sizes')})")
    else:
        r.add(FALTA, "apple-touch-icon", "iOS ignores the SVG and screenshots the page instead")

    titulo_ios = h.metas.get("apple-mobile-web-app-title", "")
    r.add(
        OK if titulo_ios else INFO,
        "apple-mobile-web-app-title",
        titulo_ios or "without it, iOS truncates the <title> under the icon",
    )

    # --- Structured data ----------------------------------------------------
    r.abrir("Structured data")

    if not h.jsonld:
        r.add(FALTA, "JSON-LD", "this is what describes the business or article to Google")
    for bloque in h.jsonld:
        try:
            datos = json.loads(bloque)
        except json.JSONDecodeError as e:
            r.add(REVISAR, "JSON-LD", f"not valid JSON: {e}")
            continue
        for item in datos if isinstance(datos, list) else [datos]:
            tipo = item.get("@type", "no @type") if isinstance(item, dict) else "?"
            r.add(OK, "JSON-LD", f"@type {tipo}")


def revisar_red(base: str, h: LectorHead, cabeceras: dict, r: Reporte) -> None:
    partes = urllib.parse.urlsplit(base)
    raiz = f"{partes.scheme}://{partes.netloc}"

    # --- robots.txt and sitemap --------------------------------------------
    r.abrir("robots.txt and sitemap.xml")

    status, _, cuerpo, _ = pedir(f"{raiz}/robots.txt")
    if status != 200:
        r.add(FALTA, "robots.txt", f"answers {status}; it is the first thing Google looks for")
        sitemaps: list[str] = []
    else:
        sitemaps = re.findall(r"(?im)^\s*sitemap:\s*(\S+)", cuerpo)
        r.add(OK, "robots.txt", f"{len(cuerpo)} bytes")
        if sitemaps:
            r.add(OK, "declares the sitemap", sitemaps[0])
        else:
            r.add(
                FALTA,
                "Sitemap: in robots.txt",
                "the only standard place to point at it without submitting it by hand",
            )

    url_sitemap = sitemaps[0] if sitemaps else f"{raiz}/sitemap.xml"
    status, cab_sm, cuerpo, _ = pedir(url_sitemap)
    if status != 200:
        r.add(FALTA, "sitemap.xml", f"{url_sitemap} answers {status}")
    else:
        urls = len(re.findall(r"<loc>", cuerpo))
        indices = len(re.findall(r"<sitemap>", cuerpo))
        que = f"{indices} indexed sitemaps" if indices else f"{urls} URLs"
        r.add(OK, "sitemap.xml", que)
        tipo = cab_sm.get("content-type", "")
        if "xml" not in tipo:
            r.add(REVISAR, "sitemap MIME type", f"{tipo} — should be application/xml")

    # --- One canonical domain ----------------------------------------------
    r.abrir("Canonical domain")

    status, cab, _, _ = pedir(f"http://{partes.netloc}{partes.path or '/'}", seguir=False)
    if status is None:
        r.add(INFO, "http:// → https://", "did not answer")
    elif status in (301, 308):
        r.add(OK, "http:// → https://", f"{status} to {cab.get('location', '')}")
    elif status == 302:
        r.add(REVISAR, "http:// → https://", "302 temporary; this calls for a 301")
    else:
        r.add(FALTA, "http:// → https://", f"answers {status} without redirecting")

    host = partes.netloc
    otro = host[4:] if host.startswith("www.") else f"www.{host}"
    status, cab, _, _ = pedir(f"{partes.scheme}://{otro}{partes.path or '/'}", seguir=False)
    if status is None:
        r.add(INFO, f"{otro}", "does not resolve (fine: a single form of the domain)")
    elif status in (301, 308):
        r.add(OK, f"{otro} → canonical", cab.get("location", ""))
    elif status == 200:
        r.add(REVISAR, f"{otro}", "serves 200: two URLs for the same content")
    else:
        r.add(INFO, f"{otro}", f"answers {status}")

    # --- Headers ------------------------------------------------------------
    r.abrir("Response headers")

    for nombre, recomendada in (
        ("x-content-type-options", "nosniff"),
        ("referrer-policy", "strict-origin-when-cross-origin"),
        ("x-frame-options", "SAMEORIGIN"),
    ):
        v = cabeceras.get(nombre, "")
        r.add(OK if v else FALTA, nombre, v or f"suggested: {recomendada}")

    cache = cabeceras.get("cache-control", "")
    if not cache:
        r.add(REVISAR, "cache-control on the HTML", "no policy; must-revalidate is the safe one")
    elif "max-age=0" in cache or "no-cache" in cache or "must-revalidate" in cache:
        r.add(OK, "cache-control on the HTML", cache)
    else:
        r.add(REVISAR, "cache-control on the HTML", f"{cache} — cached HTML serves stale content")

    if cabeceras.get("set-cookie"):
        r.add(
            REVISAR,
            "Set-Cookie on the HTML",
            "with this header many CDNs and WAFs stop caching the response",
        )

    # --- The og:image really exists ----------------------------------------
    og_img = h.metas.get("og:image", "")
    if og_img.startswith("http"):
        r.abrir("The og:image")
        status, cab_img, _, _ = pedir(og_img, metodo="HEAD")
        if status != 200:
            r.add(FALTA, "og:image reachable", f"answers {status}")
        else:
            tipo = cab_img.get("content-type", "")
            if "webp" in tipo:
                r.add(REVISAR, "format", "WebP; several preview clients cannot read it. Use JPEG")
            else:
                r.add(OK, "format", tipo)

            peso = int(cab_img.get("content-length", 0) or 0)
            if peso:
                estado = OK if peso < 1_500_000 else REVISAR
                r.add(estado, "weight", f"{peso / 1024:.0f} KB")

            trozo, _ = descargar_inicio(og_img)
            medidas = dimensiones(trozo) if trozo else None
            if medidas:
                ancho, alto = medidas
                declarado_w = h.metas.get("og:image:width", "")
                declarado_h = h.metas.get("og:image:height", "")
                texto = f"{ancho}×{alto}"
                if (ancho, alto) == (1200, 630):
                    r.add(OK, "dimensions", texto)
                else:
                    r.add(REVISAR, "dimensions", f"{texto} — 1200×630 is what platforms expect")
                if declarado_w and (declarado_w, declarado_h) != (str(ancho), str(alto)):
                    r.add(
                        REVISAR,
                        "declared dimensions",
                        f"og:image:width/height say {declarado_w}×{declarado_h}, "
                        f"the file measures {texto}",
                    )


def descargar_inicio(url: str, bytes_max: int = 4096) -> tuple[bytes, int | None]:
    """Only the file header: enough to read the dimensions."""
    peticion = urllib.request.Request(url, headers={"User-Agent": UA, "Range": "bytes=0-4095"})
    opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=contexto_ssl()))
    try:
        with opener.open(peticion, timeout=15) as r:
            return r.read(bytes_max), r.status
    except Exception:
        return b"", None


def main() -> int:
    global VERIFICAR_TLS

    p = argparse.ArgumentParser(description="Audit the SEO tags of a URL.")
    p.add_argument("url")
    p.add_argument(
        "--no-network",
        action="store_true",
        help="markup only: skips robots.txt, sitemap, redirects and og:image",
    )
    p.add_argument(
        "--local",
        action="store_true",
        help="accept a self-signed certificate (Herd .test domains). Never use it against a site on the public internet",
    )
    args = p.parse_args()

    VERIFICAR_TLS = not args.local

    url = args.url if "://" in args.url else f"https://{args.url}"

    status, cabeceras, cuerpo, final = pedir(url)
    if status != 200 or not cuerpo:
        print(f"Could not read {url} (status {status}).")
        if ULTIMO_ERROR:
            print(f"  {ULTIMO_ERROR}")
        if "CERTIFICATE_VERIFY_FAILED" in ULTIMO_ERROR:
            print("  A local site with a self-signed certificate needs --local.")
        return 2

    if final.rstrip("/") != url.rstrip("/"):
        print(f"Note: {url} redirects to {final}")

    lector = LectorHead()
    lector.feed(cuerpo)

    print(f"\nSEO audit of {final}")

    reporte = Reporte()
    revisar_head(lector, reporte)
    if not args.no_network:
        revisar_red(final, lector, cabeceras, reporte)

    faltan = reporte.imprimir()
    return 1 if faltan else 0


if __name__ == "__main__":
    sys.exit(main())
