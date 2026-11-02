# Citi Bike history recovery

Checked November 1, 2026. The signed-in account profile shows 1,862 rides. The website currently stops after 28 completed rides, with Show More disabled after August 15, 2021. The official Lyft export supplies those same 28 NYC rentals (41 bike/scooter rows in total). This is not a complete lifetime export, and the cause of the missing older records is unconfirmed.

The owner's [mycitibike repository](https://github.com/andrewfurman/mycitibike) preserves 207 records from January 2014 through May 2015. Both master and gh-pages contain the same-sized ride snapshot. Its code joins station names against a saved station feed, then draws straight endpoint lines. It contains data, not a current authenticated downloader. The import recovers 202 completed records; five have no end time/station and are retained only in the source snapshot. One historical station name is absent from the station feed, so Google directions resolves its original station name directly.

Combined sources contain 230 completed NYC trips: six match Strava and 224 add unique rentals. Counts are not presented as a reconciled 1,862-ride lifetime archive. No price, account credential or Google-derived route is needed in the normalized ride records.

## Other projects reviewed

| Project | Relevant capability | Limit |
| --- | --- | --- |
| [fhoffa/code_snippets/baywheels](https://github.com/fhoffa/code_snippets/tree/master/baywheels) | Signed-in GraphQL pagination with station-detail export; supports Citi Bike | Uses the website's available history; not proven to recover this account's cutoff. [Users report success, including a ten-year export](https://www.reddit.com/r/Citibike/comments/13f4ux3/anybody_know_how_to_export_my_ride_history/). |
| [erikleon/citibike2strava](https://github.com/erikleon/citibike2strava) | Uses emailed ride receipts, including route map information, to prepare Strava activities | A possible independent source when receipts survive; not run, and nothing was uploaded to Strava. |
| [rgardner/citi-bike-scraper](https://github.com/rgardner/citi-bike-scraper) | Legacy personal trip scraper | Archived in 2019; predates the current site. |
| [chrnola/citibike-api-docs](https://github.com/chrnola/citibike-api-docs) | Documents a private Citi Bike API | Last code update in 2020; not verified against the current service. |

The GitHub topic page also contains many anonymous system-wide analysis projects; those cannot identify this user's missing personal rides. Another [first-hand investigation](https://www.imer.in/labnotes/01-citibike-citibike-citibike/) documents app history pagination and route polylines, suggesting that the app can expose different detail from the web page. No device rooting, certificate interception or third-party downloader was installed.

## Map behavior

Use Google cycling routes between the original stations, as requested by the owner. Keep the UI simple: Citi Bike rides appear in the Rides map with normal paging. Strava GPS is retained for confirmed duplicates. Source details stay here and in Info; generated Google paths are not represented as recorded GPS in source data.

Only allowlisted, unmatched Citi Bike IDs may request routing. Repeated directed station pairs share a D1 coordinate cache. Google routing coordinates expire after 28 days; daily cleanup removes expired entries, keeping retention below Google's 30-day limit. Returned Google paths are never committed to Git or drawn over OpenStreetMap. The fallback map retains source station endpoints. See [Google routing terms](https://cloud.google.com/maps-platform/terms/maps-service-terms) and [cycling mode documentation](https://developers.google.com/maps/documentation/routes/vehicles).

Nine rentals return to the same recorded station. They remain station dots: a same-station directions query cannot reconstruct the loop taken in between.
