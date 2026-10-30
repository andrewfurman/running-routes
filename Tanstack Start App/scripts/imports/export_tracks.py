#!/usr/bin/env python3
"""Extract the embedded GeoJSON running tracks from the map snapshot."""
from pathlib import Path
import json
import re

root = Path(__file__).resolve().parents[3]
html = (root / 'Tanstack Start App/legacy/visualization/index.html').read_text(encoding='utf-8')
match = re.search(r'const recentTracks=(.*);\n', html)
if not match:
    raise SystemExit('Could not find embedded running tracks')
collection = json.loads(match.group(1))
(root / 'runs.geojson').write_text(json.dumps(collection, separators=(',', ':')) + '\n', encoding='utf-8')
print(f"Exported {len(collection['features'])} tracks to runs.geojson")
