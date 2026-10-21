---
title: "Case D"
parent: "Cases"
nav_order: 4
has_children: true
has_toc: false
generated: true
description: "Case D — high-rise among city blocks: 1:1:4 tower in a regular array of 82 low blocks, pedestrian-height scalar speed (thermistor, 3 wind directions) plus a 33-point split-fibre velocity field at WD = 0."
---

# Case D

1:1:4 tower in a regular array of 82 low blocks, pedestrian-height scalar speed (thermistor, 3 wind directions) plus a 33-point split-fibre velocity field at $$\mathrm{WD} = 0$$.
{: .fs-5 .fw-300 .lede }

[Reference data]({{ '/cases/case-d/data/' | relative_url }}){: .btn .btn-primary } [Validation]({{ '/cases/case-d/validation/' | relative_url }}){: .btn } [Case as JSON]({{ '/api/cases/D.json' | relative_url }}){: .btn }

<figure class="figure render">
<a href="{{ '/assets/geometry/case-d.png' | relative_url }}"><img src="{{ '/assets/web/case-d.png' | relative_url }}" width="1600" height="800" loading="lazy" alt="Case D — high-rise among city blocks"></a>
<figcaption>A 0.25 m tower (blue) among 82 low blocks over 1.40 m × 1.35 m (1:400 model scale); the arrow is WD = 0°.</figcaption>
</figure>

## At a glance

| Fact | Value |
|---|---|
| Tower | $$0.25H\thinspace\times\thinspace 0.25H\thinspace\times\thinspace H = 62.5\thinspace\times\thinspace 62.5\thinspace\times\thinspace 250\thinspace\mathrm{mm}$$ (1:1:4) |
| Scale | 1:400 ($$H = 100\thinspace\mathrm{m}$$ full scale; the 5 mm measurement plane = 2 m) |
| Reynolds number $$\mathrm{Re_H}$$ | 110,000 |
| $$U_H$$ (m/s) | 6.65 |
| Wind directions (°) | 0, 22.5, 45 |
| Measurement height (m) | 0.005 |
| Measured | 267 rows over 78 points: $$V_{\mathrm{s}}$$, $$U$$, $$V$$, $$W$$, $$\overline{u'u'}$$, $$\overline{v'v'}$$, $$\overline{w'w'}$$, $$k$$ |

{% include nomenclature.md %}

## Validation

| Engine | Status | Compared with | R (range) | FAC2 (range) |
|---|---|---|---|---|
| OpenFOAM 12 | <span class="label label-green status">scored</span> | Wind tunnel | +0.78 … +0.95 | 0.48 … 0.92 |
| OpenLB | <span class="label label-grey status">not comparable</span> | — | — | — |
| FluidX3D | <span class="label label-grey status">not comparable</span> | — | — | — |
| ML surrogate | <span class="label label-green status">scored</span> | Wind tunnel | +0.22 … +0.59 | 0.34 … 0.64 |
{: .scores }

{: .warning-title }
> Before you compare
>
> - The cleaned table is in SI units and one frame, with this case's corrections applied once. Do not apply them again.
> - Origin: tower centre on the ground plane (the array\'s bounding box is centred on it). Length unit: m (model scale; converted from the workbook\'s millimetres).
> - The published coordinates are multiplied by 0.001 in the cleaned table (`coordinate_scale_applied`).
> - Wind direction: $$+x$$ toward $$+y$$, read from Figure 4 of the data paper. Solved Eddy3D fields score R 0.80 (22.5 deg) and 0.85 (45 deg) in Figure 4\'s sense, 0.40 and 0.17 mirrored.
> - 6 known issues in the published files are listed under [Known data issues]({{ '/cases/case-d/data/' | relative_url }}#known-data-issues).
