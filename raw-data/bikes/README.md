# Cycling history

`tracks.geojson` contains 547 drawable GPS cycling tracks. `summary.json` reconciles 1,445 cycling activity records, including 898 records without a drawable GPS line. The signed-in Strava Ride listing showed 1,445 records when checked October 30, 2026. The most recent ride in that listing was October 29; no October 30 ride was listed.

The baseline was the existing official-export-derived cycling snapshot: 530 GPS rides and 1,428 cycling records through October 17. Seventeen newer rides were downloaded with Strava's signed-in Export GPX control and merged by activity ID. Their unmodified GPX files and SHA-256 provenance are in `2026-10-30/`. These sources do not contain browser session credentials.

Reapply an incremental manifest:

```sh
python3 scripts/imports/import_bike_history.py --manifest /private/path/to/rides.json --date YYYY-MM-DD
```

The manifest is a JSON list with `activity_id`, `activity_type` and `file`; `date` is optional when GPX timestamps exist. The activity type must be a cycling type, and repeated IDs do not increase the total. Relative file paths resolve beside the manifest. The importer preserves the original bytes and rejects conflicting raw files for an already-preserved activity ID.

Rebuild from an official full Strava export:

```sh
python3 scripts/imports/import_bike_history.py --archive /private/path/to/strava.zip --date YYYY-MM-DD
```

The archive must contain `activities.csv` at its root. FIT parsing uses `scripts/imports/requirements.txt`. Only cycling geometry and cycling originals are published; the account ZIP, other sports and unrelated account data are not copied. A full export replaces the base collection, so provide any newer incremental manifest in the same command if needed.

The importer rebuilds `visualization/bikes.html` for the legacy map and produces the canonical GeoJSON/summary files for the web app. It does not query Strava or automatically discover/download activities. Browser downloads remain a signed-in UI step; no official API token is required for imports. Future API integration must use an authorized official Strava token kept outside Git.
