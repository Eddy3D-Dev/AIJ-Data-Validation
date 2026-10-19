## What this changes

<!-- one paragraph: what, and why -->

## Checklist

- [ ] Built in the pinned image (`podman run --rm -v "$PWD:/w" -w /w "$(cat scripts/BUILD_IMAGE)" bash scripts/build_all.sh`) and committed what it wrote
- [ ] `python scripts/release.py check` passes: if a served byte changed, `VERSION` is bumped and `CHANGELOG.md` has the section
- [ ] No frozen `docs/api/<release>/` tree edited; no regenerated geometry render committed from an arm64 machine
- [ ] A new dependency is pinned in `requirements.txt` and `requirements.lock` is regenerated
- [ ] Markdown renders on GitHub and on the site (`scripts/check_markdown.py` passes in the build)
- [ ] A submission: `python validation/score_submissions.py submissions/<slug>` passes and the generated `validation/results/submissions/<slug>/` is committed
- [ ] No PDF added
