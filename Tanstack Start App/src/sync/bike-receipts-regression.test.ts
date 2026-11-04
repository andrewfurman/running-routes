import test from 'node:test'
import assert from 'node:assert/strict'
import {withReceiptTrips,withCitiRoutes,fallbackTracks} from '../components/citi-route-bundle.ts'
import {activityCaptionLines,averagePaceLabel,requestedRun,gpsActivitySummary} from '../components/activity-summary.ts'
import {activitySport} from '../components/activity-navigation.ts'
import {receiptRouteProperties,type ReceiptTrip} from './bike-receipts.ts'
import {cyclingCoordinates,routePair} from './citi-bike-routing.ts'
import type {FeatureCollection} from '../components/types'
const receiptId='receipt-0123456789abcdef0123'
const receipt:ReceiptTrip={id:receiptId,matchStatus:'new',provider:'JUMP',source:'Bike receipt',city:'Seattle',start:'2019-05-10T16:08:00Z',end:'2019-05-10T16:19:00Z',timeZone:'America/Los_Angeles',distanceMeters:1609.344,elapsedSeconds:660,receiptDurationSeconds:600,timestampPrecision:'minute',startCoordinates:null,endCoordinates:null,startAddress:'100 Example Street, Seattle, WA',endAddress:'200 Example Avenue, Seattle, WA'}
const source:FeatureCollection={type:'FeatureCollection',features:[{type:'Feature',properties:{activity_id:'42',activity_type:'Ride',distance_meters:2000},geometry:{type:'LineString',coordinates:[[-122.3,47.6],[-122.31,47.61]]}},{type:'Feature',properties:{activity_id:'citi-existing',activity_type:'Ride',geometry_source:'station_endpoints',distance_meters:null},geometry:{type:'MultiPoint',coordinates:[[-74,40.7],[-73.99,40.71]]}}]}
function routeBundle(coordinates:number[][]=[[-122.3,47.6],[-122.305,47.605],[-122.31,47.61]]):FeatureCollection{return {type:'FeatureCollection',features:[{type:'Feature',properties:receiptRouteProperties(receipt),geometry:{type:'LineString',coordinates}}]}}
function database(){const rows=new Map<string,{coordinates:string;expires_at:number}>();const db={prepare(sql:string){let args:any[]=[];const statement={bind(...v:any[]){args=v;return statement},async all<T>(){return {results:(rows.has(args[0])?[rows.get(args[0])!]:[]) as T[]}},async run(){if(sql.startsWith('INSERT'))rows.set(args[0],{coordinates:args[1],expires_at:args[2]});if(sql.startsWith('DELETE'))rows.delete(args[0]);return {}}};return statement},async batch(){return []}};return {db,rows}}
test('receipt bundle merge is idempotent and preserves recorded Strava GPS and mileage',()=>{
 const bundle=routeBundle();bundle.features.push(bundle.features[0]);const once=withReceiptTrips(source,bundle),twice=withReceiptTrips(once,bundle)
 assert.equal(once.features.length,3);assert.equal(twice,once);assert.equal(once.features[0],source.features[0]);assert.equal(source.features.length,2)
 assert.deepEqual(once.features[2].geometry,{type:'MultiPoint',coordinates:[[-122.3,47.6],[-122.31,47.61]]})
 assert.equal(once.features[2].properties.distance_meters,1609.344);assert.equal(gpsActivitySummary(once)?.count,3)
 const displayed=withCitiRoutes(once,bundle);assert.equal(displayed.features[2].geometry.type,'LineString');assert.equal(displayed.features[0],source.features[0]);assert.equal(displayed.features[2].properties.distance_meters,1609.344)
})
test('same-address receipt draws a single endpoint, never a fabricated loop or extra ride',()=>{
 const bundle=routeBundle([[-122.3,47.6],[-122.3,47.6]])
 const displayed=withCitiRoutes(withReceiptTrips(source,bundle),bundle)
 assert.deepEqual(displayed.features[2].geometry,{type:'MultiPoint',coordinates:[[-122.3,47.6]]})
 assert.equal(displayed.features.length,3)
})
test('OpenStreetMap fallback excludes receipt-derived Google paths and endpoints while keeping actual GPS and original Citi stations',()=>{
 const displayed=withCitiRoutes(withReceiptTrips(source,routeBundle()),routeBundle())
 const fallback=fallbackTracks(displayed)
 assert.deepEqual(fallback.features,source.features);assert.equal(displayed.features.length,3)
 assert.equal(fallback.features.some(f=>f.properties.receipt_id),false)
})
test('receipt captions use local trip timezone and receipt duration for pace without altering recorded distance',()=>{
 const props=receiptRouteProperties(receipt)
 assert.deepEqual(activityCaptionLines(props),{stats:'1.0 miles at 10:00 per mile',time:'9:08 am to 9:19 am'})
 assert.equal(averagePaceLabel({...props,moving_seconds:540}),'9:00 /mi')
 assert.equal(props.distance_meters,1609.344)
 assert.deepEqual(activityCaptionLines({...props,time_zone:'Europe/Rome',start_time_utc:'2025-07-18T00:19:00Z',elapsed_seconds:1560}).time,'2:19 am to 2:45 am')
 const unknown=activityCaptionLines({...props,provider:'Divvy',distance_meters:null,receipt_duration_seconds:600})
 assert.equal(unknown.stats,'Divvy bike');assert.equal(unknown.time,'9:08 am to 9:19 am')
})
test('receipt links are accepted and open in Rides before the temporary receipt bundle loads',()=>{
 assert.equal(requestedRun('?activity='+receiptId),receiptId)
 assert.equal(activitySport(receiptId,[],{type:'FeatureCollection',features:[]}),'bikes')
 assert.equal(requestedRun('?activity=receipt-not-a-valid-fingerprint'),undefined)
})
test('receipt route properties contain selected ride facts rather than private email/account fields',()=>{
 const props=receiptRouteProperties({...receipt,emailBody:'not public',emailId:'123',paymentMethod:'not public'} as ReceiptTrip&{emailBody:string;emailId:string;paymentMethod:string})
 assert.equal(props.receipt_id,receiptId);assert.equal(props.time_zone,'America/Los_Angeles');assert.equal(props.receipt_duration_seconds,600)
 assert.equal('emailBody' in props,false);assert.equal('emailId' in props,false);assert.equal('paymentMethod' in props,false)
})
test('international receipt addresses are sent intact without a New York station-name suffix',()=>{
 assert.deepEqual(routePair({...receipt,startAddress:'33 Am Friedrichshain, Berlin, Germany',endAddress:'16 Alte Schönhauser Straße, Berlin, Germany'}),{origin:{address:'33 Am Friedrichshain, Berlin, Germany'},destination:{address:'16 Alte Schönhauser Straße, Berlin, Germany'}})
 assert.deepEqual(routePair({...receipt,startAddress:'Via Orefici 2, Milano, Italy',endAddress:'Via Guglielmo Silva 36, Milano, Italy'}).origin,{address:'Via Orefici 2, Milano, Italy'})
})
test('same-address rental geocodes one point once and uses the temporary cache on repeats',async()=>{
 const {db,rows}=database();let calls=0
 const same={...receipt,endAddress:'  100 EXAMPLE STREET, SEATTLE, WA  '}
 const fetcher:typeof fetch=async input=>{calls++;const url=new URL(String(input));assert.equal(url.hostname,'maps.googleapis.com');assert.equal(url.pathname,'/maps/api/geocode/json');assert.equal(url.searchParams.get('address'),receipt.startAddress);return Response.json({results:[{geometry:{location:{lat:47.6,lng:-122.3}}}]})}
 const first=await cyclingCoordinates(same,db,'test-key',fetcher,1000)
 assert.deepEqual(first,[[-122.3,47.6],[-122.3,47.6]])
 assert.deepEqual(await cyclingCoordinates(same,db,'test-key',fetcher,2000),first);assert.equal(calls,1);assert.equal(rows.size,1)
 assert.equal([...rows.values()][0].expires_at,1000+28*86400000)
})
