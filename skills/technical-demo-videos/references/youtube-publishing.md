# Automated YouTube publishing

Read this only when the user wants to automate YouTube upload or post-upload configuration.

## Official capability and boundary

Google does not provide a general-purpose official `youtube` CLI for this workflow. Use the official YouTube Data API v3, preferably through Google's supported client libraries. The reusable `scripts/youtube_publish.py` wrapper covers:

1. `videos.insert`: resumable video upload plus title, description, tags, category, language, privacy, audience declaration, embedding, license, and optional schedule.
2. `playlistItems.insert`: add the returned video ID to one explicitly supplied playlist ID.
3. `captions.insert`: upload the timed SRT as a named language track.
   For a corrected SRT on an existing video, `captions.update` replaces the
   media of the exact track recorded in the upload receipt.
4. `thumbnails.set`: upload an optional custom PNG or JPEG.

YouTube Studio settings that are not exposed by these resources still require manual configuration. Do not promise automation for an undocumented Studio control.

## One-time account setup

The user must perform or authorize these steps:

1. Create or select a Google Cloud project.
2. Enable YouTube Data API v3.
3. Create an OAuth 2.0 client for a Desktop application and download its client-secret JSON.
4. Complete the browser consent flow on the first executed upload.
5. Identify the expected YouTube channel ID. The upload script verifies that the OAuth token exposes this exact channel before any mutation.
6. Choose either one exact playlist ID or explicitly choose no playlist. List or resolve playlists only after OAuth; never infer an ID from a playlist name.

When the channel or playlist IDs are unknown, inspect the authenticated account without uploading:

```bash
python3 scripts/youtube_publish.py --inspect-account \
  --client-secrets /secure/path/client_secret.json \
  --token /secure/path/youtube-token.json
```

Present the returned channel IDs/titles and playlist IDs/titles to the user. Account inspection is read-only, but starting OAuth or accessing an external account still requires authorization. Do not select a channel or playlist on the user's behalf.

Use the `https://www.googleapis.com/auth/youtube.force-ssl` scope when one workflow must upload video, manage playlists, and upload captions. Store the refresh token outside the source repository with owner-only permissions. Never commit the client-secret JSON, token, or upload receipt containing private operational data.

API projects created after July 28, 2020 that have not passed YouTube's compliance audit can upload only private videos. Treat that as a platform restriction, not a script failure.

## Safe publication contract

- Before generating the manifest, obtain approval for the expected channel, playlist or explicit no-playlist choice, privacy/schedule, captions, and thumbnail.
- Generate `production/<slug>-youtube-upload.json` from those approved decisions.
- Use paths relative to the manifest. The video and SRT normally point one directory upward to the episode root.
- Keep `privacyStatus` as `private` by default.
- A public, unlisted, or scheduled publication requires explicit user authorization and the script's `--allow-public` switch.
- Run without `--execute` first. Dry-run validates files and prints the expected channel, explicit playlist choice, privacy/schedule, captions, thumbnail, hashes, intended mutations, and a confirmation token without authenticating or calling YouTube.
- Present that dry run and wait for separate upload authorization. Pass its exact token through `--confirm-plan`; any file or metadata change invalidates it and requires a new dry run.
- After OAuth and before any mutation, compare the authenticated channel with `expectedChannelId` and verify that any selected playlist exists on that channel. Abort on a mismatch.
- On execution, write `production/<slug>-youtube-upload-receipt.json` immediately after `videos.insert`, then update it after playlist, caption, and thumbnail operations. A retry reuses the recorded video ID and skips completed stages.
- Verify the returned video ID, URL, playlist insertion, caption-track ID, processing state, and intended privacy status before declaring publication complete.
- Do not delete or replace an existing YouTube video automatically. Stop and request direction when metadata or file hashes disagree with an existing receipt.

## Manifest shape

```json
{
  "schemaVersion": 1,
  "videoFile": "../03-semantic-final.mp4",
  "captionsFile": "../03-semantic-subtitles-en.srt",
  "thumbnailFile": null,
  "title": "Example title",
  "description": "Example description",
  "tags": ["Example Product", "Technical Tutorial"],
  "categoryId": "28",
  "defaultLanguage": "en",
  "expectedChannelId": "UC_EXACT_CHANNEL_ID",
  "privacyStatus": "private",
  "selfDeclaredMadeForKids": false,
  "embeddable": true,
  "license": "youtube",
  "publishAt": null,
  "playlistId": null,
  "caption": {
    "language": "en",
    "name": "English",
    "isDraft": false
  }
}
```

`categoryId` `28` is Science & Technology. Keep the ID configurable rather than deriving it from prose.
`playlistId: null` is an explicit decision to leave the video out of playlists; omitting the field is invalid. All target fields remain user/project data, never skill defaults.

## Usage

Dry run requires only Python:

```bash
python3 scripts/youtube_publish.py production/<slug>-youtube-upload.json
```

Copy the printed `confirmationToken` only after the user approves that exact dry-run summary.

Account inspection and real execution additionally need Google's official Python clients:

```bash
python3 -m pip install google-api-python-client google-auth-oauthlib google-auth-httplib2
python3 scripts/youtube_publish.py production/<slug>-youtube-upload.json \
  --client-secrets /secure/path/client_secret.json \
  --token /secure/path/youtube-token.json \
  --confirm-plan CONFIRMATION_TOKEN_FROM_APPROVED_DRY_RUN \
  --execute
```

To replace an already uploaded caption track without deleting or duplicating
the video, repeat the command with `--replace-captions`. This requires the
existing receipt and its exact `captionId`.

Add `--allow-public` only after the user approves `unlisted`, `public`, or `publishAt`. Do not use that flag for the normal private-first review workflow.

## Official references

- Video upload: https://developers.google.com/youtube/v3/docs/videos/insert
- Official Python upload guide: https://developers.google.com/youtube/v3/guides/uploading_a_video
- Authenticated channel lookup: https://developers.google.com/youtube/v3/docs/channels/list
- Authenticated playlist lookup: https://developers.google.com/youtube/v3/docs/playlists/list
- Playlist insertion: https://developers.google.com/youtube/v3/docs/playlistItems/insert
- Caption upload: https://developers.google.com/youtube/v3/docs/captions/insert
- Caption replacement: https://developers.google.com/youtube/v3/docs/captions/update
- Custom thumbnail: https://developers.google.com/youtube/v3/docs/thumbnails/set
- OAuth for installed apps: https://developers.google.com/youtube/v3/guides/auth/installed-apps
- Quotas: https://developers.google.com/youtube/v3/determine_quota_cost
