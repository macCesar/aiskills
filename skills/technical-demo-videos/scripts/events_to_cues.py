#!/usr/bin/env python3
"""Convert timestamped recording events into a narration cue skeleton."""

import argparse
import json
from pathlib import Path


def load_events(path):
  payload = json.loads(path.read_text())
  events = payload.get('events') if isinstance(payload, dict) else payload
  if not isinstance(events, list) or not events:
    raise SystemExit('event log must contain a non-empty event array')
  return payload, events


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('events_json', type=Path)
  parser.add_argument('output_json', type=Path)
  args = parser.parse_args()

  payload, events = load_events(args.events_json)
  if args.output_json.exists():
    raise SystemExit(f'refusing to overwrite: {args.output_json}')

  previous = None
  for event in events:
    if not isinstance(event, dict) or 'name' not in event or 'timestamp_ms' not in event:
      raise SystemExit('each event must contain name and timestamp_ms')
    current = event['timestamp_ms']
    if not isinstance(current, (int, float)):
      raise SystemExit('timestamp_ms values must be numeric and ordered')
    if previous is not None and current < previous:
      raise SystemExit('timestamp_ms values must be numeric and ordered')
    previous = current

  starts = [event for event in events if event['name'] == 'recording_started']
  if len(starts) != 1:
    raise SystemExit('event log must contain exactly one recording_started event')
  stops = [event for event in events if event['name'] == 'recording_stopped']
  if len(stops) != 1:
    raise SystemExit('event log must contain exactly one recording_stopped event')

  start_index = events.index(starts[0])
  stop_index = events.index(stops[0])
  if stop_index <= start_index:
    raise SystemExit('recording_stopped must follow recording_started')

  captured_events = events[start_index:stop_index + 1]
  origin = starts[0]['timestamp_ms']
  normalized = []
  for event in captured_events:
    current = event['timestamp_ms']
    normalized.append({
      'event': event['name'],
      'at': round((current - origin) / 1000, 3),
      **({'path': event['path']} if 'path' in event else {})
    })

  stop = normalized[-1]['at']
  visual = [
    event for event in normalized
    if event['event'] not in {'recording_started', 'recording_stopped'}
  ]
  cues = []
  for index, event in enumerate(visual):
    end = visual[index + 1]['at'] if index + 1 < len(visual) else stop
    cues.append({
      'id': index + 1,
      'event': event['event'],
      'start': event['at'],
      'end': end,
      'text': ''
    })

  result = {
    'source_events': str(args.events_json),
    'duration': stop,
    'events': normalized,
    'cues': cues
  }
  if isinstance(payload, dict) and payload.get('demo'):
    result['demo'] = payload['demo']
  args.output_json.write_text(json.dumps(result, indent=2) + '\n')


if __name__ == '__main__':
  main()
