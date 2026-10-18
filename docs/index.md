---
title: "Home"
nav_order: 1
description: "Wind-tunnel and field reference data from the Architectural Institute of Japan Urban Wind Environment benchmark, Cases A to M, cleaned case by case, with Eddy3D's validation against it and a static API."
---

# AIJ UWE benchmark
{: .no_toc }

Wind-tunnel and field reference data from the **AIJ UWE** (Architectural Institute of Japan, Urban Wind Environment)
benchmark, Cases A to M, cleaned and packaged case by case, with Eddy3D's validation against it where it exists.
{: .fs-6 .fw-300 .lede }

[Browse the cases]({{ '/cases/' | relative_url }}){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 } [Use the API]({{ '/api-reference/' | relative_url }}){: .btn .fs-5 .mb-4 .mb-md-0 .mr-2 } [Data paper (DOI)](https://doi.org/10.1002/2475-8876.70083){: .btn .fs-5 .mb-4 .mb-md-0 }

## The cases

{% include case-gallery.md %}

## Cases at a glance

{% include cases-table.md %}

*Scored by* names the engines with a published run for the case. *Scored* means a run exists and its scores are served,
not that it agrees: how well it agrees is in the numbers and their reading on the
[Validation]({{ '/validation/' | relative_url }}) pages. An engine that is not listed has no result for the case, and
nothing here is a claim about it.

## Where to go

- **[Cases]({{ '/cases/' | relative_url }})**: a page per case with its render, status and key numbers, then its reference data and its validation.
- **[Validation]({{ '/validation/' | relative_url }})**: every case against every engine in one table, the method, and the reading of each result.
- **[Known data issues]({{ '/known-data-issues/' | relative_url }})**: what in the published files changes a comparison if it is not accounted for (units, signs, frames, scalar vs vector speed).
- **[API]({{ '/api-reference/' | relative_url }})**: every endpoint with `curl` and Python examples, and the walk for [agents]({{ '/agents/' | relative_url }}).
- **[About and cite]({{ '/about/' | relative_url }})**: how to cite the benchmark and each case, the licence, and how a release is reproduced.

The measurement data belongs to its collectors and distributors, named per case (CC BY 4.0).
