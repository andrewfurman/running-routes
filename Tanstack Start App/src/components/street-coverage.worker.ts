import {calculateStreetCoverage} from './street-coverage'
import type {FeatureCollection} from './types'
self.onmessage=async(event:MessageEvent<FeatureCollection>)=>{
 try{const response=await fetch('/data/streets19083.json');if(!response.ok)throw Error('Street inventory unavailable');const inventory=await response.json();self.postMessage({coverage:calculateStreetCoverage(inventory,event.data)})}
 catch{self.postMessage({error:'Street coverage could not be calculated. Try Refresh.'})}
}
