import test from 'node:test'
import assert from 'node:assert/strict'
import {cyclingCoordinates,purgeCitiRoutes,routeKey,routePair} from './citi-bike-routing.ts'
const trip={id:'citi-test',matchStatus:'new',startCoordinates:[-74,40.7],endCoordinates:[-73.98,40.75]}
function database(){const rows=new Map<string,{coordinates:string;expires_at:number}>();const db={prepare(sql:string){let args:any[]=[];const statement={bind(...v:any[]){args=v;return statement},async all<T>(){return {results:(rows.has(args[0])?[rows.get(args[0])!]:[]) as T[]}},async run(){if(sql.startsWith('INSERT'))rows.set(args[0],{coordinates:args[1],expires_at:args[2]});if(sql.includes('DELETE')&&sql.includes('pair_key'))rows.delete(args[0]);if(sql.includes('DELETE')&&sql.includes('expires_at'))for(const [key,row] of rows)if(row.expires_at<=args[0])rows.delete(key);return {}}};return statement},async batch(){return []}};return {db,rows}}
test('repeated station pairs share a temporary coordinate cache without adding mileage',async()=>{
 const {db,rows}=database();let calls=0;const fetcher:typeof fetch=async(_url,init)=>{calls++;assert.equal(JSON.parse(init!.body as string).travelMode,'BICYCLE');assert.equal((init!.headers as any)['X-Goog-FieldMask'],'routes.polyline.encodedPolyline');return Response.json({routes:[{polyline:{encodedPolyline:'_p~iF~ps|U_ulLnnqC_mqNvxq`@'}}]})}
 const points=await cyclingCoordinates(trip,db,'test-key',fetcher,1000);assert.equal(points.length,3);assert.deepEqual(await cyclingCoordinates({...trip,id:'second-rental'},db,'test-key',fetcher,2000),points);assert.equal(calls,1);assert.equal(rows.size,1)
 await purgeCitiRoutes(db,1000+28*86400000);assert.equal(rows.size,0)
})
test('missing historical station coordinates can route by its original station name',async()=>{
 const pair=routePair({...trip,endCoordinates:null,endStation:'Lexington Ave & E 26 St'});assert.deepEqual(pair.destination,{address:'Lexington Ave & E 26 St, New York, NY'});assert.notEqual(await routeKey(trip),await routeKey({...trip,startCoordinates:trip.endCoordinates,endCoordinates:trip.startCoordinates}))
})
test('failed directions do not populate the cache',async()=>{
 const {db,rows}=database();await assert.rejects(()=>cyclingCoordinates(trip,db,'test-key',async()=>new Response('no',{status:403})));assert.equal(rows.size,0)
})
test('same-station rentals do not invent a loop or call Google',async()=>{
 const {db}=database();assert.deepEqual(await cyclingCoordinates({...trip,endCoordinates:trip.startCoordinates},db,'test-key',async()=>{throw Error('must not fetch')}),[])
})
