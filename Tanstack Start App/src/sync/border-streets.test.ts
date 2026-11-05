import fs from 'node:fs'
import test from 'node:test'
import assert from 'node:assert/strict'
import inventory from '../../../raw-data/geography/19083-streets.json' with {type:'json'}
const boundary=JSON.parse(fs.readFileSync(new URL('../../../raw-data/boundaries/19083.geojson',import.meta.url),'utf8'))
function inRing(p:number[],ring:number[][]){let inside=false;for(let i=0,j=ring.length-1;i<ring.length;j=i++){const a=ring[j],b=ring[i],dx=b[0]-a[0],dy=b[1]-a[1],t=Math.max(0,Math.min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/(dx*dx+dy*dy||1)));if(Math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)<2e-8)return true;if((a[1]>p[1])!==(b[1]>p[1])&&p[0]<(b[0]-a[0])*(p[1]-a[1])/(b[1]-a[1])+a[0])inside=!inside}return inside}
test('Havertown coverage and orange lines retain only geometry inside the displayed ZIP boundary',()=>{
 const geometry=boundary.geometry,polygons=geometry.type==='MultiPolygon'?geometry.coordinates:[geometry.coordinates]
 for(const street of inventory.streets)for(const line of street.lines)for(const point of line)assert.ok((polygons as number[][][][]).some(p=>inRing(point,p[0])),street.name)
 const marvine=inventory.streets.find(s=>s.name==='Marvine Avenue')!;assert.ok(marvine.lengthMeters>100&&marvine.lengthMeters<120);assert.ok(inventory.streets.some(s=>s.name==='Burmont Road'))
})
