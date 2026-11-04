# Running Routes

[Open the map](https://runningroutes.aifurman.com/)

A mobile-friendly TanStack Start app for Andrew Furman's running history, upcoming full-street targets and cycling history around Havertown. Use the Runs / Bikes / Videos switch, explore the full map, page through upcoming destinations, or watch the year-to-date time-lapse. Purple GPS history and the 19083 outline are always displayed; there are no visibility checkboxes or Fit area button. City selector in the top header opens recorded cities and areas. There is no separate map toolbar row, leaving the full space below the header for the map. Info keeps the map legend, sync status and iPhone installation help; Google Maps is the default with no provider switcher.

## Layout

- `Tanstack Start App/` contains the entire web app: source, icons, manifest, dependencies and lockfile, Vite/TypeScript/Wrangler configuration, deployment and import/planning/calendar scripts. `legacy/` preserves the earlier HTML visualizations and tools.
- `raw-data/` contains public GPS tracks, original recent ride GPX exports, boundaries, current targets and dated research.
- The root [`sample.env`](sample.env) is a committed template with blank Cloudflare, Google Maps and Strava settings. Copy it to root `.env` and fill in credentials locally; `.env` is ignored and must never be committed.

`.nojekyll` was a GitHub Pages marker, unrelated to npm packages. It is no longer needed: this app runs on a Cloudflare Worker.

## Development and deployment

Use Node.js 22.12 or newer and Python 3. From the repository root:

```sh
cp -n sample.env .env
```

Fill in the root `.env` locally. `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` authorize deployment; `GOOGLE_MAPS_API_KEY` configures Maps; `STRAVA_WEB_COOKIE` stores the private browser session, and `STRAVA_SYNC_ADMIN_TOKEN` protects manual imports. These values are deployed as needed by the existing scripts. Do not put real values into `sample.env`. Google Workspace CLI credentials remain in its local credentials file, outside Git.

```sh
cd "Tanstack Start App"
npm ci
npm run dev
```

`predev` and `prebuild` generate separate public data assets from `raw-data`. GPS history is fetched by sport rather than embedded in the HTML. To check and deploy:

```sh
npm run typecheck
npm run build
npm run deploy
```

Deployment reads `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID` and optional `GOOGLE_MAPS_API_KEY` from the environment or the ignored root `.env`. It deploys the `running-routes` Worker at runningroutes.aifurman.com and sets the Maps runtime secret. For local Google Maps, put `GOOGLE_MAPS_API_KEY` in ignored `Tanstack Start App/.dev.vars`; otherwise OpenStreetMap works without a key. The app uses Google Maps when configured; a fallback map is used only if Google Maps cannot load. There is no provider switcher or key input field. Browser Maps keys are visible to visitors when used; restrict the key to the required Maps APIs and authorized origins.

On iPhone, open the site in Safari, tap Share, then Add to Home Screen. The app includes an icon and standalone manifest. Maps require an internet connection; this is not an offline navigation app.

## Data updates

The current public dataset contains 1,877 GPS runs and 547 GPS rides through November 1, 2026. The cycling source has 1,445 records; 898 have no drawable GPS track. Runs exclude rides and walks. Selected D1 metadata also preserves six runs without GPS; unavailable times and distances are not invented.

From the app folder, update cycling data using an official Strava export or a manifest of signed-in GPX downloads:

```sh
python3 scripts/imports/import_bike_history.py --help
python3 scripts/planning/build_app_data.py
```

`raw-data/bikes/2026-10-30/` preserves the newer original GPX files and a hash manifest. Imports deduplicate by activity ID. Browser login cookies and session tokens never enter the repository. Optional `STRAVA_ACCESS_TOKEN` is reserved for an official API token; the current import uses files and does not require it. The full all-sport export remains private in the Family Newspaper archive.

`raw-data/plans/current-targets.json` supplies upcoming app targets; `history-targets.json` preserves older targets. The calendar synchronization tool uses the dated plan selected by `raw-data/route-research/current-plan.json`. Keep these views consistent when editing a plan, then rebuild app data.

## Bike-share receipt history

Reviewed Uber/JUMP/Lime and Lyft/Divvy receipts add 45 bike rides across Seattle, Chicago, Milan, Washington DC and Berlin. Confirmed matches keep their original Strava/Citi Bike record; unresolved cases and scooters stay out. [Receipt facts and repeatable import](raw-data/bike-receipts/README.md) document recorded mileage, deduplication and endpoint routing. Google cycling paths share the existing temporary D1 cache; private email bodies and payment data are never published.

The Rides map also shows [local Census reference outlines](docs/local-reference-boundaries.md) for Ardmore, Penn Wynne, Bryn Mawr, Narberth and Drexel Hill, alongside Havertown's teal 19083 outline. These outlines preserve current city membership and counts.

## Planning and Google Calendar

Use the calendar's numbered address as a destination anchor, not a prescribed loop. Preview nearby purple-line gaps before heading out, allow opportunistic extra streets, then compare the actual GPS with the planned destination before future scheduling. See the [October 31 planned-vs-actual review](docs/run-reviews/2026-10-31-glen-ridge-road.md): full Glen Ridge Road plus extra Windsor Park Lane coverage.

Prioritize unfinished streets within 19083, vary neighborhoods, target entire connected streets, and generally keep the one-way walking approach under two miles unless an exception was approved. GPS proximity does not guarantee CityStrides completion. The boundary is a Census ZCTA approximation, not exact USPS delivery coverage.

**Calendar locations must be numbered street addresses near each segment's midpoint.** Keep cross streets and one-way mileage in the title, without a weekday/date prefix (the event date is already on the calendar); preserve the exact navigation address in the location field for Apple Watch navigation. Combined outings may have consecutive events for separate streets.

Authenticate Google Workspace CLI privately with `gws auth login --services calendar` and check `gws auth status`. Alternatively set `GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE` to a private OAuth credentials file outside this repository. No Workspace API key is required. From the app folder:

```sh
python3 scripts/calendar/sync_plan.py          # preview
python3 scripts/calendar/sync_plan.py --apply  # write and read back
python3 scripts/calendar/sync_plan.py --verify
```

The tool checks unrelated conflicts and preserves existing event reminders. `GOOGLE_CALENDAR_ID` defaults to `primary`.

## Public repository and change tracking

This repository is public and includes precise GPS traces and dated destinations with the owner's approval. Only the blank root `sample.env` template may be committed. Never commit real environment files, OAuth credentials, refresh tokens or Cloudflare tokens. Run `python3 "Tanstack Start App/scripts/checks/check_public_commit.py"` before every commit; CI checks tracked content too. The credential check permits root `sample.env` only with blank assignments; it blocks populated values and all real environment files.

All changes, including new drafts, go through a pull request for tracking. Merge each PR into `main` as soon as the draft works and applicable checks pass, then continue through new PRs. Do not leave draft PRs open. Deploy the merged app with the command above.

## Time-lapse videos

The **Time lapses** tab plays downloadable H.264 MP4 videos stored in the dedicated Cloudflare R2 bucket `running-routes-media`. The Worker binding `TIMELAPSE_MEDIA` streams only explicitly listed video/poster filenames at `/media/`, with byte-range support for seeking. Bucket listing and uploads are not public endpoints. Videos do not load until requested.

The 2026 edition contains all 201 GPS runs dated January 2–October 30 in the current source, ordered by Eastern date/time. The current 1080×1920 (9:16) Story edition places the date and daily mileage/run count above a Google map, with full-year progress, a growing cumulative mileage counter and line graph below it. Orange draws the current run and purple preserves earlier runs. The clip is 54.25 seconds. The same main map switches locations for travel runs; there is no side map. Google branding and provider attribution stay visible. Rides and activities without GPS are excluded. The video is a snapshot, not an automatic feed.

To reproduce it, from `Tanstack Start App` with Python video dependencies installed in a virtual environment:

```sh
pip install -r scripts/videos/requirements.txt
python scripts/videos/prepare_distances.py --archive /private/path/to/strava-export.zip --year 2026 --output ../raw-data/runs/2026-distances.json
python scripts/videos/render_story.py --year 2026 --output /private/tmp/running-routes-videos --basemaps /private/path/to/basemaps.json
python scripts/videos/publish.py /private/tmp/running-routes-videos --manifest /private/tmp/running-routes-videos/runs-2026-story-v2.json
```

Keep the generated MP4/JPEG in R2, not Git. Commit the audit metadata from the output JSON into `raw-data/videos/` and update `src/components/timelapses.json` (omit activity IDs from the interface manifest). The media route allowlist is generated from the checked-in video catalog. Merge the tracking PR and deploy. Metadata records source/video SHA-256, included activity IDs, frame dimensions and duration. Rendering uses five attributed, full-viewport Google Maps background captures made with `/video-map` for this personal recreational video. The local basemaps JSON lists each capture filename, area ID/label, exact center latitude/longitude and integer zoom. For the Story edition capture at 1080×810 with heading north; do not rotate or tilt. The landscape renderer remains available using 1280×720 captures. The renderer uses Web Mercator to align GPS tracks, checks every included coordinate fits its area, and leaves the bottom attribution strip intact. No bulk tile download or standalone basemap dataset is included in the repository.

The default app view selects today's scheduled run in America/New_York, or the next scheduled day if today has none. Reopening the app after backgrounding resets to that view; expired target dates are excluded. Large teal/purple arrows page through scheduled days, with separate street chips for combined outings. Navigation remains in Google Calendar, so the map has no Navigate button. City selector opens a geographic area chooser, initially fitting the largest recorded area rather than the world. The city selector separates Havertown, Ardmore, Narberth, Horsham, Coopersburg, Ridgefield, New York City and Philadelphia using Census boundaries. Each activity is assigned once by its median GPS coordinate; city mileage sums whole recorded activities rather than clipping miles at municipal limits. Suburbs use Census ZIP Code Tabulation Areas, and NYC/Philadelphia use incorporated-city boundaries. Other locations retain approximate regional groups. Source polygons and queries are retained in `raw-data/geography/city-regions.json`.

`/video-map` is a full-viewport Google Maps capture helper for the personal time-lapse. Choose an area, wait for Map ready, then hide controls. Escape restores them. Capture only the handful of area backgrounds needed for the video, preserving the full map, Google logo and provider attribution. Recreational video attribution guidance: https://about.google/brand-resource-center/products-and-services/geo-guidelines/ .

The Story mileage source is `raw-data/runs/2026-distances.json`: 189 recorded Strava distances from the numeric meter field in the private account-export CSV, plus 12 recorded numeric meter distances read from the signed-in Strava website and cross-checked against downloaded original FIT sessions. The backfill now uses the website numeric meter field, cross-checked against original FIT session distances, rather than rounded display miles or simplified GPS geometry. Separate GPS lines are never bridged. The raw private CSV/ZIP and original FIT sensor files stay outside Git; only the selected public run IDs, distances and provenance are retained here. Daily totals group by America/New_York date. The current video contains no geometry-estimated distances, so its totals have no tilde. The cumulative curve uses calendar dates on its x axis and starts from zero on January 1; year progress is measured against the full year rather than ending at 100% in October. Final totals are 201 GPS runs on 199 days, 669.23 miles through October 30. The renderer validates source hashes, complete activity coverage and distances before encoding.

`raw-data/runs/2026-strava-recorded-backfill.json` records the 12 activity URLs, displayed mileage precision and original FIT hashes. `prepare_distances.py` automatically applies this recorded backfill when present.

## Daily Strava import and D1 storage

The Worker imports **runs and rides at 7 AM, 10 AM, and 7 PM America/New_York**. Cloudflare cron `0 11,12,14,15,23,0 * * *` covers both UTC offsets; the handler checks Eastern local time, including daylight saving transitions. One Durable Object serializes imports and skips duplicates only within the same scheduled time slot, allowing all three daily imports. Each poll reconciles the previous 30 days, upserts activities by Strava ID into D1, and stores GPS paths in R2. Both maps and City Stats merge the live records without counting existing Strava IDs twice. This imports workouts already available in Strava; Apple Health must still send them to Strava first.

The current connection uses the owner's explicitly authorized **private browser session** with Strava's signed-in website, not the official OAuth API. Set `STRAVA_WEB_COOKIE` and `STRAVA_SYNC_ADMIN_TOKEN` only in the ignored root `.env` (blank placeholders in committed root `sample.env`), then run `npm run deploy` inside the app. The deploy helper installs them as private Worker secrets. The session is limited to requests to `www.strava.com`; redirects are not followed. Its signed-in athlete ID must match `STRAVA_ATHLETE_ID=14049141`. Cookies never enter D1, public JSON, Git or logs. When Strava expires the session, status becomes `needs_browser_login`; replace the private secret after signing in again. OAuth client credentials are not configured for the current browser-session setup. Strava’s [current API setup guide](https://developers.strava.com/docs/getting-started/) requires a subscription to create an API app (checked November 1, 2026).

Every import reconciles at least the previous 30 days, overlapping the last successful checkpoint by 30 days too. This catches workouts that Apple Health uploads to Strava several days after recording; successful sync status does not prove every Watch workout has reached Strava. All pages of activities are read until the cutoff, and supported runs and cycling activities are upserted by ID. Numeric recorded distances are used, other sports are excluded, and newly discovered GPS activities download their original GPX. Runs and rides stay separate in their respective maps and running street coverage. Disconnected GPX segments stay separate. Failures preserve the previous success checkpoint. Website changes or expired sessions can interrupt this integration; check `/api/strava-sync/status` for the last successful import.

Storage is intentionally duplicated for now:

- **D1 `running-routes` / binding `RUNS_DB`:** indexed activity metadata, dates, recorded distance and GPS object references. Initial snapshot: 1,880 runs, 1,874 with GPS, six without GPS.
- **R2 `running-routes-media`:** baseline `runs/history.geojson`, new `strava/tracks/<id>.geojson`, normalized incremental `strava/latest-runs.json`, and videos.
- **Repo `raw-data/runs`:** retained GPS files, selected activity metadata in `activities.json`, distance provenance and explicit snapshots. The original private all-sport export and FIT sensor files remain outside Git.

The public `/api/strava-sync/runs` endpoint retains its original name for compatibility but returns both runs and rides. It reads D1 metadata and merges incremental GPS with the detailed checked-in tracks. Only selected distance, time and GPS fields are exposed. Heart rate, notes and authentication data are excluded. The runtime importer does not push to GitHub: refresh repo snapshots explicitly and use a tracking PR, immediately merged after validation. This keeps runtime updates separate from versioned snapshots while retaining both copies.

```sh
# From Tanstack Start App
npm run test
python3 scripts/imports/strava_sync.py                  # status
python3 scripts/imports/strava_sync.py --run            # protected manual import
python3 scripts/imports/snapshot_run_database.py --write # update repo files for a PR
python3 scripts/imports/seed_run_database.py --sql /private/tmp/runs.sql
# wrangler d1 execute running-routes --remote --file /private/tmp/runs.sql
npm run deploy
```

The schema is in `Tanstack Start App/migrations/0001_runs.sql`. Seeding upserts by ID and rejects older snapshot timestamps. Runtime sync does not change future targets or Google Calendar. Those remain an explicit planning workflow. The header now has one Runs / Bikes / Videos switch; Calendar and the Routes header control are removed.

## Fixed Havertown Story edition

The v3 portrait video keeps one Havertown Google Maps background for the entire year, eliminating travel-map jumps. Only local tracks are drawn; **all 201 runs still count toward daily miles, cumulative miles, the line graph and year progress**, including seven runs away from the fixed map. The 2026 total is 669.23 recorded miles through October 30. This is a dated rendered snapshot, not automatically regenerated by the daily importer. Video and poster live in R2; their hashes and full activity coverage are recorded in `raw-data/videos/runs-2026-story-v3.json`.

## City explorer and mileage

The header uses a map-pin icon, Running Routes title, illustrated Runs / Bikes / Videos controls, mapped-activity counts and total recorded GPS miles. Video mode hides those activity metrics. City selector opens the recorded areas for the active sport. Selecting a city enters exploration mode: closing X dismisses only the picker, preserves that city and viewport, and leaves the route card hidden. **Upcoming run** explicitly returns to the scheduled plan. Opening the picker again keeps the selected area.

Each option shows the total recorded miles and activity count. Clusters sharing the same named region are combined into one city-selector entry and mileage total. Whole activities are assigned to a GPS area; these are regional clusters (roughly 45 km), not mileage clipped to legal city boundaries. GPS-less activities cannot be assigned to a city. Recorded distances are attached to the generated map assets from `raw-data/runs/activities.json` and `raw-data/bikes/recorded-distances.json`; runtime Strava data can update them. Missing mileage is marked as a partial subtotal rather than estimated from simplified geometry. All 1,877 current GPS runs and 547 GPS rides currently have recorded distances.

`raw-data/geography/history-places.json` records cached place names, source IDs and distances to the nearest named place. Names that previously appeared as coordinates were resolved offline using [GeoNames cities500](https://download.geonames.org/export/dump/), licensed [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). No activity coordinates are sent to GeoNames. Distant offshore tracks use named coastal regions rather than a claimed exact city. Existing broad regional labels remain approximate. Refresh after importing history in a new region:

```sh
# Download GeoNames cities500.zip separately, then from the app folder:
python3 scripts/imports/resolve_history_places.py --cities /private/tmp/cities500.zip
python3 scripts/imports/prepare_bike_distances.py --archive /private/path/strava-export.zip
# Optional --web-backfill reads missing numeric ride distances using the private session.
npm run build
```

The selected GeoNames names used by the browser are generated into `src/components/city-names.json`. Keep the metadata and browser cache in the same tracking PR. Do not commit the private all-sport archive or authentication cookies.

## Home Screen refresh and latest-run review

The header’s circular-arrow **Refresh** button reloads the entire document, not just map data. HTML is served with `Cache-Control: no-store`, so a Home Screen launch/refresh picks up current code and its versioned JS/CSS URLs. Hashed assets and saved videos retain their own caching. Reopen the app once to receive the release that adds the button.

[Open the latest recorded run](https://runningroutes.aifurman.com/?activity=latest), or use **Info → Show latest run**. The requested run is fitted and highlighted in bright gold with a dark navy outline; a linked planned street is orange. Upcoming run returns to the schedule. Numeric `?activity=<id>` links select a particular imported activity. Cold launches without an activity query still open today’s upcoming plan.

See [iPhone Home Screen blur research](docs/ios-home-screen-blur.md) for the distinction between the app’s layout and iOS’s status-area fade. The iPhone-only extra 16px clearance is a mitigation requiring a native-device check; Chrome emulation is not proof that the iOS compositor blur is gone.

## Current video editions

Videos contains two current snapshots: the year-to-date Story through October 31 (202 runs, 673.17 recorded miles), and a rolling seven-day Story for October 25–31 (five runs, 20.21 miles). The week draws each run in gold, converts completed runs to dark blue, and keeps older history light purple. Final stats linger for four seconds: moving time, circular-mean Eastern start time, average distance and total-moving-time pace. There is no redundant introductory heading above the players.

Videos remain dated rendered snapshots; the daily Worker imports GPS/metadata but does not encode MP4s. See [video generation](docs/video-generation.md) for reproducing and rolling the seven-day window forward.

The October 31 weekly video revision uses a taller, unscaled 1080×1000 Google Maps Static API capture (540×500 at scale 2), with the full attribution footer preserved. Its single heading is “Week ending October 31st”; miles display to one decimal, running time to whole minutes, and the final stats linger for four seconds. The Runs/Bikes/Videos switcher reserves the same metrics space in Videos so its size and position stay stable.

The November 4–5 adjustment is logged in `raw-data/route-research/2026-10-31-rodmor-thursday/`: full Rodmor Road on Wednesday, then Grove Place Thursday. Both calendar entries retain numbered midpoint addresses.

## 19083 street progress

Runs → Info shows estimated street coverage, streets run on, partial/untouched counts and streets outstanding. It recalculates in a background worker using the map's latest running GPS, including delayed runtime imports. See [coverage method and reproducible source](docs/19083-street-coverage.md); the result is separate from official CityStrides completion. The remaining Philadelphia-region bucket is split into nearby towns using offline public place names, while preserving single-run destinations elsewhere.

The app uses five bottom tabs: Runs (default), Bikes, Time Lapses, City Stats and Havertown coverage. City Stats combines run count/miles and ride count/miles; city names open running maps when available, while ride-count links open cycling maps. The large route arrows move backward from the first upcoming day through recorded GPS activities and forward into scheduled days. Recorded activity navigation highlights the full saved route. Missing recording days are skipped rather than inventing routes.

City Stats uses TanStack Table with three columns: City, Runs and Bike rides. Counts appear above mileage; Runs and Bike rides sort by count in either direction. The table fills the tab, keeps column headers pinned, truncates long city names and retains full accessible names. City maps offer Back to City Stats for both sports.

The Running Routes header remains visible on every tab, including City Stats. Sort controls use Lucide arrow icons; the table header’s accessible sort state continues to indicate ascending or descending order.

Bikes opens on the latest imported ride. Large arrows browse saved cycling activities in recording order, highlighting each full GPS route; the newest ride has no forward planning action. The cloud importer updates both runs and rides three times daily; Rides opens on the latest imported ride.

Historical run cards show the recorded Eastern start time and average moving pace. Header mileage totals round to whole miles. Atlantic Ocean clusters share one city entry with their combined counts and recorded mileage.

The weekly video uses Sunday–Saturday calendar boxes showing each run’s start time, miles and pace. The active day highlights in gold while its route draws; completed routes turn dark blue over light-purple earlier history. The October 31 revision includes all six imported runs, including the recovered Tuesday workout.

The Havertown tab fills the available space with a map of unfinished road sections in orange, inside the teal 19083 outline. Its overlay shows the percentage of named streets fully covered and the remaining count, including partial streets. Covered portions and historical purple tracks are hidden on this tab; the Runs tab retains the running history. Click an orange road to see its name and coverage percentage. This uses the same GPS estimate as Info, not official CityStrides completion. The cycling tab is labeled **Rides**.

The latest weekly video uses a 1080×1200 Google map (20% taller than the prior calendar edition), captured at 540×600 with scale 2 and its attribution intact. Final statistics show weekly mileage, total running time and average start time; average distance and average pace have been removed from the summary to give the map more room. The daily Sunday–Saturday boxes still show each run’s start time, mileage and pace.

The weekly calendar video uses a separate Sunday–Saturday header above date-and-run cells. Its final weekly mileage, running time and average start share one horizontal row. The map is tightened by 12% around the same Havertown center, with provider attribution preserved; all six routes in the October 31 edition still fit.

The weekly video draws the teal Census 19083 ZIP outline during its opening second, then keeps it visible. The gold calendar outline eases to each run’s day over two thirds of a second before that route draws. Average start is shown throughout, calculated only from runs revealed so far, using the existing circular Eastern-time average. Before the first run it displays a dash.

[November 1 planned-versus-actual review](docs/run-reviews/2026-11-01-gladstone-deferred.md): the latest 4.03-mile run missed Gladstone and added partial Wilson Drive coverage. Monday Walnut/Covington and Tuesday Wilson remain; Gladstone moves to Wednesday, Grove stays Thursday and Rodmor moves to Friday.

Historical run and ride cards show only the date and a compact distance/pace/start–finish caption between Previous/Next buttons. Finish uses recorded elapsed time; missing timing is omitted. Selected GPS routes fit the visible map above the floating card and refit on viewport/card resize; late plan or boundary loads do not replace that framing.

[Instagram Reels editing guide](docs/video/instagram-reels.md) records the approved weekly style, goal intro, Saturday celebration, soundtrack workflow and rendering checks. The supplied [short-form tools reference](docs/video/short-form-tools-reference.md) is preserved alongside it. FFmpeg/Pillow remain the working renderer; Remotion is a future option rather than an installed dependency.

On desktop (1024 px and wider), navigation sits in the header; mobile retains bottom tabs. Runs and Rides open with the paging card visible. Close its X to explore without the card, keeping the selected map view; Show controls restores it.

The sample environment lists only the current browser-session Strava setup (`STRAVA_WEB_COOKIE` and `STRAVA_SYNC_ADMIN_TOKEN`), with no unused OAuth client/refresh-token placeholders. Selecting a city’s rides explicitly clears the latest-ride selection so the map opens that city; the Rides tab itself still defaults to the latest ride.

### Collapsed map controls and sync credentials

Close the paging card to hide the selected gold activity highlight, planned orange streets and weekday pins while preserving the purple recorded tracks, the ZIP outline and the current camera. Show controls restores the selected activity highlight. The small Show controls pill floats at the bottom of the map and restores the plan.

`STRAVA_WEB_COOKIE` authenticates the Worker to Strava; it is never required from public visitors. `STRAVA_SYNC_ADMIN_TOKEN` separately protects the public manual-import endpoint. Keeping the cookie private does not authenticate callers of that endpoint. The scheduled imports does not need the admin token, but manual imports do. Keep both private; do not reuse the Strava cookie as an endpoint password.

### Citi Bike history

The official Lyft export contributes 28 completed NYC rentals: six match existing Strava GPS rides and 22 are new station-only trips. See [source and matching notes](raw-data/citi-bike/README.md). Rides and City Stats include the 22 new trips once, as teal endpoint dots, without invented paths or mileage. Select New York City in City Stats to explore. The private full export is not committed.

### Recovered historical Citi Bike rides

Recovered 202 completed 2014–2015 rides from `andrewfurman/mycitibike`, bringing the combined Citi Bike archive to 230 trips. Six match Strava; 224 new rentals appear in Rides using Google cycling paths between their stations. The 1,862 lifetime account count remains unreconciled. [Recovery sources and importer notes](docs/citi-bike-history-recovery.md).

Citi Bike paths load together as a cached GeoJSON bundle, alongside Strava history. Selecting NYC reuses that data instead of progressively fetching individual rides. Google-generated coordinates remain in the expiring D1 cache, outside Git.


[November 3 reconciliation](docs/run-reviews/2026-11-03-walnut-covington.md): Monday was skipped, Tuesday completed Walnut/Covington, and Wilson moves to Saturday. Gladstone, Grove and Rodmor retain Wednesday–Friday. Bike rides are retrospective only and must not create Google Calendar events. History cards show distance/pace followed by recorded start/end time on a separate line. Activity deep links preserve their sport so rides reopen in Rides.

Citi Bike rentals with missing export mileage contribute zero miles to displayed totals, at the owner’s request. Raw values remain null to preserve that the distance is unknown. Header and city mileage show plain numbers without ≥ symbols; Google cycling paths are used for visualization, not for inventing recorded mileage.

Future run targets include a `neighborhood` label on map cards and Calendar titles/descriptions. See [neighborhood planning guidance](docs/route-planning-neighborhoods.md). Keep numbered midpoint street addresses in Calendar Location.

[November 4–9 plan](docs/run-reviews/2026-11-04-to-09-plan.md) extends upcoming runs through Monday with six simple neighborhood names. Add Nancy Drive Sunday and full Charles Drive Monday; all six approaches remain below two miles.

Upcoming Calendar titles use **Neighborhood · 3.7 mi** for Apple Watch. This is estimated round-trip mileage (twice the midpoint walking approach plus one full target traversal), not the one-way approach. Street/cross-street detail stays in the description; the exact numbered navigation address stays in Location.

[November 4 reconciliation](docs/run-reviews/2026-11-04-hillcrest-completed.md): Hillcrest/Wilson was completed Wednesday instead of Richland/Gladstone. Richland moves to Saturday; the remaining Thursday–Monday plan is preserved.

City Stats uses a spacious desktop table with full city names while retaining the compact mobile table. Selecting a city’s Runs or Bike rides count filters the map to the exact deduplicated activities assigned to that city by the same classification pass used for its totals. Hide upcoming street targets while exploring a city, and show the selected city’s count/mileage in the header. Whole recorded routes remain visible, including portions crossing city boundaries; neighboring cities’ separately classified activities are excluded. Back to City Stats restores the table, and the main Runs/Rides tabs restore the full history.

Current planning rule: [highlight and target unfinished sections only](docs/route-planning.md), with a numbered pin near the main remaining gap. The [November 5–11 plan](docs/run-reviews/2026-11-05-to-11-unfinished-plan.md) moves Grove/Charles pins and adds Willowbrook/Wexford. Runtime highlights refresh from running GPS in a Web Worker; Calendar addresses are reconciled when replanning.

Wednesday November 11 is unscheduled. Wexford is retained as an optional map target, marked Opt and excluded from Calendar appointments and scheduled-day counts.
