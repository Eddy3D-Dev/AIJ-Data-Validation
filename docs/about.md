---
title: "About and cite"
nav_order: 6
description: "What this site and repository are, how to cite the AIJ UWE benchmark and its cases, the licence, and how a release is reproduced."
---

# About and cite

## What this is

Wind-tunnel and field reference data from the **AIJ UWE** (Architectural Institute of Japan, Urban Wind Environment)
benchmark, cleaned and packaged case by case, together with Eddy3D's validation against it. The cleaned tables
re-release every case in one schema (SI units, one frame per case), regenerated from the published files by a
checked, deterministic build. The same material is served as this website and as a [static API]({{ '/api-reference/' | relative_url }}).

The measurements are not ours: they belong to their collectors and distributors, named on each case's Data page.
The validation scores are Eddy3D's, and each says which run it comes from and how to reproduce it.

## Cite

Cite the benchmark, and the dataset of each case you use.

- Kikumoto, H., Okaze, T., Yoshie, R., Tachibana, T., Ishihara, T., Nonomura, Y., Kiyota, N., Kondo, H., Mochida, A.,
  Tominaga, Y. (2026). *Comprehensive Experimental Database for Validating CFD Simulations in Urban Wind
  Environment: Benchmark Cases Curated by the Architectural Institute of Japan.* Japan Architectural Review 9(1),
  e70083. [doi:10.1002/2475-8876.70083](https://doi.org/10.1002/2475-8876.70083)
- Tominaga, Y. et al. (2008). *AIJ guidelines for practical applications of CFD to pedestrian wind environment
  around buildings.* JWEIA 96, 1749–1761. [doi:10.1016/j.jweia.2008.02.058](https://doi.org/10.1016/j.jweia.2008.02.058)
- Each case's own requested citation and Zenodo DOI are on its Data page (*Cases*, then the case, then *Reference
  data*, section *Attribution*) and in `/api/cases/{id}.json` (`citation_requested`, `doi`).
- This repository: [`CITATION.cff`](https://github.com/SustainableUrbanSystemsLab/CFD-Test-Cases-Architectural-Institute-of-Japan-AIJ/blob/main/CITATION.cff)
  is what GitHub's *Cite this repository* button reads.

## Licence

The measurement data is distributed under CC BY 4.0 (SPDX `CC-BY-4.0`) by its collectors and editors, who are named
per case. The data paper is linked, not stored here.

## Reproducing a release

Every release is a tag whose files never change. A release rebuilds byte for byte from its tag, in one container image
pinned by digest, with every Python package pinned by hash; the site's CI rebuilds everything on each push and fails if
a single byte differs from what is committed, or if served content changed without the version moving. The
[versions page]({{ '/api-reference/versions/' | relative_url }}) says what each number promises and lists the changes, and the
[changelog](https://github.com/SustainableUrbanSystemsLab/CFD-Test-Cases-Architectural-Institute-of-Japan-AIJ/blob/main/CHANGELOG.md)
has every release.

## Where the files are

The [repository](https://github.com/SustainableUrbanSystemsLab/CFD-Test-Cases-Architectural-Institute-of-Japan-AIJ)
holds the files exactly as published by their collectors (`raw/`), the cleaned tables (`clean/`), the validation
snapshots and figures (`validation/`), and the build scripts. Its README describes each folder.
