# Running reconciliation · October 28, 2026

On Tuesday October 27 the planned Monroe Avenue run was not done: the Strava activity list shows rides and a walk, but no run. On Wednesday October 28 Andrew ran 3.67 miles at 5:28 AM; [CityStrides marked Monroe Avenue complete](https://citystrides.com/activities/102219129), together with South Kirklyn Avenue and West Llandaff Road. The [Strava run](https://www.strava.com/activities/20762546856) has 37:33 moving and 39:27 elapsed. Every sample of the planned Monroe section is within 15 m of its GPX track (max nearest distance 13.1 m).

The Tuesday event is marked as a missed plan; Wednesday now records the actual 5:28:18–6:07:45 run. Golf House Road was not covered and moves to Thursday; the other targets shift one day to preserve the alternating directions and all six destinations. All event times/locations/titles/descriptions were read back after saving. The Tuesday November 3 run is new; other dated events were updated in place. Sunday remains 5:00–5:45 AM before the 6:00 AM work block; the fall clock change is reflected in offsets.

| Date | Target | One-way walking | Calendar time |
|---|---|---:|---|
| Thu Oct 29 | Golf House Road, Exeter–Harvest | 1.9 mi | 5:30–6:15 AM |
| Fri Oct 30 | Rodmor Road, Steel–Belfield (full street) | 1.9 mi | 5:30–6:15 AM |
| Sat Oct 31 | Chestnut Avenue, Haverford–Biddle (main connected street) | 1.7 mi | 5:30–6:15 AM |
| Sun Nov 1 | Fairlamb Avenue, Westgate–Rose Tree | 1.5 mi | 5:00–5:45 AM |
| Mon Nov 2 | Dover Road, Crest–Remington (full street) | 2.1 mi | 5:30–6:15 AM |
| Tue Nov 3 | Coopertown Road, Darby–College | 1.7 mi | 5:30–6:15 AM |

All numbered midpoint addresses and Google walking approaches were verified October 26; distances are one-way and do not include the target traversal or return. Dover's 2.06-mile approach remains Andrew's explicitly approved exception to the under-two-mile limit. Chestnut intentionally includes previously covered blocks and uses the short Lorraine connection between staggered sections.

## Evidence and coverage

Two official GPX downloads were obtained in the authenticated Strava UI: October 26 run `20739791044` (4.31 mi) and October 28 run `20762546856` (3.67 mi). Both were absent from the previous map. Their untouched GPX files are stored in the private R2 research archive, with checksums and provenance in `activity-exports.json`; simplified Run-only features are in `new-tracks.geojson`. The map now shows **1,872 distinct running GPS tracks**; rides and walks remain excluded. Existing all-sport exports are preserved separately.

All six target geometries were audited at 5-metre intervals against the entire 1,872-track running history and against each new run separately; results are in `coverage-audit.json`. Golf House, Rodmor, Fairlamb, Dover and the Coopertown section have 0% of samples within 25 m of recorded runs. Full Chestnut remains 33.5% near recorded runs, an intentional complete-street target. Neither new run changed that status. GPS proximity is evidence, not a guarantee of CityStrides node credit.

The same six target sections remain at least **904 m (0.56 mi)** apart. Walking approaches were checked against the other target sections in the October 26 plan; no overlaps were detected at 25 m tolerance. A freeform return may differ. The prior plan is retained in `previous-targets.json`; `history-targets.json` retains the missed Tuesday and completed Wednesday records, and the verified calendar results are in `calendar-verified.json`.

The full-window map opens by default on October 29–November 3, with the Routes drawer and details collapsed. The new running HTML and GPX files are mirrored to R2, with verification and path manifest; the separate bike map remains unchanged.
