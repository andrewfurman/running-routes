import {MapView} from './MapView'
import type {StreetCoverage} from './street-coverage'
import type {MapProvider,Target} from './types'
const noTargets:Target[]=[]
const noSelection=()=>{}
interface Props {coverage?:StreetCoverage;error?:string;provider:MapProvider;mapsKey:string;boundary?:any;onProviderFailure:(reason:string)=>void}
export function HavertownCoverageMap({coverage,error,provider,mapsKey,boundary,onProviderFailure}:Props){
 const percent=coverage?.total?100*coverage.complete/coverage.total:0
 return <main className="map-page coverage-map-page" aria-label="Havertown unfinished roads map"><div className="map-wrap">
  <MapView provider={provider} mapsKey={mapsKey} boundary={boundary} targets={noTargets} selected={0} focusRequest={0} historyRequest={0} coverageMode missingRoads={coverage?.missingRoads} onSelect={noSelection} onProviderFailure={onProviderFailure}/>
  <section className="coverage-map-card" aria-label="19083 coverage summary" aria-live="polite">
   <h1>Havertown · 19083</h1>
   {coverage?<><div className="coverage-map-percentage"><strong>{percent.toFixed(1)}%</strong><span>streets fully covered</span></div><progress value={coverage.complete} max={coverage.total} aria-label="Estimated fully covered streets"/><p><strong>{coverage.complete} / {coverage.total}</strong> complete · <strong>{coverage.outstanding}</strong> to finish</p><p className="coverage-orange-key"><span aria-hidden="true"/>Orange shows the road sections still missing.</p><small>{coverage.partial} partial · {coverage.untouched} untouched · GPS estimate</small></>:<p role="status">{error||'Finding your unfinished streets…'}</p>}
  </section>
 </div></main>
}
