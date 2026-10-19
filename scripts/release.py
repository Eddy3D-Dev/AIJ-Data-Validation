"""The release version: one semantic version for everything this repository publishes.

VERSION holds it, once. clean/build.py writes it into the cleaned release (manifest.json, Parquet metadata),
scripts/build_api.py into the API (index.json `versions.release` and `release`), and CITATION.cff and
CHANGELOG.md must agree with it. A release is the commit CI tags vX.Y.Z when VERSION changes on main.

What moves which number (the Data Package versioning recipe, https://datapackage.org/recipes/data-package-version/,
applied to the files and the API this repository serves):

  MAJOR  an incompatible change: a served file, endpoint, field or column renamed or removed; a CSV column added,
         removed or reordered; a unit, frame or normalisation changed; a major change of the API schema.
  MINOR  a backward-compatible addition: a new case, configuration, run, endpoint, field or file.
  PATCH  a backward-compatible fix: a corrected value, score, caption or metadata text.

Documentation, figures and tooling that do not change a served byte need no release.

    python scripts/release.py check          # CI: VERSION, CHANGELOG.md, CITATION.cff and the built outputs agree,
                                             #     the version moves with the change since the last tag, the
                                             #     frozen docs/api/<release>/ of every earlier release still equals its tag,
                                             #     and no text file of raw/ holds CRLF in the git index
    python scripts/release.py notes          # the CHANGELOG.md section of VERSION (the release notes)
    python scripts/release.py archive DIR    # DIR/aij-uwe-vX.Y.Z.tar.gz and its SHA256SUMS, byte-reproducible
                                             #     (fixed order, owner and mtime = SOURCE_DATE_EPOCH or 0)

Standard library only, so the check runs anywhere git does.
"""
from __future__ import annotations

import gzip
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import tarfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
HEADING = re.compile(r"^## \[(?P<v>[^\]]+)\](?: - (?P<d>\d{4}-\d{2}-\d{2}))?\s*$")
LEVELS = ("patch", "minor", "major")

# What a release publishes: the API and the cleaned tables. The hand-written notes, the build script, its log and
# its inputs are not served data; a change there alone needs no release.
SURFACE = ["docs/api", "clean"]
NOT_SURFACE = ["clean/build.py", "clean/build.log", "clean/README.md", "clean/SCHEMA.md", "clean/QUESTIONS.md",
               "clean/sources"]

# docs/api/<release>/ is the frozen copy of one release: the same files as the unversioned docs/api/ at that release,
# addressed by the release number. A new release adds a whole one; that is a copy, not new served content.
RELEASE_TREE = re.compile(r"^docs/api/(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)/")

# The release archive: the served data with what is needed to cite and read it. It carries the unversioned docs/api/,
# which at the release equals the frozen copy; the frozen copies stay out so that an archive does not repeat them.
ARCHIVE_FILES = ["VERSION", "CHANGELOG.md", "CITATION.cff", "README.md"]
ARCHIVE_TREES = ["clean", "docs/api"]
ARCHIVE_SKIP = ["clean/build.py", "clean/sources"]


def parse(v):
    m = SEMVER.match(v or "")
    if not m:
        raise ValueError(f"not a MAJOR.MINOR.PATCH version: {v!r}")
    return tuple(int(x) for x in m.groups())


def version():
    with io.open(os.path.join(REPO, "VERSION"), encoding="utf-8") as f:
        v = f.read().strip()
    parse(v)
    return v


def changelog():
    """[(version, date or None, body)] in file order; '## [Unreleased]' comes back with version 'Unreleased'."""
    out, cur = [], None
    with io.open(os.path.join(REPO, "CHANGELOG.md"), encoding="utf-8") as f:
        for line in f.read().replace("\r\n", "\n").split("\n"):
            m = HEADING.match(line)
            if m:
                cur = [m["v"], m["d"], []]
                out.append(cur)
            elif cur is not None:
                cur[2].append(line)
    return [(v, d, "\n".join(b).strip("\n")) for v, d, b in out]


def release_date(v=None):
    v = v or version()
    for ver, d, _ in changelog():
        if ver == v:
            return d
    return None


def bump(v, level):
    a, b, c = parse(v)
    return {"major": f"{a + 1}.0.0", "minor": f"{a}.{b + 1}.0", "patch": f"{a}.{b}.{c + 1}"}[level]


def level_of(old, new):
    for level in ("major", "minor", "patch"):
        if bump(old, level) == new:
            return level
    return None


def git(*args):
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True, encoding="utf-8")


def latest_tag():
    tags = [t.strip() for t in git("tag", "--list", "v*").stdout.split()]
    versions = sorted((parse(t[1:]), t) for t in tags if SEMVER.match(t[1:]))
    return versions[-1][1] if versions else None


def surface_changes(tag):
    """[(status, path)] of the served files between the tag and the working tree (renames as delete + add)."""
    return surface_diff(tag, SURFACE + [f":(exclude){p}" for p in NOT_SURFACE])


def required_level(tag, changes):
    """The smallest bump that describes the changes, with the reason."""
    need, why = "patch", "served content changed"
    for status, path in changes:
        if status.startswith("D") and RELEASE_TREE.match(path):
            continue        # the copies of 2.0.0 to 3.2.0 were withdrawn at 3.2.1, before anyone used them; the alias still serves every file
        if status.startswith("D"):
            return "major", f"{path} was removed or renamed"
        if status.startswith("A") and LEVELS.index(need) < 1 and not RELEASE_TREE.match(path):
            need, why = "minor", f"{path} was added"
        if status.startswith("M") and path.endswith(".csv"):
            old = git("show", f"{tag}:{path}").stdout.split("\n", 1)[0].strip()
            with io.open(os.path.join(REPO, path), encoding="utf-8") as f:
                new = f.readline().strip()
            if old != new:
                return "major", f"the columns of {path} changed ({old!r} -> {new!r})"
    old_index, new_index = git("show", f"{tag}:docs/api/index.json").stdout, None
    with io.open(os.path.join(REPO, "docs", "api", "index.json"), encoding="utf-8") as f:
        new_index = f.read()
    if old_index:
        o = parse(json.loads(old_index)["versions"]["schema"])
        n = parse(json.loads(new_index)["versions"]["schema"])
        if n[0] > o[0]:
            return "major", f"the API schema went from {'.'.join(map(str, o))} to {'.'.join(map(str, n))}"
        if n[1] > o[1] and LEVELS.index(need) < 1:
            need, why = "minor", f"the API schema added to its contract ({'.'.join(map(str, o))} -> {'.'.join(map(str, n))})"
    return need, why


def frozen_trees():
    """The versions that have a frozen copy of the API under docs/api/."""
    api = os.path.join(REPO, "docs", "api")
    return sorted((n for n in os.listdir(api) if SEMVER.match(n) and os.path.isdir(os.path.join(api, n))), key=parse)


def check_frozen_trees(v, errors):
    """docs/api/<release>/ exists for VERSION, and every other one is an untouched copy of a tagged release."""
    trees = frozen_trees()
    if v not in trees:
        errors.append(f"docs/api/{v}/ (the frozen copy of the API for {v}) is missing; run scripts/build_api.py")
    for t in trees:
        index_path = os.path.join(REPO, "docs", "api", t, "index.json")
        if not os.path.isfile(index_path):
            errors.append(f"docs/api/{t}/index.json is missing")
            continue
        with io.open(index_path, encoding="utf-8") as f:
            held = json.load(f)["versions"]["release"]
        if held != t:
            errors.append(f"docs/api/{t}/ holds release {held}")
        if t == v:
            continue
        if parse(t) > parse(v):
            errors.append(f"docs/api/{t}/ is newer than VERSION {v}")
        elif not git("rev-parse", "-q", "--verify", f"refs/tags/v{t}").stdout.strip():
            errors.append(f"docs/api/{t}/ is the frozen copy of {t}, which is not tagged v{t}; only VERSION's own copy may exist before its release")
        else:
            moved = surface_diff(f"v{t}", [f"docs/api/{t}"])
            if moved:
                errors.append(f"docs/api/{t}/ is frozen at v{t} but differs from the tag ({len(moved)} file(s), e.g. {moved[0][1]})")


def surface_diff(tag, paths):
    r = git("diff", "--name-status", "--no-renames", tag, "--", *paths)
    if r.returncode:
        raise SystemExit(f"git diff against {tag} failed: {r.stderr.strip()}")
    return [tuple(line.split("\t", 1)) for line in r.stdout.splitlines() if line.strip()]


def check_line_endings(errors):
    """Every text file of raw/ is LF in the index (clean/manifest.json hashes the LF form, so a CRLF blob would make a
    fresh clone and a Windows checkout disagree about it). The `-text` mirrors under clean/sources are byte-exact on purpose."""
    r = git("ls-files", "--eol", "raw", "clean/sources")
    if r.returncode:
        raise SystemExit(f"git ls-files --eol failed: {r.stderr.strip()}")
    bad = []
    for line in r.stdout.splitlines():
        info, _, path = line.partition("\t")
        if re.search(r"\bi/(crlf|mixed)\b", info) and "attr/-text" not in info:
            bad.append(path)
    if bad:
        errors.append(f"{len(bad)} text file(s) of raw/ or clean/sources/ hold CRLF in the index ({', '.join(bad[:4])}"
                      f"{' ...' if len(bad) > 4 else ''}): commit them as LF (git add --renormalize)")


def check():
    errors = []
    v = version()
    check_line_endings(errors)
    entries = changelog()
    released = [(ver, d) for ver, d, _ in entries if ver != "Unreleased"]
    if not released or released[0][0] != v:
        errors.append(f"CHANGELOG.md: the newest released section is {released[0][0] if released else 'missing'}, VERSION is {v}")
    elif not released[0][1]:
        errors.append(f"CHANGELOG.md: [{v}] has no date ('## [{v}] - YYYY-MM-DD')")
    for (a, _), (b, _) in zip(released, released[1:]):
        if not (SEMVER.match(a) and SEMVER.match(b)) or parse(a) <= parse(b):
            errors.append(f"CHANGELOG.md: sections must run newest first with valid versions ({a} above {b})")
    date = release_date(v)

    with io.open(os.path.join(REPO, "CITATION.cff"), encoding="utf-8") as f:
        cff = f.read()
    cv = re.search(r"^version:\s*['\"]?([^'\"\s]+)", cff, re.M)
    cd = re.search(r"^date-released:\s*['\"]?(\d{4}-\d{2}-\d{2})", cff, re.M)
    if not cv or cv.group(1) != v:
        errors.append(f"CITATION.cff: version is {cv.group(1) if cv else 'missing'}, VERSION is {v}")
    if not cd or cd.group(1) != date:
        errors.append(f"CITATION.cff: date-released is {cd.group(1) if cd else 'missing'}, CHANGELOG.md dates {v} {date}")

    with io.open(os.path.join(REPO, "docs", "api", "index.json"), encoding="utf-8") as f:
        index = json.load(f)
    if index.get("versions", {}).get("release") != v or index.get("release", {}).get("date") != date:
        errors.append(f"docs/api/index.json: release {index.get('versions', {}).get('release')} "
                      f"({index.get('release', {}).get('date')}), expected {v} ({date}); run scripts/build_api.py")
    with io.open(os.path.join(REPO, "clean", "manifest.json"), encoding="utf-8") as f:
        if json.load(f).get("version") != v:
            errors.append(f"clean/manifest.json: version is not {v}; run clean/build.py")
    check_frozen_trees(v, errors)

    tag = latest_tag()
    if tag is None:
        print(f"no release is tagged yet: v{v} will be the first")
    else:
        t = tag[1:]
        changes = surface_changes(tag)
        if parse(v) < parse(t):
            errors.append(f"VERSION {v} is older than the latest release {tag}")
        elif v == t:
            if changes:
                need, why = required_level(tag, changes)
                shown = ", ".join(p for _, p in changes[:6]) + (" ..." if len(changes) > 6 else "")
                errors.append(f"served content changed since {tag} ({why}; {len(changes)} file(s): {shown}) but VERSION is "
                              f"still {v}. Set VERSION to {bump(v, need)} (a {need} release) or higher, and add its section "
                              f"to CHANGELOG.md and CITATION.cff.")
            else:
                print(f"{tag} is the current release and nothing it serves has changed")
        else:
            level = level_of(t, v)
            if level is None:
                errors.append(f"VERSION {v} does not follow {tag}: the next version is {bump(t, 'patch')}, "
                              f"{bump(t, 'minor')} or {bump(t, 'major')}")
            else:
                need, why = required_level(tag, changes) if changes else ("patch", "no served file changed")
                if LEVELS.index(level) < LEVELS.index(need):
                    errors.append(f"VERSION {v} is a {level} release after {tag}, but {why}: that needs a {need} "
                                  f"release ({bump(t, need)})")
                else:
                    print(f"v{v} is a {level} release after {tag} ({len(changes)} served file(s) changed; {why})")
    if errors:
        for e in errors:
            print(f"::error::{e}")
        raise SystemExit(1)
    print(f"release {v} ({date}): VERSION, CHANGELOG.md, CITATION.cff, clean/manifest.json and docs/api/index.json agree")


def notes():
    v = version()
    for ver, d, body in changelog():
        if ver == v:
            print(body)
            return
    raise SystemExit(f"CHANGELOG.md has no section for {v}")


def _members():
    paths = [p for p in ARCHIVE_FILES]
    for tree in ARCHIVE_TREES:
        for root, dirs, files in os.walk(os.path.join(REPO, tree)):
            dirs.sort()
            for name in files:
                rel = os.path.relpath(os.path.join(root, name), REPO).replace(os.sep, "/")
                if not any(rel == s or rel.startswith(s + "/") for s in ARCHIVE_SKIP) and not RELEASE_TREE.match(rel):
                    paths.append(rel)
    return sorted(paths)


def archive(outdir):
    """A tar.gz whose bytes depend only on the files: sorted members, root:root, 0644, one mtime, gzip mtime 0.
    Built in the pinned image (same zlib), it is byte-identical on every rebuild of the same commit."""
    v = version()
    mtime = int(os.environ.get("SOURCE_DATE_EPOCH", "0"))
    prefix = f"aij-uwe-v{v}"
    os.makedirs(outdir, exist_ok=True)
    tar_path = os.path.join(outdir, f"{prefix}.tar.gz")
    sums = []
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w", format=tarfile.PAX_FORMAT) as tar:
        for rel in _members():
            with open(os.path.join(REPO, rel), "rb") as f:
                data = f.read()
            info = tarfile.TarInfo(f"{prefix}/{rel}")
            info.size, info.mtime, info.mode = len(data), mtime, 0o644
            info.uid = info.gid = 0
            info.uname = info.gname = "root"
            tar.addfile(info, io.BytesIO(data))
            sums.append((hashlib.sha256(data).hexdigest(), f"{prefix}/{rel}"))
    with open(tar_path, "wb") as raw, gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0, compresslevel=9) as gz:
        gz.write(buf.getvalue())
    with open(tar_path, "rb") as f:
        tar_sha = hashlib.sha256(f.read()).hexdigest()
    with io.open(os.path.join(outdir, f"{prefix}.SHA256SUMS"), "w", encoding="utf-8", newline="\n") as f:
        f.write(f"{tar_sha}  {prefix}.tar.gz\n")
        for h, p in sums:
            f.write(f"{h}  {p}\n")
    print(f"{tar_path}: {len(sums)} files, sha256 {tar_sha}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "check":
        check()
    elif cmd == "notes":
        notes()
    elif cmd == "archive" and len(sys.argv) == 3:
        archive(sys.argv[2])
    elif cmd == "version":
        print(version())
    else:
        raise SystemExit(__doc__)
