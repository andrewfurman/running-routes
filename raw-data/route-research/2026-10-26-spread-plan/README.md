# Seven directions and shared run/bike map · October 26, 2026

Andrew requested a Runs/Bikes switcher in the upper left, statistics in the header, the yellow explanation panel moved off the main map into Info, and geographically separated daily targets. He clarified that he does **not** want yellow lettering throughout the interface. The current Google/OSM provider behavior is unchanged pending his decision after advice: Google is the configured default and OSM remains available as a fallback.

## Revised calendar and map

All seven existing October 27–November 2 events were patched in place and read back. Titles explicitly include weekday, month/day, direction, one-way mileage, street and cross streets. Numbered Google-verified midpoint locations and ordered endpoint links remain mandatory. All walking distances were refreshed from 1700 Manor Road with Google Directions on October 26.

| Day/date | Direction | Street and target section | Numbered destination | One-way |
|---|---|---|---|---:|
| Tue Oct 27 | SE | Monroe Avenue: South Harwood–Lansdowne | 8536 Monroe Ave, Upper Darby Township, PA 19082 | 1.4 mi |
| Wed Oct 28 | N | Golf House Road: Exeter–Harvest | 20 Golf House Rd, Haverford, PA 19041 | 1.9 mi |
| Thu Oct 29 | S | Concord Avenue: Marvine–Dermond | 1107 Concord Ave, Drexel Hill, PA 19026 | 2.1 mi |
| Fri Oct 30 | NE | Chestnut Avenue: Roland–Nelson Place | 2137 Chestnut Ave, Ardmore, PA 19003 | 1.8 mi |
| Sat Oct 31 | SW | Fairlamb Avenue: Westgate–Rose Tree | 218 Fairlamb Ave, Havertown, PA 19083 | 1.5 mi |
| Sun Nov 1 | E | Dover Road: Aikens–Remington | 823 Dover Rd, Wynnewood, PA 19096 | 2.0 mi |
| Mon Nov 2 | NW | Williams Road: Blackburn–Meadows | 21 Williams Rd, Haverford, PA 19041 | 2.4 mi |

Tuesday–Saturday remain 5:30–6:15 AM Eastern. Sunday remains 5:00–5:45 AM before the 6 AM work block. Monday is **5:15–6:15 AM**, allowing an hour for the farther northwest destination. Conflict checks and DST offsets were verified against the live calendar. The saved title, address, description and times were individually read back for every event.

## Separation and coverage evidence

Every pair of target sections is at least **1,131 metres / 0.70 miles** apart, measured between the closest points of their full polylines in UTM 18N. Consecutive direction changes range from 117.3° to 175.2°. All seven sections have **0% of five-metre samples within 25 m of any of the 1,870 archived/recent running GPS tracks**. This supports an unrecorded section in the saved running history; it is not proof of never having run a whole street or of CityStrides credit. Rides and walks remain excluded from the running map.

The Google walking approach to each numbered destination was compared with every other selected target at 25 m tolerance. None overlaps any sampled portion of another target. Andrew's return is a freeform meander, so this reduces accidental coverage without claiming to predict or prevent every return-route overlap. `spacing-audit.json` stores all pairwise distances, bearing changes and approach-overlap results. `mapping-evidence.json` stores numbered-address verification, walking distances and route step geometry, without keys.

The old clustered plan is preserved in `previous-targets.json`. Past actual-run outcomes remain in `history-targets.json`. The three latest run features are reused from the prior reconciliation and deduplicated by activity ID; the running track count remains 1,870. The bike source data is unchanged (530 GPS rides); its display shell and header statistics were updated.

A larger fresh OpenStreetMap street graph was fetched through Overpass on October 26, bounding box south 39.93, west −75.37, north 40.04, east −75.25. The previous cached graph omitted some north/south named streets, which had biased the candidate list southwest. The normalized graph and untouched query response are stored in R2 as `street-graph-2026-10-26.json` and `street-graph-source-2026-10-26.json`, indexed in `tools/r2_path_manifest.json`. `candidates.json` preserves the audited options; the selected full section coordinates and audit metrics are in `targets.json`.

## Display behavior and validation

`tools/route_map_shell.py` supplies the same upper-left Runs/Bikes segmented navigation and Info dialog on both pages. Statistics sit beside the switcher: running GPS count/planned days, or the existing cycling counts/date range. The yellow explanation and configuration controls are inside Info, with ordinary text colors preserved. The original Google key loading and OpenStreetMap fallback behavior remain in place.

Verified both navigation directions, header statistics, Info open/close and live Google Maps rendering in Chrome. The dialog is parsed before the original map script so the hidden configuration controls are available during startup. Both HTML transformations are idempotent; JavaScript syntax, Python compilation, source geometry counts, calendar/map agreement and repository size checks pass. The two single-file HTML map pages are mirrored to R2; code, source metadata and the updated manifest are committed without credentials.
