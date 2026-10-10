# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

SEISMIC WORLD ("Seismic JP" in the README) is a static, client-side web app that visualizes global earthquake data (M4.5+, from USGS) as a time-series animation on a Leaflet map, with audio feedback keyed to magnitude. There is no build step, bundler, or backend — it's plain HTML/CSS/JS served as static files, plus Python scripts that pre-fetch USGS data into JSON files committed to the repo.

Live site (production, Vercel — auto-deploys on push to `main`): https://prime-plasma-world-1yze.vercel.app/
All canonical/OGP/sitemap URLs point to this Vercel domain. (The `deploy.yml` GitHub Pages workflow still exists but is not the canonical site.)
Sister site for Japan only: SEISMIC JP (https://prime-plasma.vercel.app/, separate repo `prime-plasma`).

## Commands

There is no package.json/build tooling. Everything runs via Python (data fetching) and a static file server (serving the app).

```bash
# Install the one Python dependency
pip install requests

# Serve the app locally (from repo root)
python -m http.server 8080
# open http://localhost:8080

# Refresh data (see "Data pipeline" below for which script does what)
python scripts/fetch_data.py            # rolling last-365-days -> data/earthquakes.json
python scripts/fetch_1month_data.py     # rolling last-30-days -> data/earthquakes_1month.json
python scripts/fetch_current_year.py    # Jan 1 of current year -> now -> data/earthquakes_<year>.json
python scripts/fetch_archive_data.py    # backfills 2011-2025, one file per year (rate-limited, slow)
```

There are no linters, formatters, or automated tests configured for this repo.

## Architecture

**Frontend (no build step — files are loaded directly by the browser):**
- [index.html](index.html) — single page shell; loads Leaflet, Driver.js, and Google Fonts from CDNs, plus local `css/style.css`, `js/tutorial.js`, `js/app.js`. All UI (header, stats, info panel, year tabs, timeline controls, legend) lives here as static markup that `app.js` populates/toggles.
- [js/app.js](js/app.js) — all application logic in one `DOMContentLoaded` handler, no modules/frameworks:
  - Builds the Leaflet map with an Esri "World Dark Gray" base + reference (label) tile layer pair (CARTO was dropped because it now requires an API key — see comment in the file before reverting).
  - Builds the year tabs (`buildYearTabs`) dynamically from `ARCHIVE_START_YEAR` (2011) through the current year, plus fixed "Last Month" / "Last Year" tabs — there is no hardcoded tab markup in the HTML, so a new year needs no HTML edit. `dropUnavailableYearTab()` HEAD-checks the current year's file and removes its tab if the archive fetch hasn't produced it yet.
  - `getDataUrl(year)` maps a tab's year key to a data file: `'latest'` → `data/earthquakes.json`, `'1month'` → `data/earthquakes_1month.json`, else `data/earthquakes_<year>.json`.
  - `loadYear()`/`initWithData()` fetch a year's GeoJSON, flatten it into a sorted-by-time array on `state.data`, and reset the timeline slider bounds.
  - The animation loop (`animate`, driven by `requestAnimationFrame`) advances `state.currentTime` at a rate derived from `state.playbackSpeed` and a fixed 90s baseline duration for the full dataset, calling `triggerEvents` to spawn markers/sounds for any events whose timestamp falls in the frame's time window. Scrubbing the slider (`handleSliderChange`) recomputes `state.eventIndex` by binary/linear search on the sorted data so playback can resume correctly from an arbitrary point.
  - Circle size scales exponentially with magnitude: `size = 1.8^M * 3`. Color thresholds: cyan <5, orange (yellow in UI copy) 5–6, red 6+ (`getMagColor`).
  - Audio is a WebAudio oscillator per event (`playSound`) — pitch drops and volume rises with magnitude; `AudioContext` is created/resumed lazily on the first play press (`initAudio`) to satisfy browser autoplay policies.
- [js/tutorial.js](js/tutorial.js) — Driver.js-based first-visit walkthrough (Japanese UI text), triggered once via `localStorage['seismic_tutorial_seen']` and replayable from the header's tutorial button.
- [css/style.css](css/style.css) — single stylesheet, CSS custom properties in `:root` for the light-glass UI palette and magnitude colors (the map tiles themselves are dark gray). `.year-tabs-overlay` sits at the top-center and `.header-overlay` is pushed below it (`top` = 92px desktop / 86px tablet / 70px ≤768px / 58px ≤480px); if you change the tab bar's height, re-check that they don't overlap at every breakpoint.
- `data/plates.geojson` and `data/active_faults.geojson` exist but are **not currently loaded by any code path** — don't assume they're wired into the map without checking again.

**Data pipeline (`scripts/*.py`, each standalone, no shared module):**
- `fetch_data.py` — rolling last 365 days → `data/earthquakes.json` (the "Last Year" tab / default view loaded on page load).
- `fetch_1month_data.py` — rolling last 30 days → `data/earthquakes_1month.json` (the "Last Month" tab); writes compact (non-indented) JSON, unlike the other scripts.
- `fetch_current_year.py` — Jan 1 of the current year through now → `data/earthquakes_<year>.json`; this is what keeps the current year's archive tab populated as the year progresses.
- `fetch_archive_data.py` — one-off backfill for `2011..2025` → `data/earthquakes_<year>.json` per year, with a 2s sleep between requests to stay under USGS rate limits. `ARCHIVE_START_YEAR` in `app.js` must stay in sync with this script's `start_year`.
- All scripts hit the same USGS FDSN endpoint (`https://earthquake.usgs.gov/fdsnws/event/1/query`) with `minmagnitude=4.5`, `format=geojson`, and write straight into `data/` — the raw GeoJSON `FeatureCollection` shape is consumed as-is by `app.js` (`f.properties.time`, `f.properties.mag`, `f.geometry.coordinates`).

**CI/CD (`.github/workflows/`):**
- `update-data.yml` — runs daily (cron `0 0 * * *`, i.e. 9am JST), runs `fetch_data.py` + `fetch_1month_data.py` + `fetch_current_year.py`, and commits any changed `data/earthquakes*.json` files back to `main` with `[skip ci]` (also `workflow_dispatch`-able). Note this does *not* run `fetch_archive_data.py` — past years' archive files are not auto-refreshed.
- `deploy.yml` — on every push to `main`, uploads the entire repo as a Pages artifact and deploys to GitHub Pages. There's no build/filter step, so anything committed to `main` is published as-is.

When editing data-fetching scripts, keep the output GeoJSON shape (`FeatureCollection` with `properties.time`/`properties.mag` and `geometry.coordinates: [lon, lat, depth]`) consistent with what `app.js`'s `initWithData()` expects — it does no schema validation.

## SEO & sharing assets

- `<head>` in [index.html](index.html) carries the Japanese title/description, canonical, Open Graph (incl. `og:image:width/height/alt`, `og:locale` ja_JP + alternate en_US), Twitter card, and JSON-LD — all with absolute `https://prime-plasma-world-1yze.vercel.app/` URLs.
- Copy describes the data as **daily-updated**, not "real-time" — the data refreshes once a day via CI.
- [images/og-image.png](images/og-image.png) is a 1200×630 **screenshot of the app itself** (tutorial dismissed via `localStorage['seismic_tutorial_seen']`, info panel closed, a few seconds of playback). Retake it whenever the header/branding or layout changes visibly — the previous one went stale and still showed the old "SISMIC" typo. Keep it a compressed (256-color) PNG.
- `robots.txt`, `sitemap.xml` (single URL; update `<lastmod>` on major changes), and `google70a12f1405272d9f.html` (Google Search Console verification — do not delete) live at the repo root.
- External links use `target="_blank" rel="noopener"`.
