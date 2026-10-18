---
title: "Case E — Niigata district"
parent: "Cases"
nav_order: 5
has_children: true
has_toc: false
generated: true
description: "Real district in Niigata at 1:250, before and after a 60 m high-rise and two 18 m mid-rises; pedestrian-height velocity ratio (thermistor), 16 wind directions."
---

# Case E — Niigata district

Real district in Niigata at 1:250, before and after a 60 m high-rise and two 18 m mid-rises; pedestrian-height velocity ratio (thermistor), 16 wind directions.
{: .fs-5 .fw-300 .lede }

[Reference data]({{ '/cases/case-e/data/' | relative_url }}){: .btn .btn-primary } [Validation]({{ '/cases/case-e/validation/' | relative_url }}){: .btn } [Case as JSON]({{ '/api/cases/E.json' | relative_url }}){: .btn }

| | |
|---|---|
| <a href="{{ '/assets/geometry/case-e-before.png' | relative_url }}"><img src="{{ '/assets/web/case-e-before.png' | relative_url }}" width="1600" height="800" loading="lazy" alt="Case E — Niigata district, bc"></a><br><span class="caption">Before construction: the existing district, about 400 m across (full scale).</span> | <a href="{{ '/assets/geometry/case-e-after.png' | relative_url }}"><img src="{{ '/assets/web/case-e-after.png' | relative_url }}" width="1600" height="800" loading="lazy" alt="Case E — Niigata district, ac"></a><br><span class="caption">After construction: the 60 m high-rise and the two 18 m mid-rises (blue) added.</span> |
{: .figures }

<p class="caption">The two states, on one scale (full-scale metres, +x east, +y north); the arrow marks SW, the direction Eddy3D is scored at.</p>

## At a glance

| Fact | Value |
|---|---|
| District | Niigata City urban area near the Shinano River; dense low-rise stock (median top 6 m, max 30 m) |
| Scale | 1:250 |
| Reynolds number | 17,000 |
| Normalisation | velocity ratio = mean scalar speed at 2 m / inflow velocity at 15.9 m (the Niigata meteorological station height); U(15.9 m) = 0.504531 x UR = 3.935 m/s with UR = 7.8 m/s at ZR = 250 m |
| Wind directions | N, NNE, NE, ENE, E, ESE, SE, SSE, S, SSW, SW, WSW, W, WNW, NW, NNW |
| Measurement height (m) | 2.0 |
| Measured | 2,560 rows over 80 points: velocity\_ratio |

## Validation

| Engine | Status | Compared with | R (range) | FAC2 (range) |
|---|---|---|---|---|
| OpenFOAM 12 | <span class="label label-green status">scored</span> | Wind tunnel | +0.69 … +0.85 | 0.74 … 0.95 |
| OpenLB | <span class="label label-grey status">not comparable</span> | — | — | — |
| FluidX3D | <span class="label label-grey status">not comparable</span> | — | — | — |
| ML surrogate | <span class="label label-green status">scored</span> | Wind tunnel | +0.23 … +0.43 | 0.22 … 0.84 |
{: .scores }

{: .warning-title }
> Before you compare
>
> - The cleaned table is in SI units and one frame, with this case's corrections applied once. Do not apply them again.
> - Origin: centre of the reproduced area, ground plane. Length unit: m (FULL scale).
> - Wind direction: meteorological FROM-direction, clockwise from north; the compass name is the direction the wind comes from (N = 0 deg blows toward -y, E = 90 deg toward -x). This case keeps its geographic frame instead of \'+x along the wind\' because the district is real and its coordinates are the data\'s.
> - 7 known issues in the published files are listed under [Known data issues]({{ '/cases/case-e/data/' | relative_url }}#known-data-issues).
