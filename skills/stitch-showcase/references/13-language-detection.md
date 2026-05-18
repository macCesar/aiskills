# Section: Language Detection

## Purpose

The `<html lang="…">` attribute on the generated `index.html` and
`viewer.html` tells the browser which natural language the content uses.
If the value disagrees with the actual content, Chrome shows a "Translate
this page" banner and assistive technologies pronounce words with the
wrong phoneme set. This document explains how the build picks the value
and how to override it.

## Resolution Order

The `lang` attribute is chosen by the first rule that fires:

1. **CLI flag** (future — not implemented yet): `--lang es` on
   `build_showcase.py`.
2. **`showcase.json` field**:

   ```json
   {
     "source": "stitch",
     "type": "mobile",
     "name": "My App",
     "lang": "es"
   }
   ```

3. **`## Lang` section in `DESIGN.md`** (same shape as `## Type`):

   ```markdown
   ## Lang
   es
   ```

4. **Auto-detection** from the text content of `DESIGN.md` (project name,
   section names, descriptions). The detector counts Spanish signals:

   - Accented characters (`á é í ó ú ñ`).
   - Common Spanish stop words (`de`, `el`, `la`, `los`, `las`, `para`,
     `con`, `pantalla`, `aplicación`, `usuario`, etc.).

   If the Spanish score crosses a small threshold, the lang resolves to
   `"es"`; otherwise it falls through.

5. **Default**: `"en"`.

## When to Override

The auto-detector handles obvious cases (a project whose DESIGN.md is
entirely Spanish or entirely English), but it can be fooled by very
short DESIGN.md files or by projects where the UI language differs from
the documentation language. Use an explicit override when:

- The DESIGN.md is in English but the actual screen content is Spanish
  (you'd be documenting an es-MX app in English for a client).
- The DESIGN.md is sparse and the heuristic has nothing to score on.
- You want a non-Spanish, non-English language (`pt`, `fr`, `de` …) —
  the auto-detector only distinguishes Spanish vs everything else.

## Why It Matters

- **Chrome's translate prompt**: with `lang="en"` and Spanish content,
  Chrome offers to translate the page to the user's locale. Users
  perceive this as a bug.
- **Screen readers**: VoiceOver and TalkBack switch pronunciation
  engines per `lang`. A wrong value makes Spanish text sound like a
  speech synthesizer trying to pronounce "configuración" as English.
- **Search engines**: the `lang` attribute is a soft signal but it's
  read by indexers when ranking pages by locale.

## Common Mistake: Mismatched Lang and Content

The previous template hard-coded `lang="en"` even for Spanish-only
projects. The fix wasn't to flip the default to `"es"` (that just moves
the bug to English projects) — it was to detect or accept an override.
The same logic now lives in `parse_design_md.py` (`_detect_lang`) and
`build_showcase.py` (the `{{HTML_LANG}}` placeholder substitution).

If you ever see Chrome offering to translate one of your showcases:
that's the signal that the resolved `lang` is wrong. Add an override to
`showcase.json` or `DESIGN.md` and rebuild.
