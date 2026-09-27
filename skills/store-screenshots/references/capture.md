# Capture real screens

## Establish a reproducible session

Inventory installed tools, devices, runtimes, app IDs, and compatible builds. Record device ID/model, OS/runtime, native pixels, logical size/density, orientation, app version/build, locale/theme, capture time, and navigation steps. Use an explicit serial/UDID throughout. Keep actual account information, credentials, and private content out of published screenshots; use an authorized demo account when needed.

Prefer an available simulator/emulator that matches the app's supported platform and selected upload slot. Do not prescribe one permanent device model. Check official store requirements first. Native resolution may differ from final canvas resolution; preserve the original and compose it proportionally later.

Installing a compatible build on an authorized emulator is part of capture work. Do not reset, uninstall, or overwrite a user's physical-device app/data without authorization. Preserve source edits and existing build outputs; use an isolated build location when necessary. Mark debug/test content accurately and verify it represents the release.

## Android

Discover devices and configurations:

```bash
adb devices -l
emulator -list-avds
adb -s SERIAL shell wm size
adb -s SERIAL shell wm density
adb -s SERIAL shell getprop ro.build.version.release
```

On macOS the SDK emulator is commonly under `$HOME/Library/Android/sdk/emulator/emulator`; use the discovered SDK path, not an obsolete `tools/emulator`. Choose a compatible ABI/runtime. Tablet identity depends on logical size and app behavior as well as physical pixels; a resized phone is not evidence of tablet support.

Resolve the installed package's launchable activity with package-manager tools, then launch with its normal launcher intent:

```bash
adb -s SERIAL shell am start -a android.intent.action.MAIN -c android.intent.category.LAUNCHER -f 0x10200000 -n PACKAGE/ACTIVITY
adb -s SERIAL exec-out screencap -p > candidate.png
```

Use accessibility/UI automation (available Appium, Maestro, UIAutomator, or computer tools) to navigate. Inspect the current hierarchy/screen before tapping; avoid brittle coordinates across devices. Discover command syntax from the installed tool's help. Record navigation so another agent can reproduce it.

Use binary capture, no pseudo-terminal or text decoding. Inspect `candidate.png`, then copy/promote that exact file to the selected capture path. Do not take a second frame after inspection and silently substitute it; live content may have changed.

If changing emulator resolution, density, rotation, network, or demo status bar, record original settings and restore session overrides afterward. Never infer real throttling from a “3G” status icon. Check emulator network configuration and actual requests before diagnosing a slow server.

## iOS / iPadOS (macOS + Xcode)

```bash
xcrun simctl list devices available --json
xcrun simctl list runtimes --json
xcrun simctl boot UDID
xcrun simctl bootstatus UDID -b
xcrun simctl install UDID /path/to/SimulatorBuild.app
xcrun simctl launch UDID BUNDLE_ID
xcrun simctl io UDID screenshot candidate.png
```

Skip boot if already booted. A device-only build cannot necessarily run in Simulator. Select an installed runtime supported by the project, build with its documented workflow, and verify the actual phone/tablet UI.

`simctl` captures and launches; it is not a general tap/navigation API. Use available accessibility automation, Appium, Maestro, XCTest, or computer control for navigation. If none is available, report the specific navigation blocker and complete independent preparation; do not claim simulated captures. Optional `simctl status_bar` overrides should follow the installed help and be cleared afterward.

## A screenshot is ready only when its content is ready

Wait for observable state: expected title and content, resolved images, dismissed loading indicator, intended scroll position, and intact navigation. Fixed sleep alone is insufficient. Check the saved pixels, not just the automation result. A partial image, ellipsis instead of a logo, or empty page is a failed capture.

For live content, refresh and verify current results, selected category, cache behavior, and featured ordering before blaming API logic. Group related takes in a stable session; note unavoidable content differences between platforms. Network failures in one emulator do not establish a production outage.

After two repeated identical failures, gather logs/network evidence and change the diagnostic approach rather than waiting indefinitely. Keep failed takes out of final folders. If app changes or backend access are needed beyond authorization, identify the blocker; do not conceal it by painting over the screenshot. Once fixed within scope, recapture affected screens and recheck the series.

Preserve selected native PNGs unchanged. Clean system status bars through device controls when appropriate; never manufacture app state or silently edit out real errors.
