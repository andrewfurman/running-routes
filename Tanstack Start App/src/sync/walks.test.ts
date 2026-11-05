import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import {supportedSport,sportsFor} from './sports.ts'
import {activitySport} from '../components/activity-navigation.ts'
import {latestWalkId,latestRunId} from '../components/activity-summary.ts'
import {calculateStreetCoverage} from '../components/street-coverage.ts'
test('walk import retains all records, unique GPS IDs and selected public fields',()=>{
 const records=JSON.parse(fs.readFileSync(new URL('../../../raw-data/walks/activities.json',import.meta.url),'utf8')).walks,tracks=JSON.parse(fs.readFileSync(new URL('../../../raw-data/walks/tracks.geojson',import.meta.url),'utf8'))
 const summary=JSON.parse(fs.readFileSync(new URL('../../../raw-data/walks/summary.json',import.meta.url),'utf8'));assert.equal(records.length,summary.walkRecords);assert.equal(tracks.features.length,summary.mappedWalks);assert.equal(new Set(records.map((r:any)=>r.activityId)).size,records.length)
 assert.ok(records.every((r:any)=>r.sportType==='Walk'));assert.ok(tracks.features.every((f:any)=>f.properties.activity_type==='Walk'&&!('description' in f.properties)&&!('heart_rate' in f.properties)))
 assert.ok(supportedSport('Walk'));assert.equal(sportsFor('runs').includes('Walk'),false);assert.equal(sportsFor('bikes').includes('Walk'),false)
 assert.equal(activitySport(records[0].activityId,records), 'walks');assert.ok(latestWalkId(tracks));assert.equal(latestRunId(tracks),undefined)
 const coverage=calculateStreetCoverage({bounds:[-180,-90,180,90],streets:[{name:'Test',lengthMeters:111,lines:[[[-75.3,40],[-75.299,40]]]}]},tracks)
 assert.equal(coverage.gpsRuns,0);assert.equal(coverage.runOn,0)
})

test('new walking classifications cannot leave the same activity on Runs or Rides',async()=>{
 const {mergeSportTracks}=await import('../components/live-runs.ts')
 const base={type:'FeatureCollection' as const,features:[{type:'Feature' as const,properties:{activity_id:'42',activity_type:'Run'},geometry:{type:'LineString',coordinates:[[-75.3,40],[-75.301,40.001]]}}]}
 const live=[{activityId:'42',sportType:'Walk',date:'2026-11-05',geometry:base.features[0].geometry,distanceMeters:1000,movingSeconds:500,elapsedSeconds:600,distanceSource:'strava_web'}] as any
 assert.equal(mergeSportTracks(base,live,'runs').features.length,0);assert.equal(mergeSportTracks(base,live,'bikes').features.length,0);assert.equal(mergeSportTracks({type:'FeatureCollection',features:[]},live,'walks').features.length,1)
})
