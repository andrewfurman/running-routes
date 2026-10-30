import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/api/maps-config')({
  server: {
    handlers: {
      GET: async () => {
        const { env } = await import('cloudflare:workers')
        return Response.json(
          { googleMapsApiKey: env.GOOGLE_MAPS_API_KEY || '' },
          { headers: { 'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff' } },
        )
      },
    },
  },
})
