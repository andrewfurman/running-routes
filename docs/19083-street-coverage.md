# 19083 running coverage

The Runs Info view calculates coverage in a background Web Worker from the current map tracks, including runtime imports. It does not wait for a redeployment to include a newly imported run. Bikes and walks never contribute.

The denominator is unique named public streets with at least ten metres inside the Census 2020 ZCTA 19083 polygon. A fresh October 31 OpenStreetMap/Overpass inventory supplies tags and geometry. The inventory is clipped to the boundary, same-name pieces count once, and duplicate linework is unioned. Public residential, living-street, unclassified, primary/secondary/tertiary and pedestrian roads are included. Motorways, private/no-access roads, foot-prohibited roads, service drives and unnamed paths are excluded. This is a named-street inventory, not CityStrides' separate city/node database.

For each ten-metre street sample, a recorded running segment must be within twenty metres and align within thirty degrees. Opposite running direction is allowed; perpendicular intersection crossings are rejected. Disconnected GPX segments and recording jumps over 250 metres are not joined. A street is “run on” after fifty metres of matched coverage, or half its length if shorter than 100 metres. “Fully covered” uses at least 95% of the in-boundary length to allow modest GPS error. Partial plus untouched streets are outstanding. The panel separately reports street-distance coverage, because long and short streets should not contribute the same distance.

These are approximate GPS results. Parallel roads, GPS drift and OSM errors can change credit. The Census ZCTA approximates ZIP coverage; it is not exact USPS delivery geography. Official CityStrides completions are not asserted.

October 31 baseline after recovering Tuesday's run: 333 streets, 236 essentially fully covered (70.9%), 42 partial, 55 untouched, and 97 outstanding. 278 have been run on in part (83.5%); 85.7 of 104.2 street miles are matched (82.2%). The runtime panel recalculates from the latest runs, so these snapshot numbers may advance. Selected activity metadata and GPS are retained in the repository; the full Health store is not copied.

Reproduce the inventory using the app planning dependencies:

```sh
python scripts/planning/prepare_zip_streets.py --download
python scripts/planning/build_app_data.py
```

The raw query/response, normalized inventory and an audit result live under `raw-data/geography/19083-*`. OpenStreetMap source: https://www.openstreetmap.org/copyright .

## Philadelphia-area city selector

Activities still have one city assignment each and whole recorded mileage. Named Census postal/city regions are applied first. For remaining Philadelphia-area points, an offline nearest-town lookup uses public GeoNames cities500 place centers within 12 km; these are approximate area names. This joins runs just outside the Narberth/Ardmore postal polygons to those town entries and separates Horsham, Maple Glen and West Conshohocken instead of keeping the regional bucket. Single-run locations elsewhere are preserved.

```sh
python scripts/planning/prepare_local_towns.py --cities /private/path/to/cities500.zip
```

The lookup sends no workout coordinates to GeoNames. Public source and CC BY 4.0 attribution are retained in `raw-data/geography/local-towns-source.json` and the Info panel.

The city table fills its tab and scrolls beneath pinned column headers. City names are visually capped at roughly “New York City, NY” width, with full names retained in the button title and accessible name. City-map views link back to City Stats for both sports. Census town boundaries classify residual activity 578893310 as Wilton, CT: its median is in Wilton and about 79.4% of route geometry lies there, versus 20.6% in Ridgefield. The activity still counts once.
