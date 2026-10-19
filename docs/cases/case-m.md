---
title: "Case M — TPU Atsugi campus"
parent: "Cases"
nav_order: 13
has_children: true
has_toc: false
generated: true
description: "Tracer-gas release on the Tokyo Polytechnic University Atsugi campus: 1:600 tunnel (velocity at 180°, ethylene concentration at 175°, 180° and 185°) and 18 field runs with PMCH, 15 points 3 m above ground."
---

# Case M

Tracer-gas release on the Tokyo Polytechnic University Atsugi campus: 1:600 tunnel (velocity at 180°, ethylene concentration at 175°, 180° and 185°) and 18 field runs with PMCH, 15 points 3 m above ground.
{: .fs-5 .fw-300 .lede }

[Reference data]({{ '/cases/case-m/data/' | relative_url }}){: .btn .btn-primary } [Validation]({{ '/cases/case-m/validation/' | relative_url }}){: .btn } [Case as JSON]({{ '/api/cases/M.json' | relative_url }}){: .btn }

<figure class="figure render">
<a href="{{ '/assets/geometry/case-m.png' | relative_url }}"><img src="{{ '/assets/web/case-m.png' | relative_url }}" width="1600" height="800" loading="lazy" alt="Case M — TPU Atsugi campus"></a>
<figcaption>TPU Atsugi campus: terrain and buildings of the 1:600 model (full-scale metres, 1080 m by 720 m); the arrow is the wind at WD = 180°, blowing toward +x (north).</figcaption>
</figure>

## At a glance

| Fact | Value |
|---|---|
| Scale | 1:600 |
| Normalisation | concentration ratio = $$C/c_0$$, $$c_0 = \dfrac{q}{U_R H_R^2}$$: 132.5 ppm in the tunnel (the paper rounds to 1.33e2); per run in the field (1,444 ... 7,379 ppq) |
| Wind directions (°) | 175, 180, 185 |
| Measurement height (m) | 3 |
| Measured | 330 rows over 15 points: $$U$$, $$V$$, $$W$$, $$\overline{u'u'}$$, $$\overline{v'v'}$$, $$\overline{w'w'}$$, $$k$$, $$C$$, $$c_{\mathrm{rms}}$$, $$c^\ast$$ |

{% include nomenclature.md %}

## Validation

| Engine | Status | Compared with | R (range) | FAC2 (range) |
|---|---|---|---|---|
| OpenFOAM 12 | <span class="label label-green status">scored</span> | Wind tunnel | +0.18 … +0.73 | 0.13 … 0.73 |
| OpenFOAM 12 | <span class="label label-green status">scored</span> | Field | +0.22 … +0.46 | 0.07 |
| OpenLB | <span class="label label-yellow status">pending</span> | — | — | — |
| FluidX3D | <span class="label label-yellow status">pending</span> | — | — | — |
| ML surrogate | <span class="label label-yellow status">pending</span> | — | — | — |
{: .scores }

{% include nomenclature-scores.md %}

{: .warning-title }
> Before you compare
>
> - The cleaned table is in SI units and one frame, with this case's corrections applied once. Do not apply them again.
> - Origin: centre of the tunnel turntable on the floor plane (ground surface there at $$z = 33.07\thinspace\mathrm{m}$$). Length unit: m (FULL scale).
> - The published coordinates are multiplied by 600 in the cleaned table (`coordinate_scale_applied`).
> - Wind direction: meteorological FROM-direction, so 180° blows toward $$+x$$; flow\_dir = (-cos WD, +sin WD), and a larger WD turns the plume toward -y. Measured on the tunnel\'s 175 / 180 / 185° and on the 18 field runs.
> - 10 known issues in the published files are listed under [Known data issues]({{ '/cases/case-m/data/' | relative_url }}#known-data-issues).
