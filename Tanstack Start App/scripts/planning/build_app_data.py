#!/usr/bin/env python3
"""Prepare cacheable map data separately from the TanStack Start application."""
from datetime import date, datetime, timedelta, timezone
import json
from pathlib import Path
import shutil
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[3]
PUBLIC=ROOT/'Tanstack Start App/public/data'
PUBLIC.mkdir(parents=True,exist_ok=True)

def read(path):return json.loads((ROOT/path).read_text())
def write(name,value):(PUBLIC/name).write_text(json.dumps(value,separators=(',',':'))+'\n')
def day_of(value):
    try:return date.fromisoformat(value[:10]).isoformat()
    except ValueError:
        return datetime.strptime(value,'%b %d, %Y, %I:%M:%S %p').replace(tzinfo=timezone.utc).astimezone(ZoneInfo('America/New_York')).date().isoformat()
runs=read('raw-data/runs/tracks.geojson')
assert all(f['properties'].get('activity_type') in {'Run','TrailRun','Trail Run','VirtualRun','Virtual Run'} for f in runs['features'])
def with_recorded_distances(tracks,metadata):
    distances={r['activityId']:r for r in metadata}
    for feature in tracks['features']:
        row=distances.get(str(feature['properties']['activity_id']))
        if row:feature['properties'].update(distance_meters=row['distanceMeters'],distance_source=row['distanceSource'])
    return tracks
write('runs.geojson',with_recorded_distances(runs,read('raw-data/runs/activities.json')['runs']))
bikepath=ROOT/'raw-data/bikes/tracks.geojson'
if bikepath.exists():write('bikes.geojson',with_recorded_distances(read('raw-data/bikes/tracks.geojson'),read('raw-data/bikes/recorded-distances.json')['records']))
else:
    import re
    bike=json.loads(re.search(r'const bikes=(.*);\n',(ROOT/'Tanstack Start App/legacy/visualization/bikes.html').read_text())[1]);write('bikes.geojson',bike)
shutil.copyfile(ROOT/'raw-data/boundaries/19083.geojson',PUBLIC/'boundary19083.geojson')
targets=read('raw-data/plans/current-targets.json');write('targets.json',targets)
events=[]
for f in runs['features']:
    p=f['properties'];day=day_of(p['date']);aid=str(p['activity_id']);events.append({'id':'strava-'+aid,'title':'Recorded run','start':day,'end':(date.fromisoformat(day)+timedelta(days=1)).isoformat(),'allDay':True,'type':'past','activityId':aid,'street':'','url':'https://www.strava.com/activities/'+aid})
for i,t in enumerate(targets):
    a=t.get('start_time','04:00' if t['date']=='2026-11-01' else '05:30');b=t.get('end_time','04:45' if t['date']=='2026-11-01' else '06:15');z=ZoneInfo('America/New_York');events.append({'id':'plan-'+t['date']+'-'+t['street'],'title':t['street'],'street':t['street'],'start':datetime.fromisoformat(t['date']+'T'+a).replace(tzinfo=z).isoformat(),'end':datetime.fromisoformat(t['date']+'T'+b).replace(tzinfo=z).isoformat(),'type':'planned','targetIndex':i,'address':t['navigation_address'],'outingId':t.get('outing_id')})
write('calendar.json',events)
bikes=json.loads((PUBLIC/'bikes.geojson').read_text());bike_summary=read('raw-data/bikes/summary.json') if (ROOT/'raw-data/bikes/summary.json').exists() else {'gps_ride_count':len(bikes['features']),'total_ride_count':1428,'without_gps_count':898,'as_of':'2026-10-17'}
bike_summary=dict(bike_summary,gps_ride_count=len(bikes['features']),total_ride_count=bike_summary.get('cycling_records',1428),without_gps_count=bike_summary.get('records_without_drawable_gps',898))
write('summary.json',{'runCount':len(runs['features']),'bikeCount':len(bikes['features']),'gpsRuns':len(runs['features']),'gpsRides':len(bikes['features']),'plannedTargets':len(targets),'plannedOutings':len({t['date'] for t in targets}),'asOf':'2026-10-30','bikes':bike_summary});write('bikes-summary.json',bike_summary)
print(f'Prepared {len(runs["features"])} runs, {len(bikes["features"])} rides and {len(events)} calendar events')
