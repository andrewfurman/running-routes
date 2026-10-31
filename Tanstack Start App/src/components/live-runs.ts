import type {FeatureCollection,CalendarEvent} from './types'
import type {SyncedRun} from '../sync/types'
import {easternDay} from './scheduled-days.ts'
export function mergeSyncedTracks(base:FeatureCollection,runs:SyncedRun[]):FeatureCollection {
 const features=new Map(base.features.map(f=>[String(f.properties.activity_id),f]))
 for(const run of runs){const existing=features.get(run.activityId);if(!existing&&!run.geometry)continue;features.set(run.activityId,{type:'Feature',geometry:existing?.geometry||run.geometry!,properties:{...existing?.properties,activity_id:run.activityId,date:run.date,activity_type:'Run',distance_meters:run.distanceMeters,source:run.distanceSource,strava_url:`https://www.strava.com/activities/${run.activityId}`}})}
 return {type:'FeatureCollection',features:[...features.values()]}
}
export function mergeSyncedEvents(base:CalendarEvent[],runs:SyncedRun[]):CalendarEvent[]{
 const events=new Map(base.map(e=>[e.id,e]))
 for(const run of runs){const start=easternDay(new Date(run.date));const next=new Date(start+'T12:00:00Z');next.setUTCDate(next.getUTCDate()+1);events.set('strava-'+run.activityId,{id:'strava-'+run.activityId,title:'Recorded run',start,end:next.toISOString().slice(0,10),type:'past',activityId:run.activityId})}
 return [...events.values()]
}
