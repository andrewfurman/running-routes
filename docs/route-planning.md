# Populate upcoming running targets

The current goal is **unfinished road sections**, superseding the old rule that highlighted a whole street when only part was missing. Keep the full connected street geometry as an audit reference. Never paint already-covered portions orange to make a full street look like a new target.

1. Refresh the private Strava sync, then the selected running-only repository snapshot. Exclude rides and keep disconnected GPS lines separate.
2. Audit each proposed reference street against running GPS with the shared `auditPlannedGaps` / `calculateStreetCoverage` logic: 20 m proximity and aligned direction, sampled every 10 m. This is a GPS estimate, not official CityStrides credit.
3. Store `missing_coordinates` as **separate lines**. Do not draw a straight connector across covered sections. Reject already-complete targets. Keep `target_coordinates` as full reference geometry, not orange display geometry.
4. Choose the longest meaningful remaining gap. Move the numbered navigation address/pin near its midpoint. Confirm the address has a street number and the correct street and ZIP; a verified building address can be slightly beside the road. For multiple gaps, show all of them and describe the connector without highlighting covered pavement.
5. Verify the Google walking approach is under two miles unless an exception has been approved. Recompute the Watch title estimate as twice the approach plus the total unfinished target length, rounded to a tenth. Connections and a meander home may add mileage.
6. Use simple neighborhood names and vary directions across the week. Check Calendar for travel, appointments and late arrivals. Preserve exact numbered addresses in Location and compact **Neighborhood · 3.7 mi** titles; put street details and gap endpoints in the description. No bike ride Calendar entries.
7. Apply Calendar changes with Google Workspace CLI, read them back, and ensure dates, pins, streets and estimated mileage match the map. Publish through a tracking PR, immediately merged after checks, then deploy.

Recompute stored gaps before writing events:

```sh
node --experimental-strip-types 'Tanstack Start App/scripts/planning/audit_target_gaps.ts'   raw-data/plans/current-targets.json /private/tmp/audited-targets.json
```

Review the output, update numbered addresses and one-way walking distances, then save the canonical targets and matching current-plan snapshot before running `scripts/calendar/sync_plan.py --apply`. The Calendar script rejects unaudited or unnumbered future targets.

The app also recomputes highlights in a Web Worker against the latest merged running history, so a new run can remove covered orange sections. It does not silently move Calendar addresses; reconcile the pin and event when replanning. Both Google Maps and the fallback map draw only the separate missing lines and frame the gaps plus their navigation pin.

Example: November 9 Charles Drive is about 85% covered. Highlight only its approximately 72 m David Drive-end gap and navigate to 205 Charles Dr, rather than the old full-street midpoint at 148 Charles Dr. November 5 Grove Place has two gaps, approximately 113 m and 66 m, with a numbered pin at 11 Grove Pl near the main gap.
