# Walking history

The private Strava account export contributes **829 walking records**, including **813 GPS tracks** and **16 records without GPS**, through October 14, 2026. Recorded distance totals 919.1 miles. IDs deduplicate imports; missing GPS is preserved as metadata instead of invented routes.

`tracks.geojson` contains sanitized GPS geometry with disconnected segments preserved. `activities.json` retains only IDs, type, UTC date, recorded distance/time and GPS availability. `source-manifest.json` records original file hashes and formats. The original account ZIP and sensor files remain private; notes, photos and health fields are excluded.

Run `python3 scripts/imports/import_walk_history.py --archive /private/path/to/strava-export.zip` from the app folder to rebuild this selected archive. FIT sources require fitdecode. New walks are also supported by the existing 7 AM, 10 AM and 7 PM Eastern Strava sync, using the private browser session. Recent activities merge by ID with the static archive.

Walks have their own map and City Stats column. They never contribute to running-street coverage or running plans. City assignment uses the same midpoint grouping as runs and rides. Map/city counts use drawable GPS; all 829 source records remain available here.
