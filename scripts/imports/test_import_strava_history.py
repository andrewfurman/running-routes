"""Conversion and raw archive round-trip checks using synthetic activity files."""
import csv
import gzip
import hashlib
import io
import json
import re
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch
from zipfile import ZipFile

import fitdecode
import import_strava_history as importer


def fit_file():
    # FIT record definition: signed 32-bit semicircle latitude and longitude.
    data = bytes([0x40, 0, 0]) + struct.pack('<H', 20) + bytes([2, 0, 4, 0x85, 1, 4, 0x85])
    for lon, lat in [(-75, 40), (-75.001, 40.001)]:
        data += b'\x00' + struct.pack('<ii', round(lat * 2**31 / 180), round(lon * 2**31 / 180))
    header = struct.pack('<BBHI4s', 12, 0x10, 100, len(data), b'.FIT')
    body = header + data
    return body + struct.pack('<H', fitdecode.utils.compute_crc(body))


class HistoryImportTest(unittest.TestCase):
    def test_raw_roundtrip_and_all_formats(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = root / 'strava.zip'
            files = {'activities/a.gpx': b'<gpx xmlns="urn:gpx"><trk><trkseg><trkpt lon="-75" lat="40"/><trkpt lon="-75.01" lat="40.01"/></trkseg><trkseg><trkpt lon="-76" lat="41"/><trkpt lon="-76.01" lat="41.01"/></trkseg></trk></gpx>',
                     'activities/b.fit.gz': gzip.compress(fit_file()),
                     'activities/c.tcx': b'  \n<?xml version="1.0"?><TrainingCenterDatabase><Track><Trackpoint><Position><LatitudeDegrees>42</LatitudeDegrees><LongitudeDegrees>-77</LongitudeDegrees></Position></Trackpoint><Trackpoint><Position><LatitudeDegrees>42.01</LatitudeDegrees><LongitudeDegrees>-77.01</LongitudeDegrees></Position></Trackpoint></Track></TrainingCenterDatabase>',
                     'activities/indoor.gpx': b'<gpx/>', 'photos/example.jpg': b'raw-photo-bytes'}
            metadata = io.StringIO()
            writer = csv.DictWriter(metadata, fieldnames=['Activity ID', 'Filename', 'Activity Type', 'Activity Date'])
            writer.writeheader()
            for i, filename in enumerate(n for n in files if n.startswith('activities/')):
                writer.writerow({'Activity ID': i, 'Filename': filename, 'Activity Type': ['Run', 'Ride', 'Walk', 'Run'][i], 'Activity Date': 'Oct 15, 2026 </script>'})
            with ZipFile(archive, 'w') as zipped:
                zipped.writestr('activities.csv', metadata.getvalue())
                for name, data in files.items():
                    zipped.writestr(name, data)
            library = root / 'library'
            library.mkdir()
            preview = library / 'preview.html'
            preview.write_text('const targets=[1,2,3];\nconst recentTracks={};\n<div>Purple = old coverage</div>Recent GPS tracks')
            with patch.object(importer, 'LIBRARY', library):
                importer.import_archive(archive, '2026-10-15')
            output = library / '2026-10-15-strava-history'
            manifest = json.loads((output / 'manifest.json').read_text())
            restored = b''.join((output / 'raw' / p['file']).read_bytes() for p in manifest['parts'])
            self.assertEqual(restored, archive.read_bytes())
            self.assertEqual(hashlib.sha256(restored).hexdigest(), manifest['archive_sha256'])
            self.assertEqual(manifest['mapped_activities'], 3)
            self.assertEqual(manifest['activities_without_gps'], 1)
            tracks = json.loads(gzip.decompress((output / 'tracks.geojson.gz').read_bytes()))
            self.assertEqual(len(tracks['features'][0]['geometry']['coordinates']), 2)
            self.assertEqual(tracks['features'][1]['geometry']['coordinates'][0][0], [-75, 40])
            self.assertEqual(tracks['features'][2]['geometry']['coordinates'][0][0], [-77, 42])
            self.assertNotIn('</script>', preview.read_text())
            self.assertIn('const targets=[1,2,3]', preview.read_text())
            self.assertIn('1 GPS running tracks', preview.read_text())
            shown = json.loads(re.search(r'const recentTracks=(.*);\n', preview.read_text())[1])
            self.assertEqual([f['properties']['activity_id'] for f in shown['features']], ['0'])
            self.assertEqual({f['properties']['activity_type'] for f in tracks['features']}, {'Run', 'Ride', 'Walk'})
            self.assertEqual(manifest['running_map_activities'], 1)

    def test_unsupported_format_leaves_map_untouched(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp) / 'bad.zip'
            with ZipFile(archive, 'w') as zipped:
                zipped.writestr('activities.csv', 'Filename\nactivities/unknown.bin\n')
                zipped.writestr('activities/unknown.bin', b'not a track')
            with self.assertRaisesRegex(ValueError, 'Unsupported activity format'):
                importer.extract_tracks(archive)

    def test_invalid_coordinates_rejected(self):
        with self.assertRaises(ValueError):
            importer.clean_segments([[(float('nan'), 40), (-75, 40)]])

    def test_simplification_keeps_turns_and_segment_endpoints(self):
        points = [[-75, 40], [-75.0001, 40], [-75.001, 40], [-75.001, 40.001]]
        self.assertEqual(importer.simplify(points), [points[0], points[2], points[3]])


if __name__ == '__main__':
    unittest.main()
