import test from 'node:test'
import assert from 'node:assert/strict'
import {createCitiRouteLoader,withCitiRoutes} from '../components/citi-route-bundle.ts'
import type {FeatureCollection} from '../components/types'
test('one GeoJSON request is shared across concurrent and repeat map visits until expiry',async()=>{
 let calls=0,clock=0;const load=createCitiRouteLoader(async url=>{assert.equal(url,'/api/citi-bike-routes');calls++;return Response.json({type:'FeatureCollection',features:[],expiresAt:clock+1000,unavailable:0})},()=>clock)
 const [a,b]=await Promise.all([load(),load()]);assert.equal(a,b);assert.equal(calls,1);await load();assert.equal(calls,1);clock=1001;await load();assert.equal(calls,2)
})
test('cached geometry is applied together without changing Strava tracks, mileage or source data',()=>{
 const tracks:FeatureCollection={type:'FeatureCollection',features:[{type:'Feature',properties:{activity_id:'citi-one',geometry_source:'station_endpoints',distance_meters:null},geometry:{type:'MultiPoint',coordinates:[[1,2],[3,4]]}},{type:'Feature',properties:{activity_id:'strava-one',distance_meters:1000},geometry:{type:'LineString',coordinates:[[5,6],[7,8]]}}]}
 const routes:FeatureCollection={type:'FeatureCollection',features:[{type:'Feature',properties:{activity_id:'citi-one'},geometry:{type:'LineString',coordinates:[[1,2],[2,3],[3,4]]}},{type:'Feature',properties:{activity_id:'strava-one'},geometry:{type:'LineString',coordinates:[[0,0],[1,1]]}}]}
 const displayed=withCitiRoutes(tracks,routes);assert.equal(displayed.features[0].geometry.type,'LineString');assert.equal(tracks.features[0].geometry.type,'MultiPoint');assert.equal(displayed.features[0].properties.distance_meters,null);assert.equal(displayed.features[1],tracks.features[1]);assert.equal(withCitiRoutes(tracks),tracks)
})
