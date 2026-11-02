import unittest
from import_citi_bike import normalize,reconcile,legacy_trips
from pathlib import Path
class CitiBikeImportTest(unittest.TestCase):
 def row(self,start='2025-08-30 12:00:00 UTC',end='2025-08-30 12:10:00 UTC'):
  return {'unlocked_at':start,'dropped_off_at':end,'start_lat':'40.75','start_lng':'-73.98','destination_lat':'40.76','destination_lng':'-73.97'}
 def test_stable_ids_dedupe_and_incomplete_rentals(self):
  rows,excluded=normalize([self.row(),self.row(),self.row(end='')]);self.assertEqual(len(rows),1);self.assertEqual(excluded,1);self.assertIsNone(rows[0]['distanceMeters']);self.assertEqual(rows,normalize([self.row()])[0])
 def test_single_strava_recording_can_cover_two_rentals(self):
  trips,_=normalize([self.row(),self.row('2025-08-30 12:12:00 UTC','2025-08-30 12:20:00 UTC')])
  rides=[{'Activity ID':'1','Activity Type':'Ride','Activity Date':'Aug 30, 2025, 12:00:00 PM','Elapsed Time':'1200'}]
  tracks={'features':[{'properties':{'activity_id':'1'},'geometry':{'type':'LineString','coordinates':[[-73.98,40.75],[-73.97,40.76]]}}]}
  rows=reconcile(trips,rides,tracks);self.assertTrue(all(t['matchStatus']=='matched' for t in rows));self.assertTrue(all(t['stravaActivityIds']==['1'] for t in rows))
 def test_same_time_without_geometry_requires_review(self):
  trips,_=normalize([self.row()]);rides=[{'Activity ID':'1','Activity Type':'Ride','Activity Date':'Aug 30, 2025, 12:00:00 PM','Elapsed Time':'600'}]
  self.assertEqual(reconcile(trips,rides,{'features':[]})[0]['matchStatus'],'review')
 def test_same_stations_at_other_time_are_new(self):
  trips,_=normalize([self.row()]);rides=[{'Activity ID':'1','Activity Type':'Ride','Activity Date':'Aug 30, 2025, 3:00:00 PM','Elapsed Time':'600'}]
  self.assertEqual(reconcile(trips,rides,{'features':[]})[0]['matchStatus'],'new')
 def test_legacy_snapshot_recovers_completed_rides_with_eastern_timezone(self):
  rows,summary=legacy_trips(Path(__file__).resolve().parents[3]/'raw-data/citi-bike/legacy');self.assertEqual(summary['sourceRecords'],207);self.assertEqual(summary['incomplete'],5);self.assertEqual(len(rows),202);self.assertTrue(any(r['start']=='2015-05-02T16:30:59Z' for r in rows));self.assertEqual(sum(r['endCoordinates'] is None for r in rows),1)
if __name__=='__main__':unittest.main()
