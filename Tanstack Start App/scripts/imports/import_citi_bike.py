#!/usr/bin/env python3
"""Extract NYC bike trips only; keep the full Lyft privacy archive outside Git."""
import argparse,csv,hashlib,io,json,math,zipfile
from datetime import datetime,timezone
from pathlib import Path
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[3]
def stamp(value):
 if not value:return None
 for fmt in ('%Y-%m-%d %H:%M:%S UTC','%b %d, %Y, %I:%M:%S %p'):
  try:return datetime.strptime(value,fmt).replace(tzinfo=timezone.utc).timestamp()
  except ValueError:pass
 raise ValueError('Unsupported activity timestamp')
def meters(a,b):return math.hypot((a[0]-b[0])*math.cos(math.radians((a[1]+b[1])/2)),a[1]-b[1])*111320

def normalize(rows):
 result={};excluded=0
 for row in rows:
  start=stamp(row['unlocked_at']);end=stamp(row['dropped_off_at'])
  if not start or not end or end<=start:excluded+=1;continue
  a=[float(row['start_lng']),float(row['start_lat'])];b=[float(row['destination_lng']),float(row['destination_lat'])]
  if not all(-74.3<p[0]<-73.6 and 40.45<p[1]<41 for p in (a,b)):excluded+=1;continue
  identity=json.dumps([start,end,a,b],separators=(',',':'));rid='citi-'+hashlib.sha256(identity.encode()).hexdigest()[:20]
  result[rid]={'id':rid,'start':datetime.fromtimestamp(start,timezone.utc).isoformat().replace('+00:00','Z'),'end':datetime.fromtimestamp(end,timezone.utc).isoformat().replace('+00:00','Z'),'startCoordinates':a,'endCoordinates':b,'elapsedSeconds':end-start,'distanceMeters':None,'geometrySource':'station endpoints only'}
 return sorted(result.values(),key=lambda r:r['start']),excluded

def legacy_trips(folder):
 def read(name):return json.loads((folder/name).read_text().split('=',1)[1].strip().rstrip(';'))
 raw=read('myrides.js');stations={s['stationName']:s for s in read('stations.js')['stationBeanList']};result=[];incomplete=0
 for row in raw['startDatetime']:
  if row['EndTime']=='-' or not row['EndLocation']:incomplete+=1;continue
  start=datetime.strptime(row['StartDateTime'],'%m/%d/%Y %I:%M:%S %p').replace(tzinfo=ZoneInfo('America/New_York'));end=datetime.strptime(row['EndTime'],'%m/%d/%Y %I:%M:%S %p').replace(tzinfo=ZoneInfo('America/New_York'))
  if end<=start:incomplete+=1;continue
  def point(name):
   station=stations.get(name);return [station['longitude'],station['latitude']] if station else None
  identity=json.dumps([start.isoformat(),end.isoformat(),row['StartStation'],row['EndLocation']],separators=(',',':'))
  result.append({'id':'citi-'+hashlib.sha256(identity.encode()).hexdigest()[:20],'start':start.astimezone(timezone.utc).isoformat().replace('+00:00','Z'),'end':end.astimezone(timezone.utc).isoformat().replace('+00:00','Z'),'startCoordinates':point(row['StartStation']),'endCoordinates':point(row['EndLocation']),'startStation':row['StartStation'],'endStation':row['EndLocation'],'elapsedSeconds':(end-start).total_seconds(),'distanceMeters':None,'geometrySource':'station endpoints only','source':'andrewfurman/mycitibike archived rides'})
 return result,{'sourceRecords':len(raw['startDatetime']),'completed':len(result),'incomplete':incomplete,'sourceCommit':'1e06badcf3ec12824171cecc02a07ace2a029552'}

def reconcile(trips,rides,tracks):
 features={str(f['properties']['activity_id']):f for f in tracks['features']};output=[]
 for trip in trips:
  start=stamp_iso(trip['start']);end=stamp_iso(trip['end']);matches=[];possible=[]
  for ride in rides:
   if 'Ride' not in ride.get('Activity Type','') and ride.get('Activity Type') not in {'Handcycle','Velomobile'}:continue
   rs=stamp(ride['Activity Date']);duration=float(ride.get('Elapsed Time') or 0);re=rs+duration
   if re<start-180 or rs>end+180:continue
   aid=ride['Activity ID'];f=features.get(aid);near=False
   if f:
    lines=f['geometry']['coordinates'];pts=lines if f['geometry']['type']=='LineString' else [p for line in lines for p in line]
    near=all(endpoint and any(meters(endpoint,p)<250 for p in pts) for endpoint in (trip['startCoordinates'],trip['endCoordinates']))
   overlap=max(0,min(end,re)-max(start,rs))/max(1,end-start)
   strong_time=abs(start-rs)<180 and abs(end-re)<240
   if near and (overlap>=.75 or strong_time):matches.append(aid)
   elif strong_time or (near and overlap>.2):possible.append(aid)
  row=dict(trip,matchStatus='matched' if matches else 'review' if possible else 'new',stravaActivityIds=sorted(set(matches or possible)))
  output.append(row)
 return output

def stamp_iso(value):return datetime.fromisoformat(value.replace('Z','+00:00')).timestamp()
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--lyft-archive',type=Path,required=True);ap.add_argument('--strava-archive',type=Path,required=True);args=ap.parse_args()
 with zipfile.ZipFile(args.lyft_archive) as z:rows=list(csv.DictReader(io.StringIO(z.read('lyft_bike_scooters.csv').decode('utf-8-sig'))))
 with zipfile.ZipFile(args.strava_archive) as z:rides=list(csv.DictReader(io.StringIO(z.read('activities.csv').decode('utf-8-sig'))))
 trips,excluded=normalize(rows);legacy,legacy_summary=legacy_trips(ROOT/'raw-data/citi-bike/legacy');trips=sorted({t['id']:t for t in trips+legacy}.values(),key=lambda t:t['start']);result=reconcile(trips,rides,json.loads((ROOT/'raw-data/bikes/tracks.geojson').read_text()))
 out=ROOT/'raw-data/citi-bike';out.mkdir(exist_ok=True)
 (out/'trips.json').write_text(json.dumps({'source':'Official Lyft privacy export and andrewfurman/mycitibike archive; NYC completed trips only','archiveSha256':hashlib.sha256(args.lyft_archive.read_bytes()).hexdigest(),'trips':result},indent=2)+'\n')
 summary={'sourceRows':len(rows),'nycCompletedTrips':len(trips),'lyftNycCompletedTrips':len(trips)-len(legacy),'legacy':legacy_summary,'excludedNonNycOrIncomplete':excluded,'matched':sum(t['matchStatus']=='matched' for t in result),'review':sum(t['matchStatus']=='review' for t in result),'new':sum(t['matchStatus']=='new' for t in result),'accountCounterReported':1862,'accountCounterReconciled':False,'gpsPathsProvided':False,'recordedDistancesProvided':False}
 (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary))
if __name__=='__main__':main()
