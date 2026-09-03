---
name: technical-demo-videos
description: Plan and produce reproducible macOS screen-recorded technical demonstrations from a project path and a conversational goal. Use when the user wants a coding, CLI, build, simulator, emulator, or app workflow recorded in VS Code, including reviewable scripts, timed narration, captions, retakes, or final video assembly. Present the recording plan for approval before controlling the UI or starting a capture.
---

# Technical Demo Videos

Turn a natural-language request into a reviewable production plan and, after approval, a reproducible recording package. Treat domain-specific projects such as Titanium, Flutter, native mobile, web, or a CLI as inputs; do not encode one repository, framework, command, or directory layout in this skill.

Act as the project's technical screenwriter, director, producer, screen operator, voice-script writer, and editor. Translate the user's informal explanation into a concise visual story that is technically accurate, pleasant to watch, and practical to reproduce. These roles are responsibilities, not permission to override the user's creative brief, change the product, publish media, spend money, or begin recording without approval.

## Establish the request

Resolve these facts from the user's message and the inspected project:

- source project path;
- demonstration goal and intended audience;
- exact command or UI operation;
- target platform, device, simulator, or emulator;
- files, terminal output, and runtime result that prove success;
- spoken language, caption language, and desired voice workflow;
- artifact destination and naming convention.

Preserve meaningful series conventions. When a project slug combines an order and the demonstrated command, such as `02-images`, keep that slug across the plan, recorder, recipe, takes, event logs, narration, captions, and final render. Do not invent a marketing title that breaks traceability unless the user requests one.

Infer safe details from the project and existing conventions. Ask only when a missing choice would materially change the demonstration. Use the applicable domain skill or official documentation to validate commands and expected results. Do not execute the showcased command during planning unless a harmless preflight is necessary and the user authorized implementation rather than review only.

## Route technical knowledge

This skill owns production and recording decisions; it is not the technical authority for every stack. Detect the project's languages, framework, build system, requested feature, and teaching angle before drafting the proposal. Assemble the smallest useful panel of installed skills, which may combine:

- **platform and framework expertise:** mobile and web frameworks, application platforms, databases, build systems, CLIs, or release tooling;
- **software judgment:** architecture, senior engineering, refactoring, security, performance, testing, maintainability, or framework-specific best practices;
- **presentation quality:** UI/UX, visual hierarchy, accessibility, responsive design, technical writing, diagrams, or documentation;
- **deliverable expertise:** voice, captions, image work, presentations, or publishing when the brief actually needs them.

This routing is a hard gate: do not draft the recording plan, visible sequence, narration intent, recipe, or recorder until every applicable domain skill has been loaded and its required task-specific references have been read. If a requested command, option, API, or behavior belongs to another installed skill, treat that skill and its cited sources as the technical authority. Verify the exact behavior in the inspected project or implementation when the documentation leaves any uncertainty. Never fill a technical gap with a plausible-looking command, option, output path, or product claim.

Use those skills to establish:

- the exact valid command and required working directory;
- prerequisites, configuration, credentials, devices, and expected duration;
- success and failure signals;
- files or runtime behavior that prove the claim;
- framework-specific actions that should or should not appear on screen.

Apply specialists only when their perspective materially affects this video. A command-only demo may need the framework skill and engineering judgment but no UI redesign. A UI walkthrough may need UI/UX and accessibility guidance in addition to the framework skill. An architecture explanation may need diagrams and software-architecture analysis without changing the application.

Then apply this skill to turn those verified facts into the visual sequence, narration intent, automation, and edit. If no suitable domain skill is installed, inspect the project and consult official primary documentation when current or uncertain facts matter. Never invent a command or expected result merely to complete a script.

Reconcile advice in this order: the user's explicit brief and scope, factual platform constraints, observable project behavior, safety and correctness, then stylistic recommendations. Clearly label an optional best practice as a recommendation; do not present it as a prerequisite. Mention the specialist skills used in the written proposal so the user can review the basis of the technical and creative decisions.

## Phase 1: propose before recording

Inspect the source project without changing it. Draft a production package and present the plan to the user before any UI automation or screen recording. The proposal must include:

1. the exact initial frame and preparation that will remain outside the video;
2. every visible action in order, including commands exactly as typed;
3. the proof shown after each meaningful action;
4. estimated visual timing and narration beats;
5. files that will be generated and files that will remain untouched;
6. cleanup behavior and any external cost, login, device, or permission dependency.

Shape the proposal as a short story: establish what exists before the command, show the action without wasted motion, prove the promised result, and finish on the strongest useful frame. Every spoken claim must have matching visual evidence. Remove dead time, redundant file browsing, terminal noise, and actions that do not advance the demonstration. Narration explains meaning while the image supplies evidence; it should not mechanically read filenames already visible.

Use a beat table with these columns unless the user requests another format: `Beat`, `Estimated time`, `On screen`, `Operator action`, `Narration intent`, and `Proof/exit condition`. Follow it with the proposed exact command text, initial-frame checklist, expected generated artifacts, and open questions or risks.

Write the draft `recording-plan.md` and recipe/recorder files when the user asked to create the production package, but mark them as draft. Then stop and request review. Approval of the concept is not approval to begin recording.

Read [references/story-direction.md](references/story-direction.md) when drafting or revising the proposal. Read [references/package-contract.md](references/package-contract.md) when creating the package. Read [references/recording-workflow.md](references/recording-workflow.md) before generating or running macOS/VS Code automation. Also read [references/vscode-default-profile.md](references/vscode-default-profile.md), load an approved workstation profile when one exists, and preserve its calibrated layout across takes. When none exists, calibrate once outside capture and save the resulting values with the production package.

## Phase 2: generate the reproducible package

After the plan is approved, generate one permanent recorder and its data under the episode's `production/` subfolder. Build the recorder from reusable primitives in `scripts/recording_runtime.py`, but copy that runtime into the production package so recreation does not depend on this installed skill or its future version. Reserve the episode root for the final upload-ready MP4, external SRT, and one publishing-metadata document.

The recorder must:

- accept or derive the source project path without embedding a random temporary path;
- create a fresh disposable copy for every take unless the workflow genuinely requires the original; select a short, dedicated copies directory from the recipe, `TECHNICAL_DEMO_COPIES_ROOT`, or the runtime default, append a random slug, and keep helpers in a separate system-temp directory so printed absolute paths remain readable;
- verify preconditions before opening applications;
- prepare the initial frame before capture begins;
- identify and assert the exact target window before every UI action block;
- record real event timestamps from the same clock as capture;
- refuse to overwrite existing recordings or user-provided audio;
- let validation-only checks inspect draft, approved, and finalized packages, while allowing a real capture only when the recipe is explicitly approved and its timing is ready;
- stop capture before closing the project window;
- close only the window it opened and remove all temporary copies and helpers in `finally` cleanup.

For VS Code captures, make the accepted workstation-profile preparation part of every generated recorder. Project-specific recipes begin after that common preparation and contain only the actions that tell the episode's story. Store display selection, logical geometry, shortcuts, terminal-divider coordinates, and panel behavior as profile data rather than scattering machine-specific values through the recorder.

Retakes modify the same permanent recorder or declarative recipe. Names such as `take-02` identify output media, never different throwaway automation scripts.

## Phase 3: announce and capture

Immediately before a real capture, send a commentary message beginning with `🎬` that says recording is about to start and asks the user not to move the mouse or keyboard. Allow a short visible lead time before starting. Never begin a capture in the same tool call that first announces it.

Do all setup outside the recording: open the isolated project window, arrange panels, open the terminal, choose the correct device or simulator state, and remove Welcome or unrelated tabs. Capture only the approved sequence. Do not introduce extra pauses merely to fit provisional narration.

When a simulator or emulator is needed only for a later proof beat, boot it, wait for readiness, warm the build, and terminate any previously running copy of the demonstrated app without activating the simulator window. Bring that app to the foreground only at the scheduled recorded action. This keeps preparation invisible and avoids leaving an old runtime state on screen.

After capture, perform only inexpensive structural checks: confirm that capture exited, the video and event log exist, and the disposable copy was removed. Then ask the user how the take looked before extracting frames, building contact sheets, transcribing, or performing detailed visual analysis. The user watched the live sequence and is the primary first reviewer.

Inspect frames only when the user requests it, reports a specific problem that needs diagnosis, or could not watch the take. Correct confirmed automation defects by editing the same recorder and creating a new take. Do not generate final narration for a rejected take.

## Phase 4: narration and delivery

Choose the timing authority explicitly. The default is capture-first: write narration after an accepted visual sequence, derive cue boundaries from its event log, then create narration text, cue JSON, and external SRT. When the user wants an externally generated voice track to determine the video duration, use audio-first instead: approve final narration before capture, preserve ordinary paragraph breaks, measure the returned audio, and only then lock and execute the visual recipe. Keep an audio-first recipe in draft until those measurements exist.

For voice-generator input, use fluent prose and normal paragraph breaks by default. Do not inject pause-control tags such as `[short pause]`, `[pause]`, `[long pause]`, or SSML `<break>` unless the user explicitly requests provider-specific pause markup. Do not burn subtitles into the image unless explicitly requested.

If the user generates voice audio in an external service, preserve the original file. Align speech blocks to cues without stretching the voice, and report a paragraph/block mismatch rather than guessing. Creating paid audio or using an external account requires the user's authorization.

Measure the first and last audible speech in the returned audio instead of relying only on the container duration. Unless the brief specifies otherwise, allow roughly 0.35 seconds before the first spoken word and 1.5 seconds after the last spoken word, with a normal acceptable post-roll range of 1–2 seconds. Count silence already present in the audio toward those margins, avoid doubling it, and never use `-shortest` when it would remove the clean final frame. Read [references/audio-timing.md](references/audio-timing.md) before timing or assembling narration.

Do not settle for placing the complete narration track under the capture when the spoken paragraphs and visible actions drift apart. After the take is accepted, compare every narration paragraph with its intended event and perform block-level editorial alignment whenever needed: preserve every spoken sample unchanged, trim only surplus silence at known paragraph boundaries, and place each paragraph against the action or proof it explains. Adjust visual holds or cuts when that produces the more natural result; never create one conspicuous pause to absorb a distributed timing mismatch. Record the source and final ranges in the cue sheet or recording plan so the edit is reproducible. If paragraph boundaries cannot be identified confidently, stop and report the mismatch instead of cutting through speech.

Verify the final video visually and audibly. Review the beginning, every paragraph transition, every command/result beat, and the ending rather than checking duration alone. Keep a clean final frame after the last spoken line. Preserve the complete reproducible package and remove only intermediates identified by the package contract.

Before naming any render `<slug>-final.mp4`, read [references/youtube-master.md](references/youtube-master.md) and pass its delivery-master quality gate. A stream-copied mux is a review preview, not a final upload file. Validate resolution, constant frame rate, bitrate, H.264 profile, pixel format, BT.709 metadata, AAC sample rate, and fast-start layout; never infer quality from the `.mp4` extension or 4K dimensions alone.

Use `scripts/events_to_cues.py` to normalize a completed event log. The generated SRT must reflect final audio alignment rather than estimated plan timings.

When the user requests a vertical or social-media derivative, read [references/vertical-social-video.md](references/vertical-social-video.md). Keep it opt-in: do not reframe a horizontal master or burn dynamic captions merely because social delivery might be useful later.

When the user requests titles, descriptions, keywords, hashtags, upload settings, or a complete social publishing handoff, read [references/publishing-metadata.md](references/publishing-metadata.md). Browse current official platform documentation because these recommendations and limits change, then create one clearly grouped metadata document for each episode.

When the user requests automated YouTube upload, playlist placement, captions, scheduling, or metadata publication, read [references/youtube-publishing.md](references/youtube-publishing.md). Use `scripts/youtube_publish.py` with a production manifest. Dry-run and validate by default; an actual API upload is an external mutation and requires explicit authorization in that turn. Default new uploads to private, never invent a playlist ID, and preserve an upload receipt so retries do not create duplicate videos.
