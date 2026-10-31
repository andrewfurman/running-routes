import {readRuns} from './sync/database'
import handler from '@tanstack/react-start/server-entry'
import {isEightAMEastern} from './sync/strava-sync'
import type {SyncEnv} from './sync/types'
export {StravaSync} from './sync/strava-sync'
function sync(env:SyncEnv){return env.STRAVA_SYNC.get(env.STRAVA_SYNC.idFromName('andrew-furman'))}
export default {
 async fetch(request:Request,env:SyncEnv){
  const url=new URL(request.url)
  if(url.pathname==='/api/strava-sync/status'&&request.method==='GET')return sync(env).fetch('https://internal/status')
  if(url.pathname==='/api/strava-sync/runs'&&request.method==='GET'){return Response.json(await readRuns(env),{headers:{'Cache-Control':'no-store'}})}
  if(url.pathname==='/api/strava-sync/run'&&request.method==='POST'){
   if(!env.STRAVA_SYNC_ADMIN_TOKEN||request.headers.get('Authorization')!==`Bearer ${env.STRAVA_SYNC_ADMIN_TOKEN}`)return new Response('Unauthorized',{status:401})
   return sync(env).fetch('https://internal/sync?force=1',{method:'POST'})
  }
  return handler.fetch(request)
 },
 async scheduled(event:{scheduledTime:number},env:SyncEnv){
  if(!isEightAMEastern(event.scheduledTime))return
  const response=await sync(env).fetch('https://internal/sync',{method:'POST'});if(!response.ok)throw Error('Strava sync handler failed');const status:any=await response.json();if(status.state!=='synced')throw Error(`Strava sync failed: ${status.errorCode}`)
 },
}
