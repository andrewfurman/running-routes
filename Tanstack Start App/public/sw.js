const CACHE='running-routes-shell-v1';
self.addEventListener('install',()=>self.skipWaiting());
self.addEventListener('activate',event=>event.waitUntil(self.clients.claim()));
// Cache only static icons. Map tiles, route history, runtime config and calendar remain online.
self.addEventListener('fetch',event=>{const url=new URL(event.request.url);if(url.origin!==self.location.origin||!url.pathname.startsWith('/icons/'))return;event.respondWith(caches.open(CACHE).then(async cache=>{const hit=await cache.match(event.request);if(hit)return hit;const response=await fetch(event.request);if(response.ok)cache.put(event.request,response.clone());return response;}));});
