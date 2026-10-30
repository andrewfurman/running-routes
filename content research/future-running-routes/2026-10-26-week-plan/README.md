# Seven-day run plan · October 27–November 2, 2026

Checked Andrew's signed-in Strava activity list and CityStrides in Google Chrome on October 26. The latest recorded activity is a Sunday October 25 bike ride, not a run. Sunday has two rides and no run. No Monday October 26 run was visible at review; today's original Holbrook appointment remains unchanged and completion is unverified.

## Reconciled actual runs

- Friday October 23: Strava 20698250814, 3.71 mi, 37:51 moving. All samples of the planned Bennington section are within 15 m of this run (maximum 12.8 m). Calendar event now records the actual GPS start/end, 05:09:19–05:47:21 AM.
- Saturday October 24: two consecutive recordings, 20710360307 (2.50 mi, 25:39 moving) and 20710360282 (0.97 mi, 10:08 moving), total 3.47 mi. Oxford Hill target covered within 15 m, maximum 2.8 m. [CityStrides 102038028](https://citystrides.com/activities/102038028) explicitly lists Oxford Hill Lane and Wendover Drive completed. Calendar records both activities and exact GPS timestamps.
- Sunday October 25: missed Monroe run, consistent with Andrew's report and the Strava list. The historical appointment is marked missed, with Monroe rescheduled to Tuesday October 27. Bike rides are excluded from run coverage.

## Seven booked destinations

All locations are Google-verified street-number addresses near the target segment midpoint. Mileage is the one-way **walking** approach from 1700 Manor Road, checked with Google Directions on October 26. Apple Watch may choose a different walking route; target traversal and return add mileage. Reach one endpoint, traverse the entire section, then meander home.

| Date | Street | Numbered destination | One-way | Eastern time |
|---|---|---|---:|---|
| Tue Oct 27 | Monroe Avenue | 8536 Monroe Ave, Upper Darby Township, PA 19082 | 1.4 mi | 5:30–6:15 AM |
| Wed Oct 28 | Fairlamb Avenue | 218 Fairlamb Ave, Havertown, PA 19083 | 1.5 mi | 5:30–6:15 AM |
| Thu Oct 29 | Marilyn Drive | 1732 Marilyn Dr, Havertown, PA 19083 | 1.3 mi | 5:30–6:15 AM |
| Fri Oct 30 | Walnut Hill Lane | 217 Walnut Hill Ln, Havertown, PA 19083 | 1.5 mi | 5:30–6:15 AM |
| Sat Oct 31 | Rose Tree Lane | 1837 Rose Tree Ln, Havertown, PA 19083 | 1.7 mi | 5:30–6:15 AM |
| Sun Nov 1 | Windsor Park Lane | 342 Windsor Park Ln, Havertown, PA 19083 | 1.8 mi | **5:00–5:45 AM** |
| Mon Nov 2 | Glen Ridge Road | 317 Glen Ridge Rd, Havertown, PA 19083 | 1.7 mi | 5:30–6:15 AM |

Sunday starts earlier because Dad Working Sunday begins at 6:00 AM. Google Calendar events use America/New_York; November 1–2 correctly use UTC−05:00 after the fall clock change. The other five dates use UTC−04:00. All seven slots were checked against Andrew's existing events before insertion, and all ten changed/created records were individually read back.

## Coverage and sources

The purple overlay now contains **1,870 distinct GPS runs**: the previous 1,867 plus three official GPX exports. Rides, walks, hikes and all other sports remain excluded; the complete source archives and separate Bike LifeMap are preserved. New raw GPX files are unchanged, indexed by SHA-256 in `latest-activities.json` and `tools/r2_path_manifest.json`, and stored in R2. `new-tracks.geojson` holds normalized display geometry.

`coverage-audit.json` compares all 1,870 run tracks to approximately five-metre target samples in UTM 18N with 15 m and 25 m thresholds, including individual Friday/Saturday matching and candidate street sections from the saved street graph. Monroe, Fairlamb, Rose Tree, Windsor Park and Glen Ridge have no sampled point within 25 m of recorded run GPS. Marilyn retains an 84.3% gap and Walnut Hill a 93.3% gap; these are partly covered targets, not wholly never-run streets. GPS absence is not proof a street was never run or of CityStrides completion credit. Intervening approaches/meanders may cover future targets, so recheck on the next update.

`address-research.json` preserves Google geocoding verification and walking-distance evidence, without API credentials. `calendar-planned-changes.json` records intended writes; `calendar-verified.json` contains saved event readbacks. `history-targets.json` preserves past-plan outcomes separately from the seven new destinations in `targets.json`.

The single HTML map in R2 defaults to all seven new destinations. `current-plan.json` selects this snapshot; the local server applies the same data idempotently. Full-plan history remains available. `tools/running_route_updates.py` now derives counts, dates and selection from the current snapshot so it can display seven-day plans without retaining old three-day labels or an unscheduled-Tuesday message.
