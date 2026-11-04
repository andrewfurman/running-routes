import {auditPlannedGaps} from './planned-gaps'
import type {FeatureCollection,Target} from './types'
self.onmessage=(event:MessageEvent<{targets:Target[];tracks:FeatureCollection}>)=>{try{self.postMessage({targets:auditPlannedGaps(event.data.targets,event.data.tracks)})}catch{self.postMessage({error:'Unfinished target sections could not be refreshed.'})}}
