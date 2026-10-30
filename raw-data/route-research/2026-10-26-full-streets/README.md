# Full-map view, complete streets and closer destinations

Andrew's October 26 revision: give the map the largest possible area, replace the far Williams Road target, keep one-way destinations under two miles until closer options are exhausted, and cover full Dover Road and the main Chestnut Avenue instead of one block. He explicitly approved full Dover's 2.06-mile approach as an exception.

## Current plan and verified calendar

| Date | Target | Numbered midpoint address | One-way walking | Target length |
|---|---|---|---:|---:|
| Tue Oct 27 | Monroe Avenue: South Harwood–Lansdowne | 8536 Monroe Ave, Upper Darby Township | 1.36 mi | 0.18 mi |
| Wed Oct 28 | Golf House Road: Exeter–Harvest | 20 Golf House Rd, Haverford | 1.91 mi | 0.16 mi |
| Thu Oct 29 | **Rodmor Road, Steel–Belfield, complete street** | 77 Rodmor Rd, Havertown | 1.90 mi | 0.45 mi |
| Fri Oct 30 | **Chestnut Avenue, Haverford–Biddle, complete main street** | 2429 Chestnut Ave, Ardmore | 1.75 mi | 0.73 mi |
| Sat Oct 31 | Fairlamb Avenue: Westgate–Rose Tree | 218 Fairlamb Ave, Havertown | 1.49 mi | 0.18 mi |
| Sun Nov 1 | **Dover Road, Crest–Remington, complete street** | 812 Dover Rd, Wynnewood | **2.06 mi, approved exception** | 0.23 mi |
| Mon Nov 2 | **Coopertown Road, Darby–College, southern stretch** | 10 Coopertown Rd, Haverford | 1.73 mi | 0.56 mi |

Concord Avenue was also over the new limit (2.14 miles), so Rodmor replaces it. Coopertown replaces Williams (2.38 miles). The remaining three original targets are unchanged. Six exact walking distances are below 3,218.688 metres; Dover is the approved exception. Title distances remain rounded to one decimal; exact metres and two-decimal distances are in descriptions. New numbered addresses were reverse-geocoded onto the matching street and then routed from 1700 Manor Road with Google walking directions on October 26. Addresses stay near the arc-length midpoint, not at an endpoint. Distances are approaches only, excluding target traversal and the freeform return. Apple Watch may choose a different approach.

Chestnut is staggered at Lorraine Avenue; follow the short Lorraine connection between its two blocks. The mapped connected main street ends at Haverford Road and Biddle Street. Separate same-named roads beyond Biddle/County Line and in Narberth are excluded. The street geometry comes from the October 26 OSM graph archived with the prior spread-plan snapshot; Google Maps was also inspected for the street naming and Lorraine connection. Coopertown's target is explicitly its southern Darby–College stretch, not the continuation north of College.

All seven existing calendar events were updated in place and individually read back. Weekday/date, cross streets, one-way mileage, midpoint address, target scope and source notes agree with `targets.json`. Guests, end times and reminders were preserved. Monday returns to the ordinary **5:30–6:15 AM** slot for the closer destination; Sunday remains **5:00–5:45 AM** before work, with the November 1 standard-time offset. Other starts stay unchanged. `calendar-verified.json` is the saved readback, not merely a proposed update.

## Coverage and spacing

The source is the same 1,870 running-only GPS tracks; cycling data is unchanged. Dover, Rodmor and the selected Coopertown stretch have no 5-metre samples within 25 m of recorded running tracks. **33.5% of full Chestnut is already near recorded runs**; that overlap is intentional to satisfy Andrew's complete-street preference, and is labeled on the map and calendar. No claim that full Chestnut is never-run or that CityStrides completion is established.

The updated targets have a minimum section-to-section separation of **904 m (0.56 mi)**; consecutive bearings change by 114–161 degrees. Google walking approaches were checked against all other target sections at 25 m tolerance with 5 m samples; no overlap was found. Return meanders remain unpredictable. `spacing-audit.json` contains pairwise measurements and approach comparisons; `mapping-evidence.json` contains updated address/direction evidence without credentials. Previous targets are preserved alongside the new plan.

## Map behavior and verification

Both run and bike pages give the full available area to the interactive map under compact header/toolbar rows. Routes/Rides opens an overlay drawer, and run details are a collapsed floating panel by default. Reload starts with all seven current targets framed, the drawer hidden and details collapsed; no persistent sidebar or large description block takes map space. Runs/Bikes, header counts and Info remain available; provider behavior is unchanged.

Chrome desktop measured the map at 87.5% of the viewport area. Verified route drawer, current names, full Chestnut scope/midpoint navigation, bike switching and map rendering. Transformation repeatability, current target names, 1,870 Run-only features, 530 bike tracks, exact distance limits and calendar agreement were checked. Both HTML pages are mirrored and hash-verified in R2, with the manifest in Git. Large original all-sport archives remain unchanged.
