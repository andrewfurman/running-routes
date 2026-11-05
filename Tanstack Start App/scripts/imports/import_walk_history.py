#!/usr/bin/env python3
"""Import selected walking facts and sanitized GPS from a private Strava account ZIP.
Never copy the full account archive, original sensor files, notes or photos to Git.
"""
import argparse,csv,gzip,hashlib,io,json,math
from pathlib import Path
from datetime import datetime,timezone
from zipfile import ZipFile
from import_strava_history import clean_segments,fit_segments,xml_segments
ROOT=Path(__file__).resolve().parents[3]
WALK_TYPES={'Walk','Virtual Walk','VirtualWalk'}
def number(value):
 if not value:return None
 result=float(value)
 if not math.isfinite(result) or result<0:raise ValueError('Invalid recorded numeric field')
 return result
def import_walks(archive,output):
 records=[];features=[];provenance=[]
 with ZipFile(archive) as zipped:
  rows=list(csv.reader(io.StringIO(zipped.read('activities.csv').decode('utf-8-sig'))));columns={name:i for i,name in enumerate(rows.pop(0))};seen=set()
  for row in rows:
   if row[columns['Activity Type']] not in WALK_TYPES:continue
   aid=row[columns['Activity ID']]
   if not aid.isdigit() or aid in seen:raise ValueError('Invalid or duplicate walk ID')
   seen.add(aid);kind=row[columns['Activity Type']];stamp=datetime.strptime(row[columns['Activity Date']],'%b %d, %Y, %I:%M:%S %p').replace(tzinfo=timezone.utc).isoformat().replace('+00:00','Z')
   filename=row[columns['Filename']];segments=[]
   if filename:
    raw=zipped.read(filename);data=gzip.decompress(raw) if filename.endswith('.gz') else raw;ext=Path(filename.removesuffix('.gz')).suffix.lower()
    if ext not in {'.fit','.gpx','.tcx'}:raise ValueError('Unsupported walk GPS format')
    segments=clean_segments(fit_segments(data) if ext=='.fit' else xml_segments(data,ext))
    provenance.append({'activityId':aid,'sourceSha256':hashlib.sha256(raw).hexdigest(),'format':ext.removeprefix('.'),'mapped':bool(segments)})
   record={'activityId':aid,'date':stamp,'sportType':kind,'distanceMeters':number(row[columns['Distance']]),'movingSeconds':number(row[columns['Moving Time']]),'elapsedSeconds':number(row[columns['Elapsed Time']]),'hasGps':bool(segments),'distanceSource':'strava_export'}
   records.append(record)
   if segments:features.append({'type':'Feature','properties':{'activity_id':aid,'activity_type':kind,'date':stamp,'start_time_utc':stamp,'distance_meters':record['distanceMeters'],'moving_seconds':record['movingSeconds'],'elapsed_seconds':record['elapsedSeconds'],'source':'Selected official Strava walking export','strava_url':'https://www.strava.com/activities/'+aid},'geometry':{'type':'MultiLineString','coordinates':segments}})
 output.mkdir(parents=True,exist_ok=True)
 records.sort(key=lambda r:(r['date'],r['activityId']));features.sort(key=lambda f:(f['properties']['date'],f['properties']['activity_id']))
 summary={'source':'Selected walking facts and GPS from the private Strava account export','archiveSha256':hashlib.sha256(Path(archive).read_bytes()).hexdigest(),'walkRecords':len(records),'mappedWalks':len(features),'withoutGps':len(records)-len(features),'recordedMiles':sum((r['distanceMeters'] or 0)/1609.344 for r in records),'dateRange':[records[0]['date'],records[-1]['date']] if records else [],'privateSensorFilesPublished':False}
 for name,value in [('tracks.geojson',{'type':'FeatureCollection','features':features}),('activities.json',{'source':summary['source'],'walks':records}),('source-manifest.json',{'archiveSha256':summary['archiveSha256'],'activities':provenance}),('summary.json',summary)]:
  (output/name).write_text(json.dumps(value,separators=(',',':'))+'\n')
 return summary
if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--archive',type=Path,required=True);parser.add_argument('--output',type=Path,default=ROOT/'raw-data/walks');args=parser.parse_args();print(json.dumps(import_walks(args.archive,args.output),indent=2))
