import {WALK_SPORTS} from '../sync/sports.ts'
import type {FeatureCollection} from './types'
const runTypes=new Set(['Run','TrailRun','Trail Run','VirtualRun','Virtual Run'])
export function latestRunId(tracks?:FeatureCollection){
 let latest:string|undefined;let time=-Infinity
 for(const feature of tracks?.features||[]){if(!runTypes.has(feature.properties.activity_type))continue;const stamp=Date.parse(feature.properties.date);if(Number.isFinite(stamp)&&stamp>=time){time=stamp;latest=String(feature.properties.activity_id)}}
 return latest
}
export function requestedRun(search:string){const value=new URLSearchParams(search).get('activity');return value==='latest'||/^(?:\d{1,20}|(?:citi|receipt)-[a-f0-9]{20})$/.test(value||'')?value:undefined}
export function gpsActivitySummary(tracks?:FeatureCollection){
 if(!tracks)return null
 let meters=0,missing=0;const seen=new Set<string>()
 for(const feature of tracks.features){const id=String(feature.properties.activity_id);if(seen.has(id))continue;seen.add(id);const value=feature.properties.distance_meters;if(typeof value==='number'&&Number.isFinite(value)&&value>=0)meters+=value;else missing++}
 return {count:seen.size,miles:meters/1609.344,missing}
}

export function activityTimestamp(properties:Record<string,any>){const value=properties.start_time_utc||(properties.source_csv_date_utc?properties.source_csv_date_utc+' UTC':properties.date);return Date.parse(/^\d{4}-\d{2}-\d{2}$/.test(value||'')?value+'T12:00:00Z':value)}
export function latestBikeId(tracks?:FeatureCollection){return [...(tracks?.features||[])].filter(f=>/Ride/.test(f.properties.activity_type)||['Handcycle','Velomobile'].includes(f.properties.activity_type)).sort((a,b)=>activityTimestamp(b.properties)-activityTimestamp(a.properties)||Number(b.properties.activity_id)-Number(a.properties.activity_id))[0]?.properties.activity_id?.toString()}

export function averagePaceLabel(properties:Record<string,any>){const miles=properties.distance_meters/1609.344,seconds=properties.moving_seconds??properties.receipt_duration_seconds;if(!Number.isFinite(miles)||miles<=0||!Number.isFinite(seconds)||seconds<=0)return 'Unavailable';const pace=Math.round(seconds/miles);return `${Math.floor(pace/60)}:${String(pace%60).padStart(2,'0')} /mi`}

export function activityCaption(properties:Record<string,any>){
 const parts:string[]=properties.geometry_source==='station_endpoints'?['Citi Bike']:[];const miles=properties.distance_meters/1609.344
 if(typeof properties.distance_meters==='number'&&Number.isFinite(miles)&&miles>=0)parts.push(`${miles.toFixed(1)} mi`)
 const pace=averagePaceLabel(properties);if(pace!=='Unavailable')parts.push(pace)
 const hasTime=properties.start_time_utc||properties.source_csv_date_utc||!/^\d{4}-\d{2}-\d{2}$/.test(properties.date||'')
 const start=activityTimestamp(properties)
 if(hasTime&&Number.isFinite(start)){
  const clock=(stamp:number)=>new Date(stamp).toLocaleTimeString('en-US',{timeZone:properties.time_zone||'America/New_York',hour:'numeric',minute:'2-digit'}).replace(/\s/g,'').toLowerCase()
  const elapsed=properties.elapsed_seconds
  parts.push(Number.isFinite(elapsed)&&elapsed>=0?`${clock(start)} to ${clock(start+elapsed*1000)}`:clock(start))
 }
 return parts.join(' · ')
}

export function activityCaptionLines(properties:Record<string,any>){
 const miles=properties.distance_meters/1609.344
 let stats=typeof properties.distance_meters==='number'&&Number.isFinite(miles)&&miles>=0?`${miles.toFixed(1)} miles`:properties.geometry_source==='station_endpoints'?'Citi Bike':properties.geometry_source==='receipt_endpoints'?`${properties.provider||'Bike-share'} bike`:''
 const pace=averagePaceLabel(properties);if(pace!=='Unavailable')stats+=` at ${pace.replace(' /mi',' per mile')}`
 const start=activityTimestamp(properties),hasTime=properties.start_time_utc||properties.source_csv_date_utc||!/^\d{4}-\d{2}-\d{2}$/.test(properties.date||'')
 const clock=(stamp:number)=>new Date(stamp).toLocaleTimeString('en-US',{timeZone:properties.time_zone||'America/New_York',hour:'numeric',minute:'2-digit'}).replace(/\s+/g,' ').toLowerCase()
 const elapsed=properties.elapsed_seconds
 const time=hasTime&&Number.isFinite(start)?Number.isFinite(elapsed)&&elapsed>=0?`${clock(start)} to ${clock(start+elapsed*1000)}`:clock(start):''
 return {stats,time}
}

export function latestWalkId(tracks?:FeatureCollection){return [...(tracks?.features||[])].filter(f=>WALK_SPORTS.includes(String(f.properties.activity_type).replace(/ /g,''))).sort((a,b)=>activityTimestamp(b.properties)-activityTimestamp(a.properties))[0]?.properties.activity_id?.toString()}
