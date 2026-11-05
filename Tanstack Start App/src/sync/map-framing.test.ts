import test from 'node:test'
import assert from 'node:assert/strict'
import {activityMapInsets} from '../components/map-framing.ts'
test('historical route fits above the phone card rather than behind it',()=>{
 const padding=activityMapInsets(390,650,430)
 assert.ok(padding.bottom>220)
 const visibleBottom=650-padding.bottom
 assert.ok(visibleBottom<430)
 const center=(padding.top+visibleBottom)/2
 assert.ok(center<325)
 assert.equal(padding.left,padding.right)
})
test('map framing preserves a usable area on short screens and works without a card',()=>{
 const short=activityMapInsets(650,250,30)
 assert.ok(250-short.top-short.bottom>=120)
 const open=activityMapInsets(1280,700)
 assert.equal(open.top,open.bottom)
 assert.equal(open.left,open.right)
})

test('Havertown overview includes local recorded history rather than planned destinations or distant cities',async()=>{
 const {havertownOverviewPoints}=await import('../components/map-framing.ts')
 const local:[number,number]=[-75.31,39.98],seattle:[number,number]=[-122.3,47.6]
 const points=havertownOverviewPoints({type:'FeatureCollection',features:[{type:'Feature',properties:{activity_id:'local'},geometry:{type:'LineString',coordinates:[local,[-75.32,39.97]]}},{type:'Feature',properties:{activity_id:'seattle'},geometry:{type:'LineString',coordinates:[seattle,[-122.31,47.61]]}}]},{type:'Feature',geometry:{type:'Polygon',coordinates:[[[-75.34,39.95],[-75.27,39.95],[-75.27,40],[-75.34,40],[-75.34,39.95]]]},properties:{}})
 assert.ok(points.includes(local));assert.ok(!points.includes(seattle));assert.ok(points.every(p=>p[0]>-76&&p[0]<-75));assert.deepEqual(havertownOverviewPoints(),[])
})
