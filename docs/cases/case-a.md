---
title: "Case A — 1:1:2 building"
parent: "Cases"
nav_order: 1
has_children: true
has_toc: false
generated: true
description: "Isolated 1:1:2 building, velocity field (split-fibre hot wire)."
---

# Case A

Isolated 1:1:2 building, velocity field (split-fibre hot wire).
{: .fs-5 .fw-300 .lede }

[Reference data]({{ '/cases/case-a/data/' | relative_url }}){: .btn .btn-primary } [Validation]({{ '/cases/case-a/validation/' | relative_url }}){: .btn } [Case as JSON]({{ '/api/cases/A.json' | relative_url }}){: .btn }

<figure class="figure render">
<a href="{{ '/assets/geometry/case-a.png' | relative_url }}"><img src="{{ '/assets/web/case-a.png' | relative_url }}" width="1600" height="800" loading="lazy" alt="Case A — 1:1:2 building"></a>
<figcaption>Isolated 1:1:2 building, b = 0.08 m, H = 0.16 m (model scale); the wind blows along +x.</figcaption>
</figure>

## At a glance

| Fact | Value |
|---|---|
| Building | 1:1:2 (width : depth : height) prism |
| Reynolds number $$\mathrm{Re_H}$$ | 24,000 |
| $$U_H$$ (m/s) | 4.491 |
| Wind directions (°) | 0 |
| Measurement planes | vertical centre plane $$y/b = 0$$, horizontal $$z/b = 0.125$$, horizontal $$z/b = 1.25$$ |
| Measured | 186 rows over 186 points: $$U$$, $$V$$, $$W$$, $$\overline{u'u'}$$, $$\overline{v'v'}$$, $$\overline{w'w'}$$, $$k$$ |

{% include nomenclature.md %}

## Validation

| Engine | Status | Compared with | R (range) | FAC2 (range) |
|---|---|---|---|---|
| OpenFOAM 12 | <span class="label label-green status">scored</span> | Wind tunnel | +0.48 … +0.96 | 0.35 … 0.82 |
| OpenLB | <span class="label label-green status">scored</span> | Wind tunnel | +0.20 … +0.81 | 0.00 … 0.64 |
| FluidX3D | <span class="label label-green status">scored</span> | Wind tunnel | +0.59 … +0.85 | 0.22 … 0.60 |
| ML surrogate | <span class="label label-green status">scored</span> | Wind tunnel | -0.13 … +0.43 | 0.26 … 0.62 |
{: .scores }

{% include nomenclature-scores.md %}

{: .warning-title }
> Before you compare
>
> - The cleaned table is in SI units and one frame, with this case's corrections applied once. Do not apply them again.
> - Origin: building centre on the ground plane. Length unit: m (model scale).
> - 3 known issues in the published files are listed under [Known data issues]({{ '/cases/case-a/data/' | relative_url }}#known-data-issues).
