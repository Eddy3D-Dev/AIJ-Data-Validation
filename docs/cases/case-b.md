---
title: "Case B — 1:4:4 slab"
parent: "Cases"
nav_order: 2
has_children: true
has_toc: false
generated: true
description: "Isolated 1:4:4 slab, velocity field (split-fibre hot wire)."
---

# Case B — 1:4:4 slab

Isolated 1:4:4 slab, velocity field (split-fibre hot wire).
{: .fs-5 .fw-300 .lede }

[Reference data]({{ '/cases/case-b/data/' | relative_url }}){: .btn .btn-primary } [Validation]({{ '/cases/case-b/validation/' | relative_url }}){: .btn } [Case as JSON]({{ '/api/cases/B.json' | relative_url }}){: .btn }

<figure class="figure render">
<img src="{{ '/assets/geometry/case-b.png' | relative_url }}" alt="Case B — 1:4:4 slab">
<figcaption>Isolated 1:4:4 slab, 0.05 m along the wind, 0.20 m across, 0.20 m tall (model scale); the wind blows along +x.</figcaption>
</figure>

## At a glance

| Fact | Value |
|---|---|
| Building | 1:4:4 (depth : width : height) slab |
| Reynolds number Re\_H | 72,000 |
| U\_H (m/s) | 5.133 |
| Wind directions (°) | 0 |
| Measurement planes | vertical centre plane y/H = 0, horizontal z/H = 1/16 |
| Measured | 224 rows over 224 points: U, V, W, uu, vv, ww, k |

## Agreement with the tunnel

| Engine | Status | R | FAC2 |
|---|---|---|---|
| OpenFOAM 12 | <span class="label label-green status">scored</span> | +0.40 … +0.96 | 0.28 … 0.70 |
| OpenLB | <span class="label label-green status">scored</span> | +0.49 … +0.90 | 0.04 … 0.64 |
| FluidX3D | <span class="label label-green status">scored</span> | +0.85 … +0.95 | 0.48 … 0.64 |
| ML surrogate | <span class="label label-green status">scored</span> | -0.24 … +0.01 | 0.36 … 0.46 |
{: .scores }

R and FAC2 are the range over the headline scores of an engine's runs (velocity components, k, wind directions; negative controls left out). *Scored* means a run exists and its scores are served, not that it agrees: every score, its figures and its reading are on the [Validation page]({{ '/cases/case-b/validation/' | relative_url }}).

{: .warning-title }
> Before you compare
>
> The cleaned table is in SI units and one frame, with this case's corrections applied once; do not apply them again to the published files.
>
> - The lateral velocity V is multiplied by -1 in the cleaned table (`lateral_sign_applied`): the published file's V has the other sign convention.
> - The published coordinates are multiplied by 0.001 in the cleaned table (`coordinate_scale_applied`).
> - 3 known issues in the published files are listed under [Known data issues]({{ '/cases/case-b/data/' | relative_url }}#known-data-issues).
