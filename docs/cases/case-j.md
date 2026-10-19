---
title: "Case J — 1:1:2 building, non-isothermal"
parent: "Cases"
nav_order: 10
has_children: true
has_toc: false
generated: true
description: "Isolated 1:1:2 building with a floor tracer source in an unstably stratified boundary layer: velocity, temperature, tracer concentration and their turbulent fluxes at 444 points on three planes."
---

# Case J

Isolated 1:1:2 building with a floor tracer source in an unstably stratified boundary layer: velocity, temperature, tracer concentration and their turbulent fluxes at 444 points on three planes.
{: .fs-5 .fw-300 .lede }

[Reference data]({{ '/cases/case-j/data/' | relative_url }}){: .btn .btn-primary } [Validation]({{ '/cases/case-j/validation/' | relative_url }}){: .btn } [Case as JSON]({{ '/api/cases/J.json' | relative_url }}){: .btn }

<figure class="figure render">
<a href="{{ '/assets/geometry/case-j.png' | relative_url }}"><img src="{{ '/assets/web/case-j.png' | relative_url }}" width="1600" height="800" loading="lazy" alt="Case J — 1:1:2 building, non-isothermal"></a>
<figcaption>Isolated 1:1:2 building, b = 0.08 m, H = 0.16 m (model scale); the orange ring marks the floor tracer source, 0.25 H behind the building (seen through it); the wind blows along +x.</figcaption>
</figure>

## At a glance

| Fact | Value |
|---|---|
| Building | 1:1:2 (width : depth : height) prism, $$b = 0.08\thinspace\mathrm{m}$$, $$H = 2b = 0.16\thinspace\mathrm{m}$$ |
| Reynolds number $$\mathrm{Re_H}$$ | 16,000 |
| $$U_H$$ (m/s) | 1.4581 |
| Wind directions (°) | 0 |
| Measurement planes | vertical centre plane $$y/H = 0$$, horizontal $$z/H = 0.025$$ (y \<= 0 side only), horizontal $$z/H = 0.25$$ |
| Measured | 444 rows over 444 points: $$U$$, $$V$$, $$W$$, $$\overline{u'u'}$$, $$\overline{v'v'}$$, $$\overline{w'w'}$$, $$k$$, $$C$$, $$c_{\mathrm{rms}}$$, $$c^\ast$$, $$T$$, $$T_{\mathrm{rms}}$$, $$\overline{u'\theta'}$$, $$\overline{v'\theta'}$$, $$\overline{w'\theta'}$$ |

{% include nomenclature.md %}

## Validation

| Engine | Status | Compared with | R (range) | FAC2 (range) |
|---|---|---|---|---|
| OpenFOAM 12 (UMF) | <span class="label label-green status">scored</span> | Wind tunnel | +0.32 … +0.92 | 0.29 … 1.00 |
| OpenFOAM 12 (UMF) buoyantKEpsilon | <span class="label label-green status">scored</span> | Wind tunnel | +0.36 … +0.92 | 0.29 … 1.00 |
| OpenLB | <span class="label label-yellow status">pending</span> | — | — | — |
| FluidX3D | <span class="label label-yellow status">pending</span> | — | — | — |
| ML surrogate | <span class="label label-yellow status">pending</span> | — | — | — |
{: .scores }

{% include nomenclature-scores.md %}

{: .warning-title }
> Before you compare
>
> - The cleaned table is in SI units and one frame, with this case's corrections applied once. Do not apply them again.
> - Origin: the building\'s leeward (downwind) wall centre on the ground; $$x = 0$$ is the leeward wall. Length unit: m (model scale).
> - 10 known issues in the published files are listed under [Known data issues]({{ '/cases/case-j/data/' | relative_url }}#known-data-issues).
