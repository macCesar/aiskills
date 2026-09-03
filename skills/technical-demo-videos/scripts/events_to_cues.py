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
  for event in events:
    if not isinstance(event, dict) or 'name' not in event or 'timestamp_ms' not in event:
      raise SystemExit('each event must contain name and timestamp_ms')

  starts = [event for event in events if event['name'] == 'recording_started']
  if len(starts) != 1:
    raise SystemExit('event log must contain exactly one recording_started event')

  origin = starts[0]['timestamp_ms']
  normalized = []
  previous = -1
  for event in events:
    current = event['timestamp_ms']
    if not isinstance(current, (int, float)) or current < previous:
      raise SystemExit('timestamp_ms values must be numeric and ordered')
    previous = current
    normalized.append({
      'event': event['name'],
      'at': round((current - origin) / 1000, 3),
      **({'path': event['path']} if 'path' in event else {})
    })

  stop = next(
    (event['at'] for event in reversed(normalized)
     if event['event'] == 'recording_stopped'),
    normalized[-1]['at']
  )
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
