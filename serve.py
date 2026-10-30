#!/usr/bin/env python3
"""Serve the running map locally, optionally using a Google Maps browser key."""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import argparse
import json
import os

ROOT = Path(__file__).resolve().parent

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self):
        if self.path.split('?', 1)[0] == '/maps-config.json':
            body = json.dumps({'googleMapsApiKey': os.environ.get('GOOGLE_MAPS_API_KEY', '')}).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            super().do_GET()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8768)
    args = parser.parse_args()
    print(f'Running map: http://127.0.0.1:{args.port}/', flush=True)
    with ThreadingHTTPServer(('127.0.0.1', args.port), Handler) as server:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
