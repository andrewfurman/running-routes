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
 return {...tracks,features:tracks.features.map(f=>{const path=paths.get(String(f.properties.activity_id));return f.properties.geometry_source==='station_endpoints'&&path?{...f,geometry:path}:f})}
}
