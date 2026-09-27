#!/usr/bin/env python3
"""Tiny check-in API for the trip tracker.

Two endpoints that matter:
  GET  /checkin/<token>  -- mobile page with "Rest stop" / "Night stay" buttons
  POST /api/checkin      -- records one check-in (requires the token)
  GET  /api/checkins     -- public, returns all check-ins as JSON (read by the map)

Check-ins are appended to a JSON file on the mounted volume at DATA_DIR.
"""
import json
import os
import uuid
from datetime import datetime, timezone

from flask import Flask, abort, jsonify, request

app = Flask(__name__)

DATA_DIR = os.environ.get("DATA_DIR", "/data")
DATA_FILE = os.path.join(DATA_DIR, "checkins.json")
TOKEN = os.environ["CHECKIN_TOKEN"]
KINDS = {"pause", "night"}


def load():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE) as f:
        return json.load(f)


def save(checkins):
    os.makedirs(DATA_DIR, exist_ok=True)
    tmp = DATA_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(checkins, f)
    os.replace(tmp, DATA_FILE)


CHECKIN_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Check in</title>
<style>
  body {{ font-family: system-ui, sans-serif; margin: 0; padding: 24px; background: #111; color: #eee; }}
  h1 {{ font-size: 1.1rem; font-weight: normal; color: #999; }}
  button {{
    display: block; width: 100%; margin: 12px 0; padding: 28px; font-size: 1.4rem;
    border: none; border-radius: 12px; color: #fff; -webkit-tap-highlight-color: transparent;
  }}
  #pause {{ background: #ff9f1c; }}
  #night {{ background: #5f27cd; }}
  #status {{ margin-top: 20px; font-size: 1.1rem; min-height: 3em; }}
</style>
</head>
<body>
<h1>Where are you right now?</h1>
<button id="pause">☕ Rest stop</button>
<button id="night">🌙 Night stay</button>
<div id="status"></div>
<script>
const token = {token!r};
const status = document.getElementById('status');

function checkin(kind) {{
  status.textContent = 'Getting your location…';
  navigator.geolocation.getCurrentPosition(pos => {{
    fetch('/api/checkin', {{
      method: 'POST',
      headers: {{ 'Content-Type': 'application/json' }},
      body: JSON.stringify({{
        token, kind,
        lat: pos.coords.latitude,
        lon: pos.coords.longitude,
        accuracy: pos.coords.accuracy,
      }}),
    }})
      .then(r => r.ok ? status.textContent = '✓ Saved. You can close this page.'
                       : r.text().then(t => status.textContent = 'Error: ' + t))
      .catch(e => status.textContent = 'Error: ' + e);
  }}, err => {{
    status.textContent = 'Could not get location: ' + err.message;
  }}, {{ enableHighAccuracy: true, timeout: 15000 }});
}}

document.getElementById('pause').onclick = () => checkin('pause');
document.getElementById('night').onclick = () => checkin('night');
</script>
</body>
</html>
"""


@app.get("/checkin/<token>")
def checkin_page(token):
    if token != TOKEN:
        abort(404)
    return CHECKIN_PAGE.format(token=token)


@app.post("/api/checkin")
def api_checkin():
    data = request.get_json(force=True, silent=True) or {}
    if data.get("token") != TOKEN:
        abort(401)
    if data.get("kind") not in KINDS:
        abort(400, "kind must be 'pause' or 'night'")
    try:
        lat, lon = float(data["lat"]), float(data["lon"])
    except (KeyError, TypeError, ValueError):
        abort(400, "lat/lon required")

    entry = {
        "id": uuid.uuid4().hex,
        "kind": data["kind"],
        "lat": lat,
        "lon": lon,
        "accuracy": data.get("accuracy"),
        "ts": datetime.now(timezone.utc).isoformat(),
    }
    checkins = load()
    checkins.append(entry)
    save(checkins)
    return jsonify({"ok": True})


@app.get("/api/checkins")
def api_checkins():
    resp = jsonify(load())
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp


@app.get("/")
def index():
    return "Trip tracker API is running.\n"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
