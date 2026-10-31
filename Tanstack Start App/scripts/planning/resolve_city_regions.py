#!/usr/bin/env python3
"""Refresh public Census postal/city boundaries for the history selector. Requires shapely."""
import urllib.request,urllib.parse,json
from pathlib import Path
base='https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/'
regions=[]
for label,zip in [('Havertown, PA','19083'),('Ardmore, PA','19003'),('Narberth, PA','19072'),('Horsham, PA','19044'),('Coopersburg, PA','18036'),('Ridgefield, CT','06877')]:
 service='PUMA_TAD_TAZ_UGA_ZCTA/MapServer/1'; params={'f':'geojson','where':f"ZCTA5='{zip}'",'outFields':'*','outSR':4326,'returnGeometry':'true','geometryPrecision':6}
 d=json.load(urllib.request.urlopen(base+service+'/query?'+urllib.parse.urlencode(params)));assert d.get('features'),d
 regions.append({'label':label,'source':base+service,'query':params['where'],'geometry':d['features'][0]['geometry']})
for label,state,name in [('New York City, NY','36','New York'),('Philadelphia, PA','42','Philadelphia')]:
 service='Places_CouSub_ConCity_SubMCD/MapServer/11';params={'f':'geojson','where':f"STATE='{state}' AND BASENAME='{name}'",'outFields':'*','outSR':4326,'returnGeometry':'true','geometryPrecision':6}
 d=json.load(urllib.request.urlopen(base+service+'/query?'+urllib.parse.urlencode(params)));assert d.get('features'),d
 regions.append({'label':label,'source':base+service,'query':params['where'],'geometry':d['features'][0]['geometry']})
from shapely.geometry import shape,mapping
for r in regions:r['geometry']=mapping(shape(r['geometry']).simplify(.00005,preserve_topology=True))
root=Path(__file__).resolve().parents[3];(root/'raw-data/geography/city-regions.json').write_text(json.dumps({'source':'US Census TIGERweb BAS 2026 / Census 2020 ZCTA','method':'Postal areas for named suburbs; incorporated city boundaries for NYC and Philadelphia. Activities assigned by median GPS coordinate once; mileage is whole recorded activity distance.','regions':regions},indent=2)+'\n');(root/'Tanstack Start App/src/components/city-regions.json').write_text(json.dumps([{'label':r['label'],'geometry':r['geometry']} for r in regions],separators=(',',':'))+'\n');print([(r['label'],len(str(r['geometry']))) for r in regions])
