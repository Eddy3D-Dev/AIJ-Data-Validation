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
<a href="{{ '/assets/geometry/case-j.png' | relative_url }}"><img src="{{ '/assets/web/case-j.png' | relative_url }}" width="1600" height="800" loading="lazy" alt="Case J — 1:1:2 building, non-isothermal"></a>
<figcaption>Isolated 1:1:2 building, b = 0.08 m, H = 0.16 m (model scale); the orange ring marks the floor tracer source, 0.25 H behind the building (seen through it); the wind blows along +x.<br><a class="original" href="{{ '/assets/geometry/case-j.png' | relative_url }}">1200 dpi original, 1.4 MB</a></figcaption>
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

| Engine | Status | R | FAC2 |
|---|---|---|---|
| OpenFOAM 12 | <span class="label label-yellow status">pending</span> | — | — |
| UMF | <span class="label label-green status">scored</span> | +0.32 … +0.92 | 0.29 … 1.00 |
| UMF buoyantKEpsilon | <span class="label label-green status">scored</span> | +0.36 … +0.92 | 0.29 … 1.00 |
| OpenLB | <span class="label label-yellow status">pending</span> | — | — |
| FluidX3D | <span class="label label-yellow status">pending</span> | — | — |
| ML surrogate | <span class="label label-yellow status">pending</span> | — | — |
{: .scores }

{: .warning-title }
> Before you compare
>
> - The cleaned table is in SI units and one frame, with this case's corrections applied once.
> - Origin: the building\'s leeward (downwind) wall centre on the ground; x = 0 is the leeward wall. Length unit: m (model scale).
> - 10 known issues in the published files are listed under [Known data issues]({{ '/cases/case-j/data/' | relative_url }}#known-data-issues).

<details markdown="block">
<summary>Interpretation: Using the cleaned table</summary>

Do not apply the corrections again to the published files.

</details>
