---
title: "Case D — high-rise among city blocks"
parent: "Cases"
nav_order: 4
has_children: true
has_toc: false
generated: true
description: "1:1:4 tower in a regular array of 82 low blocks, pedestrian-height scalar speed (thermistor, 3 wind directions) plus a 33-point split-fibre velocity field at WD = 0."
---

# Case D — high-rise among city blocks

1:1:4 tower in a regular array of 82 low blocks, pedestrian-height scalar speed (thermistor, 3 wind directions) plus a 33-point split-fibre velocity field at WD = 0.
{: .fs-5 .fw-300 .lede }

[Reference data]({{ '/cases/case-d/data/' | relative_url }}){: .btn .btn-primary } [Validation]({{ '/cases/case-d/validation/' | relative_url }}){: .btn } [Case as JSON]({{ '/api/cases/D.json' | relative_url }}){: .btn }

<figure class="figure render">
<a href="{{ '/assets/geometry/case-d.png' | relative_url }}"><img src="{{ '/assets/web/case-d.png' | relative_url }}" width="1600" height="800" loading="lazy" alt="Case D — high-rise among city blocks"></a>
<figcaption>A 0.25 m tower (blue) among 82 low blocks over 1.40 m × 1.35 m (1:400 model scale); the arrow is WD = 0°.<br><a class="original" href="{{ '/assets/geometry/case-d.png' | relative_url }}">1200 dpi original, 2.2 MB</a></figcaption>
</figure>

## At a glance

| Fact | Value |
|---|---|
| Tower | 0.25H x 0.25H x H = 62.5 x 62.5 x 250 mm (1:1:4) |
| Scale | 1:400 (H = 100 m full scale; the 5 mm measurement plane = 2 m) |
| Reynolds number Re\_H | 110,000 |
| U\_H (m/s) | 6.65 |
| Wind directions (°) | 0, 22.5, 45 |
| Measurement height (m) | 0.005 |
| Measured | 267 rows over 78 points: Vs, U, V, W, uu, vv, ww, k |

## Agreement with the tunnel

| Engine | Status | R | FAC2 |
|---|---|---|---|
| OpenFOAM 12 | <span class="label label-green status">scored</span> | +0.78 … +0.95 | 0.48 … 0.92 |
| OpenLB | <span class="label label-grey status">not comparable</span> | — | — |
| FluidX3D | <span class="label label-grey status">not comparable</span> | — | — |
| ML surrogate | <span class="label label-green status">scored</span> | +0.22 … +0.59 | 0.34 … 0.64 |
{: .scores }

R and FAC2 are the range over the headline scores of an engine's runs (velocity components, k, wind directions; negative controls left out). *Scored* means a run exists and its scores are served, not that it agrees: every score, its figures and its reading are on the [Validation page]({{ '/cases/case-d/validation/' | relative_url }}).

{: .warning-title }
> Before you compare
>
> The cleaned table is in SI units and one frame, with this case's corrections applied once; do not apply them again to the published files.
>
> - The published coordinates are multiplied by 0.001 in the cleaned table (`coordinate_scale_applied`).
> - The sense in which the wind direction rotates is a convention to check before comparing at any direction other than 0° (see *Frame and units* on the Data page).
> - 6 known issues in the published files are listed under [Known data issues]({{ '/cases/case-d/data/' | relative_url }}#known-data-issues).
