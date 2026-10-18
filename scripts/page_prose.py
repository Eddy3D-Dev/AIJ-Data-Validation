"""Split the prose of the generated pages into what a page shows and what it collapses.

A served string (a known issue, a run note, a frame or normalisation text) often holds a fact and the reasoning behind
it in one sentence. The API serves the string whole and unchanged. A page shows the fact and puts the reasoning in a
collapsed section: `Interpretation: <topic>` for a reading of a result, `Data notes: <topic>` for an explanation of what
is odd in a published file.

An entry is registered by the start of the string it applies to and cuts the string at markers:

    add("start of the string", "Topic", (marker, kind[, lead[, optional]]), ...)

`marker` is text that occurs once in the string; the cut falls before it, and the piece up to the next cut has `kind`:
"F" the page shows it, "I" it goes to an Interpretation section, "N" to a Data notes section. The text before the
first marker is "F". `lead`, if given, is removed from the front of the piece ("so ", ", which is "); a tuple
(old, new) replaces it, and the first letter is capitalised. `optional` makes a marker that is absent from this
string a no-op (one entry then serves the same sentence in two cases). Every word of the served string ends up on the
page, in the visible text or in the collapsed section; only the joins between pieces change.

`whole(start, topic)` registers a text that is interpretation from its first word to its last: the page shows nothing of
it. A text that all runs of a page share is printed once, in the section for all runs, and so is its collapsed section.

Entries that match nothing in a build are an error, so a rewritten source string cannot leave a stale entry behind.
A collapsed section must hold a topic, not a fragment: scripts/build_api.py refuses one shorter than MIN_SECTION characters.
Standard library only.
"""
from __future__ import annotations

import re

SUMMARY = {"I": "Interpretation", "N": "Data notes"}
_ENTRIES = {}
USED = set()


def add(start, topic, *cuts):
    if start in _ENTRIES:
        raise ValueError(f"page_prose: two entries for {start!r}")
    for k in _ENTRIES:
        if k.startswith(start) or start.startswith(k):
            raise ValueError(f"page_prose: {start!r} and {k!r} overlap")
    kinds = {c[1] for c in cuts}
    if not kinds <= {"F", "I", "N"} or len(kinds - {"F"}) > 1:
        raise ValueError(f"page_prose: {start!r}: one section kind per entry, got {sorted(kinds)}")
    _ENTRIES[start] = (topic, cuts)


def whole(start, topic):
    """The whole string is interpretation (a note that only reads a result)."""
    if start in _ENTRIES:
        raise ValueError(f"page_prose: two entries for {start!r}")
    for k in _ENTRIES:
        if k.startswith(start) or start.startswith(k):
            raise ValueError(f"page_prose: {start!r} and {k!r} overlap")
    _ENTRIES[start] = (topic, None)


def unused():
    """Entries no string matched in this build."""
    return sorted(set(_ENTRIES) - USED)


def _capital(s):
    m = re.match(r"([A-Za-z]+)(?=[\s,;:-]|$)", s)
    if m and m.group(1)[0].islower() and (len(m.group(1)) > 1 or m.group(1) == "a"):
        return s[0].upper() + s[1:]
    return s


def _unwrap(s):
    """'(text)' -> 'text' when the outer parentheses belong together."""
    if s.startswith("(") and s.endswith(")"):
        depth = 0
        for i, ch in enumerate(s):
            depth += (ch == "(") - (ch == ")")
            if depth == 0 and i < len(s) - 1:
                return s
        return s[1:-1]
    return s


def _lead(piece, lead):
    if lead is None:
        return piece.strip()
    if isinstance(lead, tuple):
        old, new = lead
        if not piece.startswith(old):
            raise ValueError(f"page_prose: piece {piece[:50]!r} does not start with {old!r}")
        return (new + piece[len(old):]).strip()
    if not piece.startswith(lead):
        raise ValueError(f"page_prose: piece {piece[:50]!r} does not start with {lead!r}")
    return _capital(piece[len(lead):].strip().lstrip(";,: "))


def _sentence_end(s):
    s = s.rstrip()
    if s[-1] in ",;:":
        return s[:-1] + "."
    return s if s[-1] in ".!?" else s + "."


def _join(pieces):
    out = ""
    for p in pieces:
        p = p.strip()
        if not p:
            continue
        if not out:
            out = p
        elif p[0] in ".,;:)":
            out = out.rstrip() + p
        else:
            out = _sentence_end(out) + " " + p
    return out


def split(text, cell=False):
    """(shown, collapsed): `shown` is the text a page prints. `collapsed` is None, or (kind, topic, text). A string with
    no entry comes back unchanged. cell=True: no sentence-ending period is added to the shown text."""
    key = next((k for k in _ENTRIES if text.startswith(k)), None)
    if key is None:
        return text, None
    USED.add(key)
    topic, cuts = _ENTRIES[key]
    if cuts is None:
        return "", ("I", topic, _sentence_end(text.strip()))
    cuts = [c for c in cuts if not (len(c) > 3 and c[3] and text.count(c[0]) == 0)]
    at = []
    for c in cuts:
        if text.count(c[0]) != 1:
            raise ValueError(f"page_prose: marker {c[0]!r} occurs {text.count(c[0])} times in {text[:60]!r}")
        at.append(text.index(c[0]))
    if at != sorted(set(at)):
        raise ValueError(f"page_prose: markers out of order in {text[:60]!r}")
    bounds = [0] + at + [len(text)]
    shown, collapsed, kind = [], [], None
    for i in range(len(bounds) - 1):
        piece = text[bounds[i]:bounds[i + 1]]
        k = "F" if i == 0 else cuts[i - 1][1]
        lead = None if i == 0 or len(cuts[i - 1]) < 3 else cuts[i - 1][2]
        piece = _lead(piece, lead)
        if k == "F":
            shown.append(piece)
        else:
            kind = k
            collapsed.append(_capital(_unwrap(piece)) if piece.startswith("(") else piece)
    out = _join(shown)
    if out and not cell:
        out = _sentence_end(out)
    elif out:
        out = out.rstrip(",;: ")
    if not collapsed:
        return out, None
    return out, (kind, topic, _sentence_end(_join(collapsed)))


# ----------------------------------------------------------------------------- the entries
# A topic collects every piece that has its label on a page, so a collapsed section holds a whole reading, never one
# clause. A clause that would stand alone is left in the text that carries it.

# Data pages: the evidence behind a frame convention (Data notes) and the reasoning behind an inflow fit (Interpretation)
# Case C
add("+x streamwise at WD = 0 (checked three ways on the data", "Frame and wind direction",
    ("(checked three ways on the data", "N"))
add("In the CSV's own frame WD rotates the wind from +x TOWARD -y", "Frame and wind direction",
    ("(the WD = 45 field is mirror-symmetric", "N"), (". Figure 3 of the data paper draws", "F"),
    (", which is the frame the point coordinates live in", "N", (", which is ", "The CSV frame is ")),
    (". The disagreement is invisible", "F"))
add("log law, kappa = 0.41, least squares on AF_caseC.csv", "Inflow fit",
    (", because Case C scores at ONE height", "I", (", because ", "The fit has two windows because ")))
add("derived during scoping, not published by AIJ; the tunnel profile is closer to a power law", "Inflow fit",
    ("; the tunnel profile is closer to a power law", "I", "; "))
# Case D
add("+x streamwise at WD = 0 (the 0 deg thermistor field", "Frame and wind direction",
    ("(the 0 deg thermistor field", "N"))
add("+x toward +y, read from Figure 4 of the data paper.", "Frame and wind direction",
    ("The array is exactly y-mirror symmetric", "N"), ("solved Eddy3D fields score", "F", ""))
add("log law, kappa = 0.41, least squares on the workbook's 13-point profile", "Inflow fit",
    (", because the measurement plane z/H = 0.02", "I", (", because ", "The fit has two windows because ")))
add("derived during scoping, not published by AIJ; a log-law inlet cannot be right", "Inflow fit",
    ("; a log-law inlet cannot be right", "I", "; "))

# Run notes (Interpretation)
# Case F
add("The thermistor reads a scalar speed and so does the cup anemometer", "Case F scalar speed and field data",
    (", which is the lower bound", "I", (", which is ", "The modelled |U| is ")), (", and as √(|U|²+2k), the speed", "F"),
    (", which is the upper bracket", "I", (", which is ", "√(|U|²+2k) is ")))
add("The field is a year of 10-minute means above 5 m/s", "Case F scalar speed and field data",
    (", and a RANS field is one steady state", "I", ", and "), (". The tunnel's 9 m column scored as a model of the field", "F"),
    (": the bar a model of the tunnel is not expected to clear", "I", (": the bar ", "The tunnel's 9 m column as a model of the field is the bar ")))
# Case G
add("The three crowns are entries of the Eddy3D vegetation library", "Case G drag sweep",
    (" The arm nearest the 28 values", "I"))
add("Eddy3D models trees as a Darcy-Forchheimer momentum sink only", "Case G drag sweep",
    (" The modelled k behind the belt", "I"))
# Case J
add("The scene is the tunnel at Froude scale 62.5", "Case J wall functions",
    (", where UMF's wall functions belong and the tunnel's laminar-sublayer heat transfer does not exist", "I",
     (", where ", "At the model's Re, ")))
add("UMF's first cell is 0.75 m, 12 mm at tunnel scale", "Case J wall functions",
    (", so near-floor temperature is a wall-function result", "I", ", so "), (". The source is a mass rate", "F"))
# Case K
add("The inflow is the measured approach profile", "Case K scores",
    (", so the modelled velocity sits under the measured mean", "I", ", so "))
add("The measured plume is not y-symmetric", "Case K scores",
    (", the best a y-symmetric model can do on this file", "I", (", the best a", "The y-symmetric ceiling is the best a")))
add("V has a constant offset and almost no antisymmetric part", "Case K scores",
    (", so it does not score the flow's divergence", "I", (", so it ", "V ")), ("; a model with V = 0 everywhere", "F"),
    (", so V's hit rate says nothing", "I", ", so "))
# Case M: the readings are notes of their own, shared by the three Schmidt-number runs
whole("The tunnel's three points nearest the source carry", "Case M near-source ordering")
whole("The tracer goes downwind:", "Case M controls")
