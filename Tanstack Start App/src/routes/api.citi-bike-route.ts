import {createFileRoute} from '@tanstack/react-router'
import archive from '../../../raw-data/citi-bike/trips.json'
import {cyclingCoordinates} from '../sync/citi-bike-routing'
const trips=new Map(archive.trips.filter(t=>t.matchStatus==='new').map(t=>[t.id,t]))
export const Route=createFileRoute('/api/citi-bike-route')({server:{handlers:{GET:async({request})=>{
 const trip=trips.get(new URL(request.url).searchParams.get('id')||'');if(!trip)return new Response('Unknown trip',{status:404})
 const {env}=await import('cloudflare:workers');if(!env.GOOGLE_MAPS_API_KEY||!env.RUNS_DB)return new Response('Cycling directions not configured',{status:503})
 try{return Response.json({coordinates:await cyclingCoordinates(trip,env.RUNS_DB,env.GOOGLE_MAPS_API_KEY)},{headers:{'Cache-Control':'private, no-store'}})}catch{return new Response('Cycling directions unavailable; station endpoints are still shown',{status:502})}
}}}})
