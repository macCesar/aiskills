# VS Code recording profile

Use this reference to calibrate a workstation once, save the accepted values with the production package, and reuse them across projects and retakes. The numbers below are an example profile for a 4K display, not universal defaults.

## Values the profile owns

- capture display number and physical resolution;
- logical display size and minimum VS Code window size;
- whether an auxiliary panel must be hidden and the shortcut that does it;
- whether Explorer remains visible and on which side;
- whether Welcome is disabled before recording;
- terminal divider detection range, drag coordinate, target height, and tolerance;
- terminal focus shortcut after an editor takes focus;
- file-preview associations needed by the demonstration.

Keep these values in the declarative recipe or pass an equivalent profile to `prepare_default_vscode()`. Do not spread coordinates and shortcuts across project-specific action code.

## Example 4K profile

- Physical capture: 3840 × 2160.
- Logical display: 1920 × 1080.
- VS Code minimum: 1850 × 1000 logical points.
- Terminal divider drag: logical `x=645` to `y=720`, verified within 8 points.
- Terminal open delay: about 1.5 seconds before divider detection.
- Main Explorer remains visible; unrelated auxiliary panels and Welcome are removed before capture.

Recalibrate those values for a different display, scaling mode, VS Code layout, keybinding, or panel placement.

## Integrated terminal preparation

1. Open a uniquely identifiable disposable project in a new VS Code window.
2. Apply the profile's panel state and close unrelated tabs before capture.
3. Use `Terminal` → `New Terminal` after targeting that exact window.
4. Wait for the panel to finish opening.
5. Capture a temporary screenshot and detect the real horizontal divider across several columns. A fresh folder does not guarantee a fresh panel height.
6. Drag the detected separator to the profile's target height.
7. Capture the layout again and verify the divider is within the configured tolerance. Abort before recording if detection fails; never guess the starting coordinate.
8. Store diagnostics under the run's temporary helper directory so cleanup removes them.
9. Leave the terminal open when preparation finishes.

Do not resize with repeated Command Palette steps: they are slower, visible, and dependent on unknown starting height. Do not send the terminal-focus shortcut immediately after creating the terminal because a toggle-style binding may close it. Use it later, after an editor or preview has taken focus and immediately before typing the command.

## Preview behavior

If a source format needs a visual preview, configure and preflight the VS Code association before capture. Open the file directly into that preview during the take. Do not expose the editor-selection menu or change a user setting inside the demonstrated project merely for recording.

## Recording boundary

All profile preparation happens before capture. The first recorded action belongs to the approved story. Save a newly accepted profile instead of rediscovering the same coordinates during every episode.
