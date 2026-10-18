---
title: "About and cite"
nav_order: 6
description: "What this site and repository are, the citations of this API, the data paper and each case, the licence, and how a release is reproduced."
---

# About and cite

## What this is

Validation data from the AIJ (Architectural Institute of Japan) benchmark cases—cleaned and packaged as an API.
The cleaned tables re-release every case in one schema (SI units, one frame per case), regenerated from the published
files by a deterministic build. The site and the [static API]({{ '/api-reference/' | relative_url }}) serve the same
files. Eddy3D's validation scores sit beside the data.

Data: Kikumoto et al. (2026), CC BY 4.0. Collectors per case on each Data page.

## Cite

{% include cite.md %}

This repository: [`CITATION.cff`](https://github.com/SustainableUrbanSystemsLab/CFD-Test-Cases-Architectural-Institute-of-Japan-AIJ/blob/main/CITATION.cff) is what GitHub's *Cite this repository* button reads.

## Licence

CC BY 4.0 (SPDX `CC-BY-4.0`). Collectors and editors are named per case.

## Reproducing a release

Every release is a tag whose files never change, and it rebuilds byte for byte from that tag.

- The build runs in one container image, pinned by digest.
- Every Python package is pinned by hash.
- CI rebuilds everything on each push.
- CI fails if a byte differs from what is committed, or if served content changed without the version moving.

The [versions page]({{ '/api-reference/versions/' | relative_url }}) says what each number promises and lists the changes. The
[changelog](https://github.com/SustainableUrbanSystemsLab/CFD-Test-Cases-Architectural-Institute-of-Japan-AIJ/blob/main/CHANGELOG.md)
has every release.

## Where the files are

The [repository](https://github.com/SustainableUrbanSystemsLab/CFD-Test-Cases-Architectural-Institute-of-Japan-AIJ)
holds the files as published by their collectors (`raw/`; text files with LF line endings, see the README), the cleaned tables (`clean/`), the validation
snapshots and figures (`validation/`), and the build scripts. Its README describes each folder.
