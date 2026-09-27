#!/usr/bin/env python3
"""Render explicit-pixel SVG canvases and verify RGB PNG deliverables."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import tempfile
import xml.etree.ElementTree as ET


def run(*args):
    return subprocess.run(args, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def require(*names):
    missing = [name for name in names if not shutil.which(name)]
    if missing:
        raise ValueError('Missing executable(s): ' + ', '.join(missing))


def size(value):
    match = re.fullmatch(r'([1-9]\d*)x([1-9]\d*)', value)
    if not match:
        raise argparse.ArgumentTypeError('Size must be positive WIDTHxHEIGHT pixels')
    return tuple(map(int, match.groups()))


def canvas(source):
    root = ET.parse(source).getroot()
    if root.tag != '{http://www.w3.org/2000/svg}svg':
        raise ValueError('Expected SVG root with SVG namespace')
    dims = []
    for key in ('width', 'height'):
        match = re.fullmatch(r'([1-9]\d*)(?:px)?', root.get(key, ''))
        if not match:
            raise ValueError(f'SVG {key} must be explicit positive integer pixels')
        dims.append(int(match.group(1)))
    view = [float(x) for x in re.split(r'[\s,]+', root.get('viewBox', '').strip()) if x]
    if view != [0, 0, *dims]:
        raise ValueError('SVG viewBox must match 0 0 width height')
    return tuple(dims)


def inspect_png(path, expected=None):
    data = path.read_bytes()
    if len(data) < 33 or data[:8] != b'\x89PNG\r\n\x1a\n' or data[12:16] != b'IHDR':
        raise ValueError(f'{path}: not a PNG')
    width, height, depth, color = struct.unpack('>IIBB', data[16:26])
    if depth != 8 or color != 2:
        raise ValueError(f'{path}: expected 8-bit RGB PNG without alpha (color type 2)')
    offset = 8
    while offset + 12 <= len(data):
        length = struct.unpack('>I', data[offset:offset + 4])[0]
        kind = data[offset + 4:offset + 8]
        if kind in (b'tRNS', b'acTL'):
            raise ValueError(f'{path}: transparency or animation is not a final RGB screenshot')
        offset += length + 12
    if expected and (width, height) != expected:
        raise ValueError(f'{path}: got {width}x{height}, expected {expected[0]}x{expected[1]}')
    # Header checks alone would accept truncated/corrupt image payloads.
    run('magick', '-regard-warnings', str(path.resolve()), 'null:')
    return {'path': str(path), 'width': width, 'height': height,
            'mode': 'RGB', 'sha256': hashlib.sha256(data).hexdigest()}


def export(args):
    source, output = args.source.resolve(), args.output.resolve()
    if output.suffix.lower() != '.png':
        raise ValueError('Output must use .png extension')
    if source == output:
        raise ValueError('Source and output must differ')
    if output.exists() and not args.force:
        raise ValueError(f'Output exists: {output}; use --force to replace')
    dimensions = canvas(source)
    require('rsvg-convert', 'magick')
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.artwork-', dir=output.parent) as temp:
        rendered = Path(temp) / 'render.png'
        final = Path(temp) / 'final.png'
        run('rsvg-convert', '--output', str(rendered), str(source))
        run('magick', str(rendered), '-background', args.background,
            '-alpha', 'remove', '-alpha', 'off', '-colorspace', 'sRGB',
            '-depth', '8', '-define', 'png:color-type=2', str(final))
        result = inspect_png(final, dimensions)
        if args.force:
            final.replace(output)
        else:
            # Atomic no-clobber promotion, even if another process wrote meanwhile.
            os.link(final, output)
        result['path'] = str(output)
        result['source_sha256'] = hashlib.sha256(source.read_bytes()).hexdigest()
        return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    render = commands.add_parser('export', help='Render SVG to validated RGB PNG')
    render.add_argument('source', type=Path)
    render.add_argument('output', type=Path)
    render.add_argument('--background', default='white')
    render.add_argument('--force', action='store_true')
    check = commands.add_parser('check', help='Decode and check final PNGs without modifying them')
    check.add_argument('--size', type=size)
    check.add_argument('files', nargs='+', type=Path)
    args = parser.parse_args()
    try:
        if args.command == 'export':
            result = export(args)
        else:
            require('magick')
            result = [inspect_png(path, args.size) for path in args.files]
        print(json.dumps(result, indent=2))
    except (OSError, ValueError, ET.ParseError, subprocess.CalledProcessError) as error:
        detail = error.stderr.decode(errors='replace') if isinstance(error, subprocess.CalledProcessError) else str(error)
        parser.exit(1, f'Error: {detail.strip()}\n')


if __name__ == '__main__':
    main()
