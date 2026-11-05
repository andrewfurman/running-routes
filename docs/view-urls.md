# Shareable map URLs

The app stores view selection in query parameters and restores it on reload and browser Back/Forward:

- Runs overview: `?sport=runs`
- Recorded run: `?sport=runs&activity=<Strava ID>`
- Planned street: `?sport=runs&target=2026-11-06-rodmor-road` (date and normalized street name, independent of list order)
- Recorded ride: `?sport=bikes&activity=<Strava ID>` (existing format retained)
- Recorded walk: `?sport=walks&activity=<Strava ID>`
- City map: `?sport=runs&city=Mainline%2C+PA`, or `sport=bikes` / `sport=walks`
- Time Lapses: `?view=timelapses`
- City Stats: `?view=cities`
- Havertown missing-road coverage: `?view=coverage`

Tab selection, planned-street paging, activity paging and city drill-down update browser history. Latest-activity entries resolve to the actual ID. Explicit links take precedence over the default Havertown overview on a cold load. Normal Runs entry still opens that overview; the first Next selects tomorrow or the next booked day in the one-week window.

Past or fully covered planned targets do not silently show a different street: open their linked recorded activity when available, otherwise explain that the planned target is no longer in the current window. Bare legacy `?activity=<ID>` links infer the sport from synced metadata and the original cycling archive.

Returning to the app from the background refreshes data without resetting a shared view or replacing its URL. Runs-tab clicks explicitly reset to the Havertown overview.
