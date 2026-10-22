# Fonts and third parties

## Applicability and official sources

Sources consulted 2026-10-22; reopen at use time:

- [Google Fonts technical considerations](https://developers.google.com/fonts/docs/technical_considerations): a stylesheet request can lead to a separate font-file request; inspect both rather than searching only HTML links.
- [Google Material Symbols self-hosting guide](https://developers.google.com/fonts/docs/material_symbols): icon fonts also have local font-file and CSS requirements.
- [SIL Open Font License official text](https://openfontlicense.org/open-font-license-official-text/): check the actual font's license, redistribution conditions and any Reserved Font Names before bundling or modifying it. Not every font uses the OFL.
- [ICO cookies and similar technologies](https://ico.org.uk/for-organisations/direct-marketing-and-privacy-and-electronic-communications/guide-to-pecr/cookies-and-similar-technologies/): device storage/access rules have their own scope and exceptions. An external request alone does not prove a consent violation; assess the actual data flow and local law. This page flags revised guidance in progress; follow its current detailed guidance link.

Determine which domains receive requests, what they receive and why. Self-hosting is a way to remove a third-party dependency/data flow, not a universal legal mandate. A CDN, proxy or embed can still expose data after a top-level stylesheet is localized.

## Inspection and corrections

- Inventory HTML links, CSS `@import`, `@font-face` and `url()`, preload/preconnect/dns-prefetch, JS loaders, build plugins, themes, dependencies, emails, native WebViews and remote embeds. Follow nested stylesheets and redirects in emitted production assets.
- For an authorized localization, obtain licensed files from the original distributor, keep required notices, preserve families, weights, italics, variable axes, language subsets and icon ligatures. Use existing asset pipelines and correct MIME/cache/CORS settings. Do not copy a proprietary font just because a remote server exposes it.
- Remove obsolete provider hints/imports. Review fallbacks and `font-display` for usable rendering while assets load. If redistribution rights are unknown, prepare the integration and ask for the license or an approved replacement rather than inventing permission.

## Technical verification

Build with the project's normal tooling if needed. With caches/service workers cleared, inspect the network on representative routes, languages, themes and embedded views. Verify no unwanted font or stylesheet requests or connection hints remain; verify local responses, text/icon rendering, fallback behavior and layout. Record any unmodifiable third-party embed separately. A source search alone cannot prove the absence of runtime requests.
