#!/usr/bin/env python3
"""Save selected recorded mileage for mapped rides; private exports and cookies never enter Git."""
import argparse,csv,hashlib,io,json,math,re,urllib.request,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args,**kwargs):return None
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--archive',type=Path,required=True);ap.add_argument('--web-backfill',action='store_true',help='Read missing recorded distances from the authorized private Strava website session');args=ap.parse_args()
 rows=list(csv.reader(io.StringIO(zipfile.ZipFile(args.archive).read('activities.csv').decode('utf-8-sig'))));header=rows.pop(0);index={h:i for i,h in enumerate(header)};export={row[index['Activity ID']]:row for row in rows}
 path=ROOT/'raw-data/bikes/recorded-distances.json';saved={r['activityId']:r for r in json.loads(path.read_text()).get('records',[])} if path.exists() else {};rides=json.loads((ROOT/'raw-data/bikes/tracks.geojson').read_text());records={};missing=set()
 for feature in rides['features']:
  aid=str(feature['properties']['activity_id']);row=export.get(aid)
  if row and row[index['Distance']]:records[aid]={'activityId':aid,'distanceMeters':float(row[index['Distance']]),'distanceSource':'strava_export'}
  elif aid in saved:records[aid]=saved[aid]
  else:missing.add(aid)
 if missing and args.web_backfill:
  env={}
  for line in (ROOT/'.env').read_text().splitlines():
   key,sep,value=line.partition('=')
   if sep and key=='STRAVA_WEB_COOKIE':env[key]=value.strip().strip('\"\'')
  if not env.get('STRAVA_WEB_COOKIE'):raise SystemExit('Private STRAVA_WEB_COOKIE is required; never commit it')
  opener=urllib.request.build_opener(NoRedirect)
  headers={'Cookie':env['STRAVA_WEB_COOKIE'],'User-Agent':'Mozilla/5.0','Accept':'text/html'}
  with opener.open(urllib.request.Request('https://www.strava.com/athlete/training',headers=headers),timeout=45) as response:html=response.read().decode()
  if not re.search(r'\bathlete_id:\s*14049141\b',html):raise SystemExit('Session owner could not be verified')
  headers.update(Accept='application/json',**{'X-Requested-With':'XMLHttpRequest'})
  for page in range(1,101):
   request=urllib.request.Request(f'https://www.strava.com/athlete/training_activities?sport_type=Ride&page={page}',headers=headers)
   with opener.open(request,timeout=45) as response:data=json.load(response)
   for activity in data['models']:
    aid=str(activity['id'])
    if aid in missing and activity['sport_type']=='Ride':records[aid]={'activityId':aid,'distanceMeters':activity['distance_raw'],'distanceSource':'strava_web'};missing.remove(aid)
   if not missing or not data['models'] or page*data['perPage']>=data['total']:break
 if missing:raise SystemExit(f'{len(missing)} rides lack recorded mileage; existing snapshot kept. Use --web-backfill with the authorized session.')
 assert all(math.isfinite(r['distanceMeters']) and r['distanceMeters']>=0 for r in records.values())
 result={'source':'Selected numeric Strava distance fields; no sensor data or private notes','archiveSha256':hashlib.sha256(args.archive.read_bytes()).hexdigest(),'records':sorted(records.values(),key=lambda r:r['activityId'])};path.write_text(json.dumps(result,indent=2)+'\n');print(f'Saved {len(records)} mapped rides with recorded Strava mileage')
if __name__=='__main__':main()
