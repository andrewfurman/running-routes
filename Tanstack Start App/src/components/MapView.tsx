import { useEffect, useRef, useState } from 'react'
import 'leaflet/dist/leaflet.css'
import type { FeatureCollection, MapProvider, Position, Target } from './types'

declare global { interface Window { google?: any; runningMapReady?: () => void; gm_authFailure?: () => void } }
let googlePromise: Promise<any> | undefined
function loadGoogle(key: string) {
  if (window.google?.maps) return Promise.resolve(window.google.maps)
  if (!googlePromise) googlePromise = new Promise((resolve, reject) => {
    window.runningMapReady = () => resolve(window.google.maps)
    window.gm_authFailure = () => { googlePromise = undefined; reject(new Error('Google Maps key was not accepted')) }
    const script = document.createElement('script')
    script.src = `https://maps.googleapis.com/maps/api/js?key=${encodeURIComponent(key)}&loading=async&callback=runningMapReady`
    script.async = true
    script.onerror = () => { googlePromise = undefined; reject(new Error('Google Maps could not load')) }
    document.head.append(script)
  })
  return googlePromise
}
function points(collection?: FeatureCollection): Position[] {
  const result: Position[] = []
  for (const feature of collection?.features || []) {
    const lines = feature.geometry.type === 'LineString' ? [feature.geometry.coordinates] : feature.geometry.type === 'Polygon' ? feature.geometry.coordinates : feature.geometry.coordinates
    for (const line of lines) for (const p of line) if (typeof p[0] === 'number') result.push(p)
  }
  return result
}
interface Props { provider: MapProvider; mapsKey: string; tracks?: FeatureCollection; targets: Target[]; boundary?: any; selected: number; focusRequest: number; fitRequest: number; historyRequest: number; showTracks: boolean; showBoundary: boolean; activityId?: string; onSelect: (index: number) => void; onProviderFailure: (reason: string) => void }
export function MapView(props: Props) {
  const host = useRef<HTMLDivElement>(null)
  const engine = useRef<any>(null)
  const select = useRef(props.onSelect)
  select.current = props.onSelect
  const [ready, setReady] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  useEffect(() => {
    let stopped = false
    let cleanup = () => {}
    setLoading(true); setError('')
    async function initialize() {
      try {
        if (!host.current) return
        if (props.provider === 'google' && props.mapsKey) {
          const g = await loadGoogle(props.mapsKey)
          window.gm_authFailure = () => { if(!stopped)props.onProviderFailure('Google Maps is unavailable for this site. Showing OpenStreetMap.') }
          if (stopped || !host.current) return
          const map = new g.Map(host.current, { center: {lat: 39.979, lng: -75.31}, zoom: 14, gestureHandling: 'greedy', streetViewControl: false, mapTypeControl: false, fullscreenControl: false })
          const e: any = { map, type: 'google', trackLayer: new g.Data(), boundaryLayer: new g.Data(), routeLines: [], markers: [] }
          e.fit = (ps: Position[], padding = 55) => { if (!ps.length) return; const b = new g.LatLngBounds(); for (const [lng, lat] of ps) b.extend({lat,lng}); map.fitBounds(b,padding); g.event.addListenerOnce(map,'idle',()=>{if(map.getZoom()>17)map.setZoom(17)}) }
          engine.current = e
          cleanup = () => { e.trackLayer.setMap(null);e.boundaryLayer.setMap(null);for(const line of e.routeLines)line.setMap(null);for(const marker of e.markers)marker.setMap(null);g.event.clearInstanceListeners(map) }
        } else {
          const mod = await import('leaflet'); const L = mod.default || mod
          if (stopped || !host.current) return
          const map = L.map(host.current, {center: [39.979,-75.31], zoom:14, preferCanvas:true, zoomControl:false})
          L.control.zoom({position:'bottomright'}).addTo(map)
          L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19,attribution:'© OpenStreetMap contributors'}).addTo(map)
          const e: any = {map,L,type:'osm',routeLines:[],markers:[]}
          e.fit = (ps: Position[], padding = 40) => {if(ps.length)map.fitBounds(L.latLngBounds(ps.map(([lng,lat])=>[lat,lng])),{padding:[padding,padding],maxZoom:17})}
          engine.current=e;cleanup=()=>map.remove()
        }
        if (stopped) {cleanup();return}
        setReady(x=>x+1);setLoading(false)
      } catch (err) { if(!stopped){setError(err instanceof Error?err.message:'Map unavailable');setLoading(false);if(props.provider==='google')props.onProviderFailure('Google Maps could not load. OpenStreetMap is available.')} }
    }
    initialize()
    return () => {stopped=true;cleanup();engine.current=null}
  }, [props.provider, props.mapsKey])
  useEffect(() => {
    const e=engine.current;if(!e)return
    if(e.type==='google') {e.trackLayer.forEach((f:any)=>e.trackLayer.remove(f));if(props.tracks)e.trackLayer.addGeoJson(props.tracks);e.trackLayer.setStyle({strokeColor:'#7442bb',strokeWeight:3,strokeOpacity:.62});e.trackLayer.setMap(props.showTracks?e.map:null)}
    else {if(e.trackLayer)e.map.removeLayer(e.trackLayer);e.trackLayer=props.tracks?e.L.geoJSON(props.tracks,{style:{color:'#7442bb',weight:3,opacity:.62}}):null;if(e.trackLayer&&props.showTracks)e.trackLayer.addTo(e.map)}
  },[ready,props.tracks,props.showTracks])
  useEffect(() => {
    const e=engine.current;if(!e)return
    if(e.type==='google'){e.boundaryLayer.forEach((f:any)=>e.boundaryLayer.remove(f));if(props.boundary)e.boundaryLayer.addGeoJson(props.boundary);e.boundaryLayer.setStyle({strokeColor:'#078f8a',strokeWeight:3,fillColor:'#0caba2',fillOpacity:.035,zIndex:20});e.boundaryLayer.setMap(props.showBoundary?e.map:null)}
    else {if(e.boundaryLayer)e.map.removeLayer(e.boundaryLayer);e.boundaryLayer=props.boundary?e.L.geoJSON(props.boundary,{style:{color:'#078f8a',weight:3,fillOpacity:.035}}):null;if(e.boundaryLayer&&props.showBoundary)e.boundaryLayer.addTo(e.map)}
  },[ready,props.boundary,props.showBoundary])
  useEffect(() => {
    const e=engine.current;if(!e)return
    for(const l of e.routeLines)e.type==='google'?l.setMap(null):e.map.removeLayer(l)
    for(const m of e.markers)e.type==='google'?m.setMap(null):e.map.removeLayer(m)
    e.routeLines=[];e.markers=[]
    props.targets.forEach((t,i)=>{
      const pos=t.navigation_coordinates||t.target_midpoint||t.target_coordinates[0]
      const day=new Date(`${t.date}T12:00:00`).toLocaleDateString('en-US',{weekday:'short'})
      if(e.type==='google'){
        const g=window.google.maps; const line=new g.Polyline({map:e.map,path:t.target_coordinates.map(([lng,lat])=>({lng,lat})),strokeColor:'#ed8d39',strokeWeight:5,zIndex:30})
        const marker=new g.Marker({map:e.map,position:{lng:pos[0],lat:pos[1]},label:{text:day,color:'#fff',fontWeight:'700',fontSize:'10px'},title:`${day}: ${t.street}`,icon:{path:g.SymbolPath.CIRCLE,fillColor:'#6840a8',fillOpacity:1,strokeColor:'#fff',strokeWeight:3,scale:19},zIndex:40})
        marker.addListener('click',()=>select.current(i));e.routeLines.push(line);e.markers.push(marker)
      }else{
        const line=e.L.polyline(t.target_coordinates.map(([lng,lat])=>[lat,lng]),{color:'#ed8d39',weight:5}).addTo(e.map)
        const marker=e.L.marker([pos[1],pos[0]],{title:`${day}: ${t.street}`,icon:e.L.divIcon({className:'weekday-marker',html:`<span>${day}</span>`,iconSize:[40,40],iconAnchor:[20,20]})}).addTo(e.map).on('click',()=>select.current(i));e.routeLines.push(line);e.markers.push(marker)
      }
    })
    const ps=props.targets.flatMap(t=>t.target_coordinates)
    if(ps.length)e.fit(ps)
    else e.fit(points(props.tracks).filter(([lng,lat])=>lng>-75.39&&lng< -75.24&&lat>39.92&&lat<40.04))
  },[ready,props.targets])
  useEffect(()=>{const e=engine.current;if(!e)return;e.routeLines.forEach((line:any,i:number)=>e.type==='google'?line.setOptions({strokeColor:i===props.selected?'#e96b1d':'#e8a364',strokeWeight:i===props.selected?7:4}):line.setStyle({color:i===props.selected?'#e96b1d':'#e8a364',weight:i===props.selected?7:4}))},[ready,props.selected,props.targets])
  useEffect(()=>{if(props.focusRequest&&props.targets[props.selected])engine.current?.fit(props.targets[props.selected].target_coordinates,70)},[props.focusRequest,ready])
  useEffect(()=>{if(props.fitRequest){const e=engine.current;if(!e)return;const f=props.boundary;const rings=f?.geometry?.coordinates||f?.features?.[0]?.geometry?.coordinates;const ps=rings?.flat?.(1);if(ps?.[0]&&typeof ps[0][0]==='number')e.fit(ps);else e.fit(props.targets.flatMap(t=>t.target_coordinates))}},[props.fitRequest,ready])
  useEffect(()=>{if(props.historyRequest)engine.current?.fit(points(props.tracks))},[props.historyRequest,ready])
  useEffect(()=>{if(!props.activityId||!props.tracks)return;const feature=props.tracks.features.find(f=>String(f.properties.activity_id)===props.activityId);if(feature)engine.current?.fit(points({type:'FeatureCollection',features:[feature]}),60)},[props.activityId,props.tracks,ready])
  return <div className="map-surface"><div className="map-canvas" ref={host} aria-label="Interactive route map"/>{loading?<div className="map-loading"><span className="spinner"/>Loading street map</div>:null}{error?<div className="map-error" role="alert">{error}</div>:null}<div className="map-credit">{props.provider==='google'?'Google Maps':'OpenStreetMap'}<span>•</span>Purple: recorded tracks<span>•</span>Teal: 19083</div></div>
}
