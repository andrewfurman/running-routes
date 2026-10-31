#!/usr/bin/env python3
"""Resolve map-area labels offline from a GeoNames cities500 download (CC BY 4.0)."""
import argparse,hashlib,json,math,subprocess,zipfile
from datetime import date
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
def km(a,b):return math.hypot((a[0]-b[0])*math.cos(math.radians((a[1]+b[1])/2)),a[1]-b[1])*111
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--cities',type=Path,required=True,help='GeoNames cities500.zip; downloaded separately, never sends GPS to a geocoder');ap.add_argument('--centers',type=Path,help='Optional precomputed area centers');args=ap.parse_args()
 if args.centers:groups=json.loads(args.centers.read_text())
 else:
  js="import {historyAreas} from './Tanstack Start App/src/components/scheduled-days.ts';import fs from 'node:fs';const groups={};for(const s of ['runs','bikes'])groups[s]=historyAreas(JSON.parse(fs.readFileSync(`raw-data/${s}/tracks.geojson`,'utf8'))).map(a=>({center:a.center,label:a.fallbackLabel,count:a.count}));console.log(JSON.stringify(groups));"
  groups=json.loads(subprocess.check_output(['node','--experimental-strip-types','--input-type=module','-e',js],cwd=ROOT,text=True))
 cities=[]
 with zipfile.ZipFile(args.cities) as z:
  for line in z.read('cities500.txt').decode().splitlines():
   f=line.split('\t');cities.append({'id':f[0],'name':f[1],'center':[float(f[5]),float(f[4])],'country':f[8],'region':f[10],'population':int(f[14] or 0)})
 areas=[]
 for sport,group in groups.items():
  for area in group:
   nearest=sorted(cities,key=lambda c:km(c['center'],area['center']))[:300]
   major=[c for c in nearest if c['population']>=50000 and km(c['center'],area['center'])<=30]
   place=min(major or nearest,key=lambda c:km(c['center'],area['center']));distance=km(place['center'],area['center']);region=place['region'] if place['country']=='US' else {'CA':'Canada'}.get(place['country'],place['country'])
   fallback=area['label'];label=fallback
   if '°' in fallback:
    label=f"{place['name']}{' area' if distance>30 else ''}, {region}"
    if place['name']=='Tempe Junction' and place['country']=='US':label='Tempe, AZ'
    if distance>100 and place['country']=='US' and place['region']=='NC':label='Atlantic Ocean · Outer Banks coast, NC'
    if distance>100 and place['country']=='US' and place['region']=='MA':label='Atlantic Ocean · Martha’s Vineyard coast, MA'
   areas.append({'sport':sport,'center':area['center'],'label':label,'geonamesId':place['id'],'nearestPlace':place['name'],'country':place['country'],'region':place['region'],'nearestPlaceKm':round(distance,2),'method':'regional anchor' if '°' not in fallback else 'nearest GeoNames populated place'})
 result={'source':'GeoNames cities500','sourceUrl':'https://download.geonames.org/export/dump/','license':'CC BY 4.0','sourceSha256':hashlib.sha256(args.cities.read_bytes()).hexdigest(),'resolvedOn':date.today().isoformat(),'notes':'Approximate activity-area labels, not municipal boundaries. Distant coastal or rural tracks use a nearby named area, not a claimed exact city.','areas':areas}
 (ROOT/'raw-data/geography/history-places.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');(ROOT/'Tanstack Start App/src/components/city-names.json').write_text(json.dumps([{'center':a['center'],'label':a['label']} for a in areas],ensure_ascii=False,indent=2)+'\n')
 for area in areas:
  if area['method']!='regional anchor':print(area['sport'],area['label'],area['nearestPlaceKm'],'km')
 print(f'Resolved {len(areas)} activity areas offline; no coordinates sent to GeoNames.')
if __name__=='__main__':main()
