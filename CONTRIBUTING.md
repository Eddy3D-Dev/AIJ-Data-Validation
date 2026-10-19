# Contributing

Three kinds of contribution, three routes. Questions go to [Discussions](https://github.com/Eddy3D-Dev/AIJ-Data-Validation/discussions);
a wrong value, a broken file or a feature goes to an [issue](https://github.com/Eddy3D-Dev/AIJ-Data-Validation/issues/new/choose).

## 1. Submit your solver's results

Score your solver as [Validate your own solver](https://eddy3d-dev.github.io/AIJ-Data-Validation/byos/) describes,
put the folder under `submissions/<your-slug>/` (`submission.yaml` and `cases/<id>/probes.csv`), run
`python validation/score_submissions.py submissions/<your-slug>` from your checkout, and open a pull request that adds the folder and nothing else. CI rebuilds
the repository, scores the folder in the pinned image, and the build writes `validation/results/submissions/<slug>/<id>.json`
and serves `/api/submissions/<slug>.json`: the pull request must include those generated files, so run the build once
(section 4) and commit what it writes. A submission is self-reported; the maintainers check the scoring, not the solve.
The inlet is a recommendation, recorded per submission, not a requirement. Partial submissions (some cases, some
quantities, one configuration) are fine: their coverage is shown.

## 2. Fix the data

The cleaned tables are generated: never edit `clean/` or `docs/api/` by hand. A correction is a change to the
cleaning code (`clean/*.py`, `scripts/aijdata.py`, `scripts/aij_case_*.py`) with the published file as its evidence, a
line in the case's `known_issues` where it is a correction of the published data, and the rebuilt outputs committed.
Open a [data issue](https://github.com/Eddy3D-Dev/AIJ-Data-Validation/issues/new?template=data-issue.yml) first if the
fix is not obvious.

## 3. Change the build, the API or the site

The build is a pure function of the repository: `scripts/build_all.sh` in the pinned image regenerates every generated
file, and CI fails on a single byte of difference. The rules:

- **Build only in the pinned image.** `podman run --rm -v "$PWD:/w" -w /w "$(cat scripts/BUILD_IMAGE)" bash scripts/build_all.sh`
  (or `docker`). The host's Python, NumPy or matplotlib give different bytes.
- **A served byte moves the version.** Anything under `docs/api/` or `clean/` that changes needs `VERSION` bumped
  (MINOR for an addition, PATCH for a corrected value, MAJOR for a removed or renamed file or field) and a section in
  `CHANGELOG.md`; `python scripts/release.py check` enforces it, and CI runs it. Documentation, figures and tooling that
  change no served byte need no release.
- **Frozen releases stay frozen.** `docs/api/<release>/` of an earlier release is never regenerated or edited.
- **Renders differ by platform.** On an arm64 Mac the geometry renders of Cases F, L and M differ from CI's amd64 bytes:
  do not commit regenerated renders; if CI reports a difference, take its `rebuilt-files` artifact.
- **Markdown renders on GitHub and on the site.** `scripts/check_markdown.py` (run by the build) enforces the rules; math
  is LaTeX between `$$ ... $$`.
- **Dependencies are pinned twice.** A new package goes into `requirements.txt` and the lock is regenerated:
  `uv pip compile requirements.txt --universal --generate-hashes --python-version 3.12 -o requirements.lock`.
- **No PDFs in the repository.**
- **`validation/score_submissions.py`** is the one scorer: the build scores the submissions with it, and its `--self-test` (the build
  runs it) re-scores every served run from its pairs and must match to 1e-9.

## 4. Running the build

```bash
podman run --rm -v "$PWD:/w" -w /w "$(cat scripts/BUILD_IMAGE)" bash scripts/build_all.sh
python scripts/release.py check
```

The first command takes a few minutes and rewrites `clean/`, `validation/figures/` and `docs/`; `git status` then shows
exactly what your change changes. The pull request template lists what to check before opening it.

## Licence

Code contributions are MIT (`LICENSE`); the data are CC BY 4.0 (`LICENSE-DATA`). A submission's values are published
under CC BY 4.0 with the submission's own `licence` field as their attribution.
