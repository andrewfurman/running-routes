export interface ObjectBody { json<T>():Promise<T> }
export interface SyncBucket { get(key:string):Promise<ObjectBody|null>;put(key:string,value:string,options?:{httpMetadata:{contentType:string}}):Promise<unknown> }
export interface SyncStorage {get<T>(key:string):Promise<T|undefined>;put<T>(key:string,value:T):Promise<void>}
export interface SyncEnv {
 RUNS_DB?:RunDatabase
 STRAVA_WEB_COOKIE?:string
 TIMELAPSE_MEDIA:SyncBucket
 STRAVA_SYNC:{idFromName(name:string):unknown;get(id:unknown):{fetch(request:Request|string,init?:RequestInit):Promise<Response>}}
 STRAVA_CLIENT_ID?:string;STRAVA_CLIENT_SECRET?:string;STRAVA_REFRESH_TOKEN?:string;STRAVA_SYNC_ADMIN_TOKEN?:string;STRAVA_ATHLETE_ID?:string
}
export interface SyncedRun {activityId:string;date:string;distanceMeters:number;distanceSource:'strava_api'|'strava_web'|'strava_export';sportType:string;movingSeconds:number;elapsedSeconds:number;geometry:{type:'LineString';coordinates:[number,number][]}|{type:'MultiLineString';coordinates:[number,number][][]}|null;geometryKey?:string|null;hasGps?:boolean}
export interface RunSnapshot {updatedAt:string;runs:SyncedRun[]}
export interface SyncStatus {state:'needs_connection'|'needs_browser_login'|'synced'|'error';schedule:string;authMode?:string;lastAttemptAt?:string;lastSuccessAt?:string;lastSuccessDay?:string;importedRuns?:number;errorCode?:string}

export interface RunStatement {bind(...values:unknown[]):RunStatement;run():Promise<unknown>;all<T>():Promise<{results:T[]}>}
export interface RunDatabase {prepare(sql:string):RunStatement;batch(statements:RunStatement[]):Promise<unknown>}
