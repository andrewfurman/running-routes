import { createFileRoute } from '@tanstack/react-router'
import { useEffect, useRef, useState } from 'react'
import { loadGoogle } from '../components/MapView'
const areas=[
 {id:'havertown',label:'Havertown',lat:39.981605,lng:-75.30839,zoom:14},
 {id:'bucks',label:'Bucks County',lat:40.490365,lng:-75.39594,zoom:15},
 {id:'new-york',label:'New York harbor',lat:40.63469,lng:-74.053,zoom:16},
 {id:'atlantic',label:'Atlantic GPS activity',lat:34.593325,lng:-74.559055,zoom:12},
 {id:'connecticut',label:'Connecticut',lat:41.28815,lng:-73.49711,zoom:15},
]
function VideoMap(){
 const host=useRef<HTMLDivElement>(null),map=useRef<any>(null)
 const [area,setArea]=useState(0),[hidden,setHidden]=useState(false),[status,setStatus]=useState('Loading Google Maps…')
 useEffect(()=>{let stopped=false;fetch('/api/maps-config').then(r=>r.json()).then(async c=>{if(!c.googleMapsApiKey)throw Error('Google Maps key not configured');const g=await loadGoogle(c.googleMapsApiKey);if(stopped||!host.current)return;map.current=new g.Map(host.current,{center:{lat:areas[0].lat,lng:areas[0].lng},zoom:areas[0].zoom,disableDefaultUI:true,gestureHandling:'none',clickableIcons:false});g.event.addListener(map.current,'tilesloaded',()=>setStatus('Map ready'));}).catch(e=>setStatus(e.message));const key=(e:KeyboardEvent)=>{if(e.key==='Escape')setHidden(false)};window.addEventListener('keydown',key);return()=>{stopped=true;window.removeEventListener('keydown',key);if(map.current)window.google.maps.event.clearInstanceListeners(map.current)}},[])
 useEffect(()=>{if(map.current){setStatus('Loading map…');map.current.setCenter({lat:areas[area].lat,lng:areas[area].lng});map.current.setZoom(areas[area].zoom)}},[area])
 return <main style={{position:'fixed',inset:0,zIndex:1000}}><div ref={host} style={{position:'absolute',inset:0}} aria-label="Google Maps video background"/>{!hidden?<section style={{position:'absolute',top:15,left:15,padding:16,background:'white',borderRadius:12,fontSize:14,boxShadow:'0 3px 20px #0002'}}><h1 style={{fontSize:17,marginTop:0}}>Video map capture</h1><label>Area <select disabled={!map.current} value={area} onChange={e=>setArea(Number(e.target.value))}>{areas.map((a,i)=><option key={a.id} value={i}>{a.label}</option>)}</select></label><p>{status}</p><p>Center {areas[area].lat}, {areas[area].lng} · Zoom {areas[area].zoom}</p><button onClick={()=>setHidden(true)}>Hide controls for capture</button><p>Escape restores controls. Preserve Google attribution.</p></section>:null}</main>
}
export const Route=createFileRoute('/video-map')({component:VideoMap})
