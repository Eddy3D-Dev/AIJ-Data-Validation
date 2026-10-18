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

Field observation behind the Tsuiji-matsu tree belt (a porous windbreak, 74 m × 2 m × 7 m with a 1.2 m gap below): normalised mean speed and k at 28 points on the centre section (sonic anemometers).
{: .fs-5 .fw-300 .lede }

[Reference data]({{ '/cases/case-g/data/' | relative_url }}){: .btn .btn-primary } [Validation]({{ '/cases/case-g/validation/' | relative_url }}){: .btn } [Case as JSON]({{ '/api/cases/G.json' | relative_url }}){: .btn }

<figure class="figure render">
<a href="{{ '/assets/geometry/case-g.png' | relative_url }}"><img src="{{ '/assets/web/case-g.png' | relative_url }}" width="1600" height="800" loading="lazy" alt="Case G — flow behind a tree belt"></a>
<figcaption>The Tsuiji-matsu tree belt, 2 m × 74 m × 7 m with a 1.2 m gap below (full scale; shown as its envelope — a porous canopy, not a solid body); the wind blows along +x and the measurements are behind the belt.<br><a class="original" href="{{ '/assets/geometry/case-g.png' | relative_url }}">1200 dpi original, 0.7 MB</a></figcaption>
</figure>

## At a glance

| Fact | Value |
|---|---|
| Normalisation | velocity\_ratio = U/UH and k\_ratio = k/UH^2, UH = the mean wind speed at 7 m during each measurement period (interpolated with the approach flow\'s power law, index 0.22); nothing is published in m/s |
| Wind directions (°) | 0 |
| Measured | 28 rows over 28 points: velocity\_ratio, k\_ratio |

## Agreement with the tunnel

**No validation has been run for this case yet.** Nothing on this page is a claim about it. Eddy3D's fixture for this case is written and its solves are queued; no result exists yet. Engine status: OpenFOAM 12 <span class="label label-yellow status">pending</span> · OpenLB <span class="label label-yellow status">pending</span> · FluidX3D <span class="label label-yellow status">pending</span> · ML surrogate <span class="label label-yellow status">pending</span>

{: .warning-title }
> Before you compare
>
> The cleaned table is in SI units and one frame, with this case's corrections applied once; do not apply them again to the published files.
>
> - The sense in which the wind direction rotates is a convention to check before comparing at any direction other than 0° (see *Frame and units* on the Data page).
> - 6 known issues in the published files are listed under [Known data issues]({{ '/cases/case-g/data/' | relative_url }}#known-data-issues).
