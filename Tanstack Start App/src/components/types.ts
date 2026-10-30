export type Position = [number, number]
export interface FeatureCollection { type: 'FeatureCollection'; features: Array<{type: 'Feature'; properties: Record<string, any>; geometry: {type: string; coordinates: any}}> }
export interface Target { date: string; number: number; street: string; display_date?: string; time_label?: string; start_time?: string; end_time?: string; target_label: string; target_coordinates: Position[]; target_midpoint?: Position; navigation_coordinates?: Position; navigation_address: string; navigation_url: string; one_way_miles?: number | null; walking_metres?: number; target_miles: number; target_scope?: string; past?: boolean; citystrides_status?: string; outing_note?: string; outing_id?: string; completed_activity?: string; recorded_run_miles?: number; first_waypoint?: {apple_maps: string}; second_waypoint?: {apple_maps: string} }
export interface CalendarEvent { id: string; title: string; start: string; end?: string; type: 'past' | 'planned'; street?: string; activityId?: string; targetIndex?: number }
export type MapProvider = 'google' | 'osm'
export type Sport = 'runs' | 'bikes'
