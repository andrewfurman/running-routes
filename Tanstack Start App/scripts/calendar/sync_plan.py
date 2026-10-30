#!/usr/bin/env python3
"""Preview current-plan calendar changes; pass --apply to write and verify them."""
import argparse
from datetime import datetime, timedelta
import hashlib
import json
import os
from pathlib import Path
import subprocess
from zoneinfo import ZoneInfo
ROOT = Path(__file__).resolve().parents[3]

def gws(action, params, body=None):
    cmd = ['gws', 'calendar', 'events', action, '--params', json.dumps(params)]
    if body is not None: cmd += ['--json', json.dumps(body)]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    data = json.loads(result.stdout)
    if 'error' in data: raise RuntimeError(data['error'].get('message', 'Calendar request failed'))
    return data

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--verify', action='store_true', help='Verify saved events without writing')
    parser.add_argument('--calendar', default=os.environ.get('GOOGLE_CALENDAR_ID', 'primary'))
    args = parser.parse_args()
    config = json.loads((ROOT / 'raw-data/route-research/current-plan.json').read_text())
    targets = json.loads((ROOT / 'raw-data/route-research' / config['snapshot'] / 'targets.json').read_text())
    zone = ZoneInfo('America/New_York')
    first = min(t['date'] for t in targets)
    last = max(t['date'] for t in targets)
    start = datetime.fromisoformat(first).replace(tzinfo=zone)
    end = datetime.fromisoformat(last).replace(tzinfo=zone) + timedelta(days=1)
    params = {'calendarId': args.calendar, 'timeMin': start.isoformat(), 'timeMax': end.isoformat(), 'singleEvents': True, 'maxResults': 250}
    listing = gws('list', params)
    events = listing.get('items', [])
    while listing.get('nextPageToken'):
        listing = gws('list', dict(params, pageToken=listing['nextPageToken']))
        events.extend(listing.get('items', []))
    operations = []
    for t in targets:
        stable = hashlib.sha256(t['street'].encode()).hexdigest()[:24]
        matches = [e for e in events if e.get('extendedProperties', {}).get('private', {}).get('runningRoutesTarget') == stable]
        if not matches:
            matches = [e for e in events if e.get('summary', '').startswith('🏃') and (' · ' + t['street'] + ' · ') in e['summary']]
        if len(matches) > 1: raise RuntimeError('Ambiguous event matches for ' + t['street'])
        old = matches[0] if matches else None
        a = datetime.fromisoformat(t['date'] + 'T' + t.get('start_time', '05:30')).replace(tzinfo=zone)
        b = datetime.fromisoformat(t['date'] + 'T' + t.get('end_time', '06:15')).replace(tzinfo=zone)
        if b <= a: raise ValueError('Invalid event duration')
        body = {'summary': f"🏃 {t['display_date']} · {t['one_way_miles']:.1f} mi one-way · {t['street']} · {t['target_label']}", 'location': t['navigation_address'],
            'start': {'dateTime': a.isoformat(), 'timeZone': 'America/New_York'}, 'end': {'dateTime': b.isoformat(), 'timeZone': 'America/New_York'},
            'description': f"{t.get('outing_note', '')}\n\n{t.get('target_scope', '')}\n\nTap the numbered address: {t['navigation_address']}. Google walking distance from home: {t['walking_metres']/1609.344:.2f} miles; target traversal and return add mileage.\n\n{t['citystrides_status']} GPS proximity does not establish CityStrides credit.\n\nMidpoint: {t['navigation_url']}\nEndpoint A: {t['first_waypoint']['apple_maps']}\nEndpoint B: {t['second_waypoint']['apple_maps']}",
            'extendedProperties': {'private': dict((old or {}).get('extendedProperties', {}).get('private', {}), runningRoutesTarget=stable)}}
        operations.append((t, old, body))
    touched = {old['id'] for _, old, _ in operations if old}
    for t, old, body in operations:
        a, b = datetime.fromisoformat(body['start']['dateTime']), datetime.fromisoformat(body['end']['dateTime'])
        for event in events:
            if event['id'] in touched or event.get('transparency') == 'transparent' or event.get('status') == 'cancelled' or 'dateTime' not in event.get('start', {}): continue
            if datetime.fromisoformat(event['start']['dateTime']) < b and datetime.fromisoformat(event['end']['dateTime']) > a:
                raise RuntimeError('Calendar conflict: ' + event.get('summary', 'Untitled event'))
    for t, old, body in operations:
        print(('UPDATE ' if old else 'CREATE ') + t['date'] + ' ' + body['start']['dateTime'][11:16] + '–' + body['end']['dateTime'][11:16] + ' ' + t['street'], flush=True)
        if args.verify:
            if not old: raise RuntimeError('Missing event: ' + t['street'])
            actual = gws('get', {'calendarId': args.calendar, 'eventId': old['id']})
            for field in ('summary', 'location', 'description', 'start', 'end'):
                if actual.get(field) != body[field]: raise RuntimeError('Saved event mismatch: ' + t['street'] + ' ' + field)
        if not args.apply: continue
        params = {'calendarId': args.calendar, 'sendUpdates': 'none'}
        if old:
            params['eventId'] = old['id']; gws('patch', params, body); eid = old['id']
        else:
            body['id'] = 'run' + hashlib.sha256((t['date'] + t['street']).encode()).hexdigest()[:32]
            body['reminders'] = {'useDefault': False, 'overrides': [{'method': 'popup', 'minutes': 0}]}
            eid = gws('insert', params, body)['id']
        actual = gws('get', {'calendarId': args.calendar, 'eventId': eid})
        for field in ('summary', 'location', 'description', 'start', 'end'):
            if actual.get(field) != body[field]: raise RuntimeError('Read-back mismatch: ' + field)
    print('Verified calendar updates' if args.apply or args.verify else 'Preview only; use --apply to update Calendar')

if __name__ == '__main__': main()
