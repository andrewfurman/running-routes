interface VideoObject {
 body: ReadableStream<Uint8Array>
 size: number
 httpEtag: string
 range?: { offset: number; length: number }
 writeHttpMetadata(headers: Headers): void
}
declare module 'cloudflare:workers' {
 export const env: { GOOGLE_MAPS_API_KEY?: string; TIMELAPSE_MEDIA: { get(key:string, options?:{range:Headers}):Promise<VideoObject|null> } }
}
