# Full-history gap review · October 16, 2026

The complete Strava archive is already committed in ../2026-10-16-strava-history/raw/: 4,404 activity records and the exact original ZIP, split into 24 verified binary parts. This review adds the three GPS activities recorded after that archive: October 15 afternoon ride 20601369992, October 16 morning run 20606504445 (3.59 miles), and morning walk 20608425525 (1.74 miles). Their downloaded GPX files remain unchanged here; source links and hashes are in latest-activities.json. The map now shows 3,211 tracks.

Walnut Place, Pickwick Road and Garden Avenue each had 100% of sampled target points within 15 metres of saved GPS tracks. Replace them with Joanna Road, Oxford Hill Lane and Ivy Rock Lane. The original Chester option was partly covered (66.7% within 25 metres); replace it with a clearer Fairlamb Avenue gap and keep Tuesday unscheduled. Ellis, Marilyn and the existing Bennington section retain substantial unrecorded interiors. Keep October 16 Charles as a past record; do not replace an elapsed run or change its event.

| Date | Target section | Numbered midpoint address | One-way miles |
|---|---|---|---|
| 2026-10-17 | Ellis Road: Garlor Drive to Lawrence Road | 636 Ellis Rd, Havertown, PA 19083 | 1.6 |
| 2026-10-18 | Joanna Road: Olympic Avenue to Prospect Avenue | 122 Joanna Rd, Havertown, PA 19083 | 1.2 |
| 2026-10-19 | Marilyn Drive: Jacalyn Drive to Lawrence Road | 1732 Marilyn Dr, Havertown, PA 19083 | 1.3 |
| 2026-10-20 | Fairlamb Avenue: Westgate Road to Rose Tree Lane | 218 Fairlamb Ave, Havertown, PA 19083 | 1.5 (unscheduled) |
| 2026-10-21 | Oxford Hill Lane: Westgate Road to Rose Tree Lane | 217 Oxford Hill Ln, Havertown, PA 19083 | 1.5 |
| 2026-10-22 | Ivy Rock Lane: Westgate Road to Rose Tree Lane | 219 Ivy Rock Ln, Havertown, PA 19083 | 1.5 |
| 2026-10-23 | Bennington Road: Myrtle Avenue to Grove Place | 17 Bennington Rd, Havertown, PA 19083 | 1.9 |

Method: clip saved GPS to the Havertown study area, project to UTM 18N metres, and compare road samples spaced at approximately five metres against the nearest saved GPS line. Report 15- and 25-metre proximity; GPS/display errors make this an estimate rather than a street-completion test. Candidates must have a core (excluding approximately 30 metres at each end) at least 25 metres from any track. The four chosen replacement sections have zero samples within 25 metres, including their endpoints. This uses all activity types conservatively; none shows a saved run trace either. Absence in the available GPS history is not proof of never having run a road.

Public road geometry came from the previously saved October 7 OpenStreetMap graph; fresh Overpass requests failed. The four selected numbered midpoint addresses and walking routes were verified with Google Geocoding and Directions on October 16. Signed-in CityStrides LifeMap was refreshed, but no new street/node completion claim is made and no completion settings were changed.

All six future calendar events were patched in place and read back. They retain their dates, 5:30–6:15 AM times and numbered locations; titles contain one-way mileage and cross streets. Tuesday has no run event. Both endpoints and the midpoint navigation link are in each description. The separate user-created Charles address event remains untouched.

Reproduce the numerical review with `python3 -m pip install -r tools/requirements-route-audit.txt`, then run this folder's recompute_audit.py. It writes recomputed-audit.json. coverage-audit.json is the saved review; targets.json is the resulting plan. The single ../preview.html embeds the updated plan and all 3,211 GPS tracks.
