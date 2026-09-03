#!/usr/bin/env python3

"""Safely publish a prepared technical-demo package through YouTube Data API."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path


SCOPE = 'https://www.googleapis.com/auth/youtube.force-ssl'
PUBLIC_STATES = {'public', 'unlisted'}


def parse_args():
  parser = argparse.ArgumentParser()
  parser.add_argument('manifest', type=Path, nargs='?')
  parser.add_argument('--client-secrets', type=Path)
  parser.add_argument('--token', type=Path)
  parser.add_argument('--receipt', type=Path)
  parser.add_argument(
    '--inspect-account', action='store_true',
    help='list the authenticated channel and playlists without uploading'
  )
  parser.add_argument('--execute', action='store_true')
  parser.add_argument(
    '--confirm-plan',
    help='confirmation token printed by the approved dry run'
  )
  parser.add_argument('--allow-public', action='store_true')
  parser.add_argument(
    '--replace-captions', action='store_true',
    help='replace the caption file for the track stored in the receipt'
  )
  return parser.parse_args()


def sha256(path):
  digest = hashlib.sha256()
  with path.open('rb') as handle:
    for chunk in iter(lambda: handle.read(1024 * 1024), b''):
      digest.update(chunk)
  return digest.hexdigest()


def metadata_sha256(payload):
  artifact_keys = {'videoFile', 'captionsFile', 'thumbnailFile'}
  metadata = {
    key: value for key, value in payload.items()
    if key not in artifact_keys
  }
  serialized = json.dumps(
    metadata, sort_keys=True, separators=(',', ':')
  ).encode()
  return hashlib.sha256(serialized).hexdigest()


def confirmation_token(video_hash, metadata_hash):
  return hashlib.sha256(
    f'{video_hash}:{metadata_hash}'.encode()
  ).hexdigest()


def resolve_optional(root, value):
  if value in (None, ''):
    return None
  path = (root / value).resolve()
  if not path.is_file():
    raise RuntimeError(f'file not found: {path}')
  return path


def load_manifest(path):
  path = path.resolve()
  payload = json.loads(path.read_text())
  if not isinstance(payload, dict):
    raise RuntimeError('manifest must contain a JSON object')
  if payload.get('schemaVersion') != 1:
    raise RuntimeError('manifest schemaVersion must be 1')
  for key in ('videoFile', 'title', 'description', 'categoryId'):
    if not payload.get(key):
      raise RuntimeError(f'manifest requires {key}')
  for key in (
    'expectedChannelId', 'playlistId', 'privacyStatus', 'publishAt',
    'captionsFile', 'thumbnailFile'
  ):
    if key not in payload:
      raise RuntimeError(f'manifest requires explicit {key}')
  if not isinstance(payload['expectedChannelId'], str) or not payload['expectedChannelId'].strip():
    raise RuntimeError('expectedChannelId must be a non-empty channel ID')
  if payload['playlistId'] is not None and (
    not isinstance(payload['playlistId'], str) or
    not payload['playlistId'].strip()
  ):
    raise RuntimeError('playlistId must be a non-empty ID or null')
  if len(payload['title']) > 100:
    raise RuntimeError('YouTube title exceeds 100 characters')
  if len(payload['description']) > 5000:
    raise RuntimeError('YouTube description exceeds 5000 characters')
  privacy = payload.get('privacyStatus', 'private')
  if privacy not in {'private', 'unlisted', 'public'}:
    raise RuntimeError('privacyStatus must be private, unlisted, or public')
  if payload.get('publishAt') and privacy != 'private':
    raise RuntimeError('publishAt requires privacyStatus private')
  if payload['captionsFile'] is not None and not isinstance(
    payload.get('caption'), dict
  ):
    raise RuntimeError('caption settings are required when captionsFile is set')

  root = path.parent
  files = {
    'video': resolve_optional(root, payload['videoFile']),
    'captions': resolve_optional(root, payload.get('captionsFile')),
    'thumbnail': resolve_optional(root, payload.get('thumbnailFile'))
  }
  return path, payload, files


def planned_operations(payload, files, receipt, replace_captions=False):
  operations = []
  if not receipt.get('videoId'):
    operations.append({
      'operation': 'videos.insert',
      'file': str(files['video']),
      'privacyStatus': payload.get('privacyStatus', 'private'),
      'publishAt': payload.get('publishAt')
    })
  if payload.get('playlistId') and not receipt.get('playlistInserted'):
    operations.append({
      'operation': 'playlistItems.insert',
      'playlistId': payload['playlistId']
    })
  if files['captions'] and (
    not receipt.get('captionsUploaded') or replace_captions
  ):
    operations.append({
      'operation': (
        'captions.update' if replace_captions else 'captions.insert'
      ),
      'file': str(files['captions']),
      'language': payload.get('caption', {}).get('language', 'en')
    })
  if files['thumbnail'] and not receipt.get('thumbnailUploaded'):
    operations.append({
      'operation': 'thumbnails.set',
      'file': str(files['thumbnail'])
    })
  return operations


def load_google_clients():
  try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
  except ImportError as exc:
    raise RuntimeError(
      'missing Google clients; install google-api-python-client, '
      'google-auth-oauthlib, and google-auth-httplib2'
    ) from exc
  return Request, Credentials, InstalledAppFlow, build, MediaFileUpload


def authenticate(client_secrets, token_path, google):
  Request, Credentials, InstalledAppFlow, build, _ = google
  credentials = None
  if token_path.is_file():
    credentials = Credentials.from_authorized_user_file(token_path, [SCOPE])
  if credentials and credentials.expired and credentials.refresh_token:
    credentials.refresh(Request())
  if not credentials or not credentials.valid:
    flow = InstalledAppFlow.from_client_secrets_file(
      str(client_secrets), [SCOPE]
    )
    credentials = flow.run_local_server(port=0)
  token_path.parent.mkdir(parents=True, exist_ok=True)
  token_path.write_text(credentials.to_json())
  os.chmod(token_path, 0o600)
  return build('youtube', 'v3', credentials=credentials)


def authenticated_channels(youtube):
  response = youtube.channels().list(
    part='id,snippet', mine=True, maxResults=50
  ).execute()
  channels = [
    {
      'id': item['id'],
      'title': item.get('snippet', {}).get('title')
    }
    for item in response.get('items', [])
  ]
  if not channels:
    raise RuntimeError('OAuth token has no accessible YouTube channel')
  return channels


def verify_expected_channel(youtube, expected_channel_id):
  channels = authenticated_channels(youtube)
  selected = next(
    (channel for channel in channels if channel['id'] == expected_channel_id),
    None
  )
  if selected is None:
    actual = ', '.join(channel['id'] for channel in channels)
    raise RuntimeError(
      f'authenticated channel mismatch: expected {expected_channel_id}; '
      f'token provides {actual}'
    )
  return selected


def authenticated_playlists(youtube):
  playlists = []
  page_token = None
  while True:
    response = youtube.playlists().list(
      part='id,snippet', mine=True, maxResults=50,
      pageToken=page_token
    ).execute()
    playlists.extend({
      'id': item['id'],
      'title': item.get('snippet', {}).get('title'),
      'channelId': item.get('snippet', {}).get('channelId')
    } for item in response.get('items', []))
    page_token = response.get('nextPageToken')
    if not page_token:
      return playlists


def verify_playlist(youtube, playlist_id, expected_channel_id):
  if playlist_id is None:
    return None
  response = youtube.playlists().list(
    part='id,snippet', id=playlist_id, maxResults=1
  ).execute()
  items = response.get('items', [])
  if not items:
    raise RuntimeError(f'playlist not found or inaccessible: {playlist_id}')
  snippet = items[0].get('snippet', {})
  actual_channel_id = snippet.get('channelId')
  if actual_channel_id != expected_channel_id:
    raise RuntimeError(
      f'playlist channel mismatch: expected {expected_channel_id}; '
      f'playlist belongs to {actual_channel_id}'
    )
  return {
    'id': items[0]['id'],
    'title': snippet.get('title'),
    'channelId': actual_channel_id
  }


def require_auth_paths(args):
  if not args.client_secrets or not args.client_secrets.is_file():
    raise RuntimeError('--client-secrets must identify the OAuth client JSON')
  if not args.token:
    raise RuntimeError('--token must identify an external token JSON path')


def save_receipt(path, receipt):
  temporary = path.with_suffix(path.suffix + '.tmp')
  temporary.write_text(json.dumps(receipt, indent=2) + '\n')
  temporary.replace(path)


def resumable_upload(request):
  response = None
  while response is None:
    status, response = request.next_chunk()
    if status:
      print(f'upload: {round(status.progress() * 100, 1)}%')
  return response


def main():
  args = parse_args()
  if args.inspect_account:
    if args.manifest:
      raise RuntimeError('--inspect-account does not accept a manifest')
    if (
      args.execute or args.confirm_plan or args.allow_public or
      args.replace_captions or args.receipt
    ):
      raise RuntimeError('--inspect-account cannot be combined with upload flags')
    require_auth_paths(args)
    google = load_google_clients()
    youtube = authenticate(
      args.client_secrets.resolve(), args.token.resolve(), google
    )
    print(json.dumps({
      'mode': 'inspect-account',
      'channels': authenticated_channels(youtube),
      'playlists': authenticated_playlists(youtube)
    }, indent=2))
    return

  if args.manifest is None:
    raise RuntimeError('manifest is required unless --inspect-account is used')
  manifest_path, manifest, files = load_manifest(args.manifest)
  receipt_path = (
    args.receipt.resolve() if args.receipt else
    manifest_path.with_name(
      manifest_path.stem.replace('-upload', '-upload-receipt') + '.json'
    )
  )
  video_hash = sha256(files['video'])
  metadata_hash = metadata_sha256(manifest)
  plan_confirmation = confirmation_token(video_hash, metadata_hash)
  receipt = {}
  if receipt_path.is_file():
    receipt = json.loads(receipt_path.read_text())
    if receipt.get('videoSha256') != video_hash:
      raise RuntimeError('receipt video hash differs; refusing a duplicate upload')
    if (
      receipt.get('metadataSha256') and
      receipt['metadataSha256'] != metadata_hash
    ):
      raise RuntimeError('receipt metadata differs; review before continuing')

  if args.replace_captions and not receipt.get('captionId'):
    raise RuntimeError(
      '--replace-captions requires captionId in the upload receipt'
    )
  if files['captions'] and receipt.get('captionsSha256'):
    captions_hash = sha256(files['captions'])
    if (
      captions_hash != receipt['captionsSha256'] and
      not args.replace_captions
    ):
      raise RuntimeError(
        'caption file differs from receipt; use --replace-captions after review'
      )
  if files['thumbnail'] and receipt.get('thumbnailSha256'):
    if sha256(files['thumbnail']) != receipt['thumbnailSha256']:
      raise RuntimeError('thumbnail file differs from receipt; review before continuing')

  plan = planned_operations(
    manifest, files, receipt, args.replace_captions
  )
  print(json.dumps({
    'mode': 'execute' if args.execute else 'dry-run',
    'manifest': str(manifest_path),
    'videoSha256': video_hash,
    'metadataSha256': metadata_hash,
    'confirmationToken': plan_confirmation,
    'target': {
      'expectedChannelId': manifest['expectedChannelId'],
      'playlistId': manifest['playlistId'],
      'privacyStatus': manifest['privacyStatus'],
      'publishAt': manifest['publishAt'],
      'captionsFile': manifest['captionsFile'],
      'thumbnailFile': manifest['thumbnailFile']
    },
    'operations': plan
  }, indent=2))
  if not args.execute:
    return

  if args.confirm_plan != plan_confirmation:
    raise RuntimeError(
      '--execute requires --confirm-plan with the token from the approved dry run'
    )

  privacy = manifest['privacyStatus']
  if (privacy in PUBLIC_STATES or manifest.get('publishAt')) and not args.allow_public:
    raise RuntimeError(
      'public, unlisted, or scheduled publication requires --allow-public'
    )
  require_auth_paths(args)

  google = load_google_clients()
  youtube = authenticate(
    args.client_secrets.resolve(), args.token.resolve(), google
  )
  channel = verify_expected_channel(
    youtube, manifest['expectedChannelId']
  )
  playlist = verify_playlist(
    youtube, manifest['playlistId'], channel['id']
  )
  MediaFileUpload = google[-1]

  video_id = receipt.get('videoId')
  if not video_id:
    snippet = {
      'title': manifest['title'],
      'description': manifest['description'],
      'tags': manifest.get('tags', []),
      'categoryId': str(manifest['categoryId']),
      'defaultLanguage': manifest.get('defaultLanguage', 'en')
    }
    status = {
      'privacyStatus': privacy,
      'selfDeclaredMadeForKids': bool(
        manifest.get('selfDeclaredMadeForKids', False)
      ),
      'embeddable': bool(manifest.get('embeddable', True)),
      'license': manifest.get('license', 'youtube')
    }
    if manifest.get('publishAt'):
      status['publishAt'] = manifest['publishAt']
    request = youtube.videos().insert(
      part='snippet,status',
      body={'snippet': snippet, 'status': status},
      media_body=MediaFileUpload(
        str(files['video']), mimetype='video/mp4',
        chunksize=8 * 1024 * 1024, resumable=True
      )
    )
    response = resumable_upload(request)
    video_id = response['id']
    receipt.update({
      'schemaVersion': 1,
      'manifest': str(manifest_path),
      'videoSha256': video_hash,
      'metadataSha256': metadata_hash,
      'channelId': channel['id'],
      'channelTitle': channel['title'],
      'playlistId': playlist['id'] if playlist else None,
      'playlistTitle': playlist['title'] if playlist else None,
      'videoId': video_id,
      'url': f'https://youtu.be/{video_id}',
      'videoUploaded': True
    })
    save_receipt(receipt_path, receipt)

  if manifest.get('playlistId') and not receipt.get('playlistInserted'):
    response = youtube.playlistItems().insert(
      part='snippet',
      body={'snippet': {
        'playlistId': manifest['playlistId'],
        'resourceId': {'kind': 'youtube#video', 'videoId': video_id}
      }}
    ).execute()
    receipt.update({
      'playlistInserted': True,
      'playlistItemId': response['id']
    })
    save_receipt(receipt_path, receipt)

  if files['captions'] and (
    not receipt.get('captionsUploaded') or args.replace_captions
  ):
    caption = manifest.get('caption', {})
    media = MediaFileUpload(
      str(files['captions']), mimetype='application/octet-stream'
    )
    if args.replace_captions:
      caption_id = receipt['captionId']
      response = youtube.captions().update(
        part='id', body={'id': caption_id}, media_body=media
      ).execute()
    else:
      response = youtube.captions().insert(
        part='snippet',
        body={'snippet': {
          'videoId': video_id,
          'language': caption.get('language', 'en'),
          'name': caption.get('name', 'English'),
          'isDraft': bool(caption.get('isDraft', False))
        }},
        media_body=media
      ).execute()
    receipt.update({
      'captionsUploaded': True,
      'captionId': response['id'],
      'captionsSha256': sha256(files['captions'])
    })
    save_receipt(receipt_path, receipt)

  if files['thumbnail'] and not receipt.get('thumbnailUploaded'):
    youtube.thumbnails().set(
      videoId=video_id,
      media_body=MediaFileUpload(str(files['thumbnail']))
    ).execute()
    receipt['thumbnailUploaded'] = True
    receipt['thumbnailSha256'] = sha256(files['thumbnail'])
    save_receipt(receipt_path, receipt)

  verification = youtube.videos().list(
    part='status,processingDetails', id=video_id
  ).execute()
  items = verification.get('items', [])
  if not items:
    raise RuntimeError('uploaded video could not be read back for verification')
  verified_video = items[0]
  actual_privacy = verified_video.get('status', {}).get('privacyStatus')
  if actual_privacy != privacy:
    raise RuntimeError(
      f'privacy verification failed: expected {privacy}, found {actual_privacy}'
    )
  receipt['verification'] = {
    'privacyStatus': actual_privacy,
    'uploadStatus': verified_video.get('status', {}).get('uploadStatus'),
    'processingStatus': verified_video.get(
      'processingDetails', {}
    ).get('processingStatus')
  }
  receipt.setdefault('metadataSha256', metadata_hash)
  save_receipt(receipt_path, receipt)

  print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
  try:
    main()
  except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as exc:
    print(f'error: {exc}', file=sys.stderr)
    raise SystemExit(1)
