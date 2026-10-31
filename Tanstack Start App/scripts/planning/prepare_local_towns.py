#!/usr/bin/env python3
"""Create Philadelphia-region fallback names offline from a public GeoNames cities500 ZIP."""
import argparse,hashlib,json,math,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--cities',type=Path,required=True);args=ap.parse_args();towns=[]
 with zipfile.ZipFile(args.cities) as archive:
  for line in archive.read('cities500.txt').decode().splitlines():
   fields=line.split('\t');lon,lat=float(fields[5]),float(fields[4])
   if fields[8]=='US' and fields[10] in {'PA','NJ','DE'} and math.hypot((lon+75.3)*.766,lat-39.98)*111<90:towns.append({'label':fields[1]+', '+fields[10],'center':[lon,lat],'geonamesId':fields[0]})
 (ROOT/'Tanstack Start App/src/components/local-towns.json').write_text(json.dumps(towns,separators=(',',':'))+'\n')
 (ROOT/'raw-data/geography/local-towns-source.json').write_text(json.dumps({'source':'GeoNames cities500','sourceUrl':'https://download.geonames.org/export/dump/','license':'CC BY 4.0','sourceSha256':hashlib.sha256(args.cities.read_bytes()).hexdigest(),'placeCount':len(towns),'method':'Offline populated-place anchors within 90 km of Havertown. Used only when no named Census region contains an activity median; closest town must be within 12 km. Approximate activity labels, not municipal-clipped mileage. No GPS sent to GeoNames.'},indent=2)+'\n')
 print('Prepared',len(towns),'local town labels')
if __name__=='__main__':main()
