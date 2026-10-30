# Seven future Havertown loops

[Review all seven maps](preview.html). Every route is a closed circuit from 1700 Manor Road at Manor and Fairfield. Distances are estimates from the mapped street geometry; the exact circuits are saved as GPX and GeoJSON. The red line is the complete route, and orange marks only a target segment included in that circuit.

## Reuse in a future newspaper

Read `index.json`, choose a `planned-unused` route, and refresh Andrew's signed-in [CityStrides map](https://citystrides.com/users/7315/map#39.98062291391764,-75.31159672723481&14) using Strava authentication. Check the orange section again: this library captures the LifeMap on October 3, not live completion status or Node Hunter results. After use, update `last_used` and `status`; never reuse the same circuit within 31 days. Home route maps are printed only when Andrew asks.

Each folder has a committed street map, a `map.json` spec for `newspaper scripts/build pages/build_geo_map.py`, `route.json` with coverage evidence and edge checks, a GPX track, and GeoJSON. To rebuild a map, run the existing renderer with the configured Google Maps credential; its route overlays are drawn locally. No credential is stored here. The original western graph was retrieved September 30; the Penfield graph was refreshed from the OpenStreetMap API October 3. Treat unmapped access changes and crossing conditions as unverified. Four western loops use the existing Princeton–Lincoln pedestrian connector; the Canterbury loop uses the mapped Twin Oaks–Covington connector.

## Validation

All seven tracks close at the exact home intersection, contain no repeated graph edges or interior nodes, and include their highlighted target segments. The source graph excludes private/no-access and foot-prohibited ways. `validation.txt` records the route checks. Google walking-direction requests were not made because sending precise home-route data was rejected by automatic approval review; distances remain OSM estimates. CityStrides visual evidence is in `evidence/`; absence of a purple track does not prove every CityStrides node will be credited.
