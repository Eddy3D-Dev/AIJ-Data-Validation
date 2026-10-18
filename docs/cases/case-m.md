---
title: "Case M — TPU Atsugi campus"
parent: "Cases"
nav_order: 13
has_children: true
has_toc: false
generated: true
description: "Tracer-gas release on the Tokyo Polytechnic University Atsugi campus: 1:600 tunnel (velocity at 180°, ethylene concentration at 175°, 180° and 185°) and 18 field runs with PMCH, 15 points 3 m above ground."
---

# Case M — TPU Atsugi campus

Tracer-gas release on the Tokyo Polytechnic University Atsugi campus: 1:600 tunnel (velocity at 180°, ethylene concentration at 175°, 180° and 185°) and 18 field runs with PMCH, 15 points 3 m above ground.
{: .fs-5 .fw-300 .lede }

[Reference data]({{ '/cases/case-m/data/' | relative_url }}){: .btn .btn-primary } [Validation]({{ '/cases/case-m/validation/' | relative_url }}){: .btn } [Case as JSON]({{ '/api/cases/M.json' | relative_url }}){: .btn }

<figure class="figure render">
<a href="{{ '/assets/geometry/case-m.png' | relative_url }}"><img src="{{ '/assets/web/case-m.png' | relative_url }}" width="1600" height="800" loading="lazy" alt="Case M — TPU Atsugi campus"></a>
<figcaption>TPU Atsugi campus: terrain and buildings of the 1:600 model (full-scale metres, 1080 m by 720 m); the arrow is the wind at WD = 180°, blowing toward +x (north).<br><a class="original" href="{{ '/assets/geometry/case-m.png' | relative_url }}">1200 dpi original, 1.8 MB</a></figcaption>
</figure>

## At a glance

| Fact | Value |
|---|---|
| Scale | 1:600 |
| Normalisation | concentration ratio = C / c0, c0 = q / (U\_R H\_R^2): 132.5 ppm in the tunnel (the paper rounds to 1.33e2); per run in the field (1,444 ... 7,379 ppq) |
| Wind directions (°) | 175, 180, 185 |
| Measurement height (m) | 3 |
| Measured | 330 rows over 15 points: U, V, W, uu, vv, ww, k, C, c\_rms, concentration\_ratio |

## Agreement with the tunnel

| Engine | Status | R | FAC2 |
|---|---|---|---|
| OpenFOAM 12 | <span class="label label-green status">scored</span> | +0.18 … +0.73 | 0.07 … 0.73 |
| OpenLB | <span class="label label-yellow status">pending</span> | — | — |
| FluidX3D | <span class="label label-yellow status">pending</span> | — | — |
| ML surrogate | <span class="label label-yellow status">pending</span> | — | — |
{: .scores }

R and FAC2 are the range over the headline scores of an engine's runs (velocity components, k, wind directions; negative controls left out). *Scored* means a run exists and its scores are served, not that it agrees: every score, its figures and its reading are on the [Validation page]({{ '/cases/case-m/validation/' | relative_url }}).

{: .warning-title }
> Before you compare
>
> The cleaned table is in SI units and one frame, with this case's corrections applied once; do not apply them again to the published files.
>
> - The published coordinates are multiplied by 600 in the cleaned table (`coordinate_scale_applied`).
> - The sense in which the wind direction rotates is a convention to check before comparing at any direction other than 0° (see *Frame and units* on the Data page).
> - 10 known issues in the published files are listed under [Known data issues]({{ '/cases/case-m/data/' | relative_url }}#known-data-issues).
