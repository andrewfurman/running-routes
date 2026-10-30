#!/usr/bin/env python3
"""Build and deploy the existing static map using local or CI credentials."""
from pathlib import Path
import os
import subprocess
root = Path(__file__).resolve().parents[2]
env = dict(os.environ)
local = root / '.env'
if local.exists():
    for line in local.read_text().splitlines():
        name, sep, value = line.strip().partition('=')
        if sep and name in {'GOOGLE_MAPS_API_KEY', 'CLOUDFLARE_API_TOKEN', 'CLOUDFLARE_ACCOUNT_ID'}:
            env.setdefault(name, value.strip().strip('\"\''))
for name in ('GOOGLE_MAPS_API_KEY', 'CLOUDFLARE_API_TOKEN', 'CLOUDFLARE_ACCOUNT_ID'):
    if not env.get(name): raise SystemExit(name + ' is required')
subprocess.run(['python3', 'scripts/planning/build_public_site.py'], cwd=root, env=env, check=True)
subprocess.run([str(root / 'node_modules/.bin/wrangler'), 'deploy'], cwd=root, env=env, check=True)
