import { createFileRoute } from '@tanstack/react-router'
import videos from '../components/timelapses.json'
const allowed = new Set([...videos.flatMap(v=>[v.videoUrl.split('/').pop()!,v.posterUrl.split('/').pop()!]), 'runs-2026-10-31-week-v2.mp4', 'runs-2026-10-31-week-v2.jpg', 'runs-2026-10-31-week.mp4', 'runs-2026-10-31-week.jpg', 'runs-2026-story-v3.mp4', 'runs-2026-story-v3.jpg', 'runs-2026-story-v2.mp4', 'runs-2026-story-v2.jpg', 'runs-2026.mp4', 'runs-2026.jpg', 'runs-2026-google.mp4', 'runs-2026-google.jpg', 'runs-2026-story-v1.mp4', 'runs-2026-story-v1.jpg'])
export const Route = createFileRoute('/media/$file')({
 server: { handlers: { GET: async ({ request, params }) => {
  if (!allowed.has(params.file)) return new Response('Not found', {status:404})
  const { env } = await import('cloudflare:workers')
  const object = await env.TIMELAPSE_MEDIA.get(params.file, {range:request.headers})
  if (!object) return new Response('Not found', {status:404})
  const headers = new Headers({'Accept-Ranges':'bytes','Cache-Control':'public, max-age=3600','X-Content-Type-Options':'nosniff'})
  object.writeHttpMetadata(headers)
  headers.set('ETag', object.httpEtag)
  headers.set('Content-Type', params.file.endsWith('.mp4')?'video/mp4':'image/jpeg')
  if (new URL(request.url).searchParams.has('download')) headers.set('Content-Disposition',`attachment; filename="${params.file}"`)
  const range = object.range
  if (request.headers.has('Range') && range) {
   headers.set('Content-Range',`bytes ${range.offset}-${range.offset+range.length-1}/${object.size}`)
   headers.set('Content-Length',String(range.length))
   return new Response(object.body,{status:206,headers})
  }
  headers.set('Content-Length',String(object.size))
  return new Response(object.body,{headers})
 } } }
})
