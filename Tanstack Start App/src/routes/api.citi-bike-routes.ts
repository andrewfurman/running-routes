import {createFileRoute} from '@tanstack/react-router'
import archive from '../../../raw-data/citi-bike/trips.json'
import {citiRouteBundle} from '../sync/citi-bike-routing'
export const Route=createFileRoute('/api/citi-bike-routes')({server:{handlers:{GET:async()=>{
 const {env}=await import('cloudflare:workers');if(!env.GOOGLE_MAPS_API_KEY||!env.RUNS_DB)return new Response('Cycling directions not configured',{status:503})
 try{return Response.json(await citiRouteBundle(archive.trips,env.RUNS_DB,env.GOOGLE_MAPS_API_KEY),{headers:{'Cache-Control':'private, no-store'}})}catch{return new Response('Cycling routes unavailable',{status:503})}
}}}})
