---
title: "Case L — 9 x 14 cube array, line source, non-isothermal"
parent: "Cases"
nav_order: 12
has_children: true
has_toc: false
generated: true
description: "14 rows by 9 columns of 0.06 m cubes with a tracer line source on the floor across the tunnel, in an unstably stratified boundary layer: velocity, temperature, concentration and their fluxes at 344 points in the streets and over the roofs."
---

# Case L — 9 x 14 cube array, line source, non-isothermal

14 rows by 9 columns of 0.06 m cubes with a tracer line source on the floor across the tunnel, in an unstably stratified boundary layer: velocity, temperature, concentration and their fluxes at 344 points in the streets and over the roofs.
{: .fs-5 .fw-300 .lede }

[Reference data]({{ '/cases/case-l/data/' | relative_url }}){: .btn .btn-primary } [Validation]({{ '/cases/case-l/validation/' | relative_url }}){: .btn } [Case as JSON]({{ '/api/cases/L.json' | relative_url }}){: .btn }

<figure class="figure render">
<img src="{{ '/assets/geometry/case-l.png' | relative_url }}" alt="Case L — 9 x 14 cube array, line source, non-isothermal">
<figcaption>14 x 9 array of 0.06 m cubes on a 0.12 m pitch (model scale); the orange line is the floor tracer source between rows 7 and 8; the wind blows along +x.</figcaption>
</figure>

## At a glance

| Fact | Value |
|---|---|
| Array | 14 rows (along x) by 9 columns (across y) of cubes, H = 0.06 m, pitch 0.12 m (street width = H, plan area ratio 25 %), published as BD\_caseL.stl; the data paper calls it \'9 rows by 14 columns\' |
| Reynolds number Re\_H | 5600 |
| U\_H (m/s) | 1.339415 |
| Wind directions (°) | 0 |
| Measurement planes | 8 heights (4 .. 150 mm) at 27 locations in the streets near the source, 4 heights (70 .. 150 mm) at 14 locations above the blocks, 3 heights (4 .. 30 mm) at 24 locations around |
| Measured | 344 rows over 344 points: U, V, W, uu, vv, ww, k, uv, uw, C, c\_rms, concentration\_ratio, T, T\_rms, uc, vc, wc, uT, vT, wT |

## Agreement with the tunnel

**No validation has been run for this case yet.** Nothing on this page is a claim about it. Eddy3D's fixture for this case is written and its solves are queued; no result exists yet. Engine status: OpenFOAM 12 <span class="label label-yellow status">pending</span> · OpenLB <span class="label label-yellow status">pending</span> · FluidX3D <span class="label label-yellow status">pending</span> · ML surrogate <span class="label label-yellow status">pending</span>

{: .warning-title }
> Before you compare
>
> The cleaned table is in SI units and one frame, with this case's corrections applied once; do not apply them again to the published files.
>
> - 9 known issues in the published files are listed under [Known data issues]({{ '/cases/case-l/data/' | relative_url }}#known-data-issues).
