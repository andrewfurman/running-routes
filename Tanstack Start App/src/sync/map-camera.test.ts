import test from 'node:test'
import assert from 'node:assert/strict'
import {cameraForPoints,cameraFrame,createCameraFlight} from '../components/map-camera.ts'
import {activityMapInsets} from '../components/map-framing.ts'
test('camera fits above a phone card and planned context adds less than a quarter zoom level',()=>{
 const ps:[number,number][]=[[-75.32,39.97],[-75.30,39.98]],padding=activityMapInsets(390,650,430)
 const normal=cameraForPoints(ps,390,650,padding)!,context=cameraForPoints(ps,390,650,padding,true)!
 assert.ok(normal.lat<39.975);assert.ok(normal.zoom-context.zoom<=.21);assert.ok(normal.zoom-context.zoom>=0)
 assert.equal(cameraForPoints([],390,650,30),undefined)
 assert.doesNotThrow(()=>cameraForPoints(Array.from({length:200000},()=>ps[0]),390,650,30))
})
test('route flight moves continuously with a small arc and shortest longitude direction',()=>{
 const from={lng:-75.33,lat:39.97,zoom:15},to={lng:-75.29,lat:39.99,zoom:15},mid=cameraFrame(from,to,.5)
 assert.ok(mid.lng>from.lng&&mid.lng<to.lng);assert.ok(mid.lat>from.lat&&mid.lat<to.lat);assert.ok(mid.zoom>=14.85&&mid.zoom<15)
 assert.equal(cameraFrame(from,to,1).zoom,to.zoom);assert.ok(Math.abs(cameraFrame({lng:179,lat:0,zoom:10},{lng:-179,lat:0,zoom:10},.5).lng)>179)
})
test('rapid paging cancels the old flight and reduced motion applies the final camera immediately',()=>{
 let camera={lng:-75.3,lat:40,zoom:15},id=0;const frames=new Map<number,FrameRequestCallback>()
 const flight=createCameraFlight(()=>camera,next=>{camera=next},fn=>{frames.set(++id,fn);return id},id=>{frames.delete(id)})
 const advance=(now:number)=>{const callbacks=[...frames.values()];frames.clear();callbacks.forEach(fn=>fn(now))}
 const first={lng:-75.2,lat:40.1,zoom:15},second={lng:-75.4,lat:39.9,zoom:14}
 flight.fly(first);advance(0);advance(360);assert.notEqual(camera.lng,first.lng)
 flight.fly(second);assert.equal(frames.size,1);advance(400);advance(1120);assert.deepEqual(camera,second);assert.equal(frames.size,0)
 flight.fly(first,true);assert.deepEqual(camera,first);assert.equal(frames.size,0)
 flight.fly(second);flight.cancel();assert.equal(frames.size,0)
})
