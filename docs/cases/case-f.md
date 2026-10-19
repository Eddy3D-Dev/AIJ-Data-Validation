---
title: "Case F"
parent: "Cases"
nav_order: 6
has_children: true
has_toc: false
generated: true
description: "Case F — Shinjuku district: Shinjuku sub-centre, Tokyo, November 1978: 1:800 tunnel (thermistor, 5 / 9 / 20 m) and a year of field cup anemometers; velocity ratio to the 500 m wind, 12 tunnel and 16 field directions."
---

# Case F

Shinjuku sub-centre, Tokyo, November 1978: 1:800 tunnel (thermistor, 5 / 9 / 20 m) and a year of field cup anemometers; velocity ratio to the 500 m wind, 12 tunnel and 16 field directions.
{: .fs-5 .fw-300 .lede }

[Reference data]({{ '/cases/case-f/data/' | relative_url }}){: .btn .btn-primary } [Validation]({{ '/cases/case-f/validation/' | relative_url }}){: .btn } [Case as JSON]({{ '/api/cases/F.json' | relative_url }}){: .btn }

<figure class="figure render">
<a href="{{ '/assets/geometry/case-f.png' | relative_url }}"><img src="{{ '/assets/web/case-f.png' | relative_url }}" width="1600" height="800" loading="lazy" alt="Case F — Shinjuku district"></a>
<figcaption>Shinjuku sub-centre, November 1978: terrain and buildings of the 1:800 model over a disc of 725 m radius (full-scale metres); north is +y, the towers over 100 m are blue.</figcaption>
</figure>

## At a glance

| Fact | Value |
|---|---|
| District | Shinjuku sub-centre during construction of the high-rise group, building configuration of November 1978 |
| Scale | 1:800 |
| Normalisation | velocity ratio = mean speed / the approaching mean speed at the boundary-layer height 500 m (full scale); the field values were converted to it with the tunnel (readme). $$U(500\text{ m})$$ is 10 m/s in the data paper and 10.65 m/s implied by the profile |
| Wind directions | N, NNE, NE, ENE, SE, SSE, S, SSW, SW, WNW, NW, NNW |
| Measured | 472 rows over 13 points: $$U/U_{\mathrm{ref}}$$, $$\sigma_{U/U_{\mathrm{ref}}}$$ |

{% include nomenclature.md %}

## Validation

| Engine | Status | Compared with | R (range) | FAC2 (range) |
|---|---|---|---|---|
| OpenFOAM 12 | <span class="label label-green status">scored</span> | Wind tunnel | +0.79 … +1.00 | 0.85 … 1.00 |
| OpenFOAM 12 | <span class="label label-green status">scored</span> | Field | +0.86 … +0.89 | 0.85 … 1.00 |
| OpenLB | <span class="label label-yellow status">pending</span> | — | — | — |
| FluidX3D | <span class="label label-yellow status">pending</span> | — | — | — |
| ML surrogate | <span class="label label-yellow status">pending</span> | — | — | — |
{: .scores }

{% include nomenclature-scores.md %}

{: .warning-title }
> Before you compare
>
> - The cleaned table is in SI units and one frame, with this case's corrections applied once. Do not apply them again.
> - Origin: centre of the reproduced district, tunnel floor plane. Length unit: m (FULL scale).
> - The published coordinates are multiplied by 800 in the cleaned table (`coordinate_scale_applied`).
> - Wind direction: compass FROM-direction (N = 0, E = 90), so N blows toward -y; flow\_dir = (-sin WD, -cos WD). Not stated by the sources; supported by the reference-building choice and by upwind roughness, and at NNW by a solved field (status \'corroborated by a solved field\'; the other directions stay \'unverified\').
> - 11 known issues in the published files are listed under [Known data issues]({{ '/cases/case-f/data/' | relative_url }}#known-data-issues).
