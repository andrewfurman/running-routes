#!/usr/bin/env python3
"""Preserve a Strava bulk ZIP unchanged and embed its GPS tracks in the map.

Install FIT support: python3 -m pip install fitdecode
Run: python3 tools/import_strava_history.py /path/to/export.zip --date YYYY-MM-DD
Raw archives are split into 8 MiB parts to stay below GitHub's file limit.
Concatenating the parts in manifest order restores the exact original ZIP.
No credentials or download URLs are recorded. Run only in the private repo.
"""
import argparse
import csv
import gzip
import hashlib
import io
import json
import math
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
LIBRARY = ROOT / 'content research/future-running-routes'


def simplify(points, tolerance=2.0):
    """Keep line shape within 2 metres using iterative Douglas-Peucker."""
    if len(points) <= 2:
        return points
    scale_x = 111320 * math.cos(math.radians(points[0][1]))
    xy = [(p[0] * scale_x, p[1] * 111320) for p in points]
    keep, pending = {0, len(points) - 1}, [(0, len(points) - 1)]
    while pending:
        first, last = pending.pop()
        ax, ay = xy[first]
        bx, by = xy[last]
        dx, dy = bx - ax, by - ay
        length2 = dx * dx + dy * dy
        farthest, maximum = None, tolerance * tolerance
        for i in range(first + 1, last):
            px, py = xy[i]
            t = max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / length2)) if length2 else 0
            distance2 = (px - ax - t * dx)**2 + (py - ay - t * dy)**2
            if distance2 > maximum:
                farthest, maximum = i, distance2
        if farthest is not None:
            keep.add(farthest)
            pending.extend(((first, farthest), (farthest, last)))
    return [points[i] for i in sorted(keep)]


def clean_segments(segments):
    result = []
    for segment in segments:
        points = []
        for lon, lat in segment:
            if not (math.isfinite(lon) and math.isfinite(lat) and -180 <= lon <= 180 and -90 <= lat <= 90):
                raise ValueError('Invalid GPS coordinate')
            point = [round(lon, 5), round(lat, 5)]
            if not points or point != points[-1]:
                points.append(point)
        if len(points) >= 2:
            result.append(simplify(points))
    return result


def xml_segments(data, kind):
    # Some original exports indent their XML declaration. Normalize only the
    # parser input; preserve the downloaded activity bytes in the raw archive.
    root = ET.fromstring(data.lstrip())
    if kind == '.gpx':
        groups = root.findall('.//{*}trkseg') or root.findall('.//{*}rte')
        return [[(float(p.attrib['lon']), float(p.attrib['lat'])) for p in group
                 if p.tag.rsplit('}', 1)[-1] in ('trkpt', 'rtept')] for group in groups]
    segments = []
    for track in root.findall('.//{*}Track'):
        points = []
        for position in track.findall('.//{*}Position'):
            lat = position.find('{*}LatitudeDegrees')
            lon = position.find('{*}LongitudeDegrees')
            if lat is not None and lon is not None:
                points.append((float(lon.text), float(lat.text)))
        segments.append(points)
    return segments


def fit_segments(data):
    import fitdecode
    segments, points = [], []
    with fitdecode.FitReader(io.BytesIO(data)) as reader:
        for frame in reader:
            if not isinstance(frame, fitdecode.FitDataMessage):
                continue
            if frame.name == 'event' and frame.get_value('event', fallback=None) == 'timer':
                if points:
                    segments.append(points)
                    points = []
            if frame.name == 'record':
                lon = frame.get_value('position_long', fallback=None)
                lat = frame.get_value('position_lat', fallback=None)
                if lon is not None and lat is not None:
                    points.append((lon * 180 / 2**31, lat * 180 / 2**31))
    if points:
        segments.append(points)
    return segments


def extract_tracks(archive):
    features, inventory, rows = [], [], {}
    with ZipFile(archive) as zipped:
        csv_files = [n for n in zipped.namelist() if n == 'activities.csv']
        if len(csv_files) != 1:
            raise ValueError('Expected a Strava bulk archive with activities.csv')
        csv_rows = list(csv.DictReader(io.StringIO(zipped.read(csv_files[0]).decode('utf-8-sig'))))
        for row in csv_rows:
            if row.get('Filename'):
                rows[row['Filename']] = row
        activity_count = 0
        for info in zipped.infolist():
            name = info.filename
            if not name.startswith('activities/') or info.is_dir():
                continue
            activity_count += 1
            if activity_count % 250 == 0:
                print(f'Processing activity file {activity_count}', file=sys.stderr, flush=True)
            raw = zipped.read(info)
            item = {'file': name, 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}
            kind = Path(name.removesuffix('.gz')).suffix.lower()
            if kind not in ('.gpx', '.tcx', '.fit'):
                item['status'] = 'unsupported_format'
                inventory.append(item)
                continue
            data = gzip.decompress(raw) if name.endswith('.gz') else raw
            segments = clean_segments(fit_segments(data) if kind == '.fit' else xml_segments(data, kind))
            row = rows.get(name, {})
            item['segments'] = len(segments)
            item['points'] = sum(map(len, segments))
            item['status'] = 'mapped' if segments else 'no_gps_track'
            inventory.append(item)
            if segments:
                features.append({'type': 'Feature', 'properties': {
                    'date': row.get('Activity Date', ''), 'activity_id': row.get('Activity ID', ''),
                    'activity_type': row.get('Activity Type', ''), 'source_file': name,
                    'source': 'Strava bulk account export'}, 'geometry': {
                    'type': 'MultiLineString', 'coordinates': segments}})
    if any(i['status'] == 'unsupported_format' for i in inventory):
        raise ValueError('Unsupported activity format; import stopped rather than silently omitting tracks')
    if not features:
        raise ValueError('Archive has no GPS tracks; map was not changed')
    return {'type': 'FeatureCollection', 'features': features}, inventory, activity_count, {
        'activity_records': len(csv_rows),
        'records_without_original_file': sum(not row.get('Filename') for row in csv_rows)}


def import_archive(archive, date):
    destination = LIBRARY / f'{date}-strava-history'
    if destination.exists():
        raise ValueError(f'{destination} already exists; choose a new dated export directory')
    collection, inventory, activity_count, csv_summary = extract_tracks(archive)
    preview = LIBRARY / 'preview.html'
    if not preview.exists():  # big route pages live in R2, not git
        from media_store import ensure_paths
        ensure_paths(preview)
    html = preview.read_text()
    if len(re.findall(r'const recentTracks=.*?;\n', html)) != 1:
        raise ValueError('Expected exactly one inline track collection in preview.html')
    # Escape < so activity metadata cannot terminate the inline script.
    encoded = json.dumps(collection, separators=(',', ':'), ensure_ascii=True).replace('<', '\\u003c')
    from running_route_updates import running_collection
    runs = running_collection(collection)
    encoded_runs = json.dumps(runs, separators=(',', ':'), ensure_ascii=True).replace('<', '\\u003c')
    html = re.sub(r'const recentTracks=.*?;\n', lambda _: f'const recentTracks={encoded_runs};\n', html)
    count = len(collection['features'])
    coverage = (f'Purple = {len(runs["features"]):,} GPS running tracks from the Strava archive imported {date}. '
                'Bike rides, walks and other sports are excluded from this running map. '
                'Activities without GPS have no line. This is recorded GPS coverage, '
                '<strong>not CityStrides street or node completion credit</strong>.')
    html, replacements = re.subn(r'Purple = .*?</div>', lambda _: coverage + '</div>', html, count=1)
    if replacements != 1:
        raise ValueError('Missing map coverage label')
    html = html.replace('Recent GPS tracks', 'Running GPS tracks only').replace('All exported GPS tracks', 'Running GPS tracks only')
    html = html.replace("f.properties.date+' · recorded run'", "f.properties.date+' · '+(f.properties.activity_type||'recorded activity')")
    destination.mkdir(parents=True)
    raw_dir = destination / 'raw'
    raw_dir.mkdir()
    parts, digest = [], hashlib.sha256()
    with archive.open('rb') as source:
        while chunk := source.read(8 * 1024 * 1024):
            digest.update(chunk)
            filename = f'archive.zip.part{len(parts):04d}'
            (raw_dir / filename).write_bytes(chunk)
            parts.append({'file': filename, 'bytes': len(chunk), 'sha256': hashlib.sha256(chunk).hexdigest()})
    manifest = {'source': 'Strava bulk account export', 'export_date': date,
                'archive_sha256': digest.hexdigest(), 'archive_bytes': archive.stat().st_size,
                'parts': parts, 'activity_files': activity_count, 'mapped_activities': count,
                'running_map_activities': len(runs['features']),
                'activities_without_gps': sum(i['status'] == 'no_gps_track' for i in inventory),
                'display_coordinate_precision': 5, 'raw_data_modified': False,
                'display_simplification_metres': 2,
                'inventory': inventory}
    manifest.update(csv_summary)
    (destination / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    # Keep all sports in the machine-readable archive; mirror large files to R2.
    (destination / 'tracks.geojson.gz').write_bytes(gzip.compress((encoded + '\n').encode(), mtime=0))
    (destination / 'README.md').write_text(
        f'# Strava history export · {date}\n\n'
        f'{csv_summary["activity_records"]:,} activity records, including '
        f'{csv_summary["records_without_original_file"]:,} without original activity files. '
        f'{activity_count:,} original activity files; {count:,} have drawable GPS tracks. '
        f'{manifest["activities_without_gps"]:,} have no drawable GPS track. All activity types are included.\n\n'
        'The raw directory preserves the entire downloaded account ZIP, including its CSV, photos, '
        'and other account data, as ordered binary parts. Concatenate the parts in manifest order '
        'to restore the exact ZIP and verify its SHA-256 against manifest.json. '
        'This is private personal data and belongs only in this private repository.\n\n'
        'tracks.geojson.gz and ../preview.html contain display geometry rounded to five decimal '
        'places, consecutive duplicate points removed, and simplified within 2 metres for browser performance. GPX and TCX track boundaries and FIT '
        'timer boundaries remain separate. Original files remain unchanged inside the archive. '
        'GPS coverage does not establish CityStrides completion credit.\n')
    preview.write_text(html)
    print(json.dumps({k: v for k, v in manifest.items() if k not in ('parts', 'inventory')}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    parser.add_argument('--date', required=True)
    args = parser.parse_args()
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', args.date):
        parser.error('--date must be YYYY-MM-DD')
    import_archive(args.archive, args.date)
