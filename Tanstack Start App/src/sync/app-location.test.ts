import test from 'node:test'
import assert from 'node:assert/strict'
import {readAppLocation,appLocationUrl,plannedTargetKey} from '../components/app-location.ts'
import type {Target} from '../components/types'
test('all tabs, city sport maps and individual activities restore from shareable URLs',()=>{
 for(const view of ['timelapses','cities','coverage'] as const){const url=appLocationUrl('https://example.com/?activity=42&city=old&sport=bikes',{view,sport:'runs'});assert.equal(url.searchParams.get('view'),view);assert.equal(url.searchParams.has('activity'),false);assert.equal(readAppLocation(url.search).view,view)}
 for(const sport of ['runs','bikes','walks'] as const){
  const activity=appLocationUrl('https://example.com/',{view:'map',sport,activity:'20868244376'});const restored=readAppLocation(activity.search);assert.equal(restored.sport,sport);assert.equal(restored.activity,'20868244376')
  const city=appLocationUrl(activity.href,{view:'map',sport,city:'Mainline, PA'});assert.equal(city.searchParams.has('activity'),false);assert.equal(readAppLocation(city.search).city,'Mainline, PA');assert.equal(readAppLocation(city.search).sport,sport)
 }
})
test('street pages use stable date and street IDs rather than indexes, and do not leak between tabs',()=>{
 const target={date:'2026-11-06',street:'Rodmor Road'} as Target,key=plannedTargetKey(target);assert.equal(key,'2026-11-06-rodmor-road')
 const url=appLocationUrl('https://example.com/?activity=42&view=cities',{view:'map',sport:'runs',target:key});assert.equal(readAppLocation(url.search).target,key);assert.equal(url.searchParams.has('view'),false);assert.equal(url.searchParams.has('activity'),false)
 assert.notEqual(plannedTargetKey({...target,date:'2026-11-07'}),key);assert.equal(readAppLocation('?target=javascript:alert(1)').target,undefined)
 assert.equal(readAppLocation('?activity=42').inferSport,true);assert.equal(readAppLocation('?sport=bikes&activity=42').inferSport,false)
})
