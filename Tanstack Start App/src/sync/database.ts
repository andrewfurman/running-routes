import type {SyncEnv,SyncedRun} from './types'
export async function saveRuns(env:SyncEnv,runs:SyncedRun[],updatedAt:string){
 if(!env.RUNS_DB)return
 const statements=runs.map(r=>env.RUNS_DB!.prepare(`INSERT INTO runs(activity_id,start_date,local_date,distance_meters,moving_seconds,elapsed_seconds,sport_type,distance_source,has_gps,geometry_key,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(activity_id) DO UPDATE SET start_date=excluded.start_date,local_date=excluded.local_date,distance_meters=excluded.distance_meters,moving_seconds=excluded.moving_seconds,elapsed_seconds=excluded.elapsed_seconds,sport_type=excluded.sport_type,distance_source=excluded.distance_source,has_gps=MAX(runs.has_gps,excluded.has_gps),geometry_key=COALESCE(excluded.geometry_key,runs.geometry_key),updated_at=excluded.updated_at`).bind(r.activityId,r.date,new Intl.DateTimeFormat('en-CA',{timeZone:'America/New_York',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date(r.date)),r.distanceMeters,r.movingSeconds,r.elapsedSeconds,r.sportType,r.distanceSource,r.hasGps||r.geometry?1:0,r.geometryKey||null,updatedAt))
 for(let i=0;i<statements.length;i+=100)await env.RUNS_DB.batch(statements.slice(i,i+100))
}
export async function readRuns(env:SyncEnv):Promise<{updatedAt:string|null;runs:SyncedRun[]}>{
 const [liveObject,hikeObject]=await Promise.all([
  env.TIMELAPSE_MEDIA.get('strava/latest-runs.json'),
  env.TIMELAPSE_MEDIA.get('strava/archive-hikes.json'),
 ])
 const live=liveObject?await liveObject.json<{updatedAt:string;runs:SyncedRun[]}>():{updatedAt:null,runs:[]}
 const archived=hikeObject?await hikeObject.json<SyncedRun[]>():[]
 const byId=new Map(archived.map(hike=>[hike.activityId,hike]))
 const liveGeometry=new Map(live.runs.map(activity=>[activity.activityId,activity.geometry]))
 if(env.RUNS_DB){
  const rows=await env.RUNS_DB.prepare('SELECT * FROM runs ORDER BY start_date,activity_id').all<any>()
  for(const row of rows.results){
   byId.set(row.activity_id,{
    activityId:row.activity_id,date:row.start_date,distanceMeters:row.distance_meters,
    movingSeconds:row.moving_seconds,elapsedSeconds:row.elapsed_seconds,sportType:row.sport_type,
    distanceSource:row.distance_source,hasGps:Boolean(row.has_gps),geometryKey:row.geometry_key,
    geometry:liveGeometry.get(row.activity_id)??byId.get(row.activity_id)?.geometry??null,
   })
  }
 }else{
  for(const activity of live.runs){
   byId.set(activity.activityId,{...activity,geometry:activity.geometry??byId.get(activity.activityId)?.geometry??null})
  }
 }
 const runs=[...byId.values()].sort((a,b)=>a.date.localeCompare(b.date)||a.activityId.localeCompare(b.activityId))
 return {updatedAt:live.updatedAt,runs}
}
