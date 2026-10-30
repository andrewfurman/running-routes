# Havertown runs and Health sync recovery: October 15, 2026

## Sync recovery verified

Imported the missing Health workouts from **September 19 through October 15** using Strava's iPhone Health import list. The web account increased from **4,313 to 4,404 activities (+91)** and **1,842 to 1,868 runs (+26)**. Earlier workouts were left alone. The iPhone app exposes a **90-day** Health list, despite the help article's 30-day wording.

Automatic uploads was already on; it was toggled off and back on and left enabled. Verified in iPhone settings: Background App Refresh and Cellular Data are on. Verified in Apple Health: Strava has **Full Access** to **Workouts** and **Workout Routes**. Existing access was sufficient, so permissions were not expanded. Notifications for new workouts is enabled. One ride lacked GPS information in Health and was imported without location data after the app's explicit notice.

Manual upload success is verified. **Future unattended upload remains to be tested with a newly recorded workout.** No synthetic activity was created. CityStrides is receiving the recovered activities: its completed-street total rose from **673 to 685**, with **9 completed in the past week** at the check. Processing may continue; those are CityStrides account totals, not credit attributed solely to these seven runs.

## Last seven days: October 9–15 inclusive, Eastern time

Seven recovered runs total **22.95 miles**. Six main morning runs total 22.60 miles; the additional October 13 evening run is 0.35 miles.

| Date | Run | Distance | Moving time | Source |
|---|---|---|---|---|
| 2026-10-09 | morning | 4.14 mi | 44:04 | [Strava](https://www.strava.com/activities/20595944023) |
| 2026-10-11 | morning | 3.77 mi | 40:31 | [Strava](https://www.strava.com/activities/20595942975) |
| 2026-10-12 | morning | 3.84 mi | 39:53 | [Strava](https://www.strava.com/activities/20595942972) |
| 2026-10-13 | evening | 0.35 mi | 4:17 | [Strava](https://www.strava.com/activities/20595939594) |
| 2026-10-13 | morning | 3.34 mi | 34:42 | [Strava](https://www.strava.com/activities/20595940684) |
| 2026-10-14 | morning | 3.53 mi | 36:47 | [Strava](https://www.strava.com/activities/20595929845) |
| 2026-10-15 | morning | 3.98 mi | 43:50 | [Strava](https://www.strava.com/activities/20595926176) |

## Planned versus actual

Andrew taps the calendar destination and follows **Apple Watch walking directions**, rather than loading the saved GPX circuit. Reaching one address can change the approach, return leg and distance, and it does not itself prove both ends of a target section were covered.

| Date | Target | Planned / actual | Difference | Target near actual GPS | Saved loop near actual GPS |
|---|---|---|---|---|---|
| 2026-10-09 | Kingsley Road: Delmont/Lakeside to Garden Avenue | 3.91 / 4.14 mi | +0.23 mi | 100% | 65% |
| 2026-10-11 | Myrtle Avenue: Warwick Road to Bennington Road | 3.60 / 3.77 mi | +0.17 mi | 0% | 25% |
| 2026-10-13 | Ashton Road: Holmes/Annabella to North Brierwood Road | 3.30 / 3.34 mi | +0.04 mi | 100% | 27% |
| 2026-10-14 | Wyndmoor Road: South Eagle Road to Oak Way | 3.21 / 3.53 mi | +0.32 mi | 100% | 48% |
| 2026-10-15 | Powder Mill Lane: Delmont Avenue to Remington Road | 3.90 / 3.98 mi | +0.08 mi | 100% | 92% |

- **October 9, Kingsley:** the whole target section is close to the recorded path, but only about 65% of the saved loop was covered. The route was 0.23 miles longer than the estimate.
- **October 11, Myrtle:** the actual run goes northeast of home, while the selected Myrtle section is southeast. None of the target section lies within 30 m of that run. The two target endpoints are approximately **756 m and 489 m** from its GPS track. This run did not achieve the planned Myrtle target; do not mark it complete based on the calendar or similar mileage.
- **October 13, Ashton:** the target section is covered, although only about 27% of the saved loop lies near the actual track. Similar total distance (+0.04 mi) hides a substantially different circuit.
- **October 14, Wyndmoor:** target covered, roughly 48% of the saved loop covered, actual distance +0.32 mi.
- **October 15, Powder Mill:** target covered and the closest match to its plan, roughly 92% of the saved loop covered, actual distance +0.08 mi.
- **October 12 (3.84 mi)** and **October 13 evening (0.35 mi)** have no matching saved calendar-loop plan in this review; they are included as actual runs, not assigned to another day's goal.

### Measurement limits

Percentages are approximate **length-weighted geometric proximity**, not CityStrides node credit or a street-level map-match. Saved lines were sampled at intervals no greater than 5 m; the opposite track at intervals no greater than 2 m, in a local equirectangular projection. Coverage uses a 20 m corridor. The target verdicts are identical at 10 m and 30 m (100% for four, 0% for Myrtle). Distances compare rounded Strava activity values with the original OSM geometry estimates; neither is a measured Apple Maps walking-direction distance. GPS exports may omit portions hidden by map-visibility settings. No claims are made about sidewalk choice or exact turn-by-turn Apple routing.

## Future planning and map

Evaluate the **target segment separately from the loop**. Keep the entire section between named crossroads explicit. For destination navigation, use ordered endpoint waypoints or a clear instruction to continue over the whole section; do not treat arrival at the midpoint as the finish.

The refreshed local Chrome mockup includes the current October 15–17 pins, latest available purple coverage, actual GPS overlays, the saved-loop toggle, and the comparison table. Powder Mill is marked covered in the GPS comparison; Marilyn (October 16) and St Albans (October 17) remain scheduled. No calendar events were changed and no third future day was silently scheduled. Check live coverage and credits before reusing Myrtle or any other apparently incomplete target.

Sources and measurements: [actual-comparison.json](actual-comparison.json). Actual GPS geometry, with timestamps and physiological fields omitted: [actual-runs.geojson](actual-runs.geojson). Planned geometry remains in the dated October 7 and October 13 route sets. The map is an authentic CityStrides screenshot with geographic overlays; it is a static mockup, with a link to the live map. The screenshot and mockup remain in local Codex outputs under the media policy. Original pre-sync notes and screenshot are historical evidence and have been superseded by this recovered-data review.
