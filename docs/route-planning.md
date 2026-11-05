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

## One calendar week ahead — never seven booked runs

**Only plan today and the next six calendar days, using America/New_York dates.** There must be at most one date for each weekday in the upcoming plan. If a day is off, leave it empty: six booked days are fine, and fewer are fine when there are more rest days or today's run is already complete. Never pull next Thursday or next Friday into the current window to reach seven runs.

Preserve explicit travel/rest exceptions. Wednesday November 11 stays off. The app excludes unscheduled suggestions, completed targets and dates outside this window. Combined streets can share one date, but do not create another occurrence of that weekday. The build rejects active plans beyond the reviewed week's horizon. Keep Calendar and the active map plan aligned; future street ideas remain research, not scheduled events.

Runs opens the Havertown running-history overview on a normal cold load, Runs click and app resume. No planned day is selected in this overview. The first Next press selects the earliest scheduled date after today (tomorrow when booked, otherwise the next booked day within the week). Subsequent arrows move between scheduled dates. Previous from the overview opens the most recent recorded run; Previous from the first planned date returns to the overview. Explicit activity links retain their requested historical activity.

## Boundary roads count too

Public, runnable roads along the 19083 border are part of the goal, including sections where the boundary follows the road. Do not omit a boundary street merely because the road centerline falls just outside the Census outline. A way that follows the boundary for at least 100 m and 40% of its length within a 30 m corridor seeds inclusion of the full connected same-name public street from the cached OSM source. Include its outside sections too; do not include disconnected same-name roads. Marvine Avenue is the initial example. Preserve separate lines and highlight only unfinished portions. This is a ZIP approximation, not a legal township-border inventory. Private/no-foot-access roads remain excluded.

The 19083 outline belongs on Runs and Havertown coverage, never Rides. Map paging uses one continuous camera flight with a small zoom arc; honor reduced-motion preferences.

Camera implementation references: [Google Maps camera methods](https://developers.google.com/maps/documentation/javascript/reference/map) and [fractional/vector maps](https://developers.google.com/maps/documentation/javascript/vector-map). Camera fitting retains room above the activity card; paging uses a 720 ms continuous flight and a small 0.12-level zoom arc instead of an additional full zoom level.

## Daily automatic planning

The active local Codex automation **Maintain upcoming running week** (`maintain-upcoming-running-week`) runs daily at **8:00 AM Eastern**, after the 7:00 AM Strava poll. It returns to the existing running-routes chat and checks the latest synced runs, reconciles completed targets, chooses verified unfinished streets for eligible open days, and updates the canonical plan, Google Calendar, and deployed map.

The one-calendar-week rule above still applies: today plus six days, never seven booked runs. Leave travel/rest days empty, including November 11, 2026. Do not extend the window just to fill a count. Preserve reviewed runs that remain applicable and check Calendar conflicts before filling new dates. Use numbered addresses near the longest missing gap, walking approaches under two miles unless an exception is documented, varied neighborhoods, running-only coverage, and the compact neighborhood/mileage Calendar title. No bike-ride Calendar events.

Use Google Workspace CLI and read back every Calendar mutation. Keep credentials private. Publish necessary repository changes through a passing tracking PR, merge immediately, deploy, and verify the result. If there are no changes, leave the repository and Calendar untouched. If sync, address verification, candidate availability, Calendar conflicts, checks, or deployment blocks progress, report the problem rather than inventing a plan.

This planner runs locally and needs the Mac on with the desktop app running; the existing Cloudflare Strava polling continues independently. Creating the schedule is not evidence that a scheduled planning run has already completed. See the [official scheduled-task guidance](https://learn.chatgpt.com/docs/automations).
