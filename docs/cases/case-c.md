---
title: "Case C — 3 × 3 block array"
parent: "Cases"
nav_order: 3
has_children: true
has_toc: false
generated: true
description: "3 x 3 array of 0.20 m cubes, centre block at 0D / 1D / 2D, pedestrian-height scalar speed (thermistor), 3 wind directions."
---

# Case C — 3 × 3 block array

3 x 3 array of 0.20 m cubes, centre block at 0D / 1D / 2D, pedestrian-height scalar speed (thermistor), 3 wind directions.
{: .fs-5 .fw-300 .lede }

[Reference data]({{ '/cases/case-c/data/' | relative_url }}){: .btn .btn-primary } [Validation]({{ '/cases/case-c/validation/' | relative_url }}){: .btn } [Case as JSON]({{ '/api/cases/C.json' | relative_url }}){: .btn }

| | | |
|---|---|---|
| <a href="{{ '/assets/geometry/case-c-0d.png' | relative_url }}"><img src="{{ '/assets/web/case-c-0d.png' | relative_url }}" width="1600" height="800" loading="lazy" alt="Case C — 3 × 3 block array, 0D"></a><br><span class="caption">0D: the centre block removed.<br><a class="original" href="{{ '/assets/geometry/case-c-0d.png' | relative_url }}">1200 dpi original, 0.9 MB</a></span> | <a href="{{ '/assets/geometry/case-c-1d.png' | relative_url }}"><img src="{{ '/assets/web/case-c-1d.png' | relative_url }}" width="1600" height="800" loading="lazy" alt="Case C — 3 × 3 block array, 1D"></a><br><span class="caption">1D: the centre block as tall as its neighbours, D = 0.20 m.<br><a class="original" href="{{ '/assets/geometry/case-c-1d.png' | relative_url }}">1200 dpi original, 0.9 MB</a></span> | <a href="{{ '/assets/geometry/case-c-2d.png' | relative_url }}"><img src="{{ '/assets/web/case-c-2d.png' | relative_url }}" width="1600" height="800" loading="lazy" alt="Case C — 3 × 3 block array, 2D"></a><br><span class="caption">2D: the centre block twice as tall, 2D = 0.40 m.<br><a class="original" href="{{ '/assets/geometry/case-c-2d.png' | relative_url }}">1200 dpi original, 0.9 MB</a></span> |
{: .figures }

<p class="caption">The three configurations of the centre block, on one scale; 120 measurement points each, at three wind directions.</p>

## At a glance

| Fact | Value |
|---|---|
| Array | 3 x 3 cubes, D = 0.20 m, block centres at x, y in {-0.4, 0, +0.4} m (pitch 0.40 m = 2D, street width D) |
| Reynolds number Re\_D | 52,000 |
| U\_H (m/s) | 3.654 |
| Wind directions (°) | 0, 22.5, 45 |
| Measurement height (m) | 0.02 |
| Measured | 1,080 rows over 120 points: Vs |

## Agreement with the tunnel

| Engine | Status | R | FAC2 |
|---|---|---|---|
| OpenFOAM 12 | <span class="label label-green status">scored</span> | +0.74 … +0.91 | 0.55 … 0.98 |
| OpenLB | <span class="label label-grey status">not comparable</span> | — | — |
| FluidX3D | <span class="label label-grey status">not comparable</span> | — | — |
| ML surrogate | <span class="label label-green status">scored</span> | +0.07 … +0.21 | 0.44 … 0.88 |
{: .scores }

R and FAC2 are the range over the headline scores of an engine's runs (velocity components, k, wind directions; negative controls left out). *Scored* means a run exists and its scores are served, not that it agrees: every score, its figures and its reading are on the [Validation page]({{ '/cases/case-c/validation/' | relative_url }}).

{: .warning-title }
> Before you compare
>
> The cleaned table is in SI units and one frame, with this case's corrections applied once; do not apply them again to the published files.
>
> - The sense in which the wind direction rotates is a convention to check before comparing at any direction other than 0° (see *Frame and units* on the Data page).
> - 6 known issues in the published files are listed under [Known data issues]({{ '/cases/case-c/data/' | relative_url }}#known-data-issues).
