import test from 'node:test'
import assert from 'node:assert/strict'
import {historyAreas} from '../components/scheduled-days.ts'
import type {FeatureCollection} from '../components/types'
const feature=(id:string,center:[number,number],meters?:number)=>({type:'Feature' as const,properties:{activity_id:id,...meters===undefined?{}:{distance_meters:meters}},geometry:{type:'LineString',coordinates:[center,[center[0]+.001,center[1]+.001]]}})
test('city mileage sums recorded activity distances, deduplicates IDs and preserves separate areas',()=>{const collection:FeatureCollection={type:'FeatureCollection',features:[feature('a',[-75.3,40],1609.344),feature('b',[-75.31,40],3218.688),feature('a',[-75.3,40],1609.344),feature('c',[-122.3,47.6],8046.72)]};const areas=historyAreas(collection);assert.equal(areas.length,2);assert.equal(areas[0].count,2);assert.equal(areas[0].miles,3);assert.equal(areas[1].miles,5);assert.ok(areas.every(a=>a.distanceMissing===0));assert.equal(collection.features.length,4)})
test('missing mileage is marked incomplete rather than fabricated from simplified GPS',()=>{const areas=historyAreas({type:'FeatureCollection',features:[feature('a',[-75.3,40],1609.344),feature('b',[-75.31,40])]});assert.equal(areas[0].miles,1);assert.equal(areas[0].distanceMissing,1)})
test('previously coordinate-only regions use cached place names',()=>{const areas=historyAreas({type:'FeatureCollection',features:[feature('a',[-77.56,43.13],1000),feature('b',[-109.58,38.6],2000)]});assert.ok(areas.some(a=>a.label==='Rochester, NY'));assert.ok(areas.some(a=>a.label==='Moab, UT'));assert.ok(areas.every(a=>!a.label.includes('°')))})

test('New York and Ridgefield stay separate even though the older regional name was shared',()=>{const areas=historyAreas({type:'FeatureCollection',features:[feature('a',[-74.01,40.71],1609.344),feature('b',[-73.5,41.28],3218.688)]});assert.equal(areas.length,2);assert.equal(areas.find(a=>a.label==='New York City, NY')?.miles,1);assert.equal(areas.find(a=>a.label==='Ridgefield, CT')?.miles,2)})
test('Mainline towns combine while other Philadelphia suburbs remain separate',()=>{const places:[string,[number,number]][]=[['Havertown, PA',[-75.31,39.98]],['Ardmore, PA',[-75.29,40.007]],['Narberth, PA',[-75.262,40.009]],['Willow Grove, PA',[-75.14,40.18]],['Coopersburg, PA',[-75.39,40.51]],['Philadelphia, PA',[-75.16,39.95]]];const areas=historyAreas({type:'FeatureCollection',features:places.map(([_,point],i)=>feature(String(i),point,1609.344))});assert.equal(areas.length,4);assert.equal(areas.find(a=>a.label==='Mainline, PA')?.miles,3);for(const [label]of places.slice(3))assert.equal(areas.find(a=>a.label===label)?.miles,1);assert.equal(areas.reduce((n,a)=>n+a.count,0),places.length)})
test('unresolved distant regions stay separate instead of fitting the whole world',()=>{const areas=historyAreas({type:'FeatureCollection',features:[feature('a',[-30,0],1000),feature('b',[80,0],2000)]});assert.equal(areas.length,2)})

test('nearby Narberth and Ardmore activities join Mainline while distant cities stay separate',()=>{const areas=historyAreas({type:'FeatureCollection',features:[feature('a',[-75.25295,40.00334],1609.344),feature('b',[-75.27394,40.00241],1609.344),feature('c',[-75.26312,39.99743],1609.344),feature('d',[-75.27417,40.00553],1609.344),feature('e',[126.98,37.5],1609.344)]});assert.equal(areas.find(a=>a.label==='Mainline, PA')?.count,4);assert.equal(areas.find(a=>a.label==='South Korea')?.count,1);assert.equal(areas.reduce((n,a)=>n+a.count,0),5);assert.equal(areas.some(a=>a.label==='Other Havertown / Philadelphia area'),false)})

test('the residual Wilton run joins the requested Ridgefield area',()=>{const areas=historyAreas({type:'FeatureCollection',features:[feature('wilton',[-73.46903,41.24442],1609.344)]});assert.equal(areas[0].label,'Ridgefield, CT');assert.equal(areas[0].count,1)})

test('Atlantic Ocean coastal activities combine without losing counts or mileage',()=>{const areas=historyAreas({type:'FeatureCollection',features:[feature('ocean-a',[-74.55631, 34.59351],1609.344),feature('ocean-b',[-70.6196, 40.41556],3218.688)]});assert.equal(areas.length,1);assert.equal(areas[0].label,'Atlantic Ocean');assert.equal(areas[0].count,2);assert.equal(areas[0].miles,3)})

test('station endpoints count once in NYC without invented mileage',()=>{
 const areas=historyAreas({type:'FeatureCollection',features:[{type:'Feature',properties:{activity_id:'citi-one',distance_meters:null},geometry:{type:'MultiPoint',coordinates:[[-73.98,40.75],[-73.97,40.76]]}}]})
 assert.equal(areas.length,1);assert.equal(areas[0].label,'New York City, NY');assert.equal(areas[0].count,1);assert.equal(areas[0].miles,0);assert.equal(areas[0].distanceMissing,1)
})

test('city drill-down retains exactly the counted activities, including whole cross-boundary runs and rides',()=>{
 for(const sport of ['Run','Ride']){
  const crossing=feature('narberth',[-75.262,40.009],3218.688);crossing.properties={...crossing.properties,activity_type:sport} as any
  crossing.geometry.coordinates=[[-75.31,39.98],[-75.262,40.009],[-75.2621,40.0091],[-75.2622,40.0092],[-75.31,39.98]]
  const ardmore=feature('ardmore',[-75.29,40.007],1609.344),havertown=feature('havertown',[-75.31,39.98],1609.344)
  const areas=historyAreas({type:'FeatureCollection',features:[crossing,ardmore,havertown,crossing]})
  const narberth=areas.find(a=>a.label==='Mainline, PA')!
  assert.deepEqual(narberth.activities.map(f=>f.properties.activity_id),['narberth','ardmore','havertown'])
  assert.equal(narberth.count,narberth.activities.length);assert.equal(narberth.miles,4)
  assert.equal(narberth.activities[0],crossing);assert.deepEqual(narberth.activities[0].geometry.coordinates[0],[-75.31,39.98])
  assert.deepEqual(areas.flatMap(a=>a.activities.map(f=>f.properties.activity_id)).sort(),['ardmore','havertown','narberth'])
 }
})
test('combined ocean area keeps every counted route for the map',()=>{
 const a=feature('ocean-a',[-74.55631,34.59351],1609.344),b=feature('ocean-b',[-70.6196,40.41556],3218.688)
 const [area]=historyAreas({type:'FeatureCollection',features:[a,b,a]});assert.deepEqual(area.activities,[a,b]);assert.equal(area.activities.length,area.count)
})

test('Mainline combines all four requested towns and preserves missing mileage and drill-down routes',()=>{
 const features=[feature('h',[-75.31,39.98],1609.344),feature('n',[-75.262,40.009],3218.688),feature('b',[-75.32,40.024]),feature('a',[-75.29,40.007],1609.344),feature('philly',[-75.16,39.95],8046.72)]
 const areas=historyAreas({type:'FeatureCollection',features:[...features,features[0]]}),group=areas.find(a=>a.label==='Mainline, PA')!
 assert.equal(group.count,4);assert.equal(group.miles,4);assert.equal(group.distanceMissing,1);assert.deepEqual(group.activities.map(f=>f.properties.activity_id).sort(),['a','b','h','n']);assert.equal(areas.length,2);assert.equal(areas.reduce((n,a)=>n+a.count,0),5)
})

test('Broomall joins Mainline for runs and rides without changing the underlying routes',()=>{
 for(const activity_type of ['Run','Ride']){
 const a=feature('broomall',[-75.35658,39.9815],3218.688),b=feature('havertown',[-75.31,39.98],1609.344);a.properties={...a.properties,activity_type} as any;b.properties={...b.properties,activity_type} as any
 const [area]=historyAreas({type:'FeatureCollection',features:[a,b,a]});assert.equal(area.label,'Mainline, PA');assert.equal(area.count,2);assert.equal(area.miles,3);assert.deepEqual(area.activities,[a,b])
 }
})

test('Penn Wynne combines with Mainline while Drexel Hill remains separate',()=>{
 const a=feature('penn-wynne',[-75.275,39.986],3218.688),b=feature('havertown',[-75.31,39.98],1609.344),c=feature('drexel-hill',[-75.292,39.947],1609.344)
 const areas=historyAreas({type:'FeatureCollection',features:[a,b,c,a]}),mainline=areas.find(a=>a.label==='Mainline, PA')!
 assert.equal(mainline.count,2);assert.equal(mainline.miles,3);assert.deepEqual(mainline.activities,[a,b]);assert.equal(areas.length,2);assert.equal(areas.find(a=>a.label==='Drexel Hill, PA')?.count,1)
})

test('nearby requested city groups combine their exact activity membership and miles',()=>{
 const f=[feature('ridgefield',[-73.5,41.28],1609.344),feature('wilton',[-73.46903,41.24442],1609.344),feature('horsham',[-75.14,40.18],1609.344),feature('maple-glen',[-75.18046,40.179],1609.344)]
 const areas=historyAreas({type:'FeatureCollection',features:f});assert.equal(areas.length,2);assert.equal(areas.find(a=>a.label==='Ridgefield, CT')?.count,2);assert.equal(areas.find(a=>a.label==='Willow Grove, PA')?.miles,2);assert.equal(areas.flatMap(a=>a.activities).length,4)
})
