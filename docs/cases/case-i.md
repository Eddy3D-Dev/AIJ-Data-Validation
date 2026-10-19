---
title: "Case I"
parent: "Cases"
nav_order: 9
has_children: true
has_toc: false
generated: true
description: "Case I — cube with a roof point source: Isolated cube with an ethane point source at the centre of its roof: velocity (laser Doppler, 91 points) and concentration (hydrocarbon analyser, 539 points)."
---

# Case I

Isolated cube with an ethane point source at the centre of its roof: velocity (laser Doppler, 91 points) and concentration (hydrocarbon analyser, 539 points).
{: .fs-5 .fw-300 .lede }

[Reference data]({{ '/cases/case-i/data/' | relative_url }}){: .btn .btn-primary } [Validation]({{ '/cases/case-i/validation/' | relative_url }}){: .btn } [Case as JSON]({{ '/api/cases/I.json' | relative_url }}){: .btn }

<figure class="figure render">
<a href="{{ '/assets/geometry/case-i.png' | relative_url }}"><img src="{{ '/assets/web/case-i.png' | relative_url }}" width="1600" height="800" loading="lazy" alt="Case I — cube with a roof point source"></a>
<figcaption>Isolated cube, 0.10 m on a side (model scale); the wind blows along +x. The tracer is released from a 6 mm outlet at the centre of the roof (not drawn).</figcaption>
</figure>

## At a glance

| Fact | Value |
|---|---|
| Building | cube, 0.10 m on a side (= H) |
| Reynolds number $$\mathrm{Re_H}$$ | 11,000 |
| $$U_H$$ (m/s) | 1.7 |
| Wind directions (°) | 0 |
| Measurement planes | velocity: $$y/H = 0$$ and $$z/H = 0.5$$, concentration: $$y/H = 0$$ and $$z/H = 0$$ (the ground) |
| Measured | 630 rows over 630 points: $$U$$, $$V$$, $$W$$, $$k$$, $$C$$, $$c^\ast$$ |

{% include nomenclature.md %}

## Validation

| Engine | Status | Compared with | R (range) | FAC2 (range) |
|---|---|---|---|---|
| OpenFOAM 12 | <span class="label label-green status">scored</span> | Wind tunnel | +0.90 … +1.00 | 0.36 … 0.92 |
| OpenFOAM 12 k-ε | <span class="label label-green status">scored</span> | Wind tunnel | +0.87 … +0.99 | 0.44 … 0.91 |
| OpenFOAM 12 k-ω SST | <span class="label label-green status">scored</span> | Wind tunnel | +0.44 … +0.99 | 0.38 … 0.88 |
| OpenLB | <span class="label label-yellow status">pending</span> | — | — | — |
| FluidX3D | <span class="label label-yellow status">pending</span> | — | — | — |
| ML surrogate | <span class="label label-yellow status">pending</span> | — | — | — |
{: .scores }

{% include nomenclature-scores.md %}

{: .warning-title }
> Before you compare
>
> - The cleaned table is in SI units and one frame, with this case's corrections applied once. Do not apply them again.
> - Origin: the centre of the cube on the ground plane. Length unit: m (model scale).
> - 7 known issues in the published files are listed under [Known data issues]({{ '/cases/case-i/data/' | relative_url }}#known-data-issues).
