#!/usr/bin/env python3
"""Apply the current versioned route plan to the standalone running map."""
from pathlib import Path
import re
import sys
root = Path(__file__).resolve().parent
sys.path.insert(0, str(root / 'tools'))
from running_route_updates import apply_current_plan
from route_map_shell import apply_map_shell
p = root / 'index.html'
html = apply_map_shell(apply_current_plan(p.read_text(encoding='utf-8')), 'run')
html = re.sub(r'<a href="/bike-preview.html"[^>]*>Bikes</a>', '', html)
html = html.replace('<a href="/preview.html" aria-current="page">Runs</a>', '<span class="map-title">Runs</span>')
p.write_text(html, encoding='utf-8')
print('Updated index.html from current-plan.json')
