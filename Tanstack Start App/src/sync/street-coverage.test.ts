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
