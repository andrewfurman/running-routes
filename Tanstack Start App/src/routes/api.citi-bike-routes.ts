import {createFileRoute} from '@tanstack/react-router'
import archive from '../../../raw-data/citi-bike/trips.json'
import receipts from '../../../raw-data/bike-receipts/trips.json'
import {receiptRouteProperties,type ReceiptTrip} from '../sync/bike-receipts'
import {citiRouteBundle} from '../sync/citi-bike-routing'
export const Route=createFileRoute('/api/citi-bike-routes')({server:{handlers:{GET:async()=>{
 const {env}=await import('cloudflare:workers');if(!env.GOOGLE_MAPS_API_KEY||!env.RUNS_DB)return new Response('Cycling directions not configured',{status:503})
 try{const extra=(receipts as {trips:ReceiptTrip[]}).trips.filter(t=>t.matchStatus==='new');const metadata=new Map(extra.map(t=>[t.id,t]));const bundle=await citiRouteBundle([...archive.trips,...extra],env.RUNS_DB,env.GOOGLE_MAPS_API_KEY);return Response.json({...bundle,features:bundle.features.map(f=>metadata.has(f.properties.activity_id)?{...f,properties:receiptRouteProperties(metadata.get(f.properties.activity_id)!)}:f)},{headers:{'Cache-Control':'private, no-store'}})}catch{return new Response('Cycling routes unavailable',{status:503})}
}}}})
