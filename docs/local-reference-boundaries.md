# Mainline grouping and archived boundaries

City Stats combines Havertown, Narberth, Bryn Mawr, Ardmore, Broomall, Penn Wynne and Drexel Hill under **Mainline, PA**, for both runs and rides. Counts and recorded mileage are summed without duplicating activities, and map drill-down retains every counted route. Existing midpoint assignment is preserved; this is a display group rather than a new municipal boundary.

The local town-border overlays have been removed from both map providers. The teal Census 2020 ZCTA 19083 outline remains for Havertown coverage. Drexel Hill is included in Mainline, PA.

`raw-data/geography/philadelphia-reference-boundaries.geojson` retains the previously fetched Ardmore, Bryn Mawr, Penn Wynne and Drexel Hill CDPs, Narberth borough and existing 19083 source geometry as an archive. These outlines are no longer copied to the app or rendered. They do not define Mainline membership.

The five community polygons were fetched from the official [TIGERweb BAS 2026 service](https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/Places_CouSub_ConCity_SubMCD/MapServer?f=pjson), layers 11 and 12, without simplification. Source queries, GEOIDs and vintage metadata remain in the archive. Havertown uses the separate Census 2020 ZCTA approximation, not a municipal boundary.

## Compact city names and requested groups

Use Mainline, PA; SF Bay, CA; Chicago area, IL; Cancun, MX; and New Orleans, LA. Willow Grove, including the existing Maple Glen/Horsham grouping, combines with West Conshohocken as **Outer Philly Suburbs, PA**. Mainline, PA remains separate. Wilton combines with Ridgefield, CT. Combined groups retain all their counted activities and mileage for map drill-down. Mobile city names wrap when necessary and are never shortened with an ellipsis; Charlottesville, VA remains fully readable.

All resolved city labels use a place name followed by a comma and state/province or country code. Multi-state Lake Tahoe uses CA/NV. The Atlantic Ocean, US label groups the existing U.S.-coast tracks. Unresolved locations remain separate until their names are verified.
