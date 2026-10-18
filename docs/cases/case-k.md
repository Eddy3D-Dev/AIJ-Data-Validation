---
title: "Case K — 9 x 9 cube array, point source"
parent: "Cases"
nav_order: 11
has_children: true
has_toc: false
generated: true
description: "9 x 9 array of 0.06 m cubes with a tracer point source on the floor between rows 2 and 3: velocity and tracer concentration at 203 points in the streets and over the first rows."
---

# Case K — 9 x 9 cube array, point source

9 x 9 array of 0.06 m cubes with a tracer point source on the floor between rows 2 and 3: velocity and tracer concentration at 203 points in the streets and over the first rows.
{: .fs-5 .fw-300 .lede }

[Reference data]({{ '/cases/case-k/data/' | relative_url }}){: .btn .btn-primary } [Validation]({{ '/cases/case-k/validation/' | relative_url }}){: .btn } [Case as JSON]({{ '/api/cases/K.json' | relative_url }}){: .btn }

<figure class="figure render">
<a href="{{ '/assets/geometry/case-k.png' | relative_url }}"><img src="{{ '/assets/web/case-k.png' | relative_url }}" width="1600" height="800" loading="lazy" alt="Case K — 9 x 9 cube array, point source"></a>
<figcaption>9 x 9 array of 0.06 m cubes on a 0.12 m pitch (model scale); the orange ring marks the floor tracer source between rows 2 and 3; the wind blows along +x.<br><a class="original" href="{{ '/assets/geometry/case-k.png' | relative_url }}">1200 dpi original, 2.0 MB</a></figcaption>
</figure>

## At a glance

| Fact | Value |
|---|---|
| Array | 9 rows (along x) by 9 columns (across y) of cubes, H = 0.06 m, pitch 0.12 m (street width = H, plan area ratio 25 %); the pitch is read from the MP drawings |
| Reynolds number Re\_H | 9800 |
| U\_H (m/s) | 2.33 |
| Wind directions (°) | 0 |
| Measurement planes | y/H = 0, +-1, +-2, +-3 (z up to 0.07 m), five heights from 4 mm to 70 mm; the three upper heights only on y = 0 and +-H |
| Measured | 203 rows over 203 points: U, V, W, uu, vv, ww, k, C, c\_rms, concentration\_ratio |

## Agreement with the tunnel

| Engine | Status | R | FAC2 |
|---|---|---|---|
| OpenFOAM 12 | <span class="label label-green status">scored</span> | -0.15 … +0.96 | 0.04 … 0.80 |
| OpenLB | <span class="label label-yellow status">pending</span> | — | — |
| FluidX3D | <span class="label label-yellow status">pending</span> | — | — |
| ML surrogate | <span class="label label-yellow status">pending</span> | — | — |
{: .scores }

R and FAC2 are the range over the headline scores of an engine's runs (velocity components, k, wind directions; negative controls left out). *Scored* means a run exists and its scores are served, not that it agrees: every score, its figures and its reading are on the [Validation page]({{ '/cases/case-k/validation/' | relative_url }}).

{: .warning-title }
> Before you compare
>
> The cleaned table is in SI units and one frame, with this case's corrections applied once; do not apply them again to the published files.
>
> - 9 known issues in the published files are listed under [Known data issues]({{ '/cases/case-k/data/' | relative_url }}#known-data-issues).
