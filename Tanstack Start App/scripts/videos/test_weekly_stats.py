import unittest
from weekly_stats import weekly_stats
class WeeklyStatsTests(unittest.TestCase):
 def record(self,id,date,miles,seconds):return {'activityId':id,'date':date,'distanceMeters':miles*1609.344,'movingSeconds':seconds,'elapsedSeconds':seconds+60}
 def test_inclusive_eastern_week_and_weighted_pace(self):
  rows=[self.record('old','2026-10-25T03:59:00Z',1,500),self.record('a','2026-10-25T04:00:00Z',1,600),self.record('b','2026-10-31T09:00:00Z',3,2400),self.record('future','2026-11-01T04:00:00Z',5,3000)]
  stats=weekly_stats(rows,'2026-10-31');self.assertEqual(stats['activityIds'],['a','b']);self.assertEqual(stats['totalMiles'],4);self.assertEqual(stats['movingSeconds'],3000);self.assertEqual(stats['averagePaceSecondsPerMile'],750)
 def test_average_start_is_circular_across_midnight(self):
  rows=[self.record('a','2026-10-27T03:50:00Z',1,600),self.record('b','2026-10-27T04:10:00Z',1,600)];self.assertEqual(weekly_stats(rows,'2026-10-31')['averageStartLabel'],'12:00 AM')
 def test_average_start_uses_local_clock_across_dst(self):
  rows=[self.record('a','2026-10-31T09:00:00Z',1,600),self.record('b','2026-11-01T10:00:00Z',1,600)];self.assertEqual(weekly_stats(rows,'2026-11-01')['averageStartLabel'],'5:00 AM')
 def test_missing_time_cannot_produce_false_pace(self):
  with self.assertRaises(ValueError):weekly_stats([self.record('a','2026-10-31T09:00:00Z',3,0)],'2026-10-31')
if __name__=='__main__':unittest.main()
