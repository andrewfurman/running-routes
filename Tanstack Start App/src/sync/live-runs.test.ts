import test from 'node:test'
import assert from 'node:assert/strict'
import {mergeSyncedTracks,mergeSyncedEvents} from '../components/live-runs.ts'
import type {FeatureCollection} from '../components/types'
import type {SyncedRun} from './types'
const base:FeatureCollection={type:'FeatureCollection',features:[{type:'Feature',properties:{activity_id:'1',activity_type:'Run'},geometry:{type:'LineString',coordinates:[[0,0],[.1,.1],[.2,.2]]}}]}
const run=(activityId:string):SyncedRun=>({activityId,date:'2026-11-01T03:30:00Z',distanceMeters:5000,distanceSource:'strava_api',sportType:'Run',movingSeconds:1500,elapsedSeconds:1600,geometry:{type:'LineString',coordinates:[[0,0],[.2,.2]]}})
test('runtime imports deduplicate IDs and preserve existing detailed GPS',()=>{const result=mergeSyncedTracks(base,[run('1'),run('2')]);assert.equal(result.features.length,2);assert.deepEqual(result.features[0].geometry,base.features[0].geometry);assert.equal(result.features[0].properties.distance_meters,5000);assert.equal(base.features[0].properties.distance_meters,undefined)})
test('runs without GPS update calendar data without adding fake map lines',()=>{const r=run('2');r.geometry=null;assert.equal(mergeSyncedTracks(base,[r]).features.length,1);const events=mergeSyncedEvents([], [r]);assert.equal(events.length,1);assert.equal(events[0].start,'2026-10-31');assert.equal(events[0].end,'2026-11-01')})
test('calendar reruns keep one entry per activity and retain future plans',()=>{const events=mergeSyncedEvents([{id:'plan-1',title:'Grove Place',start:'2026-11-04',type:'planned'}],[run('2')]);const updated=mergeSyncedEvents(events,[run('2')]);assert.equal(updated.length,2);assert.equal(updated.filter(e=>e.id==='plan-1').length,1)})
