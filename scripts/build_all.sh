#!/usr/bin/env bash
# Rebuild every generated file in this repository, in dependency order, in the pinned environment:
#
#   docker run --rm -v "$PWD:/w" -w /w "$(cat scripts/BUILD_IMAGE)" bash scripts/build_all.sh
#
# The image is Python 3.12.12 pinned by digest (scripts/BUILD_IMAGE); requirements.lock pins every package by hash.
# Run from a checkout of any release tag, the outputs are byte-identical to what that tag committed; CI runs exactly
# this and fails on any difference. Outputs: clean/ (the cleaned tables), validation/figures/ (the figures and
# geometry renders, drawn from the snapshots in validation/results/), and docs/ (the API, the generated pages, and a 1600 px web copy of every figure under docs/assets/web/).
# Then the citations are tested and checked against each other (scripts/citation.py is their one source), and the last step
# checks that every Markdown file, generated or not, renders the same on GitHub and in Jekyll.
set -euo pipefail
# One thread for the numerical libraries: with several, a figure's layout solve (the Case D agreement figure) came out as one of
# two layouts, a pixel apart, from run to run on the same machine, and a build that is a pure function must not.
export PYTHONHASHSEED=0 PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 MPLBACKEND=Agg OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1

pip install --quiet --disable-pip-version-check --root-user-action=ignore --no-deps --require-hashes -r requirements.lock

python clean/build.py
(cd validation && python render_geometry.py && for f in plot_*.py; do python "$f"; done)
(cd validation && python plotstyle.py)   # the palette checks, and every PNG under validation/figures at 1200 dpi
python scripts/build_api.py
python scripts/check_geometry.py   # every served and cleaned STL, parsed again from the files: closed, consistently wound, outward bodies
python scripts/test_geometry.py
python scripts/test_citation.py
python scripts/check_citation.py --self-test
python scripts/check_citation.py
python scripts/check_markdown.py --self-test
python scripts/check_markdown.py
