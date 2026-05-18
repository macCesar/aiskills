# Section: Troubleshooting & Known Issues

## Purpose

Working notes on issues that have shown up in real projects, the cause
when it's understood, and the workaround. New issues should be added here
before they show up a second time.

---

## `catalog.html` stays on "Loading…"

**Symptom**: opening `catalog.html` shows the skeleton header but the
component grid never appears.

**Cause** (suspected, not yet confirmed): in projects with very dense
HTMLs or many near-duplicate variants, `extract_catalog.py` either times
out or returns a structure the catalog viewer chokes on.

**Workaround**: the `index.html` template ships without the "Catalog"
button in the header, so end users don't hit the broken page. If you
want to inspect the catalog data, open `component_catalog.json` directly.

**Status**: open. Restore the Catalog button in
`references/index.html` once the root cause is fixed.

---

## Chrome shows "Translate this page" banner

**Symptom**: Chrome offers to translate the showcase, sometimes to a
language that isn't even one of the two involved (Portuguese is common).

**Cause**: the `<html lang="…">` attribute on `index.html` or
`viewer.html` disagrees with the actual text content. See
[`13-language-detection.md`](13-language-detection.md) for the full
resolution order.

**Workaround**: add an override.

`showcase.json`:

```json
{
  "lang": "es"
}
```

or, in `DESIGN.md`:

```markdown
## Lang
es
```

Then rebuild.

---

## Video doesn't preview in Finder / Safari rejects it

**Symptom**: a `.mp4` downloaded from Facebook / YouTube / TikTok plays
fine in VLC and Chrome but shows a black square in macOS Finder and
fails to play in Safari < 17.

**Cause**: the source was encoded in AV1, which neither macOS Finder
nor older Safari can decode.

**Workaround**: re-encode to H.264 with ffmpeg. See
[`12-video-embedding.md`](12-video-embedding.md) for the exact command.

---

## Skill installed both as plugin and standalone

**Symptom**: after `aiskills install`, the skill folder exists at both
`~/.claude/skills/<name>/` (from the standalone CLI) **and**
`~/.claude/plugins/cache/<plugin>/<version>/skills/<name>/` (from the
marketplace plugin), so changes to one path are invisible to the other.

**Cause**: older versions of the `aiskills` CLI didn't detect when the
plugin marketplace had already installed the skill and dropped a
duplicate symlink.

**Workaround**:

1. Update the CLI: `npm install -g @maccesar/aiskills@latest`.
2. Remove the standalone copy: `rm -rf ~/.claude/skills/<skill-name>`.
3. Reinstall: `aiskills install`. The CLI now skips skills that the
   plugin already provides.

---

## Showcase background and app background match (thumbnails disappear)

**Symptom**: every card in `index.html` shows a blank rectangle because
the screen has the same background color as the showcase canvas.

**Cause**: someone reused the project's brand color as the showcase
background instead of a neutral surface.

**Workaround**: see `07-theme-system.md` and the Color Strategy section
of `SKILL.md` — never use a brand color for large showcase surfaces.

---

## Stitch slugs come with `_` in place of accents

**Symptom**: filenames like `configuraci_n_oscuro.html` and the showcase
displays them as "Configuraci_N Oscuro".

**Cause**: Google Stitch strips accented characters from filenames.

**Workaround**: the build now de-mangles slugs automatically through
`scripts/slug_demangle.py`. If a slug doesn't appear in the demangler's
dictionary, override the title explicitly in `DESIGN.md` using the
`Title | Description` format:

```markdown
### Cuenta
- nuevo_slug_man_leado: Corrección Manual | Texto descriptivo.
```
