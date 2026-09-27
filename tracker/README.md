# Trip tracker (fly.io)

Tiny Flask API, separate from the GitHub Pages map. Your phone posts check-ins to it;
the map polls it for markers. No accounts, no login — just a secret token in the URL.

- `GET /checkin/<token>` — mobile page, two buttons: "Rest stop" / "Night stay"
- `POST /api/checkin` — records one check-in (needs the token)
- `GET /api/checkins` — public, returns all check-ins as JSON (read by the map)

Check-ins are stored as a JSON file on a 1GB fly volume, so they survive the
machine stopping/starting. `auto_stop_machines` is on, so it costs ~nothing
between check-ins.

## First-time deploy

You need the fly CLI and your own fly.io account (I can't run these — they need
your login):

```sh
curl -L https://fly.io/install.sh | sh
fly auth login
```

From this `tracker/` directory:

```sh
fly launch --no-deploy                       # uses fly.toml already in this dir
fly volumes create trackerdata --size 1 --region arn
fly secrets set CHECKIN_TOKEN=$(python3 -c "import secrets; print(secrets.token_urlsafe(24))")
fly deploy
```

If `ruta-swe-spa-tracker` (the app name in `fly.toml`) is already taken, `fly launch`
will ask you to pick another — update `app` in `fly.toml` to match, and update
`TRACKER_API` in the main `index.html` to `https://<your-app-name>.fly.dev/api/checkins`.

The token is never written to disk or committed — it only lives as a fly secret.
To get your check-in URL to bookmark on your phone, read it back once:

```sh
fly ssh console -C 'printenv CHECKIN_TOKEN'
```

Your URL is `https://<your-app-name>.fly.dev/checkin/<that token>`. To rotate it later,
just run the `fly secrets set` command again with a new value and update your phone bookmark.

## Redeploying after changes

```sh
fly deploy
```

## Tearing it down after the trip

```sh
fly apps destroy ruta-swe-spa-tracker
```

The map on GitHub Pages keeps working fine without it — you just stop getting
new check-in markers, and the old ones stay in `/api/checkins` only as long as
the app exists (they're not mirrored into the static site).
