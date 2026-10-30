Current plan: [six separated running targets](2026-10-28-reconciliation/README.md), Thursday October 29 through Tuesday November 3. Monroe Avenue was completed October 28; the targets alternate directions and are at least 904 m apart. The full-window map has a Runs/Bikes switcher, Info, weekday/date labels, and 1,872 running GPS tracks.

# Running route library

[Open the Bike LifeMap](bike-preview.html): a separate interactive Google map of 530 recorded bike GPS tracks, with year filters and Strava links. [Bike history details](2026-10-17-bike-history/README.md) explain the 1,428 cycling records and 898 without drawable GPS.

**Earlier plan:** [October 17 reconciliation](2026-10-17-swapped-runs/README.md): Joanna was covered Saturday; Ellis is Sunday October 18, and all later targets through October 26 retain GPS gaps. The map follows the swapped calendar dates and now has 3,216 GPS tracks. Tuesday October 20 remains unscheduled. The [full October 17–26 plan](2026-10-17-to-26/README.md) preserves the original schedule snapshot.

Calendar destinations must use verified **street-number addresses near segment midpoints** so Apple Watch navigation works. Keep cross streets in event titles and refresh one-way mileage to the numbered address. This is a standing rule in the [running instructions](../../instructions%20-%20how%20to%20make%20newspaper/standing-family-notes.md#running-routes-daily-dad-travel-only-since-2026-10-03).

## Full Strava history export

[October 16 full-history backup](2026-10-16-strava-history/README.md): **4,404 activities** from March 22, 2016 through October 15, 2026; **3,208 drawable GPS tracks**, 1,187 original files without a drawable line, and nine records without an original file. The entire 197,755,781-byte account ZIP is preserved unchanged in 24 ordered binary parts, with individual and combined SHA-256 hashes verified. The source archive retains every activity type; the running preview now embeds runs only. This is an archive snapshot, not automatic syncing or CityStrides completion credit.

[Numbered destinations and saved calendar events](2026-10-16-numbered-destinations/README.md) record the seven updated calendar locations, cross-street titles and refreshed one-way walking mileages. Tuesday remains unscheduled.

To import a future archive:

```sh
python3 -m pip install -r tools/requirements-strava.txt
python3 tools/import_strava_history.py /path/to/strava-export.zip --date YYYY-MM-DD
python3 -m unittest discover -s tools -p test_import_strava_history.py
```

The importer preserves the entire original ZIP, including CSV, activity files, photos and other account data, in ordered 8 MiB parts. Concatenating the parts in manifest order restores the exact original ZIP. The archive parts, `preview.html`, `bike-preview.html`, `tracks.geojson.gz` and other large files here live in R2, not git (see `tools/r2_path_manifest.json`). After a fresh checkout restore them with `.venv/bin/python tools/media_store.py pull-path "content research/future-running-routes"` (pass a sub-folder to fetch less; the 197 MB `raw/` parts are only needed to rebuild the ZIP). `serve_running_routes.py`, `recompute_audit.py` and the importer pull what they need automatically. After an import or a preview rebuild, run `media_store.py push-path <changed files>` and commit the updated manifest. Never commit archive download links or tokens.

GPX, TCX, FIT and gzipped files are supported. Display coordinates are rounded to five decimal places and simplified within two metres for browser performance; raw files remain unchanged. Unsupported formats stop the import rather than silently omitting tracks. The compressed machine-readable copy is `tracks.geojson.gz`. Calendar updates and any refreshed coverage claims require separate verification.

[Open the single interactive map preview](preview.html): October 23–25 highlighted by default, with full October 17–26 history, one-way walking mileage, clickable geographic pins, real tiled streets, map zoom/pan, and a toggle for 1,867 saved running GPS tracks. OpenStreetMap works immediately; internet is required for map tiles and Leaflet. A Google Maps option accepts a browser API key for the current session only. No API key is committed. Purple lines show running GPS through October 22. The live LifeMap remains the source for current CityStrides coverage and completion credit.

All home loops start and finish at 1700 Manor Road, Manor & Fairfield, Havertown. Refresh the signed-in CityStrides LifeMap before selecting a new-road target.

- [One-way Watch navigation update](2026-10-15-one-way-navigation/README.md): current calendar titles use verified outbound Google walking mileage; return routes are freeform.
- [October 19–23 extension](2026-10-19-to-23/README.md): Marilyn, Chester (unscheduled), Pickwick, Garden and Bennington, with coverage status and route exceptions.
- [October 16–18 selected streets](2026-10-16-to-18/README.md): whole Charles Drive, remaining Ellis Road nodes, and the southern Walnut Place trace gap, with ordered endpoint navigation.
- [October 15 Watch-navigation review](2026-10-15/README.md): 91 recovered Health workouts, actual GPS comparisons for October 9–15, and destination-based Watch navigation versus plotted loops.
- [October 14–17 plan and ten refreshed pins](2026-10-13/README.md): four scheduled 3–4 mile morning loops, fresh LifeMap evidence, ten verified navigation addresses and calendar event links.
- [Ten additional loop options — October 7](2026-10-07-additional/README.md): interactive picker, ten unique 3–4 mile loops, nine target sections, GPX downloads, and overlap notes.
- [Four directions — October 8–11](2026-10-07/README.md): the four planned runs and their maps and GPX files.
- [Original seven-loop library — October 3](2026-10-03/README.md): earlier route research and use history.

[Standing running preferences](../../instructions%20-%20how%20to%20make%20newspaper/standing-family-notes.md#running-routes-daily-dad-travel-only-since-2026-10-03) cover distance, shape, start/finish, new-street evidence and calendar formatting.


## Map provider and coverage

The preview uses actual geographic coordinates for target polylines and GPS tracks. Zooming requests new street tiles and redraws vector overlays; it does not scale a screenshot. This replaces the original image-zoom implementation. The Google Maps JavaScript adapter uses the same coordinates and requires a browser key with the Maps JavaScript API enabled and appropriate website restrictions. The repository and its documented legacy config had no Maps key when checked October 15. Andrew subsequently supplied a key, stored only in the main checkout’s gitignored `.env`. Google Maps rendering and controls were then verified in Chrome; the key is not in the HTML or Git. The keyless OpenStreetMap path remains available.

The HTML keeps all ten dated target/history options and 1,867 running GPS tracks inline, but loads Leaflet from its pinned CDN and OpenStreetMap tiles from the provider. It is one preview file, not an offline map. Calendar destinations and one-way mileages remain unchanged. No claims of newly completed streets are made by this visualization.

Validation: JavaScript syntax; zoom from level 14 to 15 with newly loaded tile URLs; all eight target selections; seven vector track layers toggled off/on; Show all; and the missing-Google-key prompt.


## Start with Google Maps from local configuration

Add `GOOGLE_MAPS_API_KEY` to the gitignored repo `.env`; `env.sample` contains a blank placeholder and `.env.example` is the full configuration template. Run:

```sh
python3 tools/serve_running_routes.py
```

Open the printed loopback URL. The preview automatically loads Google Maps from `/maps-config.json` when a local key is present. The server binds only to 127.0.0.1, accepts localhost/loopback Host values, serves only the two map pages and configuration endpoint, marks responses no-store, and does not log requests. It is a local preview tool, not a production host. A Maps JavaScript browser key necessarily reaches the user's browser and Google; restrict it appropriately in Google Cloud. No key value is committed. Other machines must supply their own local `.env`; opening the HTML through an ordinary static server uses the manual-key option or OpenStreetMap.
