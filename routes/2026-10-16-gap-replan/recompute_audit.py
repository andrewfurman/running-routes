from pathlib import Path
import json,gzip,re,sys
import numpy as np
from shapely.geometry import LineString,Point,box
from shapely.ops import transform
from shapely.strtree import STRtree
from pyproj import Transformer
SNAPSHOT=Path(__file__).resolve().parent
sys.path.insert(0,str(SNAPSHOT.parents[2]/'tools'))
from import_strava_history import xml_segments,clean_segments
from media_store import ensure_paths  # large inputs live in R2, not git; pulled on first run
ensure_paths(SNAPSHOT,SNAPSHOT.parent/'2026-10-16-strava-history/tracks.geojson.gz',SNAPSHOT.parent/'2026-10-17-swapped-runs')
root=SNAPSHOT.parent;data=json.loads(gzip.decompress((root/'2026-10-16-strava-history/tracks.geojson.gz').read_bytes()));to_m=Transformer.from_crs(4326,32618,always_xy=True).transform;to_deg=Transformer.from_crs(32618,4326,always_xy=True).transform
for fn,kind,aid in [('20606504445.gpx','Run','20606504445'),('20608425525.gpx','Walk','20608425525'),('20601369992.gpx','Ride','20601369992')]:
 segs=clean_segments(xml_segments((SNAPSHOT/fn).read_bytes(),'.gpx'));data['features'].append({'type':'Feature','properties':{'date':'2026-10-15' if kind=='Ride' else '2026-10-16','activity_type':kind,'activity_id':aid},'geometry':{'type':'MultiLineString','coordinates':segs}})
clip=box(-75.38,39.94,-75.26,40.03);lines=[]
for f in data['features']:
 for coords in f['geometry']['coordinates']:
  l=LineString(coords)
  if l.intersects(clip):
   g=l.intersection(clip)
   if not g.is_empty:lines.append(transform(to_m,g))
tree=STRtree(lines)
def stats(coords):
 l=transform(to_m,LineString(coords)); samples=[l.interpolate(d) for d in np.linspace(0,l.length,max(2,int(l.length/5)+1))]; ds=np.array([p.distance(lines[i]) for p,i in zip(samples,tree.nearest(samples))]);core=ds[6:-6] if len(ds)>14 else ds
 return {'length_m':round(l.length,1),'covered_within_15m_pct':round(float(np.mean(ds<=15))*100,1),'covered_within_25m_pct':round(float(np.mean(ds<=25))*100,1),'core_min_distance_m':round(float(min(core)),1),'midpoint':list(to_deg(*l.interpolate(.5,normalized=True).coords[0]))}
old=json.loads((SNAPSHOT/'previous-targets.json').read_text());audit=[{'date':t['date'],'street':t['street'],'segment':t['target_label'],**stats(t['target_coordinates'])} for t in old]
graph=json.loads((SNAPSHOT/'street-graph-2026-10-07.json').read_text());nodes=graph['nodes'];cross={}
for way in graph['ways']:
 for n in way['nodes']:cross.setdefault(n,set()).add(way['name'])
candidates=[];seen=set();home=transform(to_m,Point(-75.3099477,39.9809829))
for way in graph['ways']:
 name=way['name']
 if not name.endswith(('Road','Drive','Lane','Place','Avenue','Court','Circle')):continue
 ids=way['nodes'];cuts=[i for i,n in enumerate(ids) if len(cross[n]-{name})>0 or i in (0,len(ids)-1)]
 for a,b in zip(cuts,cuts[1:]):
  coords=[nodes[str(n)] for n in ids[a:b+1]]
  if len(coords)<2:continue
  l=transform(to_m,LineString(coords));distance=l.distance(home)
  if not 100<l.length<550 or not 600<distance<2700:continue
  st=stats(coords)
  if st['core_min_distance_m']<25:continue
  if st['covered_within_25m_pct']>35:continue
  first=sorted(cross[ids[a]]-{name});last=sorted(cross[ids[b]]-{name})
  if not first or not last:continue
  key=(name,tuple(coords[0]),tuple(coords[-1]))
  if key in seen:continue
  seen.add(key);candidates.append({'street':name,'cross_a':first[0],'cross_b':last[0],'coordinates':coords,'home_straight_m':round(distance),**st})
candidates.sort(key=lambda t:t['home_straight_m']);(SNAPSHOT/'recomputed-audit.json').write_text(json.dumps({'old':audit,'candidates':candidates},indent=2));print('OLD',json.dumps(audit));print('CANDIDATES',len(candidates));
for i,c in enumerate(candidates[:60]):print(i,c['street'],c['cross_a'],'to',c['cross_b'],c['length_m'],c['home_straight_m'],c['covered_within_25m_pct'])
