#!/usr/bin/env python3
"""Rebuild cycling data from an official Strava ZIP or merge downloaded GPX rides.

No browser token or Strava API is used. --manifest JSON is a list of
{activity_id, activity_type, file}; relative paths resolve beside the manifest.
Raw cycling files are preserved byte-for-byte with SHA-256 provenance.
"""
import argparse
from collections import Counter
import csv
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET
from zipfile import ZipFile
from zoneinfo import ZoneInfo

from import_strava_history import clean_segments, extract_tracks, xml_segments

ROOT = Path(__file__).resolve().parents[3]
CYCLING_TYPES = {'Ride', 'Virtual Ride', 'VirtualRide', 'Mountain Bike Ride', 'MountainBikeRide', 'Gravel Ride', 'GravelRide', 'E-Bike Ride', 'EBikeRide', 'E-Mountain Bike Ride', 'EMountainBikeRide', 'Handcycle', 'Velomobile'}
ZONE = ZoneInfo('America/New_York')


def read_embedded(path, name):
    match = re.search(r'const ' + re.escape(name) + r'=(.*);\n', path.read_text())
    if not match:
        raise ValueError('Missing embedded ' + name)
    return json.loads(match.group(1))


def normalize_date(value):
    if re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
        return value
    for fmt in ('%a, %m/%d/%Y', '%b %d, %Y, %I:%M:%S %p'):
        try:
            parsed = datetime.strptime(value, fmt)
            if fmt.startswith('%b'):
                parsed = parsed.replace(tzinfo=timezone.utc).astimezone(ZONE)
            return parsed.date().isoformat()
        except ValueError:
            continue
    raise ValueError('Unsupported activity date')


def validate_id(value):
    value = str(value)
    if not value.isdigit():
        raise ValueError('Activity IDs must be numeric')
    return value


def load_base(output, map_path):
    if (output / 'tracks.geojson').exists():
        return json.loads((output / 'tracks.geojson').read_text()), json.loads((output / 'summary.json').read_text())
    collection = read_embedded(map_path, 'bikes')
    stats = read_embedded(map_path, 'stats')
    return collection, {'cycling_records': stats['cycling_records'], 'known_activity_ids': [str(f['properties']['activity_id']) for f in collection['features']], 'source': 'Existing Strava cycling snapshot', 'as_of': stats['checked_date']}


def save_raw(output, date, aid, source, data):
    suffixes = ''.join(Path(source).suffixes)
    filename = aid + suffixes
    dest = output / date / filename
    if dest.exists() and dest.read_bytes() != data:
        raise ValueError('Raw export already exists with different bytes: ' + filename)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    return {'activity_id': aid, 'file': dest.relative_to(output).as_posix(), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(), 'source_url': 'https://www.strava.com/activities/' + aid}


def merge_manifest(collection, summary, manifest_path, output, checked_date):
    entries = json.loads(manifest_path.read_text())
    if not isinstance(entries, list):
        raise ValueError('Manifest must be a list')
    features = {validate_id(f['properties']['activity_id']): f for f in collection['features']}
    known = set(summary.get('known_activity_ids', features))
    total = summary['cycling_records']
    provenance = []
    for entry in entries:
        kind = entry.get('activity_type')
        if kind not in CYCLING_TYPES:
            raise ValueError('Manifest entry is not a cycling activity')
        aid = validate_id(entry['activity_id'])
        source = Path(entry['file']).expanduser()
        if not source.is_absolute():
            source = manifest_path.parent / source
        raw = source.read_bytes()
        if source.suffix.lower() != '.gpx':
            raise ValueError('Incremental files must be GPX exports')
        parsed = ET.fromstring(raw.lstrip())
        first_time = parsed.find('.//{*}trkpt/{*}time')
        if first_time is None:
            first_time = parsed.find('.//{*}time')
        if first_time is not None and first_time.text:
            stamp = datetime.fromisoformat(first_time.text.replace('Z', '+00:00'))
            date = stamp.astimezone(ZONE).date().isoformat()
        elif entry.get('date'):
            date = normalize_date(entry['date'])
        else:
            raise ValueError('A GPX time or manifest date is required')
        if entry.get('date') and date != normalize_date(entry['date']):
            raise ValueError('GPX date disagrees with the verified activity date')
        provenance.append(save_raw(output, checked_date, aid, source, raw))
        segments = clean_segments(xml_segments(raw, '.gpx'))
        if aid not in known:
            total += 1
            known.add(aid)
        if segments:
            features[aid] = {'type': 'Feature', 'properties': {'date': date, 'year': date[:4], 'activity_id': aid, 'activity_type': kind, 'source': 'Official Strava GPX export', 'strava_url': 'https://www.strava.com/activities/' + aid}, 'geometry': {'type': 'MultiLineString', 'coordinates': segments}}
        elif aid in features:
            raise ValueError('A no-GPS export would overwrite an existing drawable ride')
    return {'type': 'FeatureCollection', 'features': list(features.values())}, {'cycling_records': total, 'known_activity_ids': sorted(known), 'as_of': checked_date, 'source': 'Existing Strava history plus verified GPX exports'}, provenance


def rebuild_archive(path, output, checked_date):
    collection, _, _, _ = extract_tracks(path)
    with ZipFile(path) as zipped:
        rows = list(csv.DictReader(io.StringIO(zipped.read('activities.csv').decode('utf-8-sig'))))
        rows = [r for r in rows if r.get('Activity Type') in CYCLING_TYPES]
        known = {validate_id(r['Activity ID']) for r in rows}
        provenance = []
        for row in rows:
            filename = row.get('Filename')
            if filename and filename in zipped.namelist():
                provenance.append(save_raw(output, checked_date, row['Activity ID'], filename, zipped.read(filename)))
    features = []
    for f in collection['features']:
        if f['properties'].get('activity_type') not in CYCLING_TYPES:
            continue
        date = normalize_date(f['properties']['date'])
        f['properties'].update(date=date, year=date[:4])
        features.append(f)
    return {'type': 'FeatureCollection', 'features': features}, {'cycling_records': len(rows), 'known_activity_ids': sorted(known), 'as_of': checked_date, 'source': 'Official Strava account ZIP', 'archive_sha256': hashlib.sha256(path.read_bytes()).hexdigest()}, provenance


def summarize(collection, summary):
    features = collection['features']
    ids = [validate_id(f['properties']['activity_id']) for f in features]
    if len(set(ids)) != len(ids):
        raise ValueError('Duplicate ride IDs')
    if any(f['properties'].get('activity_type') not in CYCLING_TYPES for f in features):
        raise ValueError('Non-cycling activity in cycling map')
    features.sort(key=lambda f: (f['properties']['date'], f['properties']['activity_id']), reverse=True)
    dates = sorted(f['properties']['date'] for f in features)
    if summary['cycling_records'] < len(features):
        raise ValueError('Mapped count exceeds cycling record count')
    summary.update(mapped_rides=len(features), records_without_drawable_gps=summary['cycling_records'] - len(features), date_range=[dates[0], dates[-1]] if dates else [], years=dict(sorted(Counter(f['properties']['date'][:4] for f in features).items())), included_activity_types=sorted({f['properties']['activity_type'] for f in features}))
    return summary


def write_outputs(collection, summary, provenance, output, map_path, checked_date):
    output.mkdir(parents=True, exist_ok=True)
    summary = summarize(collection, summary)
    (output / 'tracks.geojson').write_text(json.dumps(collection, separators=(',', ':')) + '\n')
    (output / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    if provenance:
        p = output / checked_date / 'manifest.json'
        existing = json.loads(p.read_text()) if p.exists() else []
        by_id = {x['activity_id']: x for x in existing}
        by_id.update({x['activity_id']: x for x in provenance})
        p.write_text(json.dumps(list(by_id.values()), indent=2) + '\n')
    if map_path:
        stats = {k: v for k, v in summary.items() if k in {'mapped_rides', 'cycling_records', 'records_without_drawable_gps', 'years', 'date_range', 'included_activity_types'}}
        stats['checked_date'] = checked_date
        html = map_path.read_text()
        html = re.sub(r'const bikes=.*;\n', lambda _: 'const bikes=' + json.dumps(collection, separators=(',', ':')).replace('<', '\\u003c') + ';\n', html, count=1)
        html = re.sub(r'const stats=.*;\n', lambda _: 'const stats=' + json.dumps(stats, separators=(',', ':')) + ';\n', html, count=1)
        map_path.write_text(html)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path)
    parser.add_argument('--archive', type=Path)
    parser.add_argument('--date', required=True, help='Date this import was checked, YYYY-MM-DD')
    parser.add_argument('--output', type=Path, default=ROOT / 'raw-data/bikes')
    parser.add_argument('--map', type=Path, default=ROOT / 'Tanstack Start App/legacy/visualization/bikes.html')
    args = parser.parse_args()
    datetime.strptime(args.date, '%Y-%m-%d')
    if not args.manifest and not args.archive:
        parser.error('Provide --manifest and/or --archive')
    if args.archive:
        collection, summary, provenance = rebuild_archive(args.archive, args.output, args.date)
    else:
        collection, summary = load_base(args.output, args.map)
        provenance = []
    if args.manifest:
        collection, summary, more = merge_manifest(collection, summary, args.manifest, args.output, args.date)
        provenance += more
    summary = write_outputs(collection, summary, provenance, args.output, args.map, args.date)
    print(json.dumps({k: summary[k] for k in ('cycling_records', 'mapped_rides', 'records_without_drawable_gps', 'date_range')}, indent=2))

if __name__ == '__main__':
    main()
