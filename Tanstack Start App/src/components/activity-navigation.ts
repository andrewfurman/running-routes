import type {FeatureCollection,Sport} from './types'
import type {SyncedRun} from '../sync/types'
import {RIDE_SPORTS} from '../sync/sports.ts'
export function activitySport(id:string,live:SyncedRun[],bikes?:FeatureCollection):Sport{
 const activity=live.find(r=>r.activityId===id)
 if(activity)return RIDE_SPORTS.includes(activity.sportType)?'bikes':'runs'
 return id.startsWith('citi-')||bikes?.features.some(f=>String(f.properties.activity_id)===id)?'bikes':'runs'
}
