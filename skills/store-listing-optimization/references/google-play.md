# Google Play listing text

Checked 2026-10-30. Recheck current official requirements and console labels before applying.

The main listing has name (30 characters), short description (80) and full description (4,000). There is no Apple-style separate keyword field. Write relevant search terms naturally; avoid word lists, repetition, unsupported rankings and promotional claims in restricted fields. State the app's actual purpose clearly.

Inspect every existing locale and inherited resource. Copy changes can be reviewed independently of a new binary. Saving in the listing editor can leave changes ready to send: inspect Publishing overview, check the exact pending fields, submit within authorization and verify receipt. Automated checks or “in review” do not mean the public listing changed.

Listing performance now emphasizes unique install/open/pre-registration clicks, not completed acquisitions. Grow users and Statistics provide acquisition measures. Confirm the actual label, date range and audience before comparing reports. “Paid and direct” is a combined source, not proof of paid advertising alone.

For custom listings, experiments, screenshots, video and asset AI declarations, use the corresponding `store-screenshots` reference. Text editing does not establish the provenance of existing artwork or authorize changing its declaration.

Sources:

- [Main listing setup](https://support.google.com/googleplay/android-developer/answer/9859152).
- [Metadata policy](https://support.google.com/googleplay/android-developer/answer/9898842).
- [Preview assets and short description](https://support.google.com/googleplay/android-developer/answer/9866151).
- [Listing performance definitions](https://support.google.com/googleplay/android-developer/answer/9859173).

## Submit a release alongside listing changes

Release workflow checked 2026-10-31 against [Prepare and roll out a release](https://support.google.com/googleplay/android-developer/answer/9859348). Follow current console labels rather than assuming a saved editor submits changes.

For an authorized app update, upload the intended signed AAB or select its existing library entry in the intended track. Verify the versionName/versionCode parsed by Play and complete localized release notes. Continue through Next to preview/confirmation, inspect blocking errors and material warnings, and preserve the intended rollout settings.

A Save action can leave the release in Changes ready to send for review in Publishing overview. Inspect that overview and send the authorized release and listing changes; exclude unrelated drafts. Verify the sending receipt and resulting automated-check/review state. An uploaded AAB or saved release alone is incomplete. If the current control would publish immediately rather than submit for review, check that publication is within the user's authorization before using it.
