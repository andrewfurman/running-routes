import cityNames from './city-names.json' with {type:'json'}
import type { Target, FeatureCollection, Position } from './types'
export function easternDay(now = new Date()) {
 const parts = new Intl.DateTimeFormat('en-US', {timeZone:'America/New_York',year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(now)
 const part=(name:string)=>parts.find(p=>p.type===name)!.value
 return `${part('year')}-${part('month')}-${part('day')}`
}
export function upcomingTargets(targets:Target[], today:string) {
 return targets.filter(t=>!t.past&&t.date>=today).sort((a,b)=>a.date.localeCompare(b.date)||(a.start_time||'05:30').localeCompare(b.start_time||'05:30'))
}
const anchors:[string,number,number][]=[['Havertown / Philadelphia',-75.3,39.98],['New York / New Jersey',-74,40.7],['Seattle',-122.3,47.6],['Fargo',-96.8,46.9],['Indianapolis',-86.16,39.77],['St. Louis',-90.2,38.63],['Toronto / Niagara',-79.1,43.2],['San Francisco Bay Area',-122.3,37.7],['Chicago / Milwaukee',-87.8,42.1],['Charleston',-79.93,32.78],['Savannah',-81.1,32.08],['Cancún / Riviera Maya',-87,20.5],['Grand Cayman',-81.3,19.3],['Seychelles',55.45,-4.6],['London',-.1,51.5],['Japan',136,35],['South Korea',126.98,37.5],['Milan',9.19,45.46],['Portland',-122.68,45.52],['Lake Tahoe',-120,39.1],['Boise',-116.2,43.6],['San Diego',-117.16,32.7],['Washington, DC',-77,38.9],['Boston / New England',-71.1,42.3],['Minneapolis',-93.3,45],['New Orleans / Louisiana',-91,30]]
const distance=(a:Position,b:Position)=>Math.hypot((a[0]-b[0])*Math.cos((a[1]+b[1])*Math.PI/360),a[1]-b[1])*111
export function historyAreas(tracks?:FeatureCollection) {
 const areas:{center:Position;points:Position[];count:number;label:string;fallbackLabel:string;miles:number;distanceMissing:number}[]=[]
 const seen=new Set<string>()
 for(const feature of tracks?.features||[]) {
  const id=feature.properties.activity_id;if(id!=null){if(seen.has(String(id)))continue;seen.add(String(id))}
  const lines=feature.geometry.type==='LineString'?[feature.geometry.coordinates]:feature.geometry.coordinates
  const points:Position[]=lines.flat().filter((p:Position)=>Number.isFinite(p?.[0])&&Number.isFinite(p?.[1])&&Math.abs(p[0])<=180&&Math.abs(p[1])<=90)
  if(!points.length)continue
  const xs=points.map(p=>p[0]).sort((a,b)=>a-b),ys=points.map(p=>p[1]).sort((a,b)=>a-b)
  const center:Position=[xs[Math.floor(xs.length/2)],ys[Math.floor(ys.length/2)]]
  let area=areas.find(a=>distance(a.center,center)<45)
  if(!area){area={center,points:[],count:0,label:'',fallbackLabel:'',miles:0,distanceMissing:0};areas.push(area)}
  area.center=[(area.center[0]*area.count+center[0])/(area.count+1),(area.center[1]*area.count+center[1])/(area.count+1)]
  area.count++;area.points.push(...points);const meters=feature.properties.distance_meters;if(typeof meters==='number'&&Number.isFinite(meters)&&meters>=0)area.miles+=meters/1609.344;else area.distanceMissing++
 }
 for(const area of areas){const nearest=[...anchors].sort((a,b)=>distance([a[1],a[2]],area.center)-distance([b[1],b[2]],area.center))[0];area.fallbackLabel=distance([nearest[1],nearest[2]],area.center)<100?nearest[0]:`${area.center[1].toFixed(2)}°, ${area.center[0].toFixed(2)}°`;const named=[...cityNames].sort((a,b)=>distance(a.center as Position,area.center)-distance(b.center as Position,area.center))[0];area.label=named&&distance(named.center as Position,area.center)<15?named.label:area.fallbackLabel.includes('°')?'New activity area':area.fallbackLabel}
 const combined=new Map<string,(typeof areas)[number]>()
 for(const [index,area] of areas.entries()){
  const key=area.label==='New activity area'?`unresolved-${index}`:area.label;const existing=combined.get(key)
  if(!existing){combined.set(key,{...area});continue}
  const count=existing.count+area.count;existing.center=[(existing.center[0]*existing.count+area.center[0]*area.count)/count,(existing.center[1]*existing.count+area.center[1]*area.count)/count];existing.count=count;existing.miles+=area.miles;existing.distanceMissing+=area.distanceMissing;existing.points=existing.points.concat(area.points)
 }
 return [...combined.values()].sort((a,b)=>b.count-a.count)
}
