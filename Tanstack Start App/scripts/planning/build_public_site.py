#!/usr/bin/env python3
"""Generate the public site using the browser key from the deployment environment."""
import json
import os
from pathlib import Path
import shutil
root = Path(__file__).resolve().parents[3]
site = root / 'site'
site.mkdir(exist_ok=True)
shutil.copy2(root / 'index.html', site / 'index.html')
shutil.copytree(root / 'visualization', site / 'visualization', dirs_exist_ok=True, ignore=shutil.ignore_patterns('*.py', '__pycache__', 'maps-config.json'))
(site / '.nojekyll').touch()
key = os.environ.get('GOOGLE_MAPS_API_KEY', '')
if not key:
    raise SystemExit('GOOGLE_MAPS_API_KEY is required for the Google Maps deployment')
(site / 'visualization/maps-config.json').write_text(json.dumps({'googleMapsApiKey': key}) + '\n')
print('Built public Google Maps site')
