# Reproduce the year and rolling-week video snapshots

Video files and posters live in Cloudflare R2. The repo retains scripts, selected source data, exact activity IDs, statistics and SHA-256 manifests under `raw-data/videos/`. Do not commit private all-sport exports, original sensor files, tokens or the MP4 binaries.

## Current editions

| Edition | Window | Runs | Recorded miles | Length |
| --- | --- | ---: | ---: | ---: |
| Year-to-date Story v4 | January 2–October 31, 2026 | 202 | 673.17 | 54.5 seconds |
| Rolling seven days | October 25–31, 2026 | 5 | 20.21 | 16.67 seconds |

The week includes five recorded outings on October 26, 28, 29, 30 and 31. Dates with no activity are kept in the seven-day timeline; runs are not invented to fill those dates.

## Weekly colors and statistics

- Earlier running GPS is light purple (`#baa4da`).
- The active run draws progressively in gold (`#f6c553`).
- Each finished weekly route becomes dark blue (`#174f9c`) before the next gold route begins.
- The final complete local map stays for four seconds with all weekly routes blue and the full statistics visible.

For October 25–31 the recorded totals are **20.21 miles**, **3:31:23 moving time**, **5:22 AM average start**, **4.04 miles average distance**, and **10:28 per mile average moving pace**.

The seven-day window is inclusive in America/New_York: end date minus six calendar days through the end date. The default end is the current Eastern date; `--as-of` reproduces a historical snapshot. Average pace is total moving seconds divided by total recorded miles, not the unweighted mean of individual paces. Average start is the circular mean of each run's Eastern clock time, rounded to the nearest minute for display. Moving time excludes pauses; elapsed time is preserved separately in the manifest. Missing recorded moving time stops rendering rather than fabricating a pace.

Both videos use the fixed Havertown Google Maps background, preserving the entire attribution strip. Away runs still contribute their recorded mileage and statistics; the camera does not jump to travel locations. All five runs in this weekly edition fit the fixed map. The year includes 195 local map runs and seven away runs in its mileage. Weekly background lines come from all earlier saved running history, not just the current year. GPS geometry is never used as an estimated replacement for the available recorded mileage.

## Generate and publish

Use the existing video Python environment (Pillow and imageio-ffmpeg). From `Tanstack Start App/`, with private inputs outside Git:

```sh
python3 scripts/imports/strava_sync.py --run
python3 scripts/imports/snapshot_run_database.py --write
python3 scripts/videos/prepare_distances.py --archive /private/path/strava-export.zip --year 2026 --output ../raw-data/runs/2026-distances.json
python3 scripts/videos/render_story.py --year 2026 --version v4 --output /private/path/story-v4 --basemaps /private/path/story-backgrounds/basemaps.json
python3 scripts/videos/render_week.py --as-of 2026-10-31 --output /private/path/week-2026-10-31 --basemaps /private/path/story-backgrounds/basemaps.json
python3 scripts/videos/publish.py /private/path/week-2026-10-31 --manifest /private/path/week-2026-10-31/runs-2026-10-31-week.json
python3 scripts/videos/publish.py /private/path/story-v4 --manifest /private/path/story-v4/runs-2026-story-v4.json
```

The basemap config points to the existing 1080×810 Google Maps capture centered on Havertown with its exact zoom and center. Do not stretch it, remove attribution, download bulk tiles or replace it with an unregistered screenshot.

Copy each generated metadata manifest to `raw-data/videos/`. Update `src/components/timelapses.json` with the current weekly and year editions (activity ID lists stay in the raw manifests). Keep previous media filenames in the route allowlist so older app versions and saved links still work. Use a new version/date filename when replacing a published video. Inspect an active drawing frame and the final frame, verify all IDs/mileage and four-second final hold, then use a tracking PR, merge and deploy.

The Cloudflare daily job imports run data only. These local renderer commands explicitly regenerate and upload the video snapshots; no unattended encoding service or GitHub credential was added.
