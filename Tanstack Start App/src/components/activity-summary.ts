import type {FeatureCollection} from './types'
const runTypes=new Set(['Run','TrailRun','Trail Run','VirtualRun','Virtual Run'])
export function latestRunId(tracks?:FeatureCollection){
 let latest:string|undefined;let time=-Infinity
 for(const feature of tracks?.features||[]){if(!runTypes.has(feature.properties.activity_type))continue;const stamp=Date.parse(feature.properties.date);if(Number.isFinite(stamp)&&stamp>=time){time=stamp;latest=String(feature.properties.activity_id)}}
 return latest
}
export function requestedRun(search:string){const value=new URLSearchParams(search).get('activity');return value==='latest'||/^\d{1,20}$/.test(value||'')?value:undefined}
export function gpsActivitySummary(tracks?:FeatureCollection){
 if(!tracks)return null
 let meters=0,missing=0;const seen=new Set<string>()
 for(const feature of tracks.features){const id=String(feature.properties.activity_id);if(seen.has(id))continue;seen.add(id);const value=feature.properties.distance_meters;if(typeof value==='number'&&Number.isFinite(value)&&value>=0)meters+=value;else missing++}
 return {count:seen.size,miles:meters/1609.344,missing}
}

export function activityTimestamp(properties:Record<string,any>){const value=properties.start_time_utc||(properties.source_csv_date_utc?properties.source_csv_date_utc+' UTC':properties.date);return Date.parse(/^\d{4}-\d{2}-\d{2}$/.test(value||'')?value+'T12:00:00Z':value)}
export function latestBikeId(tracks?:FeatureCollection){return [...(tracks?.features||[])].filter(f=>/Ride/.test(f.properties.activity_type)||['Handcycle','Velomobile'].includes(f.properties.activity_type)).sort((a,b)=>activityTimestamp(b.properties)-activityTimestamp(a.properties)||Number(b.properties.activity_id)-Number(a.properties.activity_id))[0]?.properties.activity_id?.toString()}
