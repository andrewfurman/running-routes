import test from 'node:test'
import assert from 'node:assert/strict'
import inventory from '../../../raw-data/geography/19083-streets.json' with {type:'json'}
import source from '../../../raw-data/geography/19083-streets-osm.json' with {type:'json'}
import {lineMeters} from '../components/planned-gaps.ts'
test('Marvine coverage retains its entire connected public street rather than the old ZIP-clipped fragment',()=>{
 const street=inventory.streets.find(s=>s.name==='Marvine Avenue')!
 const ways=source.data.elements.filter(w=>w.tags?.name==='Marvine Avenue')
 const completeLength=ways.reduce((n,w)=>n+lineMeters(w.geometry!.map(p=>[p.lon,p.lat])),0)
 assert.ok(inventory.borderStreets.includes('Marvine Avenue'));assert.ok(street.lengthMeters>1800)
 assert.ok(Math.abs(street.lengthMeters/completeLength-1)<.01)
 for(const point of street.lines.flat()){assert.ok(point[0]>=inventory.bounds[0]&&point[0]<=inventory.bounds[2]);assert.ok(point[1]>=inventory.bounds[1]&&point[1]<=inventory.bounds[3])}
})
