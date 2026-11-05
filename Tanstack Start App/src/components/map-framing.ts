import type {FeatureCollection,Position} from './types'
export interface MapInsets {top:number;right:number;bottom:number;left:number}
/** Keep the selected route in the map area above the floating history card. */
export function activityMapInsets(width:number,height:number,dockTop?:number):MapInsets {
 const side=Math.min(60,Math.max(24,width*.08))
 const bottom=dockTop===undefined?side:Math.max(side,height-dockTop+side)
 return {top:side,right:side,bottom:Math.min(bottom,Math.max(side,height-side-120)),left:side}
}

/** Frame local running history, rather than the planned pins or worldwide tracks. */
export function havertownOverviewPoints(tracks?:FeatureCollection,boundary?:any):Position[]{
 const outline:Position[]=[]
 const collect=(value:any):void=>{if(!value)return;if(Array.isArray(value)){if(value.length>=2&&typeof value[0]==='number'&&typeof value[1]==='number')outline.push([value[0],value[1]]);else value.forEach(collect)}else if(value.features)value.features.forEach(collect);else collect(value.geometry||value.coordinates)}
 collect(boundary)
 let west=-75.39,east=-75.24,south=39.92,north=40.04
 if(outline.length){west=Infinity;east=-Infinity;south=Infinity;north=-Infinity;for(const [lng,lat] of outline){west=Math.min(west,lng-.01);east=Math.max(east,lng+.01);south=Math.min(south,lat-.01);north=Math.max(north,lat+.01)}}
 const local:Position[]=[]
 for(const f of tracks?.features||[]){const lines=f.geometry.type==='LineString'||f.geometry.type==='MultiPoint'?[f.geometry.coordinates]:f.geometry.coordinates;for(const line of lines)for(const p of line)if(p[0]>=west&&p[0]<=east&&p[1]>=south&&p[1]<=north)local.push(p)}
 return [...outline,...local]
}
