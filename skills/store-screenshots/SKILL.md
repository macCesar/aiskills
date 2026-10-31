---
name: store-screenshots
description: Use when preparing or auditing App Store/Google Play screenshots, videos, Headers/Search Results, store icons/banners, or editable artwork; configuring custom pages, Asset Library or listing experiments; preparing In-App Events, Promotional Content or Play Shorts; or checking asset review states and AI provenance. Also triggers on “capturas para las tiendas”. Not for app UI implementation or unrelated video production.
---

# Store screenshots

Produce store assets with editable masters and reproducible exports. Screenshots show real app UI; creative artwork can express the brand beyond the UI where the placement permits it. Work with ordinary files and command-line tools across assistants. Image generation is optional for artwork; never use it to manufacture screenshots or gameplay. Store-video preparation includes capture/edit/export guidance and FFmpeg recipes; complex recording, animation or editing still needs the appropriate available production tools.

For listing descriptions, keywords, localization or acquisition diagnosis, use `store-listing-optimization` when available. It owns text/metric review; this skill owns visual production and page/experiment configuration. A text request alone does not authorize regenerating artwork.

## Required workflow

Read the references for the requested deliverables before recommending dimensions or composing assets:

| Task involves | Required reading |
| --- | --- |
| Apple Header, Search Results, universal artwork, safe areas, upload/review | [apple-creative-assets.md](references/apple-creative-assets.md) |
| Apple screenshots, device slots, App Previews and poster frames | [apple-media.md](references/apple-media.md) |
| Apple Custom Product Pages, campaign pages, keywords and deep links | [apple-custom-product-pages.md](references/apple-custom-product-pages.md) |
| Apple Asset Library, statuses, compatibility, reuse, review and archiving | [apple-asset-library.md](references/apple-asset-library.md) |
| Apple Product Page Optimization, treatments, traffic and results | [apple-product-page-optimization.md](references/apple-product-page-optimization.md) |
| Google Play assets, custom listings/groups, library reuse, Apple/Google counterparts | [google-play.md](references/google-play.md) |
| Google listing experiments, variants, metrics and applying results | [google-experiments.md](references/google-experiments.md) |
| Recording/editing/exporting store video, FFmpeg recipes and video QA | [video-production.md](references/video-production.md) |
| Apple In-App Events or Google Promotional Content images/animation/video | [promotion-and-events.md](references/promotion-and-events.md) |
| Google icons, TV/Wear/Automotive/XR, Play Shorts or AI declarations | [google-additional-assets.md](references/google-additional-assets.md) |
| Art direction, story, typography, composition | [design.md](references/design.md) |
| New Android/iOS captures | [capture.md](references/capture.md) |
| Export, packaging, technical and visual QA | [delivery.md](references/delivery.md) |

Cite store rules and values with `[source: references/<file>.md]` and the official URL when reporting requirements. A remembered value looks just as authoritative as a checked one; citations make the distinction visible. Example: `The universal Apple image is 5244 × 2950 px [source: references/apple-creative-assets.md].` Reopen the official sources for the actual destination and record the verification date. If a reference was not read, label the claim `FROM_MEMORY (unverified):`; if live verification fails, disclose it. Do not claim an upload will be accepted from dimensions alone.

## Establish the deliverable

### Resource-constrained machines: sequential execution

On machines with 16 GB RAM or less, reported slowness/memory pressure, or an explicit user request, execute resource-heavy work **sequentially, never in parallel**. Treat an M1 with 16 GB as a sequential-workflow target, not a reason to assume capture is impossible. If capacity is unknown, default to sequential execution for capture and rendering.

- Use one booted virtual device total for this task: one iOS Simulator **or** one Android emulator, never both or multiple phone/tablet instances. Finish and shut down the task-owned device before starting the next.
- Build first, then boot/install/navigate/capture one target. Save and inspect its captures, shut it down, then generate SVGs, export PNGs and assemble review sheets as separate stages. Process one image/job at a time and wait for completion before launching the next; apply this across locales, variants and agent/tool calls too.
- Do not overlap device control with SVG generation, PNG rendering, image generation, video encoding, another build, or a contact-sheet job. Disable worker pools/batch parallelism in task-owned generators where configurable. A serial shell loop alone is insufficient if its child tool starts concurrent workers.
- Check active task jobs before starting more work. If a device becomes unresponsive, stop adding work, inspect CPU/memory pressure and competing processes, and reduce contention before retrying. An indexer can compete for resources, particularly while ingesting large generated SVGs; record observed CPU/process activity rather than diagnosing from its presence alone. Temporarily pause/defer indexing associated with this task's project via supported controls when contention is observed. Record its prior state, keep it paused through capture and heavy artwork export, then restore that state once heavy work finishes or at an interrupted handoff. If it was already paused, leave it paused. Do not change app files or persistent indexer exclusions to achieve a temporary pause, kill unrelated user processes, or disable indexing permanently.

Record the execution mode and completed target/stage so interrupted work resumes from verified outputs. See [capture.md](references/capture.md) for device transitions and [delivery.md](references/delivery.md) for serial export. This is an execution policy, not a store upload requirement. Lightweight reads can be grouped; they must not launch additional heavy jobs.

Inspect existing artwork, app UI, brand assets, project instructions, and the requested release before choosing a direction. Reuse an accepted direction and existing generators when appropriate. Discover similar skills before replacing an established workflow.

Resolve asset type (screenshot, creative image, or video), platform, upload slot/device class, locale, app orientation, mandatory sections, and whether the request is selection, one sample, or the complete series. Infer what the project makes clear; ask only for missing decisions that block the work. A request for one sample is not authorization to regenerate all designs.

Read [design.md](references/design.md) for selection, messaging, typography, and composition. Propose a small set of meaningfully different directions if none is established, recommend one, and produce a representative sample. If no user approval is required, inspect the sample and continue within the authorized scope. Honor explicit review checkpoints.

Read [delivery.md](references/delivery.md) before setting canvas dimensions. Verify current official requirements for the actual destination; do not confuse native capture resolution, accepted upload sizes, and featuring recommendations. Use the real app's orientation, never an orientation inherited from another project.

## Select the Apple page workflow

For audience/campaign destinations, use Custom Product Pages and deliver a page brief with locale/asset mapping, URL and optional keyword/deep-link configuration. For randomized comparison of the default page, use Product Page Optimization and deliver a hypothesis, baseline, treatment assets, traffic/locales and decision criteria; PPO cannot test a CPP. Asset Library supplies compatible reusable resources to either workflow; approval and placement/publication are distinct states. These workflows reuse the existing media specifications, not new canvas sizes. Read the matching references above before configuration or analysis.

Prepare the requested artifacts and reviewable configuration first. Execute console changes only within the user's authorization, including submissions, publishing, test start/stop/application and asset cleanup. When access is missing, finish independent asset preparation and name the specific unverified console state. Do not report a hypothetical experiment outcome as measured conversion lift.

Google uses Fichas de Play Store → Crear una ficha de Play Store personalizada (Custom store listings); its experiments can target default or custom listings. Use its own configuration and result rules. Distinguish ordinary listing assets, event/promotion media and restricted-access features such as Play Shorts before generating files. Confirm actual console eligibility for conditional destinations.

## Capture and compose

Read [capture.md](references/capture.md) when obtaining new screenshots. Capture each platform's real UI. An iPhone capture does not become Android artwork by changing its dimensions or frame. Tablets need the actual tablet layout. Creative images need not contain a screenshot; follow their placement's content rules and safe-area templates instead. Do not bake storefront controls, device shells, or template guides into creative exports.

For videos, follow [video-production.md](references/video-production.md) and the destination's content/access-disclosure rules. For generated/edited Google artwork, record per-asset provenance and inspect applicable AI declarations using [google-additional-assets.md](references/google-additional-assets.md). Do not flatten every asset to RGB: Play listing icons have different alpha requirements from screenshots and feature graphics.

Number final slides in reading order. Name captures sharing a slide with subnumbers (`06`, `07.1`, `07.2`). Keep required screens; group related benefits only when both remain legible. Store a mapping of slide → source captures → copy, including exclusions and the reason for them.

Build SVGs with explicit pixel dimensions and a matching viewBox. Keep text editable, logos authentic, and screenshot pixels intact. Use proportional placement, embedded screenshots, and licensed local fonts. Adapt composition to each form factor rather than stretching a phone design to a tablet.

Use the bundled helper where useful:

```bash
python3 scripts/artwork.py export slide.svg slide.png
python3 scripts/artwork.py check --size 1080x1920 slide.png
```

Paths above are relative to this skill. The size is an example, not a store requirement. Read [delivery.md](references/delivery.md) for dependencies, portable font handling, packaging, validation, and helper limits.

## Finish criteria

- All requested sections and platforms accounted for; no unreviewed loading, blank, clipped, stale, or incorrect screens passed off as final.
- Each final matches its recorded destination dimensions, format, count, and content rules.
- For image deliveries, open rendered PNGs: inspect the entire contact sheet, each slide at useful size, and suspect details at 100%. XML validity and matching dimensions do not prove visual quality.
- Export commands, fonts/licenses, sources, capture provenance, and final sequence are reproducible from the delivered package.
- For page/library/test work, identify the page or treatment, locales, asset mapping, inherited items and observed review/placement/test state. Separate proposed traffic, expected outcomes and actual Analytics results.
- For video, events or conditional assets, verify the actual slot, technical output, content rights/disclosures, eligibility and applicable processing/review/publication state; do not claim uploader support from a recipe alone.
- Report actual validation and missing access separately. Do not claim store acceptance or successful device capture unless observed. Store upload, publication, and unrelated app fixes need their own authorization.
