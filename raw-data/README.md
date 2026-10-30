# Public source data

- `runs/tracks.geojson`: running-only GPS history, extracted from the earlier map snapshot; provenance is recorded alongside it.
- `bikes/tracks.geojson`: cycling-only GPS tracks; `summary.json` records mapped and GPS-less record counts. Dated folders preserve original recent GPX files with SHA-256 manifests.
- `plans/`: current upcoming targets and prior targets used by the app.
- `boundaries/19083.geojson`: Census ZCTA outline for Havertown.
- `route-research/`: dated plan geometry, evidence and historical imports moved from the old `routes/` directory. `current-plan.json` selects the calendar synchronization snapshot.

These files intentionally include public GPS and dated destinations. Private all-sport ZIP archives, credentials and environment files must remain outside Git. Generated browser assets live in the app's ignored `public/data/` folder and are rebuilt from these sources.
