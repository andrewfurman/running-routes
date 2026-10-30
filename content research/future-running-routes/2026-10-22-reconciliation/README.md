# Actual runs and next three days · October 22, 2026

Verified in signed-in Google Chrome against Strava athlete 14049141, the local Google map, CityStrides user 7315, and the running calendar.

- Tuesday October 20: no run. Strava lists only a 1.42 mi evening walk in Manhattan. The run plan already left Tuesday explicitly unscheduled for NYC travel; there was no run calendar event to remove.
- Wednesday October 21: different 2.52 mi run, 26:07 moving, start 5:33 AM. None of the Oxford Hill target's samples are within 25 m of this run. CityStrides activity 101911395 lists zero completed and zero progressed streets. The historical calendar event now records the actual outcome, retaining the original planned time block/destination as context.
- Thursday October 22: 3.78 mi, 39:56 moving, start 5:32 AM. All samples of Ivy Rock Lane and Glen Gary's planned section are within 15 m of this run (maximum 4.4 m and 7.0 m). CityStrides activity [101948125](https://citystrides.com/activities/101948125) explicitly lists **Ivy Rock Lane and Glen Gary Road completed**. The old plan calls the latter Glen Gary Drive; CityStrides calls the street Glen Gary Road. Do not schedule that already covered section again.
- Sunday October 18's 3.55 mi run also covered the Ellis target within 25 m; this is recorded in the full-plan map history. No Monday October 19 run appears in the Strava activity list (two rides only).

## Next three days

All at 5:30–6:15 AM Eastern, with verified numbered midpoint destinations retained from the October 16 geocoding/Google walking review. Miles are one-way from 1700 Manor Road; Apple Watch can choose a different walking path. Reach an endpoint and traverse the whole section before meandering home.

| Date | Target section | Calendar location | One-way miles | GPS audit |
|---|---|---|---:|---|
| Fri Oct 23 | Bennington: Myrtle Avenue–Grove Place | 17 Bennington Rd, Havertown, PA 19083 | 1.9 | 92.2% beyond 25 m of running GPS; partial gap, not wholly unrun |
| Sat Oct 24 | Oxford Hill: Westgate Road–Rose Tree Lane | 217 Oxford Hill Ln, Havertown, PA 19083 | 1.5 | 100% beyond 25 m; replaces completed Glen Gary |
| Sun Oct 25 | Monroe: South Harwood Avenue–Lansdowne Avenue | 8536 Monroe Ave, Upper Darby Township, PA 19082 | 1.4 | 100% beyond 25 m |

Five calendar records were patched and individually read back: Wednesday and Thursday actual outcomes, and Friday–Sunday plans. See `calendar-verified.json`; Tuesday remains unscheduled. Monday October 26's existing Holbrook section remains applicable (all samples beyond 25 m), with its event unchanged.

## Data and map

Compared the running preview with Andrew's open CityStrides LifeMap in Chrome after he spotted cycling tracks. The corrected purple layer includes **1,867 GPS runs only**; 534 rides, 816 walks, seven hikes and one snowboard activity are excluded from this page. The Bike LifeMap is unchanged. CityStrides also visibly lists the October 20 walk, so its LifeMap is not strictly run-only and the corrected page need not match it exactly.

The unchanged full archive plus earlier supplements had 3,216 drawable tracks. Nine official GPX exports from October 18–22 add three runs, four rides and two walks, producing **3,225 distinct GPS activities**. `latest-activities.json` records source URLs, timestamps, byte lengths and SHA-256 hashes. Raw GPX is unchanged, kept in R2 and indexed in `tools/r2_path_manifest.json`; restore this folder with `tools/media_store.py pull-path`. `new-tracks.geojson` is the small normalized display update committed alongside the plan. Original account-export archive parts remain unchanged.

`coverage-audit.json` compares target samples at approximately five-metre spacing in UTM 18N against all activity types conservatively, with 15 m and 25 m proximity thresholds. `run_only_audit` compares 1,867 runs and drives the current calendar and map coverage labels; `audit` retains the earlier 3,225-activity conservative review. This is a recorded-location audit, not proof that a street was never run. CityStrides credit is reported only when its website explicitly confirmed it.

The main map defaults to October 23–25 and retains full-plan/history selection. `../current-plan.json` selects this snapshot; `tools/running_route_updates.py` applies its targets and deduplicated supplemental GPS to the large R2 page when served. The updated HTML is also mirrored to R2. No Maps key, Cloudflare token, R2 credential, or opaque archive prefix is committed.
