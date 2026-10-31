#!/usr/bin/env python3
"""Inspect or manually run the deployed Strava sync; credentials remain in ignored .env."""
import argparse,json,os
from pathlib import Path
from urllib.request import Request,urlopen
ROOT=Path(__file__).resolve().parents[3]
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--run',action='store_true',help='Run the protected import now');ap.add_argument('--save',type=Path,help='Save the current normalized runtime snapshot');ap.add_argument('--base',default='https://runningroutes.aifurman.com');args=ap.parse_args();key=os.environ.get('STRAVA_SYNC_ADMIN_TOKEN','')
 if not key and (ROOT/'.env').exists():
  for line in (ROOT/'.env').read_text().splitlines():
   name,sep,value=line.partition('=')
   if sep and name=='STRAVA_SYNC_ADMIN_TOKEN':key=value.strip().strip('\"\'')
 headers={'User-Agent':'RunningRoutesSync/1.0'}
 if args.run:
  if not key:raise SystemExit('Set STRAVA_SYNC_ADMIN_TOKEN in ignored .env')
  headers['Authorization']='Bearer '+key
 path='/api/strava-sync/run' if args.run else '/api/strava-sync/status';request=Request(args.base+path,headers=headers,method='POST' if args.run else 'GET');result=json.load(urlopen(request));print(json.dumps(result,indent=2))
 if args.save:
  snapshot=json.load(urlopen(Request(args.base+'/api/strava-sync/runs',headers={'User-Agent':'RunningRoutesSync/1.0'})));args.save.parent.mkdir(parents=True,exist_ok=True);args.save.write_text(json.dumps(snapshot,indent=2)+'\n');print('Saved runtime run snapshot')
if __name__=='__main__':main()
