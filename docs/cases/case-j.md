---
title: "Case J — 1:1:2 building, non-isothermal"
parent: "Cases"
nav_order: 10
has_children: true
has_toc: false
generated: true
description: "Isolated 1:1:2 building with a floor tracer source in an unstably stratified boundary layer: velocity, temperature, tracer concentration and their turbulent fluxes at 444 points on three planes."
---

# Case J — 1:1:2 building, non-isothermal

Isolated 1:1:2 building with a floor tracer source in an unstably stratified boundary layer: velocity, temperature, tracer concentration and their turbulent fluxes at 444 points on three planes.
{: .fs-5 .fw-300 .lede }

[Reference data]({{ '/cases/case-j/data/' | relative_url }}){: .btn .btn-primary } [Validation]({{ '/cases/case-j/validation/' | relative_url }}){: .btn } [Case as JSON]({{ '/api/cases/J.json' | relative_url }}){: .btn }

<figure class="figure render">
<img src="{{ '/assets/geometry/case-j.png' | relative_url }}" alt="Case J — 1:1:2 building, non-isothermal">
<figcaption>Isolated 1:1:2 building, b = 0.08 m, H = 0.16 m (model scale); the orange ring marks the floor tracer source, 0.25 H behind the building (seen through it); the wind blows along +x.</figcaption>
</figure>

## At a glance

| Fact | Value |
|---|---|
| Building | 1:1:2 (width : depth : height) prism, b = 0.08 m, H = 2b = 0.16 m |
| Reynolds number Re\_H | 16,000 |
| U\_H (m/s) | 1.4581 |
| Wind directions (°) | 0 |
| Measurement planes | vertical centre plane y/H = 0, horizontal z/H = 0.025 (y \<= 0 side only), horizontal z/H = 0.25 |
| Measured | 444 rows over 444 points: U, V, W, uu, vv, ww, k, C, c\_rms, concentration\_ratio, T, T\_rms, uT, vT, wT |

## Agreement with the tunnel

**No validation has been run for this case yet.** Nothing on this page is a claim about it. Eddy3D's fixture for this case is written and its solves are queued; no result exists yet. Engine status: OpenFOAM 12 <span class="label label-yellow status">pending</span> · OpenLB <span class="label label-yellow status">pending</span> · FluidX3D <span class="label label-yellow status">pending</span> · ML surrogate <span class="label label-yellow status">pending</span>

{: .warning-title }
> Before you compare
>
> The cleaned table is in SI units and one frame, with this case's corrections applied once; do not apply them again to the published files.
>
> - 9 known issues in the published files are listed under [Known data issues]({{ '/cases/case-j/data/' | relative_url }}#known-data-issues).
