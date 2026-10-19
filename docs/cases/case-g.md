---
title: "Case G — flow behind a tree belt"
parent: "Cases"
nav_order: 7
has_children: true
has_toc: false
generated: true
description: "Field observation behind the Tsuiji-matsu tree belt (a porous windbreak, 74 m × 2 m × 7 m with a 1.2 m gap below): normalised mean speed and k at 28 points on the centre section (sonic anemometers)."
---

# Case G — flow behind a tree belt

Field observation behind the Tsuiji-matsu tree belt (a porous windbreak, 74 m × 2 m × 7 m with a 1.2 m gap below): normalised mean speed and $$k$$ at 28 points on the centre section (sonic anemometers).
{: .fs-5 .fw-300 .lede }

[Reference data]({{ '/cases/case-g/data/' | relative_url }}){: .btn .btn-primary } [Validation]({{ '/cases/case-g/validation/' | relative_url }}){: .btn } [Case as JSON]({{ '/api/cases/G.json' | relative_url }}){: .btn }

<figure class="figure render">
<a href="{{ '/assets/geometry/case-g.png' | relative_url }}"><img src="{{ '/assets/web/case-g.png' | relative_url }}" width="1600" height="800" loading="lazy" alt="Case G — flow behind a tree belt"></a>
<figcaption>The Tsuiji-matsu tree belt, 2 m × 74 m × 7 m with a 1.2 m gap below (full scale; shown as its envelope, a porous canopy); the wind blows along +x and the measurements are behind the belt.</figcaption>
</figure>

## At a glance

| Fact | Value |
|---|---|
| Normalisation | `velocity_ratio` = $$U/U_H$$ and `k_ratio` = $$k/U_H^2$$, $$U_H$$ = the mean wind speed at 7 m during each measurement period (interpolated with the approach flow\'s power law, index 0.22); nothing is published in m/s |
| Wind directions (°) | 0 |
| Measured | 28 rows over 28 points: $$U/U_{\mathrm{ref}}$$, $$k/U_{\mathrm{ref}}^2$$ |

{% include nomenclature.md %}

## Validation

| Engine | Status | Compared with | R (range) | FAC2 (range) |
|---|---|---|---|---|
| OpenFOAM 12 | <span class="label label-green status">scored</span> | Field | +0.21 … +0.50 | 0.68 … 1.00 |
| OpenLB | <span class="label label-yellow status">pending</span> | — | — | — |
| FluidX3D | <span class="label label-yellow status">pending</span> | — | — | — |
| ML surrogate | <span class="label label-yellow status">pending</span> | — | — | — |
{: .scores }

{% include nomenclature-scores.md %}

LAD and Cd are not in the dataset (only the shading rate, 81 %). The drag values are crowns of the Eddy3D vegetation library.

{: .warning-title }
> Before you compare
>
> - The cleaned table is in SI units and one frame, with this case's corrections applied once. Do not apply them again.
> - Origin: the leeward face of the tree belt at ground level, on the vertical section through the belt\'s centre. Length unit: m (full scale).
> - Wind direction: one direction, toward +x (perpendicular to the belt); the field wind\'s angle to the belt normal is not published.
> - 6 known issues in the published files are listed under [Known data issues]({{ '/cases/case-g/data/' | relative_url }}#known-data-issues).
