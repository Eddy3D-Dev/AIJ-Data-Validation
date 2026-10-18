---
title: "Case H — 1:1:2 building with a floor point source"
parent: "Cases"
nav_order: 8
has_children: true
has_toc: false
generated: true
description: "Isolated 1:1:2 building with an ethylene point source on the floor behind it: velocity (split-fibre hot wire) and concentration (hydrocarbon analyser) at 876 points."
---

# Case H — 1:1:2 building with a floor point source

Isolated 1:1:2 building with an ethylene point source on the floor behind it: velocity (split-fibre hot wire) and concentration (hydrocarbon analyser) at 876 points.
{: .fs-5 .fw-300 .lede }

[Reference data]({{ '/cases/case-h/data/' | relative_url }}){: .btn .btn-primary } [Validation]({{ '/cases/case-h/validation/' | relative_url }}){: .btn } [Case as JSON]({{ '/api/cases/H.json' | relative_url }}){: .btn }

<figure class="figure render">
<a href="{{ '/assets/geometry/case-h.png' | relative_url }}"><img src="{{ '/assets/web/case-h.png' | relative_url }}" width="1600" height="800" loading="lazy" alt="Case H — 1:1:2 building with a floor point source"></a>
<figcaption>Isolated 1:1:2 building, 0.10 m × 0.10 m × 0.20 m (model scale); the wind blows along +x. The tracer comes from a 4 mm floor hole 0.25 H behind the leeward face (not drawn).</figcaption>
</figure>

## At a glance

| Fact | Value |
|---|---|
| Building | 1:1:2 (width : depth : height) prism, 0.10 × 0.10 × 0.20 m |
| Reynolds number $$\mathrm{Re_H}$$ | 43,000 |
| $$U_H$$ (m/s) | 3.226 |
| Wind directions (°) | 0 |
| Measurement planes | vertical centre plane y/H = 0, horizontal z/H = 1/16 (y in \[-0.2, 0.2\]), horizontal z/H = 1/4 and 1/2 (y in \[0, 0.2\]) |
| Measured | 1,652 rows over 876 points: $$U$$, $$V$$, $$W$$, $$\overline{u'u'}$$, $$\overline{v'v'}$$, $$\overline{w'w'}$$, $$k$$, $$C$$, $$c_{\mathrm{rms}}$$, $$c^\ast$$ |

{% include nomenclature.md %}

## Validation

| Engine | Status | Compared with | R (range) | FAC2 (range) |
|---|---|---|---|---|
| OpenFOAM 12 | <span class="label label-green status">scored</span> | Wind tunnel | +0.11 … +0.95 | 0.31 … 0.69 |
| OpenLB | <span class="label label-yellow status">pending</span> | — | — | — |
| FluidX3D | <span class="label label-yellow status">pending</span> | — | — | — |
| ML surrogate | <span class="label label-yellow status">pending</span> | — | — | — |
{: .scores }

{% include nomenclature-scores.md %}

{: .warning-title }
> Before you compare
>
> - The cleaned table is in SI units and one frame, with this case's corrections applied once. Do not apply them again.
> - Origin: the centre of the building\'s leeward face on the ground plane. Length unit: m (model scale).
> - The lateral velocity V is multiplied by -1 for point numbers 1-220 (the vertical-plane sheet of the workbook), +1 elsewhere in the cleaned table (`lateral_sign_applied`): the published file's V has the other sign convention.
> - 7 known issues in the published files are listed under [Known data issues]({{ '/cases/case-h/data/' | relative_url }}#known-data-issues).
