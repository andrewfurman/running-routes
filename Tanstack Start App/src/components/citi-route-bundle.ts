import type {FeatureCollection} from './types'
export type CitiRouteBundle=FeatureCollection&{expiresAt:number;unavailable:number}
export function createCitiRouteLoader(fetcher:typeof fetch=fetch,now=Date.now){
 let cached:CitiRouteBundle|undefined;let pending:Promise<CitiRouteBundle>|undefined
 return async()=>{
  if(cached&&cached.expiresAt>now())return cached
  if(pending)return pending
  pending=(async()=>{const response=await fetcher('/api/citi-bike-routes');if(!response.ok)throw Error('Cycling routes unavailable');const bundle=await response.json() as CitiRouteBundle;if(bundle.type!=='FeatureCollection'||!Array.isArray(bundle.features)||!Number.isFinite(bundle.expiresAt))throw Error('Invalid route bundle');cached=bundle;return bundle})()
  try{return await pending}finally{pending=undefined}
 }
}
export const loadCitiRouteBundle=createCitiRouteLoader()
export function withCitiRoutes(tracks:FeatureCollection,routes?:FeatureCollection):FeatureCollection{
 if(!routes)return tracks
 const paths=new Map(routes.features.map(f=>[String(f.properties.activity_id),f.geometry]))
 return {...tracks,features:tracks.features.map(f=>{const path=paths.get(String(f.properties.activity_id));return ['station_endpoints','receipt_endpoints'].includes(f.properties.geometry_source)&&path?{...f,geometry:path.type==='LineString'&&path.coordinates.every((p:number[])=>p[0]===path.coordinates[0][0]&&p[1]===path.coordinates[0][1])?{type:'MultiPoint',coordinates:[path.coordinates[0]]}:path}:f})}
}

// Google coordinates remain temporary in-memory route data, never a committed GPS trace.
export function withReceiptTrips(tracks:FeatureCollection,routes?:FeatureCollection):FeatureCollection{
 if(!routes)return tracks
 const ids=new Set(tracks.features.map(f=>String(f.properties.activity_id)))
 const added=routes.features.filter(f=>f.properties.receipt_id&&!ids.has(String(f.properties.activity_id))&&f.geometry.type==='LineString'&&f.geometry.coordinates.length>1&&Boolean(ids.add(String(f.properties.activity_id)))).map(f=>({...f,geometry:{type:'MultiPoint',coordinates:[f.geometry.coordinates[0],f.geometry.coordinates[f.geometry.coordinates.length-1]]}}))
 return added.length?{...tracks,features:[...tracks.features,...added]}:tracks
}
export function fallbackTracks(tracks:FeatureCollection):FeatureCollection{return {...tracks,features:tracks.features.filter(f=>f.properties.geometry_source!=='receipt_endpoints')}}
