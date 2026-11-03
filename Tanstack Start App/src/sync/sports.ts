export const RUN_SPORTS=['Run','TrailRun','VirtualRun']
export const RIDE_SPORTS=['Ride','MountainBikeRide','GravelRide','EBikeRide','EMountainBikeRide','VirtualRide','Handcycle','Velomobile']
export function supportedSport(sport:string){return [...RUN_SPORTS,...RIDE_SPORTS].includes(sport)}
