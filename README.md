# Running map

An interactive map of Andrew Furman's recorded running routes and upcoming street targets around Havertown, Pennsylvania. Purple lines represent running GPS tracks from Strava; weekday markers show the current plan. Bike rides and walks are excluded.

The map contains precise GPS traces and dated future destinations. It is public by the owner's choice. These are raw recorded paths, and GPS proximity to a street does not guarantee CityStrides completion.

## Run locally

Python 3 is the only server dependency:

```sh
python3 serve.py
```

Open http://127.0.0.1:8768/ in a browser. The map uses OpenStreetMap and Leaflet by default. To use Google Maps instead, provide a Google Maps JavaScript browser key with the appropriate APIs enabled:

```sh
export GOOGLE_MAPS_API_KEY='your-browser-key'
python3 serve.py
```

Restrict browser keys to authorized origins in Google Cloud. Do not commit API keys. Google Maps may incur charges under your Google Cloud account. The key is sent to the local browser, which loads Google Maps; it is not written into the HTML or this repository.

## Data and updates

`index.html` is a self-contained snapshot of the map and its embedded GeoJSON running tracks and target metadata. It contains 1,874 GPS runs through October 30, 2026, and plans through November 3, 2026. Use `python3 export_tracks.py` to extract the track collection as `runs.geojson`. The file is generated locally and ignored by Git to avoid duplicating the embedded data.

This repository is independent of the private Family Newspaper repository and its Cloudflare archive. It does not automatically import new Strava activities or update plans: refresh the snapshot when new runs or targets are available. Calendar details and the separate bike history are not copied here.

## Running research and planning

The original folder structure is under `content research/future-running-routes/`, including dated plans, street geometry, route GPX files, research and older visualizations. `tools/running_route_updates.py` and `tools/route_map_shell.py` apply the plan named by `current-plan.json`; run `python3 build_map.py` after updating the plan to rebuild `index.html`. The map snapshot and running research are versioned in this repository and do not require Cloudflare.

Personal calendar event exports, email copies, bike history and the original all-sport Strava ZIP remain private in Family Newspaper's archive. The legacy bulk import utility under `tools/` was copied for reference and is intended for a private working copy: it preserves the original all-sport archive, which must not be published in this public repository.
