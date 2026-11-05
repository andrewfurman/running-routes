import {upcomingTargets,planDayKey} from '../components/scheduled-days.ts'
import test from 'node:test'
import assert from 'node:assert/strict'
import {auditPlannedGaps,plannedLines,plannedPoints,lineMidpoint,lineMeters} from '../components/planned-gaps.ts'
import type {Target,FeatureCollection,Position} from '../components/types'
const a:Position=[-75.31,39.98],b:Position=[-75.30,39.98]
const target:Target={street:'Test Road',date:'2026-11-09',number:1,target_label:'remaining section',target_coordinates:[a,b],navigation_address:'10 Test Rd',navigation_url:'',target_miles:.53}
const tracks=(points:Position[],type='Run'):FeatureCollection=>{const dense:Position[]=[];for(let i=1;i<points.length;i++){const steps=Math.ceil(lineMeters([points[i-1],points[i]])/100);for(let n=0;n<steps;n++){const f=n/steps;dense.push([points[i-1][0]+f*(points[i][0]-points[i-1][0]),points[i-1][1]+f*(points[i][1]-points[i-1][1])])}}dense.push(points[points.length-1]);return {type:'FeatureCollection',features:[{type:'Feature',properties:{activity_id:'one',activity_type:type},geometry:{type:'LineString',coordinates:dense}}]}}

test('covered middle is removed without bridging separate unfinished sections',()=>{
 const [result]=auditPlannedGaps([target],tracks([[-75.307,39.98],[-75.303,39.98]]))
 assert.equal(result.missing_coordinates?.length,2)
 assert.ok(result.missing_coordinates!.every(line=>line.every(p=>p[0]<-75.307||p[0]>-75.303)))
 assert.ok(result.missing_miles!<target.target_miles);assert.equal(result.target_coordinates,target.target_coordinates)
 assert.deepEqual(target.missing_coordinates,undefined)
 assert.ok(result.primary_gap_midpoint)
})
test('a covered street has no orange lines and a ride cannot complete a running target',()=>{
 assert.deepEqual(plannedLines(auditPlannedGaps([target],tracks([a,b]))[0]),[])
 const [rideOnly]=auditPlannedGaps([target],tracks([a,b],'Ride'));assert.equal(rideOnly.gap_coverage_pct,0);assert.equal(plannedLines(rideOnly).length,1)
 assert.ok(Math.abs(rideOnly.missing_miles!*1609.344-lineMeters([a,b]))<.01)
})
test('old geometry is never used as an unaudited full-street orange fallback',()=>{
 assert.deepEqual(plannedLines(target),[])
 assert.deepEqual(plannedLines({...target,past:true,missing_coordinates:[[a,b]]}),[])
 assert.deepEqual(lineMidpoint([a,b]),[-75.305,39.98])
 assert.deepEqual(plannedPoints({...target,missing_coordinates:[[a,b]],navigation_coordinates:a}),[a,b,a])
})

test('upcoming view excludes unscheduled options and uses only one calendar-week window with combined-day targets intact',()=>{
 const optional={...target,date:'2026-11-11',unscheduled:true},scheduled={...target,date:'2026-11-11'},combined={...scheduled,street:'Second Street'}
 const later=Array.from({length:9},(_,i)=>({...target,date:`2026-11-${String(i+12).padStart(2,'0')}`}))
 const result=upcomingTargets([optional,...later,scheduled,combined,{...target,past:true}],'2026-11-11')
 assert.equal(new Set(result.map(t=>t.date)).size,7);assert.equal(result.length,8);assert.deepEqual(result.slice(0,2),[scheduled,combined]);assert.equal(result.at(-1)?.date,'2026-11-17');assert.equal(upcomingTargets([optional],'2026-11-20').length,0);assert.equal(upcomingTargets([scheduled,...later],'2026-11-12').at(-1)?.date,'2026-11-18')
})

test('on-deck date picks the next scheduled unfinished day and ignores past and optional targets',async()=>{
 const {nextPlannedDate}=await import('../components/planned-gaps.ts')
 const target=(date:string,extra={})=>({date,missing_coordinates:[[[0,0],[1,1]]],...extra}) as any
 assert.equal(nextPlannedDate([target('2026-11-06'),target('2026-11-04',{unscheduled:true}),target('2026-11-03'),target('2026-11-04',{missing_coordinates:[]}),target('2026-11-05'),target('2026-11-04',{past:true})],'2026-11-04'),'2026-11-05')
 assert.equal(nextPlannedDate([target('2026-11-05'),target('2026-11-05')],'2026-11-05'),'2026-11-05')
 assert.equal(nextPlannedDate([],'2026-11-04'),undefined)
})

test('a rest day leaves six days rather than pulling the same weekday from next week',()=>{
 const days=Array.from({length:9},(_,i)=>({...target,date:`2026-11-${String(i+5).padStart(2,'0')}`})).filter(t=>t.date!=='2026-11-11')
 const window=upcomingTargets(days,'2026-11-05');assert.equal(window.length,6);assert.equal(window.at(-1)?.date,'2026-11-10');assert.equal(new Set(window.map(t=>new Date(t.date+'T12:00:00Z').getUTCDay())).size,6)
 assert.deepEqual(upcomingTargets(days,''),[])
})

test('first Next from the overview selects tomorrow instead of skipping it or selecting today',async()=>{
 const {firstFutureTargetIndex}=await import('../components/scheduled-days.ts')
 const targets=[{...target,date:'2026-11-05'},{...target,date:'2026-11-06'},{...target,date:'2026-11-07'}]
 assert.equal(firstFutureTargetIndex(targets,'2026-11-05'),1);assert.equal(firstFutureTargetIndex(targets.slice(1),'2026-11-05'),0)
 assert.equal(firstFutureTargetIndex([{...target,date:'2026-11-08'}],'2026-11-06'),0)
 assert.equal(firstFutureTargetIndex([{...target,date:'2026-11-05'}],'2026-11-05'),-1)
})
