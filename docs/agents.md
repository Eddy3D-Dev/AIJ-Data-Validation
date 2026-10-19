---
title: "For agents"
parent: API
nav_order: 3
permalink: /agents/
description: "A walk through the AIJ UWE benchmark API for scripts and AI agents, and the rules for a comparison."
---

# Using this from an agent or a script

Start at [`/llms.txt`]({{ '/llms.txt' | relative_url }}). It has the walk below in plain text, every endpoint, and
every known data issue, and it is regenerated with the data. The formal contract is
[`/api/openapi.json`]({{ '/api/openapi.json' | relative_url }}), together with the JSON Schema that each document
names in `$schema`.

## The walk

1. **`GET /api/index.json`**: every endpoint and every file with its size and SHA-256, the API version, the
   `data_version`, the changelog, the licence and how to cite. If the Pages site is unreachable, `fallback_base_url`
   serves the identical files raw from the repository. `/api/` always serves the newest release, and
   `/api/versions.json` lists every release with the `base_url` of its frozen copy (see the first rule below).
2. **`GET /api/cases.json`**: every case with its frame, units, counts, engine status and links. Pick an `id`.
3. **`GET /api/cases/{id}.json`**: read `frame`, `units` and `known_issues` **before** the numbers, because they
   differ per case. A–D and H–L are model-scale metres with $$+x$$ along the wind. E, F, G and M are full-scale metres: E and
   F with $$+x$$ east, $$+y$$ north and meteorological directions, G with $$+x$$ downwind, M with $$+x$$ north and $$+y$$ west.
   `configurations` lists the values `config`, `campaign`, `instrument`, `run` and `wind_direction_deg` take in the
   point table.
4. **`GET /api/cases/{id}/points.json`** (or the `points.csv` download): every value is SI (m, m/s, m²/s²), in one
   frame per case. Unmeasured values are `null` (an empty cell in CSV). `columns` lists the fields present, and
   `column_meaning` defines each. Case E's quantity is a dimensionless `velocity_ratio` ($$V_{\mathrm{s}}/U(15.9\text{ m})$$, with
   $$U(15.9\text{ m})$$ = 3.935 m/s); Cases F and G are ratios too (`velocity_ratio`, `k_ratio`), against a reference stated in the case's
   `normalisation`. Cases H to M add a tracer concentration `C` in ppm, with `concentration_ratio` normalised as
   the case states, and J and L add temperature and turbulent fluxes.
5. **`GET /api/cases/{id}/geometry.json`**, then the STL it links: metres, outward normals, origin at the building or
   array centre. Where the geometry is boxes (A–D and G–L), the JSON carries the box list, so you need not parse STL.
6. **`GET /api/validation.json`**: every case and engine in one table. **An engine whose status is not `scored` has
   no result for that case; do not infer one.** For one case in full,
   `GET /api/cases/{id}/validation.json`: every score, the `headline` scores to quote, the figures, and
   `pairs`, the per-point measured and modelled values behind the scores.

## Rules for a comparison

- Pin the release when a result must be reproducible. Take the `base_url` of the release you used from
  `/api/versions.json` (for example `.../api/3.1.0`) and fetch every path from it instead of from `/api/`. The
  unversioned paths follow the newest release, so a script that uses them can return different numbers after the next
  release, while a release's copy never changes and every API URL inside its documents points back into it. Quote the
  release number together with `data_version`. If a release lists `self_contained: false`, its documents link outside
  its copy: build its URLs from `base_url` and the `path` in its `index.json`.
- Normalise by the case's own $$U_H$$ (`configuration.U_H_m_s`), or for Case E by $$U(15.9\text{ m})$$; normalise $$k$$ by $$U_H^2$$. Cases F
  and G are published as ratios already: read their `normalisation` before comparing.
- Compare a thermistor quantity (C, D, E, F: `Vs`, `velocity_ratio`) against the bracket $$\lvert\mathbf{U}\rvert$$ ≤ $$V_{\mathrm{s}}$$ ≤ $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$, not
  against $$\lvert\mathbf{U}\rvert$$ alone.
- Compare a concentration through `concentration_ratio` and the case's own `normalisation` ($$c_0$$ is defined per case, and in
  Case K the workbook and the data paper use different reference scales). Case M's tunnel and field rows are two
  campaigns: filter on `campaign`.
- Probe at the published coordinates; never interpolate the reference.
- The served tables already apply each case's corrections: Case B's $$V$$ is sign-unified and its coordinates are in
  metres. Do not apply those corrections a second time when starting from the raw files.
- Use the download URLs the documents give rather than building them yourself, and check each file against its
  `sha256`.
- Send a descriptive `User-Agent`. The site's CDN rejects Python `urllib`'s default one and some AI crawlers with
  HTTP 403. If you are refused anyway, `fallback_base_url` serves byte-identical files from the repository.
- Cite the release you pinned and quote its version: `cite.api` in that release's `index.json`.

## Cite

The API: `cite.api` in `/api/index.json` (`apa`, `bibtex`, `csl_json`). A case's dataset: `citation` and `doi` in `/api/cases/{id}.json`. The same citations, with the data paper's, are on the [About and cite]({{ '/about/#cite' | relative_url }}) page.
