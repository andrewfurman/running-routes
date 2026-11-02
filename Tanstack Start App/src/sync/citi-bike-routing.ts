import {decodePolyline} from './strava-sync.ts'
import type {RunDatabase} from './types'
type Point=[number,number]
export interface CitiTrip {id:string;matchStatus:string;startCoordinates:number[]|null;endCoordinates:number[]|null;startStation?:string;endStation?:string}
const TTL=28*86400000
function waypoint(point:number[]|null,name?:string){if(point?.length===2)return {location:{latLng:{latitude:point[1],longitude:point[0]}}};if(name)return {address:`${name}, New York, NY`};throw Error('Missing station')}
export function routePair(trip:CitiTrip){return {origin:waypoint(trip.startCoordinates,trip.startStation),destination:waypoint(trip.endCoordinates,trip.endStation)}}
export async function routeKey(trip:CitiTrip){const bytes=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(JSON.stringify(routePair(trip))));return [...new Uint8Array(bytes)].map(x=>x.toString(16).padStart(2,'0')).join('')}
export async function purgeCitiRoutes(db:RunDatabase|undefined,now=Date.now()){if(db)await db.prepare('DELETE FROM citi_route_cache WHERE expires_at <= ?').bind(now).run()}
const pending=new Map<string,Promise<Point[]>>()
export async function cyclingCoordinates(trip:CitiTrip,db:RunDatabase,key:string,fetcher:typeof fetch=fetch,now=Date.now()):Promise<Point[]>{
 if(trip.startCoordinates&&trip.endCoordinates&&trip.startCoordinates[0]===trip.endCoordinates[0]&&trip.startCoordinates[1]===trip.endCoordinates[1])return []
 const pair=await routeKey(trip)
 const cached=await db.prepare('SELECT coordinates,expires_at FROM citi_route_cache WHERE pair_key=?').bind(pair).all<{coordinates:string;expires_at:number}>();const row=cached.results[0]
 if(row&&row.expires_at>now)return JSON.parse(row.coordinates)
 if(row)await db.prepare('DELETE FROM citi_route_cache WHERE pair_key=?').bind(pair).run()
 if(pending.has(pair))return pending.get(pair)!
 const request=(async()=>{
  const response=await fetcher('https://routes.googleapis.com/directions/v2:computeRoutes',{method:'POST',headers:{'Content-Type':'application/json','X-Goog-Api-Key':key,'X-Goog-FieldMask':'routes.polyline.encodedPolyline'},body:JSON.stringify({...routePair(trip),travelMode:'BICYCLE'})})
  if(!response.ok)throw Error(`Cycling directions unavailable (${response.status})`)
  const body=await response.json() as {routes?:{polyline?:{encodedPolyline?:string}}[]};const encoded=body.routes?.[0]?.polyline?.encodedPolyline;if(!encoded)throw Error('No cycling route found')
  const coordinates=decodePolyline(encoded);if(coordinates.length<2)throw Error('No cycling route found')
  await db.prepare('INSERT INTO citi_route_cache(pair_key,coordinates,expires_at) VALUES(?,?,?) ON CONFLICT(pair_key) DO UPDATE SET coordinates=excluded.coordinates,expires_at=excluded.expires_at').bind(pair,JSON.stringify(coordinates),now+TTL).run()
  return coordinates
 })();pending.set(pair,request)
 try{return await request}finally{pending.delete(pair)}
}
export async function citiRouteBundle(trips:CitiTrip[],db:RunDatabase,key:string,fetcher:typeof fetch=fetch,now=Date.now()){
 const rentals=trips.filter(t=>t.matchStatus==='new');const keys=await Promise.all(rentals.map(routeKey))
 const read=async()=>new Map((await db.prepare('SELECT pair_key,coordinates,expires_at FROM citi_route_cache WHERE expires_at > ?').bind(now).all<{pair_key:string;coordinates:string;expires_at:number}>()).results.map(r=>[r.pair_key,r]))
 let rows=await read();const missing=new Map<string,CitiTrip>()
 rentals.forEach((trip,i)=>{const same=trip.startCoordinates&&trip.endCoordinates&&trip.startCoordinates[0]===trip.endCoordinates[0]&&trip.startCoordinates[1]===trip.endCoordinates[1];if(!same&&!rows.has(keys[i]))missing.set(keys[i],trip)})
 if(missing.size){const jobs=[...missing.values()];let next=0;const work=async()=>{while(next<jobs.length){const trip=jobs[next++];try{await cyclingCoordinates(trip,db,key,fetcher,now)}catch{/* Return available paths together; unavailable rentals retain their endpoints. */}}};await Promise.all(Array.from({length:4},work));rows=await read()}
 let expiresAt=now+TTL;const features: {type:'Feature';properties:{activity_id:string};geometry:{type:'LineString';coordinates:Point[]}}[]=[];let unavailable=0
 rentals.forEach((trip,i)=>{const row=rows.get(keys[i]);if(!row){if(missing.has(keys[i]))unavailable++;return}const coordinates=JSON.parse(row.coordinates) as Point[];if(coordinates.length<2)return;expiresAt=Math.min(expiresAt,row.expires_at);features.push({type:'Feature',properties:{activity_id:trip.id},geometry:{type:'LineString',coordinates}})})
 return {type:'FeatureCollection' as const,features,expiresAt:unavailable?Math.min(expiresAt,now+60000):expiresAt,unavailable}
}
