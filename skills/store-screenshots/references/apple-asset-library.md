# Apple Asset Library

Verified 2026-10-17. Asset Library stores an app's images/videos; placements determine where approved compatible assets appear. It is not a separate artwork size, a replacement for editable local masters, or an automatic publishing step.

## Upload, inspect and reuse

In Apps → app → Asset Library → +, choose Upload Creative Assets or Previews and Screenshots, select files and Upload. First validate them against [creative specifications](apple-creative-assets.md) or [media specifications](apple-media.md).

Name assets so locale, campaign and revision are identifiable. Filter by Type, Status and Format. In detail, inspect **Works With** for eligible placements and **Recent Usage** for existing use. Do not infer compatibility only from dimensions. Poster frames are shared everywhere an asset is used; assess all usages before changing one, and check whether approved-state restrictions require a new asset.

Use Browse Assets in the intended version, CPP, PPO treatment or event. Approved compatible resources can be reused; assets in Prepare for Submission can also be selected for configuration, but still need review. Record identity and destination in the manifest. Library presence/approval does not select a page, reorder its screenshots or publish a placement. Media Manager controls device/localization-specific placements; page editors operate in their current page/treatment context.

Source: [Manage your App Store assets](https://developer.apple.com/help/app-store-connect/manage-app-information/manage-your-app-store-assets).

## Submission rules

| App/submission state | Required handling |
| --- | --- |
| No approved app version yet | Include assets with the first app version submission |
| An approved app version exists | Standalone library submission is available; choose the platform, reviewed with its latest version |
| Asset assigned to an app version, CPP, PPO or event submission | Reviewed with that item; do not submit it separately while the associated item is in an active submission |

Submit through Asset Library → Edit → select assets → Add for Review → existing/new draft → Submit for Review. Managing assets permits Account Holder/Admin/App Manager/Marketing; the standalone submission guide lists Account Holder/Admin/App Manager. Check the operation's permission rather than assuming upload access grants submission access.

Source: [Submit assets from Asset Library](https://developer.apple.com/help/app-store-connect/manage-submissions-to-app-review/submit-assets-from-asset-library).

## Archive, delete and record state

Deletion is allowed only before submission (the management guide says Prepared for Submission; the status reference says Prepare for Submission). Preserve the console's actual label rather than assuming those strings are an API enum. Archiving makes an asset unavailable for new placements; carrying it into a new version of an existing placement may restore it automatically. Unarchive restores availability. Removing a placement does not delete the library asset; do not use archive as a substitute for withdrawing a live placement. Inspect usage before cleanup and stay within the requested operation's authorization.

Source: [Library lifecycle](https://developer.apple.com/help/app-store-connect/manage-app-information/manage-your-app-store-assets).

Record filename/hash, asset ID when available, type, dimensions, locale, Works With, usage, poster timestamp, processing/review state, selected placements and observed publication state. If console access is unavailable, prepare files and the mapping, and report library/placement status as unverified. If an upload fails, preserve its exact error and inspect format, type, processing state and permissions before uploading duplicates.

## Asset statuses and next action

| Status | Meaning / handling |
| --- | --- |
| Uploading | Transfer is in progress; do not assume completion |
| Processing | Validation is running; actions are unavailable until it completes |
| Prepare for Submission | Uploaded, not reviewed; can configure placements or delete |
| Ready for Review | Added to a submission, not yet sent to review |
| Waiting for Review | Submitted, review has not started |
| In Review | Review is active; cancellation acts on the submission |
| Accepted | Asset accepted, but rejected sibling items block publication; resolve/remove those items |
| Approved | Asset approved; verify placement and publication separately |
| Rejected | Inspect the reason; correct and resubmit or remove the item |
| Archived | Historical/replaced asset, hidden by default; locate using filters |

Source: [App Store asset statuses](https://developer.apple.com/help/app-store-connect/reference/app-information/app-store-asset-statuses).

Record the observed state and error before retrying. Do not re-upload duplicates merely because processing/review is pending, or describe Accepted as publicly live. Use bounded rechecks, then gather the file's probe results, submission association and error/status evidence if progress stalls; escalate missing permissions or persistent processing failures instead of polling indefinitely. Apple's documented App Preview processing allowance is in [apple-media.md](apple-media.md), not a universal deadline for every asset type.
