export const RUN_SPORTS=['Run','TrailRun','VirtualRun']
export const RIDE_SPORTS=['Ride','MountainBikeRide','GravelRide','EBikeRide','EMountainBikeRide','VirtualRide','Handcycle','Velomobile']
export const WALK_SPORTS=['Walk','VirtualWalk','Hike']
export const sportsFor=(sport:'runs'|'bikes'|'walks')=>sport==='runs'?RUN_SPORTS:sport==='bikes'?RIDE_SPORTS:WALK_SPORTS
export function supportedSport(sport:string){return [...RUN_SPORTS,...RIDE_SPORTS,...WALK_SPORTS].includes(sport)}
