---
title: "Versions and changes"
parent: API
nav_order: 2
description: "What the release, schema and data versions of the AIJ UWE benchmark API promise, the changelog, and how the files are regenerated and checked."
permalink: /api-reference/versions/
---

# Versions and changes

Two semantic versions and one fingerprint, all in `index.json` under `versions`:

| | what it versions | moves when |
|---|---|---|
| `versions.release` | what is served: the API files and the cleaned tables, as one release (the repository's `VERSION`, tag `vX.Y.Z`) | MAJOR: a file, field or column renamed or removed, a CSV column added or reordered, a unit or frame changed; MINOR: something added; PATCH: a value or text corrected |
| `schema_version` (also `versions.schema`) | the JSON contract of these documents | MAJOR: a field renamed or removed; MINOR: a field or endpoint added; the changelog below |
| `data_version` (also `versions.data`) | nothing: it is the SHA-256 of the served data, a fingerprint | whenever a served measurement, geometry or score file changes |

`release` in `index.json` gives the release's date, tag, release page, changelog and `base_url`: the raw files of
that release's frozen copy at its tag, which never change. `release_base_url` is the same copy on this site, and
`versions.json` lists every release. To pin an analysis to one release, fetch from one of them (see
[Versions and pinning]({{ '/api-reference/' | relative_url }}#versions-and-pinning)):

```bash
REL=$(curl -s -A "aij-client/1.0" $BASE/index.json | jq -r .release_base_url)   # .../api/3.2.1
curl -s -A "aij-client/1.0" "$REL/cases/A/points.csv" | head -3
```

Within a major `schema_version` the API only adds: new fields, new endpoints, new runs. Clients must ignore
fields they do not know. A field is renamed or removed only in a new major version, listed below. `index.json`
serves the same changelog as `changelog`; the releases are in [`CHANGELOG.md`](https://github.com/Eddy3D-Dev/AIJ-Data-Validation/blob/main/CHANGELOG.md).

## Changelog

{% include api-changelog.md %}

## Regenerating and checking

```bash
# everything (cleaned tables, figures, API), in the pinned image: what CI runs
docker run --rm -v "$PWD:/w" -w /w "$(cat scripts/BUILD_IMAGE)" bash scripts/build_all.sh

# the API alone
pip install --require-hashes -r requirements.lock
python scripts/build_api.py          # builds docs/api/<VERSION>/ and docs/api/, the case pages and the site includes, then verifies
python scripts/build_api.py --check  # verify only
```

The build writes the frozen copy of the release in `VERSION` (`docs/api/<VERSION>/`) and then the latest alias
(`docs/api/`), from the same code, and writes `docs/api/versions.json`. It never touches another release's copy:
once a release is tagged, `python scripts/release.py check` fails if its copy differs from the tag. A new release
therefore adds one directory to `docs/api/` and moves the alias. Copies are kept from release 3.2.1 on; the copies of earlier releases were withdrawn before anyone used them.

The build is a pure function of the repository: no timestamps and no commit hashes, so rebuilding unchanged inputs
gives byte-identical files. On every push and pull request, CI rebuilds everything in Python 3.12.12 (an image
pinned by digest) with every package pinned by hash, and fails if anything differs from what is committed or if
served content changed without the release version moving. The site deploys only after that check passes, and a
new `VERSION` is then tagged and released. Verification covers:

- every document against its JSON Schema, and `openapi.json` against the OpenAPI 3.1 specification;
- every file's size and SHA-256 against `index.json`, and every file served against the files listed, so a stray or
  missing file in any tree fails;
- every link inside every document, including that each `?v=` matches the file it points at, and that a link in a
  release's copy never leaves the copy (`versions.json` is the one file outside it);
- that the alias is the newest release, file for file: data files byte for byte, documents once their own address is
  accounted for;
- `versions.json` against a rebuild of it from the trees on disk and `CHANGELOG.md`;
- the point counts, the STL triangle counts and the archive's contents.

The point tables come from `clean/` (`points_source` in each `points.json` says which file). The scores and pairs
come from the snapshots in `validation/results/`, each registered in `RUNS` in `scripts/build_api.py`; an
unregistered snapshot stops the build.
