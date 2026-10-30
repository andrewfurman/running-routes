# Running Routes

[Open the public map](https://andrewfurman.github.io/running-routes/)

An interactive map of Andrew Furman's recorded running routes and upcoming street targets around Havertown, Pennsylvania. Purple lines represent running GPS tracks from Strava; weekday markers show the current plan. Bike rides and walks are excluded.

The map contains precise GPS traces and dated future destinations, published with the owner's approval. GPS proximity to a street does not guarantee CityStrides completion.

## Project layout

- `visualization/` — the interactive map and a local preview server.
- `routes/` — the current plan and dated route research, GPX files, geometry, and older map visualizations.
- `scripts/imports/` — scripts for extracting the map's GeoJSON or importing Strava history, plus import tests.
- `scripts/planning/` — tools for applying the current plan and rebuilding the map.

## Run locally

Python 3 is the only server dependency:

```sh
python3 visualization/serve.py
```

Open http://127.0.0.1:8768/ in a browser. The map uses OpenStreetMap and Leaflet by default. To use Google Maps, provide a Google Maps JavaScript browser key with the appropriate APIs enabled:

```sh
export GOOGLE_MAPS_API_KEY='your-browser-key'
python3 visualization/serve.py
```

Alternatively, use `python3 visualization/serve.py --env-file /path/to/local.env` to read a key from an existing local environment file.

Restrict browser keys to authorized origins in Google Cloud. Do not commit API keys. Google Maps may incur charges. The key is sent to the local browser and Google Maps; it is not written into the repository.

## Data and updates

`visualization/index.html` is a self-contained snapshot with embedded GeoJSON running tracks and target metadata: 1,874 GPS runs through October 30, 2026, and plans through November 3. Run `python3 scripts/imports/export_tracks.py` to extract the collection as `runs.geojson` (ignored by Git to avoid duplication).

The plan is selected by `routes/current-plan.json`. After editing the referenced dated plan, run `python3 scripts/planning/build_map.py` to update the visualization. The project does not automatically import new Strava activities or update plans.

Personal calendar event exports, email copies, bike history and the original all-sport Strava ZIP remain private in the Family Newspaper archive. The legacy bulk import utility preserves the entire all-sport export and must be used only in a private working copy; its output contains private data and is ignored in this public repository.

## Havertown 19083 boundary

The optional teal outline is the [U.S. Census Bureau 2020 ZIP Code Tabulation Area](https://www.census.gov/programs-surveys/geography/guidance/geo-areas/zctas.html) for 19083, retrieved from [TIGERweb](https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/tigerWMS_Current/MapServer/2). ZCTAs are statistical approximations of ZIP Code areas, not exact USPS delivery boundaries. The checked-in `visualization/19083.geojson` allows either map provider to display the same boundary without another data service.


## Planning priority

Finish unfinished streets within the Census 19083 boundary before expanding outside it. Prioritize Westgate Hills and the Hilltop area, retain numbered midpoint navigation addresses, and prefer approaches under two miles. The current neighborhood-focused plan supersedes spreading targets in different directions.
