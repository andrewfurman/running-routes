#!/usr/bin/env python3
"""Build 19083 coverage including connected public streets that follow its border."""
import json,hashlib,argparse,urllib.request,urllib.parse
from pathlib import Path
from shapely.geometry import shape,LineString,mapping
from shapely.ops import transform
from shapely import union_all
from pyproj import Transformer
ROOT=Path(__file__).resolve().parents[3]
ROAD_TYPES={'residential','living_street','unclassified','tertiary','secondary','primary','tertiary_link','secondary_link','primary_link','pedestrian','road'}
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--download',action='store_true',help='Refresh the public OSM inventory first');args=ap.parse_args()
 source=ROOT/'raw-data/geography/19083-streets-osm.json'
 if args.download:
  zone=shape(json.loads((ROOT/'raw-data/boundaries/19083.geojson').read_text())['geometry']);west,south,east,north=zone.bounds;query=f'[out:json][timeout:120];way[\"highway\"][\"name\"]({south},{west},{north},{east});out tags geom;'
  request=urllib.request.Request('https://overpass-api.de/api/interpreter',data=urllib.parse.urlencode({'data':query}).encode(),headers={'User-Agent':'RunningRoutes/1.0 personal street coverage'})
  with urllib.request.urlopen(request,timeout=150) as response:data=json.load(response)
  source.write_text(json.dumps({'source':'https://overpass-api.de/api/interpreter','query':query,'data':data},separators=(',',':'))+'\n')
 raw=json.loads(source.read_text());boundary=ROOT/'raw-data/boundaries/19083.geojson';zone=shape(json.loads(boundary.read_text())['geometry']);project=Transformer.from_crs(4326,26918,always_xy=True).transform;groups={};names={};ways={}
 edge=transform(project,zone).boundary.buffer(30)
 for way in raw['data']['elements']:
  tags=way.get('tags',{});name=' '.join(tags.get('name','').split());coords=[(p['lon'],p['lat']) for p in way.get('geometry',[])]
  if not name or len(coords)<2 or tags.get('highway') not in ROAD_TYPES or tags.get('access') in {'private','no'} or tags.get('foot')=='no':continue
  line=LineString(coords);metric=transform(project,line);near=metric.intersection(edge).length;key=name.casefold()
  ways.setdefault(key,[]).append((line,metric,near>=100 and near>=metric.length*.4));names[key]=name
 border_names=[]
 for key,parts in ways.items():
  # Grow only connected same-name public ways from a substantial border-following section.
  selected={i for i,(_,_,seed) in enumerate(parts) if seed}
  changed=True
  while selected and changed:
   changed=False
   for i,(_,metric,_) in enumerate(parts):
    if i not in selected and any(metric.distance(parts[j][1])<=1 for j in selected):selected.add(i);changed=True
  if selected:border_names.append(names[key])
  for i,(line,_,_) in enumerate(parts):
   included=line if i in selected else line.intersection(zone)
   if not included.is_empty and transform(project,included).length>=1:groups.setdefault(key,[]).append(included)

 streets=[]
 for key,parts in sorted(groups.items()):
  geometry=union_all(parts)
  def lines(g):
   if g.geom_type=='LineString':return [list(g.coords)]
   return [line for part in g.geoms for line in lines(part)] if hasattr(g,'geoms') else []
  ls=lines(geometry);length=sum(transform(project,LineString(line)).length for line in ls)
  if length<10:continue
  streets.append({'name':names[key],'lengthMeters':round(length,2),'lines':ls})
 result={'zip':'19083','source':'OpenStreetMap contributors via Overpass','sourceTimestamp':raw['data'].get('osm3s',{}).get('timestamp_osm_base'),'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'boundarySource':'Census 2020 ZCTA 19083','boundarySha256':hashlib.sha256(boundary.read_bytes()).hexdigest(),'bounds':[min(min(p[0] for line in street['lines'] for p in line) for street in streets),min(min(p[1] for line in street['lines'] for p in line) for street in streets),max(max(p[0] for line in street['lines'] for p in line) for street in streets),max(max(p[1] for line in street['lines'] for p in line) for street in streets)],'borderStreets':sorted(border_names),'borderPolicy':{'corridorMetres':30,'minimumBorderMetres':100,'minimumWayFraction':0.4,'connectedWayToleranceMetres':1},'includedHighways':sorted(ROAD_TYPES),'notes':'Unique named public streets with at least 10 metres inside the ZCTA or in a connected boundary-street component. Public ways following the border for at least 100 metres and 40% of their length within a 30 metre corridor seed full connected same-name streets, including their sections outside the ZIP. Other outside sections, private/no-access roads, foot=no roads, motorways, service drives and unnamed paths are excluded. Same-name parts count as one street. ZCTA is an approximation of postal coverage.','streets':streets}
 (ROOT/'raw-data/geography/19083-streets.json').write_text(json.dumps(result,separators=(',',':'))+'\n');print(len(streets),'named public streets;',round(sum(s['lengthMeters'] for s in streets)/1609.344,1),'street miles including boundary streets')
if __name__=='__main__':main()
