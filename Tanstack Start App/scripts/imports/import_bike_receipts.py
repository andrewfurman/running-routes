#!/usr/bin/env python3
"""Import reviewed bike receipt facts; keep full email and research provenance private."""
import argparse,hashlib,json
from datetime import datetime,timezone
from pathlib import Path
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[3]
def utc(value):return datetime.fromisoformat(value.replace('Z','+00:00')).astimezone(timezone.utc).isoformat().replace('+00:00','Z')
def normalize(row):
 if row.get('mode','bike')!='bike' or row.get('sportType','Ride')!='Ride':raise ValueError('Bike-only import')
 start=utc(row.get('startUtc') or row['startLocal']);end=utc(row.get('endUtc') or row['endLocal'])
 city=row['city'];zone=row['timeZone'];ZoneInfo(zone)
 suffix={'Berlin':'Berlin, Germany','Milan':'Milan, Italy','Seattle':'Seattle, WA','Washington DC':'Washington, DC','Chicago':'Chicago, IL','Chicago, IL':'Chicago, IL','New York City, NY':'New York, NY'}.get(city,city)
 a=row.get('startAddress') or (f"{row['startStation']}, {suffix}" if row.get('startStation') else None)
 b=row.get('endAddress') or (f"{row['endStation']}, {suffix}" if row.get('endStation') else None)
 provider=row.get('provider') or ('Divvy' if 'Chicago' in city else 'Citi Bike')
 identity=json.dumps([provider,start,end,a,b],separators=(',',':'),ensure_ascii=False)
 rid='receipt-'+hashlib.sha256(identity.encode()).hexdigest()[:20]
 status=row['matchStatus'];distance=row.get('distanceMeters')
 if distance is not None and (not isinstance(distance,(int,float)) or distance<0):raise ValueError('Invalid recorded distance')
 elapsed=int((datetime.fromisoformat(end.replace('Z','+00:00'))-datetime.fromisoformat(start.replace('Z','+00:00'))).total_seconds())
 if elapsed<=0:raise ValueError('Invalid ride interval')
 facts={'id':rid,'provider':provider,'source':row.get('source') or f"{provider} bike receipt via {row.get('bookingPlatform','email')}",'city':city,'start':start,'end':end,'timeZone':zone,'timestampPrecision':row.get('timestampPrecision','minute'),'startAddress':a,'endAddress':b,'startCoordinates':None,'endCoordinates':None,'distanceMeters':distance,'elapsedSeconds':elapsed,'receiptDurationSeconds':row.get('receiptDurationSeconds') or (row.get('displayDurationMinutes')*60 if row.get('displayDurationMinutes') else None),'recordedDistance':row.get('recordedDistance'),'matchStatus':status}
 if status=='new' and (not a or not b or row.get('routable') is False):raise ValueError('New ride needs verified endpoint pair')
 audit={'id':rid,'provider':provider,'matchStatus':status,'matchedIds':row.get('matchedIds',[]),'reason':row.get('dedupReason','')}
 return facts,audit
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--research',type=Path,required=True);args=ap.parse_args();data=json.loads(args.research.read_text());trips={};reconciliation=[]
 for row in data['records']:
  facts,audit=normalize(row);reconciliation.append(audit)
  if facts['matchStatus']=='new':trips[facts['id']]=facts
 out=ROOT/'raw-data/bike-receipts';out.mkdir(exist_ok=True)
 summary={'source':'Reviewed selected bike receipt facts; no full emails or payment data','preparedAt':data['preparedAtUtc'],'inputSha256':hashlib.sha256(args.research.read_bytes()).hexdigest(),'candidateRecords':len(data['records']),'new':len(trips),'matched':sum(r['matchStatus']=='matched' for r in reconciliation),'review':sum(r['matchStatus']=='review' for r in reconciliation),'excludedScooterRides':4,'newByCity':{city:sum(t['city']==city for t in trips.values()) for city in sorted({t['city'] for t in trips.values()})},'singleEndpointRides':sum(t['startAddress']==t['endAddress'] for t in trips.values()),'recordedMiles':sum((t['distanceMeters'] or 0)/1609.344 for t in trips.values()),'mileageMissing':sum(t['distanceMeters'] is None for t in trips.values())}
 (out/'trips.json').write_text(json.dumps({'source':summary['source'],'trips':sorted(trips.values(),key=lambda t:(t['start'],t['id']))},indent=2,ensure_ascii=False)+'\n');(out/'reconciliation.json').write_text(json.dumps(reconciliation,indent=2)+'\n');(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
