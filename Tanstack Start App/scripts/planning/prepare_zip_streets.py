#!/usr/bin/env python3
"""Clip the public OSM named-road inventory to Census ZCTA 19083 for coverage counts."""
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
 raw=json.loads(source.read_text());boundary=ROOT/'raw-data/boundaries/19083.geojson';zone=shape(json.loads(boundary.read_text())['geometry']);project=Transformer.from_crs(4326,26918,always_xy=True).transform;groups={};names={}
 for way in raw['data']['elements']:
  tags=way.get('tags',{});name=' '.join(tags.get('name','').split());coords=[(p['lon'],p['lat']) for p in way.get('geometry',[])]
  if not name or len(coords)<2 or tags.get('highway') not in ROAD_TYPES or tags.get('access') in {'private','no'} or tags.get('foot')=='no':continue
  line=LineString(coords).intersection(zone)
  if line.is_empty or transform(project,line).length<1:continue
  key=name.casefold();groups.setdefault(key,[]).append(line);names.setdefault(key,name)
 streets=[]
 for key,parts in sorted(groups.items()):
  geometry=union_all(parts)
  def lines(g):
   if g.geom_type=='LineString':return [list(g.coords)]
   return [line for part in g.geoms for line in lines(part)] if hasattr(g,'geoms') else []
  ls=lines(geometry);length=sum(transform(project,LineString(line)).length for line in ls)
  if length<10:continue
  streets.append({'name':names[key],'lengthMeters':round(length,2),'lines':ls})
 result={'zip':'19083','source':'OpenStreetMap contributors via Overpass','sourceTimestamp':raw['data'].get('osm3s',{}).get('timestamp_osm_base'),'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'boundarySource':'Census 2020 ZCTA 19083','boundarySha256':hashlib.sha256(boundary.read_bytes()).hexdigest(),'bounds':list(zone.bounds),'includedHighways':sorted(ROAD_TYPES),'notes':'Unique named public streets with at least 10 metres inside the ZCTA. Parts outside the boundary, private/no-access roads, foot=no roads, motorways, service drives and unnamed paths are excluded. Same-name parts count as one street. ZCTA is an approximation of postal coverage.','streets':streets}
 (ROOT/'raw-data/geography/19083-streets.json').write_text(json.dumps(result,separators=(',',':'))+'\n');print(len(streets),'named public streets;',round(sum(s['lengthMeters'] for s in streets)/1609.344,1),'street miles inside 19083')
if __name__=='__main__':main()
