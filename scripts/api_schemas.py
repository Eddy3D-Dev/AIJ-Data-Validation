"""JSON Schemas (draft 2020-12) of every JSON document the static API serves.

build_api.py publishes each one at <api>/schemas/<name>.schema.json, names it in every document's
`$schema`, embeds it in openapi.json, and validates every document it writes against it. The schemas
pin what a client may rely on: required keys and their types. They allow additional properties on
purpose: within a major version the API only adds, and a client must ignore what it does not know.
"""
from __future__ import annotations

DRAFT = "https://json-schema.org/draft/2020-12/schema"

SHA256 = {"type": "string", "pattern": "^[0-9a-f]{64}$"}
SEMVER = {"type": "string", "pattern": r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$"}
URL = {"type": "string", "format": "uri"}
NUM_OR_NULL = {"type": ["number", "null"]}
STR_OR_NULL = {"type": ["string", "null"]}


def obj(required, properties, **extra):
    return {"type": "object", "required": list(required), "properties": properties, **extra}


def arr(items, **extra):
    return {"type": "array", "items": items, **extra}


# Every document opens with these four keys.
HEADER = {
    "$schema": URL,
    "schema_version": {"type": "string", "pattern": r"^\d+\.\d+\.\d+$",
                       "description": "the API's version (semantic versioning); see index.json changelog"},
    "data_version": dict(SHA256, description=("SHA-256 over every served measurement, geometry and score file; "
                                              "changes when, and only when, the data does")),
    "license": {"const": "CC-BY-4.0", "description": "SPDX identifier of the data's licence"},
}

# A file to download: where it is, what it is, and how to check it arrived intact.
DOWNLOAD = obj(["url", "path", "media_type", "bytes", "sha256"], {
    "url": dict(URL, description="absolute URL; the ?v= query is the file's SHA-256 prefix, so a changed file has a new URL"),
    "path": {"type": "string", "description": "path below the API base"},
    "media_type": {"type": "string"},
    "bytes": {"type": "integer", "minimum": 0},
    "sha256": SHA256,
})

METRIC = obj(["Count", "Fb", "R"], {
    "Count": {"type": "integer", "minimum": 0},
    "MeanObserved": NUM_OR_NULL, "MeanPredicted": NUM_OR_NULL,
    "Fb": NUM_OR_NULL, "Nmse": NUM_OR_NULL, "Nad": NUM_OR_NULL, "Fac2": NUM_OR_NULL, "HitRate": NUM_OR_NULL,
    "Mg": NUM_OR_NULL, "Vg": NUM_OR_NULL, "GeometricPairs": {"type": ["integer", "null"]}, "R": NUM_OR_NULL,
})

ENGINE_ID = {"enum": ["openfoam12-realizableKE", "openfoam12-kEpsilon", "openfoam12-kOmegaSST", "umf-realizableKE", "umf-buoyantKEpsilon", "openlb", "fluidx3d", "ml-surrogate"]}
STATUS = {"enum": ["scored", "running", "pending", "not comparable"]}
CASE_ID = {"enum": ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M"]}

POINT = obj(["point_id", "x", "y", "z"], {
    "point_id": {"type": "integer"}, "config": {"type": "string"}, "instrument": {"type": "string"},
    "wind_direction": {"type": "string"}, "wind_direction_deg": {"type": "number"},
    "x": {"type": "number"}, "y": {"type": "number"}, "z": {"type": "number"},
    "campaign": {"type": "string"}, "run": {"type": "string"},
    **{q: NUM_OR_NULL for q in ("U", "V", "W", "uu", "vv", "ww", "k", "Vs", "velocity_ratio",
                                "uv", "uw", "vw", "C", "c_rms", "concentration_ratio", "T", "T_rms",
                                "uc", "vc", "wc", "uT", "vT", "wT", "velocity_ratio_sd", "k_ratio")},
})

# What a geometry file says about itself (geometry.json `stats`, and the geometry index). A BODY is a set of triangles joined through
# edges that exactly two triangles use.
GEOMETRY_FACTS = {
    "watertight": {"type": "boolean", "description": ("true when every body is closed (no boundary edge), consistently wound (every edge is traversed once in "
                                                      "each direction) and has a positive volume (outward normals)")},
    "bodies": {"type": "integer", "minimum": 0, "description": "number of bodies (buildings, or the terrain with its buildings)"},
    "edges_boundary": {"type": "integer", "minimum": 0, "description": "edges used by one triangle: 0 when every body is closed"},
    "body_contacts": {"type": "integer", "minimum": 0, "description": ("edges that four triangles share where two separate bodies touch; "
                                                                      "each body still sees the edge as an ordinary two-triangle edge, so a contact does not open a body")},
    "inconsistent_triangles": {"type": "integer", "minimum": 0, "description": "fewest triangles to reverse to wind every body consistently: 0 in every served file"},
    "min_body_volume": {"type": "number", "description": "volume of the smallest body (m^3 in the file's units cubed); positive when every body is outward"},
}

FRAME = obj(["origin", "x", "y", "z"], {k: {"type": "string"} for k in ("origin", "x", "y", "z")})


def _doc(name, title, description, required, properties):
    return {
        "title": title, "description": description,
        **obj(["$schema", "schema_version", "data_version", "license", *required], {**HEADER, **properties}),
    }


DOCUMENTS = {
    "index": _doc("index", "API index", "Every endpoint and file, versions, compatibility policy, changelog, licence and citation.",
                  ["name", "base_url", "tree", "release_base_url", "versions_url", "versions", "endpoints", "case_ids",
                   "files", "changelog", "cite"], {
        "name": {"type": "string"}, "description": {"type": "string"},
        "base_url": dict(URL, description="the root of this tree: every URL in the tree's documents starts with it"),
        "tree": {"enum": ["release", "latest"],
                 "description": ("'release': a frozen copy of one release under `/api/<release>/`, which never changes; "
                                 "'latest': the unversioned `/api/` alias, which always equals the newest release")},
        "release_base_url": dict(URL, description=("the frozen copy of `versions.release`: equal to base_url in a release "
                                                   "tree, the pinned address of this release in the latest alias")),
        "versions_url": dict(URL, description="versions.json, the list of every release (always at the unversioned /api/ path)"),
        "fallback_base_url": URL, "fallback_note": {"type": "string"}, "repository": URL, "site": URL,
        "versions": obj(["release", "schema", "data"], {"release": SEMVER, "schema": SEMVER, "data": SHA256,
                                                     "clean_manifest": STR_OR_NULL}),
        "release": obj(["version", "date", "tag", "url", "base_url", "changelog"], {
            "version": SEMVER, "date": {"type": "string", "format": "date"}, "tag": {"type": "string", "pattern": r"^v\d+\.\d+\.\d+$"},
            "url": URL, "base_url": dict(URL, description="the raw files of this release's frozen copy, at the release tag"),
            "changelog": URL}),
        "compatibility": {"type": "string"}, "caching": {"type": "string"},
        "changelog": arr(obj(["version", "date", "changes"], {
            "version": {"type": "string"}, "date": {"type": "string", "format": "date"}, "changes": arr({"type": "string"})})),
        # A single-file endpoint has a `url`; a templated one (cases/{id}.json) has none, because a URI
        # template is not something to fetch, and lists every concrete file under `urls` instead.
        "endpoints": arr({**obj(["path", "method", "media_type", "description", "templated"], {
            "path": {"type": "string"}, "templated": {"type": "boolean"},
            "url": dict(URL, pattern=r"^[^{}]*$"), "urls": arr(dict(URL, pattern=r"^[^{}]*$"), minItems=1),
            "method": {"const": "GET"}, "media_type": {"type": "string"}, "description": {"type": "string"},
            "schema": {"type": ["string", "null"]}}),
            "if": {"properties": {"templated": {"const": True}}},
            "then": {"required": ["urls"], "not": {"required": ["url"]}},
            "else": {"required": ["url"], "not": {"required": ["urls"]}}}),
        "case_ids": arr(CASE_ID),
        "files": arr(DOWNLOAD),
        "license_detail": obj(["spdx", "url"], {"spdx": {"type": "string"}, "name": {"type": "string"}, "url": URL, "note": {"type": "string"}}),
        "cite": obj(["api", "benchmark"], {
            "benchmark": {"type": "string"}, "guidelines": {"type": "string"}, "per_case": {"type": "string"},
            "api": obj(["title", "version", "url", "release_url", "doi", "apa", "bibtex", "csl_json"], {
                "title": {"type": "string"}, "version": SEMVER,
                "url": dict(URL, description="the pinned address of this release's API: the address to cite"),
                "release_url": dict(URL, description="the release's page in the repository"),
                "doi": dict(STR_OR_NULL, description="the DOI of the release's Zenodo record; null until one exists"),
                "apa": {"type": "string"}, "bibtex": {"type": "string"},
                "csl_json": dict({"type": "object"}, description="the same citation as a CSL-JSON item")})}),
    }),
    "versions": _doc("versions", "Release list", "Every release of the data and API, newest first, with the address of its files.",
                     ["latest", "latest_base_url", "versions"], {
        "description": {"type": "string"},
        "latest": dict(SEMVER, description="the newest release; the unversioned /api/ paths equal it"),
        "latest_base_url": dict(URL, description="the unversioned alias of the newest release"),
        "versions": arr(obj(["version", "date", "status", "schema_version", "data_version", "base_url", "index_url",
                             "self_contained", "tag", "tag_url", "changelog_url"], {
            "version": SEMVER, "date": {"type": "string", "format": "date"},
            "status": {"enum": ["latest", "superseded"]},
            "schema_version": {"type": "string", "pattern": r"^\d+\.\d+\.\d+$"}, "data_version": SHA256,
            "base_url": dict(URL, description="where this release's files are frozen: GET base_url + a path from its index.json"),
            "index_url": dict(URL, description="the index.json of this release"),
            "fallback_base_url": {"type": ["string", "null"], "format": "uri"},
            "self_contained": {"type": "boolean",
                               "description": ("true if every URL to a file of the API inside this release's documents points back into "
                                               "base_url (versions.json, served only at the unversioned path, aside)")},
            "note": {"type": "string"},
            "tag": {"type": "string", "pattern": r"^v\d+\.\d+\.\d+$"}, "tag_url": URL, "changelog_url": URL}), minItems=1),
    }),
    "cases": _doc("cases", "Case list", "Every case with its frame, units, counts, engine status and links.", ["cases"], {
        "cases": arr(obj(["id", "slug", "title", "frame", "units", "counts", "engines", "links"], {
            "id": CASE_ID, "slug": {"type": "string"}, "title": {"type": "string"}, "summary": {"type": "string"},
            "frame": FRAME, "units": {"type": "object"},
            "counts": obj(["rows", "distinct_points"], {"rows": {"type": "integer"}, "distinct_points": {"type": "integer"}}),
            "engines": {"type": "object", "additionalProperties": STATUS},
            "doi": STR_OR_NULL,
            "links": obj(["case", "points", "points_csv", "geometry", "geometry_stl", "validation"],
                         {k: URL for k in ("case", "points", "points_csv", "geometry", "geometry_stl", "validation", "page", "render")}),
        }), minItems=len(CASE_ID["enum"]), maxItems=len(CASE_ID["enum"])),
    }),
    "case": _doc("case", "Case", "One case in full: configuration, frame, units, inflow, point-table summary, geometry, validation status, "
                 "known data issues and attribution.",
                 ["id", "title", "frame", "units", "approach_flow", "points", "geometry", "validation", "known_issues", "people",
                  "citation"], {
        "id": CASE_ID, "slug": {"type": "string"}, "title": {"type": "string"}, "summary": {"type": "string"},
        "configuration": {"type": "object"}, "configurations": arr({"type": "object"}),
        "quantities": arr({"type": "string"}), "units": {"type": "object"}, "frame": FRAME, "inflow_fit": {"type": "object"},
        "approach_flow": obj(["source", "units", "rows", "csv"], {
            "source": {"type": "string"}, "units": {"type": "object"},
            "rows": arr(obj(["z", "U"], {"z": {"type": "number"}, "U": {"type": "number"}, "k": NUM_OR_NULL, "u_rms": NUM_OR_NULL})),
            "csv": DOWNLOAD}),
        "points": obj(["url", "csv", "rows", "distinct_points", "columns"], {
            "url": URL, "csv": DOWNLOAD, "rows": {"type": "integer"}, "distinct_points": {"type": "integer"},
            "columns": arr({"type": "string"})}),
        "geometry": obj(["url", "files"], {"url": URL, "files": arr(obj(["configuration", "url", "triangles", "watertight"], {
            "configuration": {"type": "string"}, "url": URL, "triangles": {"type": "integer"}, "watertight": {"type": "boolean"}}))}),
        "validation": obj(["url", "status", "engines"], {"url": URL, "status": {"enum": ["scored", "pending"]},
                                                         "engines": {"type": "object", "additionalProperties": STATUS}}),
        "known_issues": arr({"type": "string"}, minItems=1),
        "people": obj(["data_collectors", "editors_distributors"], {"data_collectors": arr({"type": "string"}),
                                                                    "editors_distributors": arr({"type": "string"})}),
        "doi": STR_OR_NULL, "citation_requested": {"type": "string"}, "render": URL, "page": URL,
        "citation": obj(["apa", "bibtex"], {"apa": {"type": "string"}, "bibtex": {"type": "string"}}),
    }),
    "points": _doc("points", "Point table", "The cleaned measurement table of one case: SI units, one frame, null where not measured.",
                   ["case", "columns", "column_meaning", "n", "points", "units", "frame"], {
        "case": CASE_ID, "title": {"type": "string"}, "points_source": {"type": "string"},
        "units": {"type": "object"}, "frame": FRAME, "columns": arr({"type": "string"}),
        "column_meaning": {"type": "object", "additionalProperties": {"type": "string"}},
        "n": {"type": "integer"}, "points": arr(POINT), "csv": DOWNLOAD,
    }),
    "geometry": _doc("geometry", "Case geometry", "The STL files of one case, their statistics and, where the geometry is boxes, the boxes.",
                     ["case", "units", "frame", "default_configuration", "configurations", "files"], {
        "case": CASE_ID, "title": {"type": "string"}, "units": {"type": "string"}, "frame": FRAME,
        "default_configuration": {"type": "string"}, "configurations": arr({"type": "string"}), "is_boxes": {"type": "boolean"},
        "files": arr({"allOf": [DOWNLOAD, obj(["configuration", "stats", "render"], {
            "configuration": {"type": "string"}, "format": {"type": "string"}, "source": {"type": "string"},
            "stats": obj(["triangles", "bbox_min", "bbox_max", "watertight"], {
                "triangles": {"type": "integer"}, "bbox_min": arr({"type": "number"}, minItems=3, maxItems=3),
                "bbox_max": arr({"type": "number"}, minItems=3, maxItems=3), **GEOMETRY_FACTS}),
            "render": URL, "render_caption": {"type": "string"},
            "boxes": arr(obj(["min", "max"], {"min": arr({"type": "number"}, minItems=3, maxItems=3),
                                              "max": arr({"type": "number"}, minItems=3, maxItems=3)})),
        })]}, minItems=1),
        "render": URL,
    }),
    "validation": _doc("validation", "Case validation", "Eddy3D's scores against one case, per engine and run. An engine that is not "
                       "'scored' has no result here.",
                       ["case", "status", "engines", "results"], {
        "case": CASE_ID, "title": {"type": "string"}, "status": {"enum": ["scored", "pending"]},
        "status_meaning": {"type": "object", "additionalProperties": {"type": "string"}},
        "engines": arr(obj(["engine", "status"], {"engine": ENGINE_ID, "status": STATUS})),
        "results": arr(obj(["run_id", "engine", "configuration", "headline", "scores", "figures", "pairs", "source_url"], {
            "run_id": {"type": "string"}, "engine": ENGINE_ID, "configuration": STR_OR_NULL, "quantity": STR_OR_NULL,
            "normalisation": {"type": "string"}, "notes": arr({"type": "string"}),
            "headline": {"type": "object", "additionalProperties": {"type": "string"}},
            "scores": {"type": "object", "additionalProperties": METRIC},
            "figures": arr(obj(["url", "caption"], {"url": URL, "caption": {"type": "string"}})),
            "pairs": {"anyOf": [DOWNLOAD, {"type": "null"}]}, "pairs_columns": STR_OR_NULL,
            "reproduce": {"type": "string"}, "source_file": {"type": "string"}, "source_url": URL, "cite": {"type": "string"},
        })),
    }),
    "geometry-index": _doc("geometry-index", "All geometry", "Every STL of every case in one list, and the archive that holds them.",
                           ["files", "archive"], {
        "archive": DOWNLOAD,
        "files": arr({"allOf": [DOWNLOAD, obj(["case", "configuration", "archive_name", "units", "frame", "triangles"], {
            "case": CASE_ID, "configuration": {"type": "string"}, "archive_name": {"type": "string"}, "units": {"type": "string"},
            "frame": FRAME, "triangles": {"type": "integer"}, **GEOMETRY_FACTS})]}),
    }),
    "validation-summary": _doc("validation-summary", "Validation summary", "Every case and engine in one table: status, runs and "
                               "their headline scores.", ["engines", "cases"], {
        "engines": arr(obj(["id", "name", "kind"], {"id": ENGINE_ID, "name": {"type": "string"}, "kind": {"type": "string"}})),
        "status_meaning": {"type": "object", "additionalProperties": {"type": "string"}},
        "cases": arr(obj(["case", "url", "engines"], {
            "case": CASE_ID, "title": {"type": "string"}, "url": URL,
            "engines": arr(obj(["engine", "status", "runs"], {
                "engine": ENGINE_ID, "status": STATUS,
                "runs": arr(obj(["run_id", "configuration", "headline"], {
                    "run_id": {"type": "string"}, "configuration": STR_OR_NULL,
                    "headline": arr(obj(["label", "score", "Count", "R", "Fac2", "Fb", "HitRate"], {
                        "label": {"type": "string"}, "score": {"type": "string"}, "Count": {"type": "integer"},
                        "R": NUM_OR_NULL, "Fac2": NUM_OR_NULL, "Fb": NUM_OR_NULL, "HitRate": NUM_OR_NULL}))})),
            })),
        }), minItems=len(CASE_ID["enum"]), maxItems=len(CASE_ID["enum"])),
    }),
}


def published(base):
    """{name: schema} with $schema and $id set for publication at <base>/schemas/<name>.schema.json."""
    return {name: {"$schema": DRAFT, "$id": f"{base}/schemas/{name}.schema.json", **s} for name, s in DOCUMENTS.items()}
