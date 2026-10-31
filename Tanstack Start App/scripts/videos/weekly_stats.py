"""Recorded Strava statistics for an inclusive rolling seven-day Eastern window."""
from datetime import date,datetime,timedelta
from zoneinfo import ZoneInfo
import math
ZONE=ZoneInfo('America/New_York')
def weekly_stats(records,as_of):
 end=date.fromisoformat(as_of);start=end-timedelta(days=6);selected=[]
 for record in records:
  stamp=datetime.fromisoformat(record['date'].replace('Z','+00:00')).astimezone(ZONE)
  if start<=stamp.date()<=end:
   assert math.isfinite(record['distanceMeters']) and record['distanceMeters']>=0
   assert math.isfinite(record['movingSeconds']) and record['movingSeconds']>=0
   if record['distanceMeters']>0 and record['movingSeconds']==0:raise ValueError('Recorded moving time is missing; do not invent pace')
   selected.append((stamp,record))
 selected.sort(key=lambda pair:(pair[0],pair[1]['activityId']))
 if not selected:raise ValueError('No runs in the requested seven-day window')
 meters=sum(r['distanceMeters'] for _,r in selected);seconds=sum(r['movingSeconds'] for _,r in selected);clock=[t.hour*3600+t.minute*60+t.second for t,_ in selected];angle=math.atan2(sum(math.sin(t*math.tau/86400) for t in clock),sum(math.cos(t*math.tau/86400) for t in clock))%math.tau;average=angle*86400/math.tau;minute=int((average+30)//60)%1440;h,m=divmod(minute,60)
 return {'windowStart':start.isoformat(),'windowEnd':end.isoformat(),'timeZone':'America/New_York','runCount':len(selected),'dayCount':len({t.date() for t,_ in selected}),'totalMeters':meters,'totalMiles':meters/1609.344,'movingSeconds':seconds,'elapsedSeconds':sum(r['elapsedSeconds'] for _,r in selected),'averageDistanceMiles':meters/1609.344/len(selected),'averageStartSeconds':average,'averageStartLabel':f'{h%12 or 12}:{m:02d} {"AM" if h<12 else "PM"}','averagePaceSecondsPerMile':seconds/(meters/1609.344) if meters else None,'activityIds':[r['activityId'] for _,r in selected],'records':[r for _,r in selected]}
def duration(seconds):
 seconds=round(seconds);h,remainder=divmod(seconds,3600);m,s=divmod(remainder,60);return f'{h}:{m:02d}:{s:02d}' if h else f'{m}:{s:02d}'
def pace(seconds):return duration(seconds)+' /mi' if seconds is not None else '—'
