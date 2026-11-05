#!/usr/bin/env python3
"""Generate a D1 seed from the checked-in run snapshot; never reads browser credentials."""
import argparse,hashlib,json
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[3]
def literal(value):
 if value is None:return 'NULL'
 if isinstance(value,bool):return '1' if value else '0'
 if isinstance(value,(int,float)):return str(value)
 return "'"+str(value).replace("'","''")+"'"
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--snapshot',type=Path,default=ROOT/'raw-data/runs/activities.json');ap.add_argument('--sql',type=Path,required=True);args=ap.parse_args();data=json.loads(args.snapshot.read_text());kind='walks' if 'walks' in data else 'runs';runs=data[kind];assert len(runs)==data.get('recordCount',len(runs))==len({r['activityId'] for r in runs});columns='activity_id,start_date,local_date,distance_meters,moving_seconds,elapsed_seconds,sport_type,distance_source,has_gps,geometry_key,updated_at';updated=data.get('updatedAt') or max(r['date'] for r in runs);rows=[]
 for r in runs:rows.append([r['activityId'],r['date'],r.get('localDate') or datetime.fromisoformat(r['date'].replace('Z','+00:00')).astimezone(ZoneInfo('America/New_York')).date().isoformat(),r['distanceMeters'],r['movingSeconds'],r['elapsedSeconds'],r['sportType'],r['distanceSource'],r['hasGps'],r.get('geometryKey'),updated])
 statements=[(ROOT/'Tanstack Start App/migrations/0001_runs.sql').read_text()]
 for start in range(0,len(rows),100):
  values=','.join('('+','.join(map(literal,row))+')' for row in rows[start:start+100]);statements.append('INSERT INTO runs ('+columns+') VALUES '+values+' ON CONFLICT(activity_id) DO UPDATE SET start_date=excluded.start_date,local_date=excluded.local_date,distance_meters=excluded.distance_meters,moving_seconds=excluded.moving_seconds,elapsed_seconds=excluded.elapsed_seconds,sport_type=excluded.sport_type,distance_source=excluded.distance_source,has_gps=excluded.has_gps,geometry_key=excluded.geometry_key,updated_at=excluded.updated_at WHERE excluded.updated_at >= runs.updated_at;')
 digest=hashlib.sha256(args.snapshot.read_bytes()).hexdigest();snapshot_id='repo-walks-baseline' if kind=='walks' else 'repo-baseline';statements.append("INSERT OR REPLACE INTO dataset_snapshots VALUES ("+literal(snapshot_id)+","+','.join(map(literal,[digest,len(runs),updated]))+');');args.sql.write_text('\n'.join(statements)+'\n');print(f'Prepared {len(runs)} D1 records; repo snapshot unchanged')
if __name__=='__main__':main()
