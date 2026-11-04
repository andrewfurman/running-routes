# Bike-share receipt facts

This archive contains selected factual fields from reviewed bike receipts, not full emails. `trips.json` adds **45 rides**: 35 Seattle, four Chicago, three Milan, two Washington DC and one Berlin. `reconciliation.json` records 23 duplicates retained only in their original Strava/Citi Bike source and five unresolved cases excluded from the map. Four scooter rides are excluded.

The 41 rides with a recorded distance total 72.9 miles. Four Chicago receipts supply no mileage and count as zero. Routing never replaces recorded distance with a Google estimate. Receipt timestamps use the ride's original city time zone. Rental duration is used for receipt pace; it is not Strava moving time.

Google cycling directions supply paths between receipt addresses/stations, using the existing private D1 route cache (28-day expiry). They are available on Google Maps only, not committed as GPX or embedded in the OpenStreetMap fallback. One same-address Seattle rental is a point, not an invented loop. Original Strava GPS is preserved for confirmed matches.

## Repeating the import

`Tanstack Start App/scripts/imports/import_bike_receipts.py --research /path/to/private/reviewed-records.json` accepts a reviewed normalized candidate file. It validates bike mode, intervals, zones and new-ride endpoint pairs; whitelists public facts; and generates stable trip IDs for idempotent imports. Review matching against Strava and existing Citi trips before changing a candidate to `new`. The importer consumes those reviewed decisions; it does not independently perform fuzzy matching.

Keep email bodies, IMAP identifiers, payment/account details, credentials and research screenshots private. New factual fields belong in `trips.json`; Google-derived geometry stays in temporary routing storage.

## Further recovery

The broader Himalaya Gmail search found BCycle confirmations for Indianapolis and Fargo, but these provide only bike numbers and return times, not route endpoint pairs. They have not been imported as mapped rides. Account history may provide the missing stations. Direct Lime emails and other historical operator searches did not yield additional confirmed bicycle endpoint pairs.
