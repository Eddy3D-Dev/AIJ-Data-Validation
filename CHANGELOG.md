# Changelog

Every release of this repository's data and API, newest first. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); the version follows [Semantic Versioning](https://semver.org/)
with the rules of the [Data Package version recipe](https://datapackage.org/recipes/data-package-version/), applied to
what this repository serves (the API under `docs/api/` and the cleaned tables under `clean/`):

- **MAJOR**: an incompatible change. A served file, endpoint, field or column renamed or removed; a CSV column added,
  removed or reordered; a unit, frame or normalisation changed; a major change of the API schema.
- **MINOR**: a backward-compatible addition. A new case, configuration, run, endpoint, field or file.
- **PATCH**: a backward-compatible fix. A corrected value, score, caption or metadata text.

Documentation, figures and tooling that change no served byte need no release. `VERSION` holds the number;
CI fails a change to the served files that does not move it by at least the level the change needs, and tags
`vX.Y.Z` with a GitHub Release when it moves on `main`. The API's own contract has a separate version,
`schema_version`, with its changelog in `index.json` and on the [API page](https://sustainableurbansystems.com/CFD-Test-Cases-Architectural-Institute-of-Japan-AIJ/api-reference/#versioning-and-changes).

## [3.0.0] - 2026-10-18

Preliminary section, written with the versioned API layout; the integrating change rewrites it to cover everything in 3.0.0.

### Changed (incompatible)

- The point table gained 18 columns (`campaign`, `run`, `uv`, `uw`, `vw`, `C`, `c_rms`, `concentration_ratio`, `T`,
  `T_rms`, `uc`, `vc`, `wc`, `uT`, `vT`, `wT`, `velocity_ratio_sd`, `k_ratio`), appended after the 18 of 2.0.0; see
  `clean/SCHEMA.md`.

### Added

- Release-numbered API paths: every release is a frozen copy of the whole API under `/api/<release>/` (for example
  `/api/3.0.0/index.json`), the unversioned `/api/` paths always equal the newest release, and `/api/versions.json`
  lists every release. API schema 2.3.0 (a minor change: nothing renamed or removed). Release 2.0.0 predates the
  layout; `/api/2.0.0/` holds the files of its tag with only their addresses rewritten (`scripts/host_release.py`).

## [2.0.0] - 2026-10-18

The first tagged release. Every number from here on identifies exactly one content of the served files, and
the release rebuilds byte for byte from its tag (see *Reproduce a release* in the README).

### Changed (incompatible)

- Folders and files renamed to one scheme: `case-a/` … `case-e/` for the cases, `case-x-description.ext` for the
  repository's own files, `author-year-title.pdf` for papers. The README's *Repository layout and file names*
  lists every old and new name.
- API schema 2.0.0: `gotchas` is `known_issues`; `licence` is `license` (SPDX `CC-BY-4.0`); `generated_from` and
  `generated_at` are gone (`data_version` replaces them); links are named `url`, and downloads are objects with
  `url`, `path`, `media_type`, `bytes` and `sha256`; a result's `figures` is a list of `{url, caption}`.

### Added

- Validation runs, each with its scores and per-point pairs: OpenFOAM 12 on Case C (nine configurations), Case D
  (wind directions 0°, 22.5° and 45°) and Case E (wind from SW, before and after construction); OpenLB on Cases A
  and B; FluidX3D on Cases A and B; the Eddy3D ML surrogate on Cases A–E.
- API: `validation.json`; `cases/{id}/pairs/{engine}.csv`; `cases/{id}/approach_flow.csv`; JSON Schemas for every
  document; the geometry index and archive; `llms.txt`; schema.org Dataset metadata. Schema 2.1.0 lists the files
  of templated endpoints; schema 2.2.0 adds the release (`versions.release`, `release`).
- Versioning: `VERSION`, this changelog, the version in `CITATION.cff`, release tags and archives, one pinned
  build environment (`requirements.lock` with hashes, Python 3.12.12, a container image pinned by digest), and the
  CI check that the version moves with the change.

### Fixed

- Withdrawn: the reading that the Case C model's approach flow ran at 0.83 of the tunnel's and Case E's at 0.41/0.79
  near the ground. Upstream of the arrays the probe height sits below the first cell's centre, where the sampling
  falls linearly to zero; at the measurement points the sampling is sound.
- Case D: the 22.5° and 45° rotation sense, read from Figure 4 of the data paper, is corroborated by solved fields
  (`directions.csv` status, `QUESTIONS.md` Q2).
- `clean/manifest.json`: the fitted roughness lengths `z0_m` are written to 12 significant digits, so the file is
  byte-identical on every platform.

### Removed

- The PDF of the AIJ guidelines paper (Tominaga et al. 2008, Elsevier, all rights reserved); `papers/README.md`
  cites it by DOI.

## [1.0.0] - 2026-10-14

The first release of the cleaned tables (`clean/`) and the API. It was never tagged, and the served content
changed under this number afterwards; that is why tagged releases begin at 2.0.0.
