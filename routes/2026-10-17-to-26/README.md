# October 17–26 running plan

Ten calendar days, ending Monday October 26, 2026. Nine confirmed runs, each 5:30–6:15 AM America/New_York. Tuesday October 20 remains an unscheduled Fairlamb option because of the New York train, as Andrew previously requested. Existing October 17–23 events were retained; October 24–26 were added and read back. All locations are verified street-number addresses near segment midpoints; titles include cross streets and one-way walking mileage.

The single ../preview.html opens with only Saturday October 17, Sunday October 18 and Monday October 19 target pins, orange lines and cards visible. The complete 3,211-track GPS history remains available behind them. Use the Target dates selector to switch to the full October 17–26 plan. Hidden targets are removed from both map providers, rather than merely changing card styles. Fit highlighted targets uses only the selected dates.

| Date | Section | Numbered midpoint address | One-way miles |
|---|---|---|---|
| 2026-10-17 | Ellis Road: Garlor Drive to Lawrence Road | 636 Ellis Rd, Havertown, PA 19083 | 1.6 |
| 2026-10-18 | Joanna Road: Olympic Avenue to Prospect Avenue | 122 Joanna Rd, Havertown, PA 19083 | 1.2 |
| 2026-10-19 | Marilyn Drive: Jacalyn Drive to Lawrence Road | 1732 Marilyn Dr, Havertown, PA 19083 | 1.3 |
| 2026-10-20 | Fairlamb Avenue: Westgate Road to Rose Tree Lane | 218 Fairlamb Ave, Havertown, PA 19083 | 1.5 (unscheduled) |
| 2026-10-21 | Oxford Hill Lane: Westgate Road to Rose Tree Lane | 217 Oxford Hill Ln, Havertown, PA 19083 | 1.5 |
| 2026-10-22 | Ivy Rock Lane: Westgate Road to Rose Tree Lane | 219 Ivy Rock Ln, Havertown, PA 19083 | 1.5 |
| 2026-10-23 | Bennington Road: Myrtle Avenue to Grove Place | 17 Bennington Rd, Havertown, PA 19083 | 1.9 |
| 2026-10-24 | Glen Gary Drive: Windsor Park Lane to Rose Tree Lane | 229 Glen Gary Dr, Havertown, PA 19083 | 1.5 |
| 2026-10-25 | Monroe Avenue: South Harwood Avenue to Lansdowne Avenue | 8536 Monroe Ave, Upper Darby Township, PA 19082 | 1.4 |
| 2026-10-26 | Holbrook Road: Fairhaven Road to Bennington Road | 12 Holbrook Rd, Havertown, PA 19083 | 1.9 |

The three new sections are candidates from ../2026-10-16-gap-replan/coverage-audit.json. Each has zero approximately five-metre road samples within 25 metres of any saved GPS line. Core minimum distances are 143.1 m for Glen Gary, 68.5 m for Monroe and 67.3 m for Holbrook. All activity types were included conservatively. This is evidence of no recorded coverage, not proof of never running a road or of CityStrides node status. Verify again after intervening runs; future approaches and meanders can cover later targets.

Public road geometry is the October 7 OSM snapshot from the saved audit. Google Geocoding and Directions verified the three numbered addresses and walking distances October 16. Google names the first road Glen Gary Drive; the older OSM graph calls the same geometry Glen Gary Road. The calendar and map use Google's verified address spelling. Monroe's postal municipality is Upper Darby Township and is preserved exactly for navigation.

Validation: nine calendar events read back, including all three new title/location/description/start/end records; no October 20 run; three cards and pins in the default view and ten in the full view; switching date ranges and providers in Chrome; Holbrook numbered address link and geographic zoom; JavaScript syntax and diff checks. Provider switching exposed a Leaflet canvas initialization failure with the full-history layer; initializing the map view first and using SVG fixed it, then both date ranges and the return to Google were verified.
