# Citi Bike station history

Imported November 1, 2026 from the official Lyft privacy export. The full ZIP remains private in Downloads because it contains unrelated car rides, contact details and payment records. This folder contains only selected NYC bike-trip fields and matching evidence; no account/session credentials, payment or car-trip data.

The archive has 41 bike/scooter rows: 28 completed NYC trips, 12 completed trips outside NYC, and one incomplete record. The reported 1,862 account counter is not reconciled by this export. Do not describe this as 1,862 imported Citi Bike rides.

Six NYC trips match Strava using time overlap and proximity of both stations to recorded GPS. They use the existing Strava activity and are not added twice. The other 22 appear as teal station endpoint dots in Rides and count in New York City stats. No route is drawn between station endpoints, and no mileage is inferred. All distance fields are blank in the source. Mileage totals with ≥ are incomplete.

`trips.json` preserves times, coordinates, stable hashed IDs and match decisions. `summary.json` records reconciliation counts. Uncertain matches are retained for review but omitted from app totals; reruns replace files deterministically. One Strava activity can match multiple rentals without counting the Strava ride more than once.

Rebuild using private input archives:

```sh
python3 'Tanstack Start App/scripts/imports/import_citi_bike.py' \
  --lyft-archive /path/to/lyft_data.zip \
  --strava-archive /path/to/strava-export.zip
```

Then build the app, which merges only new endpoint trips into the public ride data. Review the diff and credential scan before committing through a PR.
