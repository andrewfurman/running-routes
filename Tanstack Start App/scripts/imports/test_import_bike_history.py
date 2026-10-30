"""Cycling-only import, byte preservation and deduplication checks."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from import_bike_history import merge_manifest, summarize, write_outputs, rebuild_archive

GPX = b'''<gpx xmlns="http://www.topografix.com/GPX/1/1"><trk><trkseg><trkpt lat="40" lon="-75"><time>2026-10-29T12:00:00Z</time></trkpt><trkpt lat="40.001" lon="-75.001"><time>2026-10-29T12:01:00Z</time></trkpt></trkseg></trk></gpx>'''


class BikeImportTest(unittest.TestCase):
    def test_idempotent_merge_and_preserved_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / 'ride.gpx'; source.write_bytes(GPX)
            manifest = root / 'rides.json'; manifest.write_text(json.dumps([{'activity_id': '123', 'activity_type': 'Ride', 'date': 'Thu, 10/29/2026', 'file': 'ride.gpx'}]))
            collection = {'type': 'FeatureCollection', 'features': []}
            summary = {'cycling_records': 5, 'known_activity_ids': []}
            collection, summary, provenance = merge_manifest(collection, summary, manifest, root / 'output', '2026-10-30')
            self.assertEqual(summary['cycling_records'], 6)
            self.assertEqual((root / 'output/2026-10-30/123.gpx').read_bytes(), GPX)
            self.assertEqual(provenance[0]['sha256'], hashlib.sha256(GPX).hexdigest())
            collection, summary, provenance = merge_manifest(collection, summary, manifest, root / 'output', '2026-10-30')
            result = write_outputs(collection, summary, provenance, root / 'output', None, '2026-10-30')
            self.assertEqual(result['cycling_records'], 6)
            self.assertEqual(result['mapped_rides'], 1)
            self.assertEqual(result['records_without_drawable_gps'], 5)
            self.assertEqual(result['date_range'], ['2026-10-29', '2026-10-29'])
            self.assertNotIn(str(root), (root / 'output/2026-10-30/manifest.json').read_text())

    def test_reject_non_cycling_and_mismatched_date(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); (root / 'ride.gpx').write_bytes(GPX)
            manifest = root / 'rides.json'
            for kind, date in [('Run', '2026-10-29'), ('Ride', '2026-10-28')]:
                manifest.write_text(json.dumps([{'activity_id': '123', 'activity_type': kind, 'date': date, 'file': 'ride.gpx'}]))
                with self.assertRaises(ValueError):
                    merge_manifest({'features': []}, {'cycling_records': 0}, manifest, root / 'output', '2026-10-30')

    def test_official_archive_filters_other_sports(self):
        from zipfile import ZipFile
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); archive = root / 'export.zip'
            with ZipFile(archive, 'w') as zipped:
                zipped.writestr('activities.csv', 'Activity ID,Activity Type,Activity Date,Filename\n123,Ride,"Oct 29, 2026, 12:00:00 PM",activities/ride.gpx\n124,Run,"Oct 29, 2026, 12:00:00 PM",activities/run.gpx\n125,Ride,"Oct 29, 2026, 12:00:00 PM",\n')
                zipped.writestr('activities/ride.gpx', GPX)
                zipped.writestr('activities/run.gpx', GPX)
            collection, summary, provenance = rebuild_archive(archive, root / 'output', '2026-10-30')
            result = summarize(collection, summary)
            self.assertEqual(result['cycling_records'], 2)
            self.assertEqual(result['mapped_rides'], 1)
            self.assertEqual(result['records_without_drawable_gps'], 1)
            self.assertEqual(len(provenance), 1)
            self.assertFalse((root / 'output/2026-10-30/124.gpx').exists())

    def test_reject_duplicate_activity_ids_and_impossible_counts(self):
        feature = {'properties': {'activity_id': '123', 'activity_type': 'Ride', 'date': '2026-10-29'}}
        with self.assertRaises(ValueError):
            summarize({'features': [feature, feature]}, {'cycling_records': 2})
        with self.assertRaises(ValueError):
            summarize({'features': [feature]}, {'cycling_records': 0})

if __name__ == '__main__':
    unittest.main()
