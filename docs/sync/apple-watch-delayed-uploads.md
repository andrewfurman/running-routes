# Apple Watch → Strava → Running Routes

The website imports activities already present in Strava. A successful import does not mean every Apple Watch workout reached Strava.

On October 31, 2026, a signed-in all-sport activity check found no Run activity on Sunday October 25 or Tuesday October 27. Rides were present on both dates and a Walk was present Tuesday. Those missing running workouts could not be recovered from the Strava endpoint at that check. Mirroring initially reported “iPhone Not Found.” Once the phone was nearby and locked, the October 27 5:32 AM run was found pending in Strava’s Health list and manually imported; it became Strava activity 20805752266 (4,815.23 metres / 2.99 miles). The live Worker and repository snapshot now include it. Apple Fitness’s October 25 day view showed two Outdoor Cycle workouts and no recorded run; that Sunday run remains unverified.

The importer now reconciles at least the previous 30 days on every run, including 30 days before the previous successful checkpoint. IDs are upserted, and existing detailed GPS is retained. This catches delayed Watch uploads after newer runs have already synced, covering delayed native Apple Workout imports. The current iPhone app shows a 90-day workout list; a listed workout is not necessarily uploaded. It cannot recover workouts absent from Strava.

On iPhone, use Strava → You → Settings → Manage Apps and Devices → Health. Import the missing workouts individually and keep Automatic Uploads enabled. If absent, inspect the native Fitness/Health workout and Strava's existing Workouts/Routes read permissions. Do not delete an existing activity simply to troubleshoot without checking for duplicates first.

Direct recovery is possible from an Apple Health export or an authorized on-device HealthKit app. The Cloudflare website has no direct HealthKit connection. A direct import should select only workout/GPS fields, keep a complete Health export private, and deduplicate against later Strava uploads.

Sources: [Strava Health integration](https://support.strava.com/en-us/articles/15402024-apple-health-and-strava), [Apple Health export](https://support.apple.com/guide/iphone/share-your-health-data-iph5ede58c3d/ios), [Apple workout route access](https://developer.apple.com/documentation/healthkit/reading-route-data).

On-device settings verified October 31: Automatic uploads, Send to Health and new-workout notifications enabled; iOS Background App Refresh and Cellular Data enabled. Automatic uploads was toggled off then back on. iOS notifications use scheduled delivery, so failure alerts may be delayed. These settings reduce missed uploads but do not guarantee delivery. Confirm the activity appears in Strava after each workout; a run present only in Health is invisible to the Worker.
