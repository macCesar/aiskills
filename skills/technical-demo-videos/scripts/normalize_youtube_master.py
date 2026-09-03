#!/usr/bin/env python3

"""Create and verify a stable YouTube upload master from an approved edit."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from fractions import Fraction
from pathlib import Path


STANDARD_BITRATES = {
  2160: {
    'standard': ('35M', 35_000_000),
    'high': ('53M', 53_000_000)
  },
  1440: {
    'standard': ('16M', 16_000_000),
    'high': ('24M', 24_000_000)
  },
  1080: {
    'standard': ('8M', 8_000_000),
    'high': ('12M', 12_000_000)
  },
  720: {
    'standard': ('5M', 5_000_000),
    'high': ('7.5M', 7_500_000)
  },
  480: {
    'standard': ('2.5M', 2_500_000),
    'high': ('4M', 4_000_000)
  },
  360: {
    'standard': ('1M', 1_000_000),
    'high': ('1.5M', 1_500_000)
  }
}


def parse_args():
  parser = argparse.ArgumentParser()
  parser.add_argument('input', type=Path)
  parser.add_argument('output', type=Path)
  parser.add_argument('--fps', type=int, default=30)
  parser.add_argument('--video-bitrate')
  return parser.parse_args()


def probe(path):
  result = subprocess.run([
    'ffprobe', '-v', 'error', '-show_streams', '-show_format',
    '-of', 'json', str(path)
  ], check=True, capture_output=True, text=True)
  return json.loads(result.stdout)


def stream(payload, kind):
  selected = next(
    (item for item in payload['streams'] if item.get('codec_type') == kind),
    None
  )
  if selected is None:
    raise RuntimeError(f'{kind} stream is required')
  return selected


def parse_bitrate(value):
  suffixes = {'K': 1_000, 'M': 1_000_000}
  suffix = value[-1].upper()
  if suffix in suffixes:
    return int(float(value[:-1]) * suffixes[suffix])
  return int(value)


def default_bitrate(height, fps):
  frame_rate_class = 'high' if fps >= 48 else 'standard'
  for threshold, values in STANDARD_BITRATES.items():
    if height >= threshold:
      return values[frame_rate_class]
  return (
    ('1.5M', 1_500_000) if frame_rate_class == 'high'
    else ('1M', 1_000_000)
  )


def has_faststart(path):
  with path.open('rb') as handle:
    header = handle.read(min(path.stat().st_size, 16 * 1024 * 1024))
  moov = header.find(b'moov')
  mdat = header.find(b'mdat')
  return moov >= 0 and mdat >= 0 and moov < mdat


def validate_master(path, expected_width, expected_height, fps, bitrate):
  payload = probe(path)
  video = stream(payload, 'video')
  audio = stream(payload, 'audio')
  errors = []
  if (video.get('width'), video.get('height')) != (
    expected_width, expected_height
  ):
    errors.append('resolution changed during normalization')
  if video.get('codec_name') != 'h264' or video.get('profile') != 'High':
    errors.append('video must be H.264 High Profile')
  if video.get('pix_fmt') != 'yuv420p':
    errors.append('video pixel format must be yuv420p')
  if any(video.get(key) != 'bt709' for key in (
    'color_space', 'color_transfer', 'color_primaries'
  )):
    errors.append('video color metadata must be BT.709')
  actual_fps = Fraction(video['avg_frame_rate'])
  if actual_fps != fps:
    errors.append(f'video frame rate must be constant {fps} FPS')
  actual_bitrate = int(video.get('bit_rate', 0))
  if actual_bitrate < round(bitrate * 0.85):
    errors.append(
      f'video bitrate {actual_bitrate} is below the quality floor {bitrate}'
    )
  if audio.get('codec_name') != 'aac':
    errors.append('audio codec must be AAC')
  if int(audio.get('sample_rate', 0)) != 48_000:
    errors.append('audio sample rate must be 48 kHz')
  if int(audio.get('channels', 0)) != 2:
    errors.append('audio must be stereo')
  if 'mp4' not in payload['format'].get('format_name', ''):
    errors.append('container must be MP4')
  if not has_faststart(path):
    errors.append('MP4 moov atom must precede media data for fast start')
  if errors:
    raise RuntimeError('; '.join(errors))
  return {
    'width': video['width'],
    'height': video['height'],
    'fps': float(actual_fps),
    'videoBitrate': actual_bitrate,
    'videoCodec': video['codec_name'],
    'videoProfile': video['profile'],
    'pixelFormat': video['pix_fmt'],
    'color': 'bt709',
    'audioCodec': audio['codec_name'],
    'audioSampleRate': int(audio['sample_rate']),
    'fastStart': True
  }


def main():
  args = parse_args()
  source = args.input.resolve()
  output = args.output.resolve()
  if not source.is_file():
    raise RuntimeError(f'input not found: {source}')
  if output.exists():
    raise RuntimeError(f'refusing to overwrite: {output}')
  if output.suffix.lower() != '.mp4':
    raise RuntimeError('output must use an .mp4 extension')
  if args.fps not in {24, 25, 30, 48, 50, 60}:
    raise RuntimeError('fps must be one of 24, 25, 30, 48, 50, or 60')
  for tool in ('ffmpeg', 'ffprobe'):
    if shutil.which(tool) is None:
      raise RuntimeError(f'missing required tool: {tool}')

  source_payload = probe(source)
  source_video = stream(source_payload, 'video')
  width = int(source_video['width'])
  height = int(source_video['height'])
  bitrate_text, bitrate = default_bitrate(height, args.fps)
  if args.video_bitrate:
    bitrate_text = args.video_bitrate
    bitrate = parse_bitrate(bitrate_text)
  gop = max(1, round(args.fps / 2))
  temporary = output.with_name(f'.{output.stem}.encoding.mp4')
  temporary.unlink(missing_ok=True)

  command = [
    'ffmpeg', '-hide_banner', '-y', '-i', str(source),
    '-map', '0:v:0', '-map', '0:a:0?',
    '-vf', f'fps={args.fps},format=yuv420p',
    '-fps_mode', 'cfr', '-c:v', 'libx264', '-preset', 'fast',
    '-profile:v', 'high', '-b:v', bitrate_text,
    '-g', str(gop), '-keyint_min', str(gop), '-sc_threshold', '0',
    '-bf', '2',
    '-x264-params', (
      'force-cfr=1:colorprim=bt709:transfer=bt709:colormatrix=bt709'
    ),
    '-color_primaries', 'bt709', '-color_trc', 'bt709',
    '-colorspace', 'bt709',
    '-c:a', 'aac', '-b:a', '384k', '-ar', '48000', '-ac', '2',
    '-movflags', '+faststart', str(temporary)
  ]
  try:
    subprocess.run(command, check=True)
    report = validate_master(
      temporary, width, height, args.fps, bitrate
    )
    temporary.replace(output)
  finally:
    temporary.unlink(missing_ok=True)
  print(json.dumps({'output': str(output), **report}, indent=2))


if __name__ == '__main__':
  try:
    main()
  except (OSError, RuntimeError, ValueError, subprocess.CalledProcessError) as exc:
    print(f'error: {exc}', file=sys.stderr)
    raise SystemExit(1)
