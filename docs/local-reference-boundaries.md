# Mainline grouping and archived boundaries

City Stats combines Havertown, Narberth, Bryn Mawr, Ardmore, Broomall and Penn Wynne under **Mainline Pennsylvania**, for both runs and rides. Counts and recorded mileage are summed without duplicating activities, and map drill-down retains every counted route. Existing midpoint assignment is preserved; this is a display group rather than a new municipal boundary.

The local town-border overlays have been removed from both map providers. The teal Census 2020 ZCTA 19083 outline remains for Havertown coverage. Drexel Hill remains a separate activity group.

`raw-data/geography/philadelphia-reference-boundaries.geojson` retains the previously fetched Ardmore, Bryn Mawr, Penn Wynne and Drexel Hill CDPs, Narberth borough and existing 19083 source geometry as an archive. These outlines are no longer copied to the app or rendered. They do not define Mainline membership.

The five community polygons were fetched from the official [TIGERweb BAS 2026 service](https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/Places_CouSub_ConCity_SubMCD/MapServer?f=pjson), layers 11 and 12, without simplification. Source queries, GEOIDs and vintage metadata remain in the archive. Havertown uses the separate Census 2020 ZCTA approximation, not a municipal boundary.
