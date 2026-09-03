# macOS and VS Code recording workflow

Use this reference only when the accepted plan will control VS Code or other Mac applications.

## Preparation

Keep preparation out of the capture unless it is part of the story. Open a uniquely identifiable project window, stabilize its size and position, arrange Explorer/editor/terminal panels, close unrelated tabs, and prepare simulators or devices before starting `screencapture`.

Use [vscode-default-profile.md](vscode-default-profile.md) to define a baseline for the current workstation. Reuse an approved profile across projects instead of experimenting with panel commands or coordinates in each episode. Recalibrate only after a display, VS Code layout, keybinding, or global editor-association change.

On VS Code, use full project-relative paths with Quick Open. Keep terminal commands readable and execute them from the project root without exposing temporary absolute paths. Prefer stable commands and accessibility selectors. When coordinates are unavoidable, store them as configurable logical-display values and validate display/window geometry first.

Choose a dedicated, short copies directory before generating the recorder. Record that choice in the recipe or set `TECHNICAL_DEMO_COPIES_ROOT`; the reusable runtime otherwise uses `~/TechnicalDemos`. Place each disposable project directly beneath it with a short runtime slug such as `build-assets.a1b2c3`. Keep helpers and diagnostic screenshots in a separate system-temp directory. This makes printed absolute paths legible, keeps the Desktop clean, and lets `finally` remove only the current run's resources.

A fresh disposable folder prevents stale project tabs and generated files, but it does not guarantee a fresh panel height: VS Code can inherit non-maximized panel geometry across windows. Detect and verify the actual divider position as described in [vscode-default-profile.md](vscode-default-profile.md); do not treat a hard-coded starting `y` coordinate as part of the profile.

## Safe targeting

Before every AppleScript or UI action block:

1. find the window by the current run's unique slug;
2. raise that exact window;
3. make its owning process frontmost;
4. re-read the front window title;
5. abort unless it still contains the slug;
6. only then send the intended action.

Never assume activating an application preserves the correct window. Never paste a generated temporary slug into permanent source; create it at runtime.

## Capture and events

Use macOS `screencapture` for actual video, not a sequence of screenshots. Record `recording_started`, each visual transition, command submission/completion, relevant output, and `recording_stopped` with monotonic timestamps. Wait for observable completion such as a process exit, file creation, simulator state, or expected UI rather than an arbitrary long sleep.

Stop capture cleanly before closing the demonstration window. Close the full project window afterward so the user can see that interaction is finished. Cleanup must target only resources created by the current run.

Afterward, verify only that the expected media/log files exist and the temporary project is gone. Ask the user how the live take looked before spending time or tokens on screenshots, contact sheets, frame-by-frame review, transcription, or narration. Use deeper inspection only to investigate feedback or when the user asks for it.

## User coordination

Before capture, announce with `🎬` in a separate commentary update and ask the user not to touch input devices. Do not surface permission dialogs during the recording; preflight permissions before the announcement. If a permission or login prompt appears unexpectedly, reject the take, stop safely, and explain what must be prepared.
