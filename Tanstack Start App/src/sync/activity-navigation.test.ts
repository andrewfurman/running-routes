import test from 'node:test'
import assert from 'node:assert/strict'
import {activitySport} from '../components/activity-navigation.ts'
import type {SyncedRun} from './types'
const run={activityId:'run',sportType:'Run'} as SyncedRun,ride={activityId:'ride',sportType:'Ride'} as SyncedRun
test('activity links resolve their own sport rather than the default tab',()=>{assert.equal(activitySport('ride',[run,ride]),'bikes');assert.equal(activitySport('run',[run,ride]),'runs');assert.equal(activitySport('citi-0123456789abcdef0123',[]),'bikes');assert.equal(activitySport('old-ride',[],{type:'FeatureCollection',features:[{type:'Feature',properties:{activity_id:'old-ride'},geometry:{type:'LineString',coordinates:[]}}]}),'bikes');assert.equal(activitySport('unknown',[]),'runs')})
