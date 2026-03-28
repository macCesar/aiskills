"""
extract_zips.py — Extracts Stitch zips and renames files for stitch-showcase.

Each Stitch zip contains:
  code.html  → renamed to {zip_name}.html
  screen.png → renamed to {zip_name}.png

Usage:
    python extract_zips.py /path/to/source /path/to/output/assets
    → extracts all .zip files in /path/to/source to /path/to/output/assets/
"""
import sys
import shutil
import zipfile
import tempfile
from pathlib import Path


def extract_all(source_dir: str, assets_dir: str) -> list[dict]:
    """
    Extract and rename all Stitch zips in source_dir.

    Returns:
        List of dicts with {slug, html_path, png_path} per processed screen.
    """
    source = Path(source_dir)
    assets = Path(assets_dir)
    assets.mkdir(parents=True, exist_ok=True)

    screens = []

    # Collect sources: zips + already-extracted folders
    zips = sorted(source.glob("*.zip"))
    extracted_dirs = [d for d in sorted(source.iterdir())
                      if d.is_dir() and (d / "code.html").exists()]

    # Process zips
    for zip_path in zips:
        slug = _slug_from_name(zip_path.stem)
        result = _process_zip(zip_path, slug, assets)
        if result:
            screens.append(result)

    # Process already-extracted folders (if zip was unpacked previously)
    already_processed = {s["slug"] for s in screens}
    for dir_path in extracted_dirs:
        slug = _slug_from_name(dir_path.name)
        if slug in already_processed:
            continue
        result = _process_dir(dir_path, slug, assets)
        if result:
            screens.append(result)

    # Sort by slug name
    screens.sort(key=lambda s: s["slug"])
    return screens


def _process_zip(zip_path: Path, slug: str, assets: Path) -> dict | None:
    """Extract a Stitch zip and copy renamed files to assets/."""
    html_dst = assets / f"{slug}.html"
    png_dst  = assets / f"{slug}.png"

    # Incremental: skip if output is newer than the zip
    if html_dst.exists() and html_dst.stat().st_mtime > zip_path.stat().st_mtime:
        print(f"  ↩ {slug} (unchanged)")
        return {
            "slug": slug,
            "html_path": str(html_dst),
            "png_path": str(png_dst) if png_dst.exists() else None,
        }

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                zf.extractall(tmp_path)
        except zipfile.BadZipFile:
            print(f"  ⚠ {zip_path.name}: not a valid zip, skipping.", file=sys.stderr)
            return None

        # Find code.html and screen.png (may be inside a subdirectory)
        html_src = _find_file(tmp_path, "code.html")
        png_src = _find_file(tmp_path, "screen.png")

        if not html_src:
            print(f"  ⚠ {zip_path.name}: does not contain code.html, skipping.", file=sys.stderr)
            return None

        _copy_html(html_src, html_dst)

        png_dst_result = None
        if png_src:
            shutil.copy2(png_src, png_dst)
            png_dst_result = png_dst
        else:
            print(f"  ⚠ {zip_path.name}: does not contain screen.png.", file=sys.stderr)

    print(f"  ✓ {slug}")
    return {
        "slug": slug,
        "html_path": str(html_dst),
        "png_path": str(png_dst_result) if png_dst_result else None,
    }


def _process_dir(dir_path: Path, slug: str, assets: Path) -> dict | None:
    """Copy files from an already-extracted folder to assets/."""
    html_src = dir_path / "code.html"
    png_src = dir_path / "screen.png"
    html_dst = assets / f"{slug}.html"
    png_dst  = assets / f"{slug}.png"

    # Incremental: skip if output is newer than source
    if html_dst.exists() and html_dst.stat().st_mtime > html_src.stat().st_mtime:
        print(f"  ↩ {slug} (unchanged)")
        return {
            "slug": slug,
            "html_path": str(html_dst),
            "png_path": str(png_dst) if png_dst.exists() else None,
        }

    _copy_html(html_src, html_dst)

    png_dst_result = None
    if png_src.exists():
        shutil.copy2(png_src, png_dst)
        png_dst_result = png_dst

    print(f"  ✓ {slug} (folder)")
    return {
        "slug": slug,
        "html_path": str(html_dst),
        "png_path": str(png_dst_result) if png_dst_result else None,
    }


_NO_SCROLLBAR_CSS = '<style>*::-webkit-scrollbar{display:none!important}*{scrollbar-width:none!important;-ms-overflow-style:none!important}</style>'

def _copy_html(src: Path, dst: Path) -> None:
    """Copy HTML injecting scrollbar-hiding CSS into <head>."""
    text = src.read_text(encoding="utf-8", errors="ignore")
    if "</head>" in text:
        text = text.replace("</head>", f"{_NO_SCROLLBAR_CSS}</head>", 1)
    elif "<body" in text:
        text = text.replace("<body", f"{_NO_SCROLLBAR_CSS}<body", 1)
    dst.write_text(text, encoding="utf-8")


def _find_file(root: Path, filename: str) -> Path | None:
    """Recursively find a file by name inside root."""
    matches = list(root.rglob(filename))
    return matches[0] if matches else None


def _slug_from_name(name: str) -> str:
    """
    Convert filename/folder name to a slug.
    '01-splash-screen' → '01_splash_screen'
    'Login Screen' → 'login_screen'
    """
    import re
    s = name.strip().lower()
    s = re.sub(r"[\s\-]+", "_", s)
    s = re.sub(r"[^a-z0-9_]", "", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python extract_zips.py /path/to/source /path/to/output/assets", file=sys.stderr)
        sys.exit(1)

    import json
    screens = extract_all(sys.argv[1], sys.argv[2])
    print(json.dumps(screens, ensure_ascii=False, indent=2))
