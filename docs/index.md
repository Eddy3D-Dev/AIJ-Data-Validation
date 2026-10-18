---
title: "Home"
nav_order: 1
description: "Validation data from the AIJ (Architectural Institute of Japan) benchmark cases—cleaned and packaged as an API."
---

# AIJ UWE
{: .no_toc }

Validation data from the AIJ (Architectural Institute of Japan) benchmark cases—cleaned and packaged as an API.
{: .fs-6 .fw-300 .lede }

[Browse the cases]({{ '/cases/' | relative_url }}){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 } [Use the API]({{ '/api-reference/' | relative_url }}){: .btn .fs-5 .mb-4 .mb-md-0 .mr-2 } [Data paper (DOI)](https://doi.org/10.1002/2475-8876.70083){: .btn .fs-5 .mb-4 .mb-md-0 }

## The cases

{% include case-gallery.md %}

## Cases at a glance

{% include cases-table.md %}

## Where to go

- **[Cases]({{ '/cases/' | relative_url }})**: a page per case with its render, status and key numbers, then its reference data and its validation.
- **[Validation]({{ '/validation/' | relative_url }})**: every case against every engine in one table, and the method.
- **[Known data issues]({{ '/known-data-issues/' | relative_url }})**: what in the published files changes a comparison if it is not accounted for (units, signs, frames, scalar vs vector speed).
- **[API]({{ '/api-reference/' | relative_url }})**: every endpoint with `curl` and Python examples, and the walk for [agents]({{ '/agents/' | relative_url }}).
- **[About and cite]({{ '/about/' | relative_url }})**: how to cite the benchmark and each case, the licence, and how a release is reproduced.

Data: Kikumoto et al. (2026), CC BY 4.0. Collectors per case on each Data page.
