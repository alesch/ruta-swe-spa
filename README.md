# Route Sweden → Spain

Trip plan map, shared with family and friends. Static page built with [Leaflet](https://leafletjs.com) on OpenStreetMap tiles, hosted on GitHub Pages.

Live check-ins (rest stops and night stays) are added by a tiny backend in [`tracker/`](tracker/), hosted separately on fly.io — see [`tracker/README.md`](tracker/README.md) for setup and deployment.

## Files

- `index.html` – the page, also polls the tracker API for check-in markers
- `places.json` – standalone markers
- `tracker/` – fly.io check-in API (separate deploy, see its own README)

## Editing

```sh
python3 -m http.server 8765   # preview at http://localhost:8765
```

Map data © [OpenStreetMap](https://www.openstreetmap.org/copyright) contributors.
