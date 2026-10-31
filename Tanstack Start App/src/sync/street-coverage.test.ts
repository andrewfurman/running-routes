import test from 'node:test'
import assert from 'node:assert/strict'
import {calculateStreetCoverage} from '../components/street-coverage.ts'
import type {StreetInventory} from '../components/street-coverage.ts'
import type {FeatureCollection,Position} from '../components/types'
const p=(x:number,y:number):Position=>[-75.3+x/(111195*Math.cos(40*Math.PI/180)),40+y/111195]
const inventory:StreetInventory={bounds:[-75.31,39.99,-75.29,40.01],streets:[{name:'First',lengthMeters:100,lines:[[p(0,0),p(100,0)]]},{name:'Second',lengthMeters:100,lines:[[p(0,100),p(100,100)]]},{name:'Third',lengthMeters:100,lines:[[p(0,200),p(100,200)]]}]}
const track=(coordinates:Position[]|Position[][],type='Run',geometry='LineString'):FeatureCollection=>({type:'FeatureCollection',features:[{type:'Feature',properties:{activity_id:'a',activity_type:type,date:'2026-10-31'},geometry:{type:geometry,coordinates}}]})
test('street counts distinguish complete, partial and untouched with a consistent denominator',()=>{const tracks=track([[p(0,0),p(100,0)],[p(0,100),p(35,100)]],'Run','MultiLineString');const r=calculateStreetCoverage(inventory,tracks);assert.equal(r.total,3);assert.equal(r.complete,1);assert.equal(r.partial,1);assert.equal(r.untouched,1);assert.equal(r.runOn,2);assert.equal(r.outstanding,2);assert.equal(r.complete+r.outstanding,r.total)})
test('perpendicular intersection crossings do not complete or touch the street',()=>{const r=calculateStreetCoverage(inventory,track([p(50,-50),p(50,50)]));assert.equal(r.runOn,0);assert.equal(r.complete,0)})
test('bike rides never contribute running coverage',()=>{const r=calculateStreetCoverage(inventory,track([p(0,0),p(100,0)],'Ride'));assert.equal(r.runOn,0);assert.equal(r.gpsRuns,0)})
test('disconnected GPS segments and large recording gaps are not bridged',()=>{const r=calculateStreetCoverage(inventory,track([[p(-400,0),p(-350,0)],[p(350,0),p(400,0)]],'Run','MultiLineString'));assert.equal(r.runOn,0);const gap=calculateStreetCoverage(inventory,track([p(-100,0),p(300,0)]));assert.equal(gap.runOn,0)})
test('nearby traces outside the 20 metre tolerance are excluded',()=>{const r=calculateStreetCoverage(inventory,track([p(0,25),p(100,25)]));assert.equal(r.runOn,0)})

test('unfinished map excludes completed streets and the covered part of a partial street',()=>{
 const r=calculateStreetCoverage(inventory,track([[p(0,0),p(100,0)],[p(0,100),p(35,100)]],'Run','MultiLineString'))
 assert.deepEqual(r.missingRoads.features.map(f=>f.properties.name),['Second','Third'])
 const partial=r.missingRoads.features.find(f=>f.properties.name==='Second')!
 assert.equal(partial.properties.status,'partial')
 // With the 20m GPS tolerance, the uncovered part starts at 60m.
 assert.ok(Math.abs(partial.geometry.coordinates[0][0][0]-p(60,100)[0])<1e-8)
 assert.deepEqual(partial.geometry.coordinates[0].at(-1),p(100,100))
 assert.equal(r.missingRoads.features.some(f=>f.properties.name==='First'),false)
})
test('missing sections do not bridge covered gaps or disconnected street lines',()=>{
 const streets:StreetInventory={...inventory,streets:[{name:'Split',lengthMeters:200,lines:[[p(0,0),p(100,0)],[p(200,0),p(300,0)]]}]}
 const r=calculateStreetCoverage(streets,track([p(40,0),p(60,0)]))
 const lines=r.missingRoads.features[0].geometry.coordinates
 assert.equal(lines.length,3)
 assert.deepEqual(lines[2][0],p(200,0))
 assert.ok(lines.every((line:Position[])=>line.at(-1)![0]-line[0][0]<=p(100,0)[0]-p(0,0)[0]+1e-9))
})
