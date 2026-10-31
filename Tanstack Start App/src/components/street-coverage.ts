import type {FeatureCollection,Position} from './types'
export interface StreetInventory {bounds:number[];sourceTimestamp?:string;streets:{name:string;lengthMeters:number;lines:Position[][]}[]}
export interface StreetCoverage {missingRoads:FeatureCollection;total:number;runOn:number;untouched:number;complete:number;partial:number;outstanding:number;streetPercent:number;lengthPercent:number;coveredMiles:number;totalMiles:number;gpsRuns:number;latestDate:string;sourceTimestamp?:string;streets:{name:string;percent:number;status:'complete'|'partial'|'untouched';coveredMeters:number;lengthMeters:number}[]}
const CELL=50,RADIUS=20,COS=Math.cos(Math.PI/6)
const project=(p:Position):Position=>[(p[0]+75.3)*111195*Math.cos(40*Math.PI/180),(p[1]-40)*111195]
interface Segment {ax:number;ay:number;bx:number;by:number;dx:number;dy:number;length:number}
export function calculateStreetCoverage(inventory:StreetInventory,tracks:FeatureCollection):StreetCoverage {
 const grid=new Map<string,Segment[]>(),seen=new Set<string>();const [west,south,east,north]=inventory.bounds;let gpsRuns=0,latestDate=''
 for(const feature of tracks.features){
  if(!['Run','TrailRun','Trail Run','VirtualRun','Virtual Run'].includes(feature.properties.activity_type||''))continue
  const id=String(feature.properties.activity_id);if(seen.has(id))continue;seen.add(id);gpsRuns++
  const date=feature.properties.date||'';if(date>latestDate)latestDate=date
  const lines=feature.geometry.type==='LineString'?[feature.geometry.coordinates]:feature.geometry.coordinates
  for(const line of lines)for(let i=1;i<line.length;i++){
   const a=line[i-1],b=line[i]
   if(Math.max(a[0],b[0])<west-.001||Math.min(a[0],b[0])>east+.001||Math.max(a[1],b[1])<south-.001||Math.min(a[1],b[1])>north+.001)continue
   const [ax,ay]=project(a),[bx,by]=project(b),dx=bx-ax,dy=by-ay,length=Math.hypot(dx,dy)
   // Do not bridge large recording gaps or disconnected GPX lines.
   if(length<1||length>250)continue
   const segment={ax,ay,bx,by,dx,dy,length}
   for(let x=Math.floor((Math.min(ax,bx)-RADIUS)/CELL);x<=Math.floor((Math.max(ax,bx)+RADIUS)/CELL);x++)for(let y=Math.floor((Math.min(ay,by)-RADIUS)/CELL);y<=Math.floor((Math.max(ay,by)+RADIUS)/CELL);y++){const key=x+','+y;const values=grid.get(key);if(values)values.push(segment);else grid.set(key,[segment])}
  }
 }
 let totalMeters=0,coveredMeters=0
 const missingRoads:FeatureCollection={type:'FeatureCollection',features:[]}
 const streets=inventory.streets.map(street=>{
  let length=0,covered=0
  const missing:Position[][]=[]
  for(const line of street.lines)for(let i=1;i<line.length;i++){
   const [ax,ay]=project(line[i-1]),[bx,by]=project(line[i]),dx=bx-ax,dy=by-ay,meters=Math.hypot(dx,dy);if(!meters)continue
   const steps=Math.ceil(meters/10),weight=meters/steps;length+=meters
   for(let n=0;n<steps;n++){
    const fraction=(n+.5)/steps,x=ax+dx*fraction,y=ay+dy*fraction,candidates=grid.get(Math.floor(x/CELL)+','+Math.floor(y/CELL))||[]
    const hit=candidates.some(s=>{
     // A perpendicular intersection crossing must not count as running along a street.
     if(Math.abs(dx*s.dx+dy*s.dy)/(meters*s.length)<COS)return false
     const t=Math.max(0,Math.min(1,((x-s.ax)*s.dx+(y-s.ay)*s.dy)/(s.length*s.length)))
     return Math.hypot(x-(s.ax+t*s.dx),y-(s.ay+t*s.dy))<=RADIUS
    })
    if(hit)covered+=weight
    else {
     const a=line[i-1],b=line[i],at=(f:number):Position=>[a[0]+(b[0]-a[0])*f,a[1]+(b[1]-a[1])*f]
     const start=at(n/steps),end=at((n+1)/steps),last=missing[missing.length-1],tail=last?.[last.length-1]
     if(tail&&Math.abs(tail[0]-start[0])<1e-10&&Math.abs(tail[1]-start[1])<1e-10)last.push(end)
     else missing.push([start,end])
    }
   }
  }
  const fraction=length?covered/length:0
  // Require a meaningful stretch: 50 m, or half of a street shorter than 100 m.
  const touched=covered>=Math.min(50,length*.5)-.001
  const status=fraction>=.95?'complete':touched?'partial':'untouched'
  if(status!=='complete'&&missing.length)missingRoads.features.push({type:'Feature',properties:{name:street.name,status,percent:Math.round(fraction*1000)/10},geometry:{type:'MultiLineString',coordinates:missing}})
  totalMeters+=length;coveredMeters+=covered
  return {name:street.name,percent:Math.round(fraction*1000)/10,status,coveredMeters:covered,lengthMeters:length} as StreetCoverage['streets'][number]
 })
 const complete=streets.filter(s=>s.status==='complete').length,partial=streets.filter(s=>s.status==='partial').length,untouched=streets.length-complete-partial
 return {missingRoads,total:streets.length,runOn:complete+partial,untouched,complete,partial,outstanding:partial+untouched,streetPercent:streets.length?100*(complete+partial)/streets.length:0,lengthPercent:totalMeters?100*coveredMeters/totalMeters:0,coveredMiles:coveredMeters/1609.344,totalMiles:totalMeters/1609.344,gpsRuns,latestDate,sourceTimestamp:inventory.sourceTimestamp,streets}
}
