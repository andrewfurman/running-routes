import {calculateStreetCoverage} from './street-coverage.ts'
import type {FeatureCollection,Position,Target} from './types'
export function lineMeters(line:Position[]){let meters=0;for(let i=1;i<line.length;i++)meters+=Math.hypot((line[i][0]-line[i-1][0])*111195*Math.cos(40*Math.PI/180),(line[i][1]-line[i-1][1])*111195);return meters}
export function lineMidpoint(line:Position[]):Position|undefined{const half=lineMeters(line)/2;let covered=0;for(let i=1;i<line.length;i++){const meters=lineMeters([line[i-1],line[i]]);if(meters&&covered+meters>=half){const f=(half-covered)/meters;return [line[i-1][0]+f*(line[i][0]-line[i-1][0]),line[i-1][1]+f*(line[i][1]-line[i-1][1])]}covered+=meters}return line[0]}
export function plannedLines(target:Target):Position[][]{return target.past?[]:target.missing_coordinates||[]}
export function plannedPoints(target:Target):Position[]{return [...plannedLines(target).flat(),...(target.navigation_coordinates?[target.navigation_coordinates]:[])]}
export function auditPlannedGaps(targets:Target[],tracks:FeatureCollection):Target[]{
 const pending=targets.filter(t=>!t.past&&t.target_coordinates.length>1)
 if(!pending.length)return targets.map(t=>({...t,missing_coordinates:[],missing_miles:0}))
 const points=pending.flatMap(t=>t.target_coordinates),xs=points.map(p=>p[0]),ys=points.map(p=>p[1])
 const audit=calculateStreetCoverage({bounds:[Math.min(...xs)-.001,Math.min(...ys)-.001,Math.max(...xs)+.001,Math.max(...ys)+.001],streets:pending.map((t,i)=>({name:String(i),lengthMeters:lineMeters(t.target_coordinates),lines:[t.target_coordinates]}))},tracks)
 const metadata=new Map(pending.map((t,i)=>{const lines=(audit.missingRoads.features.find(f=>f.properties.name===String(i))?.geometry.coordinates||[]) as Position[][];const sorted=[...lines].sort((a,b)=>lineMeters(b)-lineMeters(a));return [t,{missing_coordinates:sorted,missing_miles:sorted.reduce((n,l)=>n+lineMeters(l),0)/1609.344,gap_coverage_pct:audit.streets[i].percent,primary_gap_midpoint:sorted.length?lineMidpoint(sorted[0]):undefined}]}))
 return targets.map(t=>({...t,...(metadata.get(t)||{missing_coordinates:[],missing_miles:0})}))
}
