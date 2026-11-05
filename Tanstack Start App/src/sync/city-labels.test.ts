import fs from 'node:fs'
import test from 'node:test'
import assert from 'node:assert/strict'
import {historyAreas} from '../components/scheduled-days.ts'
const runs=JSON.parse(fs.readFileSync(new URL('../../../raw-data/runs/tracks.geojson',import.meta.url),'utf8'))
const bikes=JSON.parse(fs.readFileSync(new URL('../../../raw-data/bikes/tracks.geojson',import.meta.url),'utf8'))
import {cityLabel} from '../components/city-labels.ts'
test('all current mapped city groups use a comma and a state or country suffix',()=>{
 for(const tracks of [runs,bikes])for(const area of historyAreas(tracks))assert.match(area.label,/, [A-Z]{2}(?:\/[A-Z]{2})?$/,area.label)
 assert.equal(cityLabel('outer Philly suburbs'),'Outer Philly Suburbs, PA');assert.equal(cityLabel('Chicago area, IL'),'Chicago Area, IL')
})
