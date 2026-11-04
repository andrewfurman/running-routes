# Philadelphia-area reference outlines

The Rides map can show gray Census reference outlines for **Ardmore, Penn Wynne, Bryn Mawr, Drexel Hill and Narberth**. The existing teal **19083 ZCTA** outline supplies the Havertown reference, so it is not drawn a second time in gray. These borders are reference geography. Individual activity assignment is retained, with the requested towns combined in the Mainline presentation group below. Google Maps and the OpenStreetMap fallback use the same reference polygons.

`raw-data/geography/philadelphia-reference-boundaries.geojson` retains all five newly fetched official geometries plus the existing 19083 reference, with labels, GEOIDs, source query URLs, geography types and vintage metadata. The build copies it to `/data/local-reference-boundaries.geojson`; MapView loads it only when `showLocalBoundaries` is enabled and excludes the duplicate Havertown reference. Gray borders do not independently alter activity filtering, counts, mileage or map framing. Click a Google outline or hover a fallback outline for its name and reference-boundary explanation.

Ardmore, Penn Wynne, Bryn Mawr and Drexel Hill are **Census designated places** (statistical communities); Narberth is an **incorporated borough**. The five new polygons come from the official **TIGERweb BAS 2026 service view** and are stored exactly as returned, without simplification, clipping or buffering. Havertown remains the repository's separate **Census 2020 ZCTA19083** reference, not a municipality or CDP.

Current groups combine existing ZIP polygons and nearby-town fallback assignment. Consequently some activity medians are outside these reference outlines. Changing to exact community-based classification would redistribute some rides and must be treated as a separate chosen change; the Mainline presentation group instead combines existing assignments. Do not infer that an existing group is contained by a newly displayed outline, and do not add these reference geometries to `city-regions.json` without reviewing that migration.

Suggested Info wording: **Gray outlines are Census community reference boundaries. Havertown uses ZIP area19083; current midpoint-based groups are unchanged and may extend beyond the reference outlines.**

Sources checked November4,2026:

- [Official TIGERweb service](https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/Places_CouSub_ConCity_SubMCD/MapServer?f=pjson), BAS2026 incorporated-place layer11 and Census-designated-place layer12. Exact queries are embedded in the data.
- [Census geography glossary](https://www.census.gov/programs-surveys/geography/about/glossary.html): CDPs describe named unincorporated communities with statistical, not municipal legal, boundaries.
- [Census ZCTA guidance](https://www.census.gov/programs-surveys/geography/guidance/geo-areas/zctas.html): ZCTAs support mapping ZIP Codes and differ from municipal/community areas.

## Mainline presentation group

City Stats combines the existing Havertown, Narberth, Bryn Mawr, Ardmore and Broomall groups under **Mainline Pennsylvania**, for both runs and rides. It sums counts and recorded mileage and retains every counted activity for map drill-down. Original midpoint assignment and source outlines remain unchanged; this is a regional display group, not a new municipal boundary. Other towns keep their existing groups.
