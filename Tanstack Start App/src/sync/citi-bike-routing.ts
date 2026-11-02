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
