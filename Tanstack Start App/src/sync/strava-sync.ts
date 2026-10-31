import type {SyncEnv,SyncStorage,SyncStatus,SyncedRun,RunSnapshot} from './types'
const SCHEDULE='08:00 America/New_York'
export function easternClock(time:number) {
 const p=new Intl.DateTimeFormat('en-US',{timeZone:'America/New_York',year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',hourCycle:'h23'}).formatToParts(new Date(time))
 const get=(t:string)=>p.find(x=>x.type===t)!.value
 return {day:`${get('year')}-${get('month')}-${get('day')}`,hour:Number(get('hour')),minute:Number(get('minute'))}
}
export function isEightAMEastern(time:number){const t=easternClock(time);return t.hour===8&&t.minute===0}
export function decodePolyline(encoded:string):[number,number][] {
 let index=0,lat=0,lng=0;const points:[number,number][]=[]
 const read=()=>{let result=0,shift=0,b=0;do{if(index>=encoded.length||shift>30)throw Error('invalid_polyline');b=encoded.charCodeAt(index++)-63;if(b<0||b>63)throw Error('invalid_polyline');result|=(b&31)<<shift;shift+=5}while(b>=32);return result&1?~(result>>1):result>>1}
 while(index<encoded.length){lat+=read();lng+=read();if(Math.abs(lat)>9000000||Math.abs(lng)>18000000)throw Error('invalid_coordinates');points.push([lng/1e5,lat/1e5])}
 return points
}
export function normalizeRun(activity:any):SyncedRun|null {
 if(!['Run','TrailRun','VirtualRun'].includes(activity.sport_type||activity.type))return null
 if(!Number.isSafeInteger(activity.id)||!Number.isFinite(activity.distance)||activity.distance<0||!Number.isFinite(Date.parse(activity.start_date)))throw Error('invalid_activity')
 let coordinates:[number,number][]=[]
 if(activity.map?.summary_polyline){try{coordinates=decodePolyline(activity.map.summary_polyline)}catch{/* Preserve recorded mileage even when a GPS route is unavailable. */}}
 return {activityId:String(activity.id),date:new Date(activity.start_date).toISOString(),distanceMeters:activity.distance,distanceSource:'strava_api',sportType:activity.sport_type||activity.type,movingSeconds:activity.moving_time||0,elapsedSeconds:activity.elapsed_time||0,geometry:coordinates.length>1?{type:'LineString',coordinates}:null}
}
export function configured(env:SyncEnv){return Boolean(env.STRAVA_CLIENT_ID&&env.STRAVA_CLIENT_SECRET&&env.STRAVA_REFRESH_TOKEN)}
interface Auth {accessToken:string;refreshToken:string;expiresAt:number}
export class StravaSync {
 private storage:SyncStorage;private env:SyncEnv;private queue:Promise<unknown>=Promise.resolve()
 constructor(state:{storage:SyncStorage},env:SyncEnv){this.storage=state.storage;this.env=env}
 async fetch(request:Request){const url=new URL(request.url)
  if(request.method==='GET'&&url.pathname==='/status'){const status=await this.storage.get<SyncStatus>('status');return Response.json(configured(this.env)?status||{state:'needs_connection',schedule:SCHEDULE}:{...status,state:'needs_connection',schedule:SCHEDULE})}
  if(request.method!=='POST'||url.pathname!=='/sync')return new Response('Not found',{status:404})
  const task=this.queue.then(()=>this.run(Date.now(),url.searchParams.get('force')==='1'));this.queue=task.catch(()=>{});return Response.json(await task)
 }
 async run(now:number,force=false,fetcher:typeof fetch=fetch):Promise<SyncStatus>{
  const before=await this.storage.get<SyncStatus>('status');const attempted=new Date(now).toISOString();const day=easternClock(now).day
  if(!configured(this.env)){const status:SyncStatus={...before,state:'needs_connection',schedule:SCHEDULE,lastAttemptAt:attempted};await this.storage.put('status',status);return status}
  if(!force&&before?.state==='synced'&&before.lastSuccessDay===day)return before
  try{
   let auth=await this.storage.get<Auth>('auth')
   if(!auth||auth.expiresAt<now/1000+60){
    const response=await fetcher('https://www.strava.com/oauth/token',{method:'POST',body:new URLSearchParams({client_id:this.env.STRAVA_CLIENT_ID!,client_secret:this.env.STRAVA_CLIENT_SECRET!,grant_type:'refresh_token',refresh_token:auth?.refreshToken||this.env.STRAVA_REFRESH_TOKEN!})})
    if(!response.ok)throw Error(`strava_oauth_${response.status}`)
    const data:any=await response.json();if(!data.access_token||!data.refresh_token||!Number.isFinite(data.expires_at))throw Error('invalid_oauth_response')
    auth={accessToken:data.access_token,refreshToken:data.refresh_token,expiresAt:data.expires_at}
    // Persist rotation before subsequent API calls; a later failure must not lose the new refresh token.
    await this.storage.put('auth',auth)
   }
   const get=async(url:string)=>{const r=await fetcher(url,{headers:{Authorization:`Bearer ${auth!.accessToken}`}});if(!r.ok)throw Error(`strava_api_${r.status}`);return r.json() as Promise<any>}
   const athlete=await get('https://www.strava.com/api/v3/athlete');if(String(athlete.id)!==(this.env.STRAVA_ATHLETE_ID||'14049141'))throw Error('athlete_mismatch')
   const last=before?.lastSuccessAt?Date.parse(before.lastSuccessAt)-86400000:now-7*86400000;const after=Math.floor(last/1000);const fetched:SyncedRun[]=[]
   for(let page=1;page<=10;page++){
    const activities=await get(`https://www.strava.com/api/v3/athlete/activities?after=${after}&per_page=100&page=${page}`);if(!Array.isArray(activities))throw Error('invalid_activity_page')
    for(const activity of activities){if(activity.athlete?.id&&String(activity.athlete.id)!==String(athlete.id))throw Error('activity_owner_mismatch');const run=normalizeRun(activity);if(run)fetched.push(run)}
    if(activities.length<100)break
    if(page===10)throw Error('pagination_limit')
   }
   const object=await this.env.TIMELAPSE_MEDIA.get('strava/latest-runs.json');const old=object?await object.json<RunSnapshot>():null;const byId=new Map((old?.runs||[]).map(r=>[r.activityId,r]));for(const run of fetched)byId.set(run.activityId,run)
   const runs=[...byId.values()].sort((a,b)=>a.date.localeCompare(b.date)||a.activityId.localeCompare(b.activityId));await this.env.TIMELAPSE_MEDIA.put('strava/latest-runs.json',JSON.stringify({updatedAt:attempted,runs}),{httpMetadata:{contentType:'application/json'}})
   const status:SyncStatus={state:'synced',schedule:SCHEDULE,lastAttemptAt:attempted,lastSuccessAt:attempted,lastSuccessDay:day,importedRuns:runs.length};await this.storage.put('status',status);return status
  }catch(e){const code=e instanceof Error?e.message:'sync_failed';const status:SyncStatus={...before,state:'error',schedule:SCHEDULE,lastAttemptAt:attempted,errorCode:/^(strava_(oauth|api)_\d{3}|invalid_[a-z_]+|athlete_mismatch|activity_owner_mismatch|pagination_limit)$/.test(code)?code:'sync_failed'};await this.storage.put('status',status);return status}
 }
}
