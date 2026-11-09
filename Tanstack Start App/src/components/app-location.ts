import {cityLabel} from './city-labels.ts'
import type {Sport,Target} from './types'
import {requestedRun} from './activity-summary.ts'
export type AppView='map'|'timelapses'|'cities'|'coverage'
export interface AppLocation {view:AppView;sport:Sport;activity?:string;target?:string;city?:string;inferSport?:boolean}
export function plannedTargetKey(target:Target){return `${target.date}-${target.street.normalize('NFKD').toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'')}`}
export function readAppLocation(search:string):AppLocation{
 const q=new URLSearchParams(search),v=q.get('view'),view:AppView=v==='timelapses'||v==='cities'||v==='coverage'?v:'map'
 const s=q.get('sport'),sport:Sport=view==='coverage'?'runs':s==='bikes'||s==='walks'?s:'runs'
 if(view!=='map')return {view,sport}
 const city=q.get('city')?.slice(0,160)||undefined,target=q.get('target')?.slice(0,200)||undefined,activity=requestedRun(search)||undefined
 if(city)return {view,sport,city:cityLabel(city)}
 if(target&&/^\d{4}-\d{2}-\d{2}-[a-z0-9-]+$/.test(target))return {view,sport:'runs',target}
 return {view,sport,...(activity?{activity,inferSport:!s&&activity!=='latest'}:{})}
}
export function appLocationUrl(current:string,location:AppLocation){
 const url=new URL(current)
 for(const key of ['view','sport','activity','target','city'])url.searchParams.delete(key)
 if(location.view!=='map')url.searchParams.set('view',location.view)
 else{url.searchParams.set('sport',location.sport);if(location.city)url.searchParams.set('city',location.city);else if(location.target)url.searchParams.set('target',location.target);else if(location.activity)url.searchParams.set('activity',location.activity)}
 return url
}
export function writeAppLocation(location:AppLocation,replace=false){const url=appLocationUrl(window.location.href,location);if(url.href!==window.location.href)window.history[replace?'replaceState':'pushState'](null,'',url)}
