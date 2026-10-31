# October 31, 2026 — planned destination vs actual run

The calendar destination anchored the outing; it was not a prescribed loop. Andrew reports that previewing the running map helped him spot nearby gaps and pick up extra streets while out. Preserve this flexibility in future plans.

## Planned destination

- **Target:** the full connected length of Glen Ridge Road, from Windsor Park Lane back to Windsor Park Lane, about 414 m / 0.26 miles.
- **Calendar navigation address:** **310 Glen Ridge Rd, Havertown, PA 19083**, near the middle of the target.
- **Approach estimate:** 1.7 miles one way from home by the saved Google walking check. This was an approach distance, not a planned total run or fixed loop.
- **Calendar block:** Saturday, October 31, 5:30–6:15 AM Eastern. The numbered street address remains the navigation anchor for Apple Watch walking directions.

The calendar event's address and times were read back with Google Workspace CLI on October 31. The original target is preserved in [planned-target.json](../../raw-data/run-reviews/2026-10-31/planned-target.json).

## Actual run

[Strava activity 20800939076](https://www.strava.com/activities/20800939076) was imported from the signed-in Strava website, including recorded numeric mileage and the original exported GPS geometry.

| Detail | Recorded result |
| --- | --- |
| Total distance | **3.94 miles / 6,336.18 m**, from Strava's recorded distance |
| Start | 5:23:48 AM Eastern |
| Finish | 6:04:36 AM Eastern, derived from start plus elapsed time |
| Moving time | 39:36 |
| Elapsed time | 40:48 |
| GPS samples | 2,448 points |
| Planned Glen Ridge Road target | 100% of sampled centerline within 25 m of this run's GPS |
| Closest GPS to the calendar address pin | About 29 m; the pin is on a property near the street |

The actual outing covered the planned Glen Ridge Road and more of the Windsor Park Lane loop. It also reused approach/return streets such as Lincoln Avenue, North Eagle Road, Glen Gary Road, Harvard Road, Manor Road and a section of Pennsy Trail. These are GPS-proximity observations, not a claimed turn-by-turn navigation itinerary.

[View the planned road, navigation pin and actual GPS together](../../raw-data/run-reviews/2026-10-31/planned-vs-actual.geojson). Orange is the planned road/pin; pink is the actual run.

## Extra coverage picked up

The comparison uses the **1,874 GPS runs saved before this import** as the baseline. It samples the cached street centerlines about every 5 m and checks whether each sample lies within 25 m of an old run or today's run.

| Street | Near prior running GPS | Near running GPS after today | Newly covered centerline estimate |
| --- | ---: | ---: | ---: |
| Glen Ridge Road — planned target | 0.0% | **100.0%** | About **414 m / 0.26 mi** |
| Windsor Park Lane — extra coverage | 38.1% | **96.0%** | About **712 m / 0.44 mi** |

The two streets together add roughly 1.13 km / 0.70 miles of previously uncovered sampled road centerline. That is a coverage estimate, not extra Strava run mileage. The remaining sampled Windsor Park Lane gap is roughly 49 m; inspect that small gap and CityStrides before calling the entire street complete.

GPS tolerance can include junctions or nearby parallel streets. **These measurements do not establish official CityStrides completion.** The plan history marks Glen Ridge Road as locally completed based on this run; the original plan and comparison evidence remain saved.

Today's track did not overlap the sampled targets on Gladstone Road, Walnut Place, Covington Road, Wilson Drive or Grove Place. Those future targets remain applicable based on this import; previously covered portions of those full streets still count toward their existing gap-filling plans.

## Instructions for future planning

1. Put one exact numbered street address near the target's midpoint in the calendar location so Andrew can tap it on Apple Watch and follow walking directions.
2. Treat that address as a **destination anchor**, not a mandatory route shape. Prefer a whole connected target street; a formal loop is unnecessary.
3. Before heading out, look at the purple running-history map around the destination and approach. Identify a few nearby unfinished streets or gaps that could be added if time and energy allow.
4. Leave room to meander home. An opportunistic extra street is useful progress, even when it was not the calendar's original target.
5. After importing the actual run, compare the saved planned target/address with the GPS. Record which target was reached, extra coverage, remaining gaps and recorded mileage separately.
6. Recheck future targets against the updated running history before scheduling them. Do not accidentally assign a street already picked up as an extra; do not infer official completion from a near-junction GPS match.

Use this review as a worked example. Keep the planned approach mileage, actual total mileage and newly covered street mileage distinct.

## Evidence

- [Selected recorded Strava activity fields](../../raw-data/run-reviews/2026-10-31/activity.json)
- [Original planned target and numbered address](../../raw-data/run-reviews/2026-10-31/planned-target.json)
- [Planned vs actual GeoJSON](../../raw-data/run-reviews/2026-10-31/planned-vs-actual.geojson)
- [Coverage audit, baseline hash, method and future-target checks](../../raw-data/run-reviews/2026-10-31/coverage-audit.json)
- [Updated complete run metadata snapshot](../../raw-data/runs/activities.json) and [GPS history](../../raw-data/runs/tracks.geojson)

No authentication cookies, private activity notes, heart-rate data or original sensor files are included in this review.
