"""Apply the current small, versioned plan/GPS update to the R2 HTML snapshot.

The large base page stays in R2; current-plan.json and its referenced snapshot
keep subsequent plans reproducible without uploading another full history page.
Applying the same update twice is safe: activity IDs are deduplicated.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def running_collection(collection: dict) -> dict:
    return {'type': 'FeatureCollection', 'features': [
        f for f in collection['features'] if f['properties'].get('activity_type')
        in {'Run', 'TrailRun', 'Trail Run', 'VirtualRun', 'Virtual Run'}]}


def _inline_json(value) -> str:
    return json.dumps(value, separators=(',', ':')).replace('<', '\\u003c')


def apply_current_plan(html: str) -> str:
    folder = ROOT / 'routes'
    config_path = folder / 'current-plan.json'
    if not config_path.exists():
        return html
    config = json.loads(config_path.read_text())
    snapshot = folder / config['snapshot']
    targets = json.loads((snapshot / 'targets.json').read_text())
    history = snapshot / 'history-targets.json'
    if history.exists():
        targets = json.loads(history.read_text()) + targets
    as_of = config.get('as_of_label', 'October 22')
    focus_count = sum(config['focus_start'] <= t['date'] <= config['focus_end'] for t in targets)
    added = json.loads((snapshot / 'new-tracks.geojson').read_text())
    match = re.search(r'const recentTracks=(.*);\n', html)
    if not match:
        raise ValueError('Expected one embedded GPS collection in the base map')
    tracks = json.loads(match[1])
    ids = {str(f['properties'].get('activity_id')) for f in tracks['features']}
    for feature in added['features']:
        aid = str(feature['properties']['activity_id'])
        if aid not in ids:
            tracks['features'].append(feature)
            ids.add(aid)
    # This page is the running LifeMap. Keep the raw all-sport archive intact;
    # cycling has its own page, and walks are excluded from this overlay too.
    tracks = running_collection(tracks)
    html = re.sub(r'const recentTracks=.*;\n', lambda _: 'const recentTracks='+_inline_json(tracks)+';\n', html, count=1)
    html = re.sub(r'const targets=.*;\n', lambda _: 'const targets='+_inline_json(targets)+';\n', html, count=1)
    html = re.sub(r'function targetVisible\(t\)\{[^\n]*\}',
                  "function targetVisible(t){return period==='all'||(t.date>='"+config['focus_start']+"'&&t.date<='"+config['focus_end']+"')}",html,count=1)
    html = re.sub(r'function updateVisibleCards\(\)\{[^\n]*\}',
        lambda _: "function updateVisibleCards(){document.querySelectorAll('.card').forEach((b,i)=>b.hidden=!targetVisible(targets[i]));document.querySelector('#range-summary').textContent=period==='weekend'?'"+str(focus_count)+" highlighted targets':'Full plan and actual run notes';document.querySelector('#plan-heading').textContent=period==='weekend'?"+_inline_json(config['heading'])+":"+_inline_json(config.get('history_heading','Havertown · Plan and history'))+"}",html,count=1)
    html = re.sub(r'<option value="weekend" selected>.*?</option>', '<option value="weekend" selected>'+config['focus_label']+'</option>',html,count=1)
    html = re.sub(r'let engine=null,selected=\d+,', 'let engine=null,selected='+str(next(i for i,t in enumerate(targets) if config['focus_start']<=t['date']<=config['focus_end']))+',',html,count=1)
    html = re.sub(r'<option value="all">.*?</option>', '<option value="all">Full plan and history</option>',html,count=1)
    html = html.replace('selectTarget(1,false);async function initializeMap()', 'selectTarget(selected,false);async function initializeMap()')
    html = re.sub(r"\(t.completed_activity\?.*?:'Navigate to '","(t.outcome_note?t.outcome_note:'Navigate to '",html,count=1)
    html = re.sub(r'Purple = .*?Activities without GPS have no line\.', 'Purple = '+format(len(tracks['features']),',')+' GPS running tracks through '+as_of+'. Bike rides, walks and other sports are excluded. Activities without GPS have no line.',html,count=1)
    html = html.replace('All exported GPS tracks', 'Running GPS tracks only').replace('Show full GPS history', 'Show full running history')
    html = html.replace("(t.past?' · PAST RUN':'')", "(t.past?(t.completed_activity?' · RECORDED RUN':' · PAST PLAN'):'')")
    html = re.sub(r'GPS gap audit refreshed [^.]+\.', 'GPS gap audit refreshed '+as_of+'.',html,count=1)
    html = re.sub(r'Numbered midpoint addresses and Google walking mileages checked [^.]+\.', 'Numbered midpoint addresses and Google walking mileages checked '+as_of+', 2026.',html,count=1)
    html = html.replace('Tuesday is unscheduled.', '')
    html = re.sub(r'<div class="intro">(?:<p>.*?</p>)?',lambda _: '<div class="intro"><p>'+config['summary']+'</p>',html,count=1)
    if 't.time_label?' not in html:
        html = html.replace('day.textContent=t.date+', "day.textContent=t.date+(t.time_label?' · '+t.time_label:'')+",1)
    html = html.replace('day.textContent=t.date+', 'day.textContent=(t.display_date||t.date)+',1)
    html = html.replace("title.textContent=t.number+' · '+t.street;", "title.textContent=t.number+' · '+t.street+(t.direction?' · '+t.direction:'');",1)
    html = html.replace("textContent=t.date+' · '+t.street;", "textContent=(t.display_date||t.date)+' · '+t.street;",1)
    html = html.replace("document.querySelector('#detail-credit').textContent=t.citystrides_status;", "document.querySelector('#detail-credit').textContent=(t.target_scope?t.target_scope+' ':'')+(t.connector_note?t.connector_note+' ':'')+t.citystrides_status;",1)
    return html
