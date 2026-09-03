# Production package contract

Prefer an existing project convention. Otherwise propose `demo-videos/<slug>/` beneath the project root, or an external destination when the source repository should remain untouched. Treat the episode root as the upload handoff: it contains only `<slug>-final.mp4`, `<slug>-subtitles-<language>.srt`, `<slug>-publishing-metadata.md`, and the `production/` subfolder.

## Draft and source files

- `production/recording-plan.md`: human-readable approved story, initial frame, visible actions, proof, timing intent, narration beats, risks, and cleanup.
- `production/<slug>-recording.json`: machine-readable values and ordered actions when the recorder is data-driven.
- `production/record-<slug>.py`: permanent entry point for rehearsals, retakes, and recreation.
- `production/recording_runtime.py`: copied reusable automation primitives, pinned with the package.

The recorder and recipe are source artifacts. A take number never appears in their filenames. Choose the next take number after the highest take already present in `production/`; do not reuse gaps left by rejected or archived takes.

## Capture and delivery files

- `production/<slug>-take-01.mov`: raw capture; increment for a retake and never overwrite.
- `production/<slug>-take-01-events.json`: actual monotonic timestamps for the matching capture.
- `production/<slug>-cues.json`: normalized visual and narration intervals for the accepted take.
- `production/<slug>-narration-<language>.txt`: text sent to the voice generator.
- `production/` keeps the original returned audio, with its provider filename preserved when useful.
- `<slug>-subtitles-<language>.srt`: selectable upload-ready captions in the episode root.
- `<slug>-final.mp4`: synchronized delivery master that passed the YouTube master quality gate; a stream-copied review preview does not qualify.
- `<slug>-publishing-metadata.md`: copy-ready YouTube, TikTok and Instagram metadata plus upload settings in the episode root.

Use names appropriate to the project when it already has a convention. The essential rule is that each media file can be traced to the recorder version, recipe, and event log that produced it.

## Temporary material

Disposable project copies, compiled click helpers, diagnostic screenshots, extracted frames, split audio blocks, proxy files, and rejected render intermediates are temporary. Create them in a uniquely named temporary directory and remove that exact directory after verification or failure.

Remove caches and Finder metadata such as `__pycache__/` and `.DS_Store` from the episode root before handoff. They are neither publication files nor production sources.

Never delete source projects, accepted takes, user-provided audio, or an existing artifact merely to reuse its filename.
