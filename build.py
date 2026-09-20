#!/usr/bin/env python3
"""Snap the waypoints in routes.json to roads (OSRM public demo server) and write routes.js.

Run again after editing routes.json:  python3 build.py
"""
import json
import urllib.request

OSRM = "https://router.project-osrm.org/route/v1/driving/{coords}?overview=full&geometries=geojson"

with open("routes.json") as f:
    routes = json.load(f)

for route in routes:
    coords = ";".join(f"{w['lon']},{w['lat']}" for w in route["waypoints"])
    try:
        with urllib.request.urlopen(OSRM.format(coords=coords), timeout=30) as r:
            data = json.load(r)
        if data.get("code") != "Ok":
            raise RuntimeError(data.get("code"))
        # GeoJSON is [lon, lat]; Leaflet wants [lat, lon]
        route["path"] = [[lat, lon] for lon, lat in data["routes"][0]["geometry"]["coordinates"]]
        route["km"] = round(data["routes"][0]["distance"] / 1000)
        print(f"{route['name']}: routed, {route['km']} km, {len(route['path'])} points")
    except Exception as e:
        # Fall back to straight lines between waypoints so the map still renders
        route["path"] = [[w["lat"], w["lon"]] for w in route["waypoints"]]
        route["km"] = None
        print(f"{route['name']}: routing failed ({e}), using straight lines")

with open("places.json") as f:
    places = json.load(f)

with open("routes.js", "w") as f:
    f.write("const ROUTES = " + json.dumps(routes) + ";\n")
    f.write("const PLACES = " + json.dumps(places) + ";\n")
