# Running Routes

[Open the map](https://runningroutes.aifurman.com/)

A mobile-friendly TanStack Start app for Andrew Furman's running history, upcoming full-street targets and cycling history around Havertown. Switch between Runs and Bikes, explore the full map, page through upcoming destinations, or browse recorded and planned runs in the calendar. Info contains map-provider and iPhone installation options.

## Layout

- `Tanstack Start App/` contains the entire web app: source, icons, manifest, dependencies and lockfile, Vite/TypeScript/Wrangler configuration, deployment and import/planning/calendar scripts. `legacy/` preserves the earlier HTML visualizations and tools.
- `raw-data/` contains public GPS tracks, original recent ride GPX exports, boundaries, current targets and dated research.
- Local `sample.env` documents credential placeholders; local `.env` contains real deployment credentials. Both are ignored and must remain uncommitted.

`.nojekyll` was a GitHub Pages marker, unrelated to npm packages. It is no longer needed: this app runs on a Cloudflare Worker.

## Development and deployment

Use Node.js 22.12 or newer and Python 3. From the repository root:

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

Deployment reads `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID` and optional `GOOGLE_MAPS_API_KEY` from the environment or the ignored root `.env`. It deploys the `running-routes` Worker at runningroutes.aifurman.com and sets the Maps runtime secret. For local Google Maps, put `GOOGLE_MAPS_API_KEY` in ignored `Tanstack Start App/.dev.vars`; otherwise OpenStreetMap works without a key. Info switches providers without a key input field. Browser Maps keys are visible to visitors when used; restrict the key to the required Maps APIs and authorized origins.

On iPhone, open the site in Safari, tap Share, then Add to Home Screen. The app includes an icon and standalone manifest. Maps require an internet connection; this is not an offline navigation app.

## Data updates

The current public dataset contains 1,874 GPS runs and 547 GPS rides through October 30, 2026. The cycling source has 1,445 records; 898 have no drawable GPS track. Runs exclude rides and walks. Recorded calendar entries represent GPS runs; times and distances unavailable in the export are not invented.

From the app folder, update cycling data using an official Strava export or a manifest of signed-in GPX downloads:

```sh
python3 scripts/imports/import_bike_history.py --help
python3 scripts/planning/build_app_data.py
```

`raw-data/bikes/2026-10-30/` preserves the newer original GPX files and a hash manifest. Imports deduplicate by activity ID. Browser login cookies and session tokens are not stored. Optional `STRAVA_ACCESS_TOKEN` is reserved for an official API token; the current import uses files and does not require it. The full all-sport export remains private in the Family Newspaper archive.

`raw-data/plans/current-targets.json` supplies upcoming app targets; `history-targets.json` preserves older targets. The calendar synchronization tool uses the dated plan selected by `raw-data/route-research/current-plan.json`. Keep these views consistent when editing a plan, then rebuild app data.

## Planning and Google Calendar

Prioritize unfinished streets within 19083, vary neighborhoods, target entire connected streets, and generally keep the one-way walking approach under two miles unless an exception was approved. GPS proximity does not guarantee CityStrides completion. The boundary is a Census ZCTA approximation, not exact USPS delivery coverage.

**Calendar locations must be numbered street addresses near each segment's midpoint.** Keep cross streets, weekday/date and one-way mileage in the title; preserve the exact navigation address in the location field for Apple Watch navigation. Combined outings may have consecutive events for separate streets.

Authenticate Google Workspace CLI privately with `gws auth login --services calendar` and check `gws auth status`. Alternatively set `GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE` to a private OAuth credentials file outside this repository. No Workspace API key is required. From the app folder:

```sh
python3 scripts/calendar/sync_plan.py          # preview
python3 scripts/calendar/sync_plan.py --apply  # write and read back
python3 scripts/calendar/sync_plan.py --verify
```

The tool checks unrelated conflicts and preserves existing event reminders. `GOOGLE_CALENDAR_ID` defaults to `primary`.

## Public repository and change tracking

This repository is public and includes precise GPS traces and dated destinations with the owner's approval. Never commit environment files, OAuth credentials, refresh tokens or Cloudflare tokens. Run `python3 "Tanstack Start App/scripts/checks/check_public_commit.py"` before every commit; CI checks tracked content too. The ignored `sample.env` uses placeholders only.

All changes, including new drafts, go through a pull request for tracking. Merge each PR into `main` as soon as the draft works and applicable checks pass, then continue through new PRs. Do not leave draft PRs open. Deploy the merged app with the command above.

## Time-lapse videos

The **Time lapses** tab plays downloadable H.264 MP4 videos stored in the dedicated Cloudflare R2 bucket `running-routes-media`. The Worker binding `TIMELAPSE_MEDIA` streams only explicitly listed video/poster filenames at `/media/`, with byte-range support for seeking. Bucket listing and uploads are not public endpoints. Videos do not load until requested.

The 2026 edition contains all 201 GPS runs dated January 2–October 30 in the current source, ordered by Eastern date/time. The current 1080×1920 (9:16) Story edition places the date and daily mileage/run count above a Google map, with full-year progress, a growing cumulative mileage counter and line graph below it. Orange draws the current run and purple preserves earlier runs. The clip is 54.25 seconds. The same main map switches locations for travel runs; there is no side map. Google branding and provider attribution stay visible. Rides and activities without GPS are excluded. The video is a snapshot, not an automatic feed.

To reproduce it, from `Tanstack Start App` with Python video dependencies installed in a virtual environment:

```sh
pip install -r scripts/videos/requirements.txt
python scripts/videos/prepare_distances.py --archive /private/path/to/strava-export.zip --year 2026 --output ../raw-data/runs/2026-distances.json
python scripts/videos/render_story.py --year 2026 --output /private/tmp/running-routes-videos --basemaps /private/path/to/basemaps.json
python scripts/videos/publish.py /private/tmp/running-routes-videos --manifest /private/tmp/running-routes-videos/runs-2026-story-v1.json
```

Keep the generated MP4/JPEG in R2, not Git. Commit the audit metadata from the output JSON into `raw-data/videos/` and update `src/components/timelapses.json` (omit activity IDs from the interface manifest). The media route allowlist is generated from the checked-in video catalog. Merge the tracking PR and deploy. Metadata records source/video SHA-256, included activity IDs, frame dimensions and duration. Rendering uses five attributed, full-viewport Google Maps background captures made with `/video-map` for this personal recreational video. The local basemaps JSON lists each capture filename, area ID/label, exact center latitude/longitude and integer zoom. For the Story edition capture at 1080×810 with heading north; do not rotate or tilt. The landscape renderer remains available using 1280×720 captures. The renderer uses Web Mercator to align GPS tracks, checks every included coordinate fits its area, and leaves the bottom attribution strip intact. No bulk tile download or standalone basemap dataset is included in the repository.

The default app view selects today's scheduled run in America/New_York, or the next scheduled day if today has none. Reopening the app after backgrounding resets to that view; expired target dates are excluded. Large teal/purple arrows page through scheduled days, with separate street chips for combined outings. Navigation remains in Google Calendar, so the map has no Navigate button. All History opens a geographic area chooser, initially fitting the largest recorded area rather than the world. Nearby runs are grouped within roughly 45 km; labels are approximate regional names and coordinates remain the fallback.

`/video-map` is a full-viewport Google Maps capture helper for the personal time-lapse. Choose an area, wait for Map ready, then hide controls. Escape restores them. Capture only the handful of area backgrounds needed for the video, preserving the full map, Google logo and provider attribution. Recreational video attribution guidance: https://about.google/brand-resource-center/products-and-services/geo-guidelines/ .

The Story mileage source is `raw-data/runs/2026-distances.json`: 189 recorded Strava distances from the numeric meter field in the private account-export CSV, plus 12 GPS estimates from the saved run geometry. Separate GPS lines are never bridged. The raw private CSV/ZIP stays outside Git; only the selected public run IDs, distances and provenance are retained here. Daily totals group by America/New_York date. Tildes mark totals that include estimates. The cumulative curve uses calendar dates on its x axis and starts from zero on January 1; year progress is measured against the full year rather than ending at 100% in October. Final totals are 201 GPS runs on 199 days, approximately 668.53 miles through October 30. The renderer validates source hashes, complete activity coverage and distances before encoding.
