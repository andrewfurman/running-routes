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

The 2026 edition contains all 201 GPS runs dated January 2–October 30 in the current source, ordered by Eastern date/time. The main map builds Havertown coverage while an inset draws every run, including travel outside the area. Rides and activities without GPS are excluded. The video is a snapshot, not an automatic feed.

To reproduce it, from `Tanstack Start App` with Python video dependencies installed in a virtual environment:

```sh
pip install -r scripts/videos/requirements.txt
python scripts/videos/render_year.py --year 2026 --output /private/tmp/running-routes-videos
python scripts/videos/publish.py /private/tmp/running-routes-videos --year 2026
```

Keep the generated MP4/JPEG in R2, not Git. Commit the audit metadata from the output JSON into `raw-data/videos/` and update `src/components/timelapses.json` (omit activity IDs from the interface manifest). When adding another year, add its filenames to the media route allowlist. Merge the tracking PR and deploy. Metadata records source/video SHA-256, included activity IDs, frame dimensions and duration. Rendering uses locally saved OpenStreetMap street geometry and Census boundaries, with attribution; it does not capture or export Google map tiles.
