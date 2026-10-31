#!/usr/bin/env python3
"""Extract only public GPS-run distances from a private Strava ZIP, with GPS fallback."""
import argparse,csv,hashlib,io,json,math,zipfile
from pathlib import Path
from render_year import ROOT,timestamp

def meters(a,b):
 lat1,lat2=map(math.radians,[a[1],b[1]]);dlat=lat2-lat1;dlon=math.radians(b[0]-a[0]);return 6371008.8*2*math.asin(min(1,math.sqrt(math.sin(dlat/2)**2+math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2)))
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--archive',type=Path,required=True);ap.add_argument('--year',type=int,default=2026);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--recorded',type=Path,help='Optional recorded Strava display/API backfill JSON');args=ap.parse_args();source=ROOT/'raw-data/runs/tracks.geojson';features=[f for f in json.loads(source.read_text())['features'] if timestamp(f['properties']['date']).year==args.year];ids={str(f['properties']['activity_id']) for f in features};assert len(ids)==len(features)
 with zipfile.ZipFile(args.archive) as z:
  names=[n for n in z.namelist() if n.endswith('activities.csv')];assert len(names)==1
  rows=list(csv.reader(io.StringIO(z.read(names[0]).decode('utf-8-sig'))));headers=rows[0];distance_columns=[i for i,h in enumerate(headers) if h=='Distance'];assert len(distance_columns)==2,'Expected human-readable km and numeric meter fields in Strava export';di=distance_columns[-1];ai=headers.index('Activity ID');ti=headers.index('Activity Type');official={r[ai]:float(r[di]) for r in rows[1:] if r[ai] in ids and r[di] and r[ti] in {'Run','Trail Run','Virtual Run'}}
 recorded=args.recorded or ROOT/f'raw-data/runs/{args.year}-strava-recorded-backfill.json'
 snapshot=ROOT/'raw-data/runs/activities.json'
 overrides={r['activityId']:r for r in json.loads(snapshot.read_text())['runs'] if r.get('distanceSource') in {'strava_export','strava_web','strava_api'}} if snapshot.exists() else {}
 if recorded.exists():overrides.update({r['activityId']:r for r in json.loads(recorded.read_text())['records']})
 records=[]
 for f in features:
  p=f['properties'];assert p['activity_type'] in {'Run','TrailRun','Trail Run','VirtualRun','Virtual Run'};aid=str(p['activity_id']);lines=f['geometry']['coordinates'] if f['geometry']['type']=='MultiLineString' else [f['geometry']['coordinates']];distance=official.get(aid);origin='strava_export' if aid in official else 'gps_estimate'
  if aid in overrides:distance=overrides[aid]['distanceMeters'];origin=overrides[aid]['distanceSource']
  if distance is None:distance=sum(meters(a,b) for line in lines for a,b in zip(line,line[1:]))
  assert math.isfinite(distance) and distance>=0
  records.append({'activityId':aid,'date':timestamp(p['date']).date().isoformat(),'distanceMeters':round(distance,3),'distanceSource':origin})
 records.sort(key=lambda r:(r['date'],r['activityId']));result={'year':args.year,'units':'meters','stravaDistanceRecords':sum(r['distanceSource']!='gps_estimate' for r in records),'stravaCsvRecords':sum(r['distanceSource']=='strava_export' for r in records),'stravaDisplayedRecords':sum(r['distanceSource']=='strava_displayed' for r in records),'stravaWebRecords':sum(r['distanceSource']=='strava_web' for r in records),'gpsEstimatedRecords':sum(r['distanceSource']=='gps_estimate' for r in records),'trackSourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'stravaSource':'Official account export activities.csv; numeric Distance field in meters','gpsMethod':'Great-circle distance within each saved GPS line; never bridge separate lines. Saved tracks may be simplified.','records':records};args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2)+'\n');print(f'{result["stravaDistanceRecords"]} Strava distances, {result["gpsEstimatedRecords"]} GPS estimates; {sum(r["distanceMeters"] for r in records)/1609.344:.2f} miles')
if __name__=='__main__':main()
