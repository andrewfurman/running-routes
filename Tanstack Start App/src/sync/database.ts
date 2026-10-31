import type {SyncEnv,SyncedRun} from './types'
export async function saveRuns(env:SyncEnv,runs:SyncedRun[],updatedAt:string){
 if(!env.RUNS_DB)return
 const statements=runs.map(r=>env.RUNS_DB!.prepare(`INSERT INTO runs(activity_id,start_date,local_date,distance_meters,moving_seconds,elapsed_seconds,sport_type,distance_source,has_gps,geometry_key,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(activity_id) DO UPDATE SET start_date=excluded.start_date,local_date=excluded.local_date,distance_meters=excluded.distance_meters,moving_seconds=excluded.moving_seconds,elapsed_seconds=excluded.elapsed_seconds,sport_type=excluded.sport_type,distance_source=excluded.distance_source,has_gps=MAX(runs.has_gps,excluded.has_gps),geometry_key=COALESCE(excluded.geometry_key,runs.geometry_key),updated_at=excluded.updated_at`).bind(r.activityId,r.date,new Intl.DateTimeFormat('en-CA',{timeZone:'America/New_York',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date(r.date)),r.distanceMeters,r.movingSeconds,r.elapsedSeconds,r.sportType,r.distanceSource,r.hasGps||r.geometry?1:0,r.geometryKey||null,updatedAt))
 for(let i=0;i<statements.length;i+=100)await env.RUNS_DB.batch(statements.slice(i,i+100))
}
export async function readRuns(env:SyncEnv):Promise<{updatedAt:string|null;runs:SyncedRun[]}>{
 const obj=await env.TIMELAPSE_MEDIA.get('strava/latest-runs.json');const live=obj?await obj.json<{updatedAt:string;runs:SyncedRun[]}>():{updatedAt:null,runs:[]}
 if(!env.RUNS_DB)return live
 const rows=await env.RUNS_DB.prepare('SELECT * FROM runs ORDER BY start_date,activity_id').all<any>();const geometry=new Map(live.runs.map(r=>[r.activityId,r.geometry]));
 return {updatedAt:live.updatedAt,runs:rows.results.map(r=>({activityId:r.activity_id,date:r.start_date,distanceMeters:r.distance_meters,movingSeconds:r.moving_seconds,elapsedSeconds:r.elapsed_seconds,sportType:r.sport_type,distanceSource:r.distance_source,hasGps:Boolean(r.has_gps),geometryKey:r.geometry_key,geometry:geometry.get(r.activity_id)||null}))}
}
