# Weekly running Reels

These are Andrew’s approved editing preferences for Running Routes, recorded November 1, 2026. The current Reel recap covers **October 25–31**, the last completed Sunday–Saturday week. A new Sunday run belongs to the next weekly edition.

## Our style

- Portrait **1080 × 1920, 9:16**. Keep the map as the largest area and use a fixed Havertown view rather than jumping between travel locations.
- Intro hook: **“Trying to run every road in Havertown, Pennsylvania.”** Include the week and short recap totals. Use original GPS artwork on this card, not a basemap with hidden attribution.
- Old routes stay light purple; completed runs this week are dark blue; the active route draws in gold with a dark outline. This contrast matters because Andrew is red-green colorblind.
- Draw the teal **Census 19083 ZIP outline** at the start and retain it. It approximates the postal area; do not present it as an exact municipal boundary.
- Use a real Sunday–Saturday calendar: a separate weekday header, date cells, and each run’s start time, mileage and moving pace. The gold outline slides into place before the route begins.
- Update mileage, running time and average start as runs are revealed. Average start uses only revealed runs and the circular mean of Eastern clock times, including DST. Keep final mileage, running time and average start on **one row**. No final average-distance or average-pace fields.
- After the last Saturday route finishes, use a brief gold-particle burst and gentle, decaying map shake. No flashes or rapid full-screen strobing. Preserve the map provider’s attribution footer during motion.
- Let the map settle, fade the final stats in, and linger for four seconds. Inspect the final frame for legibility and the Reel preview’s interface overlays before posting.

## Timing recipe

| Phase | Current duration |
| --- | --- |
| Goal intro card | 2 seconds |
| 19083 outline draws | 1 second |
| Day outline slides | 2/3 second before each new day |
| Active route draws | 2 seconds per run |
| Brief hold after a run | 1/3 second |
| Saturday burst and map shake | 3/4 second |
| Final stats | 1/2-second fade within a 4-second hold |

The six-run October 31 edition is **25.75 seconds**, encoded as H.264 MP4, yuv420p, 24 fps, with fast-start metadata. This is our current export choice, not a claim about Instagram’s required frame rate.

## What we use from the supplied tools note

| Tool | How it fits this repo |
| --- | --- |
| FFmpeg | Already used through `imageio_ffmpeg` to encode the actual MP4. Use it for trims, transitions, inspection and later audio mixing where needed. |
| Python + Pillow | Current deterministic frame renderer: GPS, intro card, calendar, counters and Saturday motion. This update uses these existing tools. |
| Remotion | A useful next option for reusable React motion templates, titles and frame-driven easing. It is **not installed or used by the current renderer**; do not claim a migration has happened. Its [animation documentation](https://www.remotion.dev/docs/animating-properties) describes interpolation and easing, and recommends frame-driven animation rather than ordinary CSS transitions. |
| ElevenLabs Scribe / local transcription | Useful if we add spoken narration and timed captions. The current map-only video has no speech to transcribe. See [Scribe documentation](https://elevenlabs.io/docs/overview/capabilities/speech-to-text). |
| Resolve / visual editors | Keep available as options when interactive timeline editing, grading or detailed sound work becomes necessary. They are not required for this template. |

The [supplied short-form tools reference](short-form-tools-reference.md) is preserved separately. Its broader trip-vlog suggestions are reference material, not proof that those tools, accounts or integrations are installed here. The main Remotion and Scribe capabilities above were checked against vendor documentation on November 1, 2026; the remaining candidate tools have not been newly evaluated for this repo.

## Music and posting

Andrew’s intended soundtrack for this edition is **“FE!N” by Travis Scott**. Keep the downloadable/site master silent, then select the song and excerpt in Instagram’s music picker when posting, if available for the account. The renderer does not fetch, embed or redistribute a song file. Instagram describes its in-app music picker in [Introducing Instagram Reels](https://about.fb.com/news/2020/08/introducing-instagram-reels/). No post has been published by this workflow.

## Render and verify

From the repository root, using the existing local video Python environment:

```sh
python3 "Tanstack Start App/scripts/videos/render_week.py" \
  --as-of 2026-10-31 --version v7 \
  --basemaps /absolute/private/path/weekly-taller-basemaps.json \
  --output /absolute/private/path/week-2026-10-31-v7
```

The environment needs Pillow, `imageio_ffmpeg`, and the renderer’s existing Python dependencies. The basemap manifest points to a real 1080×1200 Google map image, its center and zoom. Keep basemap capture credentials outside Git.

1. Import/deduplicate running GPS and recorded Strava distance/time before choosing the week. Never include rides in running totals, estimate mileage from a simplified polyline, or bridge disconnected GPS segments.
2. Render the chosen completed week explicitly. Retain all weekly mileage even when a travel route is outside the fixed Havertown view.
3. Inspect the intro, border draw, mid-slide, active route, Saturday burst, stats fade and final frame. Confirm there is no route motion during a calendar transition and average start has no future runs in it.
4. Decode the finished MP4, confirm portrait dimensions/duration and that the music-free master has no audio stream. Check credits are intact and all local weekly routes fit.
5. Upload the MP4 and poster with `scripts/videos/publish.py`. Commit selected JSON metadata, source scripts and documentation; keep rendered video files out of Git.
6. Update `src/components/timelapses.json`, retain previous media URLs, use a tracking PR, merge after checks, deploy and verify playback from the public site.
7. Download the current master, preview it in Instagram, select the soundtrack excerpt, check title/stats visibility and choose the intro as the cover. Publishing requires a separate user request.

All script paths in the final two steps are relative to `Tanstack Start App/`. Each rendition records source hashes, recorded totals, duration, palette and edit settings in its metadata so later edits are reproducible.

## Map-first update (November 1)

The weekly Reel begins directly on the map with the progress date and the goal of running every road in Havertown as a light text overlay. Do not prepend a separate dark title card. After the final Saturday route, use a large orange/gold fireball with a hot pale core and sparks, then let it clear before the weekly statistics fade in. Preserve the map attribution throughout. The v8 master is silent and 24.5 seconds long.

## FE!N timing edit (v9)

Use the original studio recording of **FE!N (feat. Playboi Carti)**, not the remix, live version or official music-video edit. Reference: [official artist audio](https://www.youtube.com/watch?v=U-l4ya3ejko). A private first-40-second excerpt was used for analysis. The sustained bass entrance is at approximately **23.44 s** in that reference. The silent master begins the fireball at **23.458 s** (24 fps frame rounding), completes the explosion, and holds weekly stats for **eight seconds** with a restrained bass-attack pulse. The full video is about **32.96 seconds**.

In Instagram, add the original song starting at **0:00**, and check that the strong bass entrance lands on the fireball at **0:23.46**. Instagram's available trim/version can differ; if necessary slide its audio until those two cues coincide. The public file has no embedded music. No Instagram post was made.

`raw-data/videos/fen-timing-cues.json` contains only derived bass-attack strengths and timing metadata, not audio. Original reference audio stays outside Git. Rebuild cues from a local reference with `scripts/videos/build_audio_cues.py`, then render with `--audio-cues raw-data/videos/fen-timing-cues.json --stats-hold 8`. Do not substitute a guessed BPM for the measured pulse.
