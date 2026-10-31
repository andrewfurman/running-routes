#!/usr/bin/env python3
"""Build and deploy the TanStack Start Worker using ignored local or CI credentials."""
from pathlib import Path
import os
import subprocess

APP = Path(__file__).resolve().parents[1]
REPO = APP.parent
env = dict(os.environ)
local = REPO / '.env'
if local.exists():
    for line in local.read_text().splitlines():
        name, sep, value = line.strip().partition('=')
        if sep and name in {'GOOGLE_MAPS_API_KEY', 'CLOUDFLARE_API_TOKEN', 'CLOUDFLARE_ACCOUNT_ID', 'STRAVA_CLIENT_ID', 'STRAVA_CLIENT_SECRET', 'STRAVA_REFRESH_TOKEN', 'STRAVA_SYNC_ADMIN_TOKEN'}:
            env.setdefault(name, value.strip().strip('\"\''))
for name in ('CLOUDFLARE_API_TOKEN', 'CLOUDFLARE_ACCOUNT_ID'):
    if not env.get(name):
        raise SystemExit(name + ' is required')
wrangler = APP / 'node_modules/.bin/wrangler'
if not wrangler.exists():
    raise SystemExit('Run npm ci in Tanstack Start App before deploying')
subprocess.run(['npm', 'run', 'build'], cwd=APP, env=env, check=True)
subprocess.run([str(wrangler), 'deploy'], cwd=APP, env=env, check=True)
for name in ('GOOGLE_MAPS_API_KEY', 'STRAVA_CLIENT_ID', 'STRAVA_CLIENT_SECRET', 'STRAVA_REFRESH_TOKEN', 'STRAVA_SYNC_ADMIN_TOKEN'):
    if env.get(name):
        subprocess.run([str(wrangler), 'secret', 'put', name], input=env[name] + '\n', text=True, cwd=APP, env=env, check=True)
