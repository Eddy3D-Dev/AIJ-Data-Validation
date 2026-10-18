---
title: "Case F — Shinjuku district"
parent: "Cases"
nav_order: 6
has_children: true
has_toc: false
generated: true
description: "Shinjuku sub-centre, Tokyo, November 1978: 1:800 tunnel (thermistor, 5 / 9 / 20 m) and a year of field cup anemometers; velocity ratio to the 500 m wind, 12 tunnel and 16 field directions."
---

# Case F — Shinjuku district

Shinjuku sub-centre, Tokyo, November 1978: 1:800 tunnel (thermistor, 5 / 9 / 20 m) and a year of field cup anemometers; velocity ratio to the 500 m wind, 12 tunnel and 16 field directions.
{: .fs-5 .fw-300 .lede }

[Reference data]({{ '/cases/case-f/data/' | relative_url }}){: .btn .btn-primary } [Validation]({{ '/cases/case-f/validation/' | relative_url }}){: .btn } [Case as JSON]({{ '/api/cases/F.json' | relative_url }}){: .btn }

<figure class="figure render">
<a href="{{ '/assets/geometry/case-f.png' | relative_url }}"><img src="{{ '/assets/web/case-f.png' | relative_url }}" width="1600" height="800" loading="lazy" alt="Case F — Shinjuku district"></a>
<figcaption>Shinjuku sub-centre, November 1978: terrain and buildings of the 1:800 model over a disc of 725 m radius (full-scale metres); north is +y, the towers over 100 m are blue.<br><a class="original" href="{{ '/assets/geometry/case-f.png' | relative_url }}">1200 dpi original, 1.9 MB</a></figcaption>
</figure>

## At a glance

| Fact | Value |
|---|---|
| District | Shinjuku sub-centre during construction of the high-rise group, building configuration of November 1978 |
| Scale | 1:800 |
| Normalisation | velocity ratio = mean speed / the approaching mean speed at the boundary-layer height 500 m (full scale); the field values were converted to it with the tunnel (readme). U(500 m) is 10 m/s in the data paper and 10.65 m/s implied by the profile |
| Wind directions | N, NNE, NE, ENE, SE, SSE, S, SSW, SW, WNW, NW, NNW |
| Measured | 472 rows over 13 points: velocity\_ratio, velocity\_ratio\_sd |

## Agreement with the tunnel

**No validation has been run for this case yet.** Nothing on this page is a claim about it. Eddy3D's fixture for this case is written and its solves are queued; no result exists yet. Engine status: OpenFOAM 12 <span class="label label-yellow status">pending</span> · OpenLB <span class="label label-yellow status">pending</span> · FluidX3D <span class="label label-yellow status">pending</span> · ML surrogate <span class="label label-yellow status">pending</span>

{: .warning-title }
> Before you compare
>
> The cleaned table is in SI units and one frame, with this case's corrections applied once; do not apply them again to the published files.
>
> - The published coordinates are multiplied by 800 in the cleaned table (`coordinate_scale_applied`).
> - The sense in which the wind direction rotates is a convention to check before comparing at any direction other than 0° (see *Frame and units* on the Data page).
> - 10 known issues in the published files are listed under [Known data issues]({{ '/cases/case-f/data/' | relative_url }}#known-data-issues).
