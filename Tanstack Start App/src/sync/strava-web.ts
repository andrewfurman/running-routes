import type {SyncEnv,SyncedRun} from './types'
export function parseGpx(xml:string):SyncedRun['geometry']{
 if(!/<(?:\w+:)?gpx\b/.test(xml))throw Error('invalid_gpx')
 const segments=xml.match(/<(?:\w+:)?trkseg\b[^>]*>[\s\S]*?<\/(?:\w+:)?trkseg>/g)||[xml]
 const lines=segments.map(segment=>[...segment.matchAll(/<(?:\w+:)?trkpt\b([^>]*)>/g)].map(match=>{
  const attr=(key:string)=>{const m=match[1].match(new RegExp(`\\b${key}=["']([^"']+)["']`));return m?Number(m[1]):NaN};const lat=attr('lat'),lon=attr('lon');if(!Number.isFinite(lat)||!Number.isFinite(lon)||Math.abs(lat)>90||Math.abs(lon)>180)throw Error('invalid_coordinates');return [lon,lat] as [number,number]
 })).filter(line=>line.length>1)
 return lines.length>1?{type:'MultiLineString',coordinates:lines}:lines.length?{type:'LineString',coordinates:lines[0]}:null
}
export function normalizeWebRun(a:any):SyncedRun|null{
 if(!['Run','TrailRun','VirtualRun'].includes(a.sport_type))return null
 if(!Number.isSafeInteger(a.id)||!Number.isFinite(a.distance_raw)||a.distance_raw<0||!Number.isFinite(Date.parse(a.start_time)))throw Error('invalid_activity')
 return {activityId:String(a.id),date:new Date(a.start_time).toISOString(),distanceMeters:a.distance_raw,distanceSource:'strava_web',sportType:a.sport_type,movingSeconds:a.moving_time_raw||0,elapsedSeconds:a.elapsed_time_raw||0,hasGps:Boolean(a.has_latlng),geometry:null}
}
export async function fetchWebRuns(env:SyncEnv,since:number,fetcher:typeof fetch):Promise<SyncedRun[]>{
 const headers={Cookie:env.STRAVA_WEB_COOKIE!,Accept:'application/json','X-Requested-With':'XMLHttpRequest','User-Agent':'Mozilla/5.0'}
 const get=async(path:string,accept='application/json')=>{const response=await fetcher('https://www.strava.com'+path,{headers:{...headers,Accept:accept},redirect:'manual'});if(response.status===301||response.status===302||response.status===401||response.status===403)throw Error('browser_login_required');if(!response.ok)throw Error(`strava_web_${response.status}`);return response}
 const profile=await (await get('/athlete/training','text/html')).text();const owner=profile.match(/\bathlete_id:\s*(\d+)/)?.[1];if(!owner)throw Error('browser_login_required');if(owner!==(env.STRAVA_ATHLETE_ID||'14049141'))throw Error('athlete_mismatch')
 const result:SyncedRun[]=[]
 for(let page=1;page<=100;page++){
  const response=await get(`/athlete/training_activities?keywords=&sport_type=Run&tags=&commute=&private_activities=&trainer=&gear=&new_activity_only=false&page=${page}`);if(!response.headers.get('content-type')?.includes('json'))throw Error('browser_login_required');const data:any=await response.json();if(!Array.isArray(data.models))throw Error('invalid_activity_page')
  let oldest=Infinity
  for(const activity of data.models){const run=normalizeWebRun(activity);if(!run)continue;oldest=Math.min(oldest,Date.parse(run.date));if(Date.parse(run.date)<since)continue
   if(run.hasGps){const existing=env.RUNS_DB?await env.RUNS_DB.prepare('SELECT geometry_key FROM runs WHERE activity_id=?').bind(run.activityId).all<{geometry_key:string|null}>():null
    run.geometryKey=existing?.results[0]?.geometry_key||null
    if(!run.geometryKey){const xml=await (await get(`/activities/${run.activityId}/export_gpx`,'application/gpx+xml,application/xml')).text();run.geometry=parseGpx(xml);if(!run.geometry)throw Error('invalid_gpx');run.geometryKey=`strava/tracks/${run.activityId}.geojson`;await env.TIMELAPSE_MEDIA.put(run.geometryKey,JSON.stringify({type:'Feature',properties:{activity_id:run.activityId,date:run.date,activity_type:run.sportType},geometry:run.geometry}),{httpMetadata:{contentType:'application/geo+json'}})}
   }
   result.push(run)
  }
  if(!data.models.length||oldest<since||page*data.perPage>=data.total)return result
 }
 throw Error('pagination_limit')
}
