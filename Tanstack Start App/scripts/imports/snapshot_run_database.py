#!/usr/bin/env python3
"""Refresh selected public D1 metadata and GPS snapshots for an explicit tracking PR."""
import argparse,hashlib,json,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--url',default='https://runningroutes.aifurman.com');ap.add_argument('--write',action='store_true');args=ap.parse_args()
 with urllib.request.urlopen(urllib.request.Request(args.url.rstrip('/')+'/api/strava-sync/runs',headers={'User-Agent':'RunningRoutesSync/1.0'}),timeout=60) as response:data=json.load(response)
 source=ROOT/'raw-data/runs/tracks.geojson';tracks=json.loads(source.read_text());features={str(f['properties']['activity_id']):f for f in tracks['features']};rows=[]
 for r in data['runs']:
  aid=r['activityId'];geometry=r.get('geometry')
  if aid not in features and geometry:features[aid]={'type':'Feature','properties':{'activity_id':aid,'date':r['date'],'activity_type':r['sportType'],'distance_meters':r['distanceMeters'],'source':r['distanceSource']},'geometry':geometry}
  rows.append({k:r.get(k) for k in ['activityId','date','distanceMeters','movingSeconds','elapsedSeconds','sportType','distanceSource','hasGps','geometryKey']})
 from zoneinfo import ZoneInfo
 from datetime import datetime
 rows=[{'activityId':row['activityId'],'date':row['date'],'localDate':datetime.fromisoformat(row['date'].replace('Z','+00:00')).astimezone(ZoneInfo('America/New_York')).date().isoformat(),**{k:v for k,v in row.items() if k not in {'activityId','date'}}} for row in rows]
 # Retain baseline order so geographic clustering stays stable as new runs append.
 tracks['features']=list(features.values())
 # Keep the existing GPS serialization unchanged if no new activities were added.
 if len(features)!=len(json.loads(source.read_text())['features']) and args.write:source.write_text(json.dumps(tracks,separators=(',',':'))+'\n')
 snapshot={'asOf':(data['updatedAt'] or '')[:10],'timeZone':'America/New_York','recordCount':len(rows),'gpsRecordCount':sum(bool(r['hasGps']) for r in rows),'source':'Cloudflare D1 selected public run records','trackSourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'runs':rows,'updatedAt':data['updatedAt']}
 if not snapshot['updatedAt']:raise SystemExit('No successful runtime snapshot to save')
 if args.write:
  destination=ROOT/'raw-data/runs/activities.json'
  previous={r['activityId']:r for r in json.loads(destination.read_text()).get('runs',[])} if destination.exists() else {}
  for row in rows:
   for key,value in row.items():
    if key in previous.get(row['activityId'],{}) and previous[row['activityId']][key]==value:row[key]=previous[row['activityId']][key]
  destination.write_text(json.dumps(snapshot,indent=2)+'\n')
 print(f"{'Saved' if args.write else 'Found'} {len(rows)} runs / {snapshot['gpsRecordCount']} GPS. Review and commit using a tracking PR.")
if __name__=='__main__':main()
