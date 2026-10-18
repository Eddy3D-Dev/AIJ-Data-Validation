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

Entries that match nothing in a build are an error, so a rewritten source string cannot leave a stale entry behind.
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
# Known issues and the data texts of the case pages (Data notes), then the run notes (Interpretation).

# Case A, B
add("Lateral velocity V is positive toward +y (checked:", "Lateral sign",
    ("(checked: V = -2.893", "N"), (". Case B uses the OPPOSITE sign", "F"))
add("Case A's turbulence columns are rms values", "Variance columns",
    (" so A and B share one column meaning", "N", " so "))
add("The published coordinates are MILLIMETRES", "Coordinate scale",
    ("Read as metres, every probe lands 1000x too far out.", "N"))
add("The published lateral velocity V is positive toward -y", "Lateral sign",
    ("(V = +3.630", "N"), (". The API multiplies V by -1", "F"), ("Scored without this", "N"))
add("The RANS solution is symmetric, so model V = 0", "Model symmetry",
    ("The RANS solution is symmetric", "I"), (", so model V = 0 on the centre plane", "F", (", so model V = 0 on the centre plane", "On the centre plane model V = 0")))
# Case C
add("log law, kappa = 0.41, least squares on AF_caseC.csv", "Inflow fit",
    (", because Case C scores at ONE height", "I", (", because ", "The fit has two windows because ")))
add("The measured quantity Vs is the MEAN OMNIDIRECTIONAL SCALAR speed", "Scalar speed",
    ("A RANS |U| is biased low against it; ", "I", ("A RANS |U| is biased low against it", "A RANS |U| is biased low against Vs")),
    ("the data paper suggests", "F", ""))
add("24 of the 120 points sit exactly on a building face plane", "Points on a face plane",
    (": legitimate fluid points", "N", ": "))
add("+x streamwise at WD = 0 (checked three ways on the data", "Frame",
    ("(checked three ways on the data", "N"))
add("In the CSV's own frame WD rotates the wind from +x TOWARD -y", "Wind direction convention",
    ("(the WD = 45 field is mirror-symmetric", "N"), (". Figure 3 of the data paper draws", "F"),
    (", which is the frame the point coordinates live in", "N", (", which is ", "The CSV frame is ")),
    (". The disagreement is invisible", "F"))
add("derived during scoping, not published by AIJ; the tunnel profile is closer to a power law", "Inflow fit",
    ("; the tunnel profile is closer to a power law", "I", "; "))
# Case D
add("+x streamwise at WD = 0 (the 0 deg thermistor field", "Frame",
    ("(the 0 deg thermistor field", "N"))
add("+x toward +y, read from Figure 4 of the data paper.", "Wind direction convention",
    ("The array is exactly y-mirror symmetric", "N"), ("solved Eddy3D fields corroborate", "F", ""))
add("log law, kappa = 0.41, least squares on the workbook's 13-point profile", "Inflow fit",
    (", because the measurement plane z/H = 0.02", "I", (", because ", "The fit has two windows because ")))
add("derived during scoping, not published by AIJ; a log-law inlet cannot be right", "Inflow fit",
    ("; a log-law inlet cannot be right", "I", "; "))
add("A prior Eddy3D comparison kept in the folder", "Prior comparison",
    (": a frame or geometry error", "N", (": a frame or geometry error", "That score is a frame or geometry error")))
# Case E
add("Meteorological: the compass name is the direction the wind comes FROM", "Wind direction convention",
    (" because the district is real", "N", " because "))
add("The velocity ratio is normalised by the inflow velocity at 15.9 m", "Prior comparison",
    ("A prior Eddy3D comparison in the folder", "N"))
add("The measured quantity is a scalar (thermistor) speed; a RANS", "Scalar speed",
    ("; a RANS |U| is biased low against it in a dense canopy", "I",
     ("; a RANS |U| is biased low against it", "A RANS |U| is biased low against the thermistor speed")), (". The construction signal", "F"))
# Case F
add("compass FROM-direction (N = 0, E = 90): N blows toward -y", "Wind direction convention",
    ("; supported by the reference-building choice and by upwind roughness", "N", "; "),
    (", and at NNW corroborated", "F", ", and "))
add("The thermistor reads a SCALAR speed and the cup anemometer a 10-minute mean", "Scalar speed",
    (": a RANS |U| is biased low against both", "I",
     (": a RANS |U| is biased low against both", "A RANS |U| is biased low against the thermistor and the cup anemometer")))
add("The files do not say whether a wind direction names where the wind comes from", "Wind direction labels",
    ("and a solved field corroborates that at NNW: ", "I", ("and a solved field corroborates that", "A solved field corroborates this reading")),
    ("Eddy3D's OpenFOAM 12 run for the wind from NNW", "F"))
# Case G
add("The tree belt is a POROUS canopy", "Canopy model",
    (", and a solver needs a canopy", "I", ", and "))
add("derived during cleaning, not published as a fit; the profile carries 2 decimals", "Inflow fit",
    (", so the fitted index is good to about", "I", ", so "))
add("derived during scoping, not published by AIJ; the boundary layer is unstably stratified", "Inflow fit",
    (", so a neutral log law is only a rough description", "I", ", so "))
add("least squares, kappa = 0.41, z = 0.02 .. 0.6 m (10 H) on AF_caseK.csv", "Inflow fit",
    (", so the window is a choice", "I", ", so "))
# Case I
add("V on the y = 0 plane (53 of 91 points) is 0 in the CSV", "V on the symmetry plane",
    (": a symmetry value, not a measurement", "N", (": a symmetry value", "V on that plane is a symmetry value")), (". It is NaN in the table", "F"))
# Case J, K, L
add("The +y and -y halves are not mirror images: over the 97 mirror pairs", "Mirror symmetry",
    (", so a y-symmetric model has a ceiling on this file", "I", ", so "))
add("The mean concentration is not mirror-symmetric", "Mirror pairs",
    (", so the mirror pairs are not a repeatability estimate", "N", ", so "))
add("The +y and -y halves are not mirror images: the same point differs in U by 26 %", "Mirror symmetry",
    (", so the tunnel flow has a lateral gradient", "I", ", so "))
add("The measured tracer flux through the cross-sections equals q / 1.2 m", "Tracer flux",
    (", which fixes q and the unit ppm", "N", (", which fixes ", "This fixes ")), ("; the cube-column line alone", "F"))

# Run notes (Interpretation)
# Case F
add("One direction of the tunnel's twelve", "Coverage of the run",
    (", so nothing here says how the model does at them", "I",
     (", so nothing here says how the model does at them", "Nothing here says how the model does at the other directions")))
add("Frame 'literal': the model is probed at the published z", "Vertical frame",
    ("Neither is asserted, ", "I", ("Neither is asserted", "Neither frame is asserted")),
    ("and the files do not say which one the tunnel meant", "F", "and "),
    (", which is a statement about the datum", "I", (", which is ", "The difference between the frames is ")))
add("Frame 'agl': the model is probed at the STL's own ground", "Vertical frame",
    ("Neither is asserted, ", "I", ("Neither is asserted", "Neither frame is asserted")),
    ("and the files do not say which one the tunnel meant", "F", "and "),
    (", which is a statement about the datum", "I", (", which is ", "The difference between the frames is ")))
add("At the fixture's 4 m surface cells", "First-cell probes",
    (", where the point interpolation is pulled toward the wall's zero", "I", (", where ", "In the first cell ")),
    (": read those rows as such", "I", (": read those rows", "Read the rows at the lowest probes")))
add("47 of the 203 points (the z = 4 mm plane", "First-cell probes",
    (", pulled toward the wall's zero by the point interpolation", "I", (", pulled toward", "The modelled values are pulled toward")))
add("The thermistor reads a scalar speed and so does the cup anemometer", "Scalar speed",
    (", which is the lower bound", "I", (", which is ", "The modelled |U| is ")), (", and as √(|U|²+2k), the speed", "F"),
    (", which is the upper bracket", "I", (", which is ", "√(|U|²+2k) is ")))
add("The field is a year of 10-minute means above 5 m/s", "Field data and the ceiling control",
    (", and a RANS field is one steady state", "I", ", and "), (". The tunnel's 9 m column scored as a model of the field", "F"),
    (": the bar a model of the tunnel is not expected to clear", "I", (": the bar ", "That is the bar ")))
add("The solved field correlates R", "Direction labels",
    ("A RANS field knows no compass", "I"))
# Case G
add("LAD and Cd are not in the dataset (only the shading rate, 81 %)", "Calibration",
    (", so this is a calibration, not a validation", "I", ", so "), (". The three crowns are entries", "F"),
    (", and the arm nearest the 28 values", "I", ", and "))
add("Eddy3D models trees as a Darcy-Forchheimer momentum sink only", "Modelled k behind the belt",
    (", so the modelled k behind the belt is whatever", "I", ", so "))
add("The field is the mean of the instantaneous speed of a 3-D sonic anemometer", "Scalar speed",
    (", which exceeds |U| in a turbulent wake", "I", (", which exceeds ", "The mean instantaneous speed exceeds ")),
    (": the model is scored as", "F"))
add("The approach profile and the wake were measured on different days", "Approach k",
    ("; the cause is not explained", "I", ("; the cause is not explained", "The cause of the mismatch is not explained")))
add("The fixture's structure checks passed for every arm with trees", "Structure checks",
    ("They set no band on the scores.", "I", ("They set no band", "The checks set no band")))
add("the field's U/U_H and k/U_H^2 (U_H = the wind at the tree height", "Scalar speed",
    (", because the field is the mean of an instantaneous speed", "I", ", because "), ("; hit rate D = 0.25", "F"))
# Case J, L
add("The scene is the tunnel at Froude scale 62.5", "Froude scale",
    (", where UMF's wall functions belong", "I", (", where ", "At the model's Re, ")))
add("UMF's first cell is 0.75 m, 12 mm at tunnel scale", "First cell",
    (", so near-floor temperature is a wall-function result", "I", ", so "), (". The source is a mass rate", "F"))
add("The tracer is solved steady beside the flow, as three species of one flow.", "Tracer balance",
    (", a detector of wiring errors and not a convergence claim", "I", (", a detector ", "The fixture's bar is a detector ")),
    (". The largest modelled c*", "F", None, True))
add("The tunnel is not y-symmetric although the array is", "Scoring V",
    (", so it cannot be scored as a pattern", "I", (", so it ", "V ")))
# Case K
add("The inflow is the measured approach profile", "Inflow velocity",
    (", so the modelled velocity sits under the measured mean", "I", ", so "))
add("The measured plume is not y-symmetric", "Symmetry ceiling",
    (", the best a y-symmetric model can do on this file", "I", ", "))
add("V has a constant offset and almost no antisymmetric part", "V hit rate",
    (", so it does not score the flow's divergence", "I", (", so it ", "V ")), ("; a model with V = 0 everywhere", "F"),
    (", so V's hit rate says nothing", "I", ", so "))
add("The fixture's structure checks passed. The air over the roofs", "Structure checks",
    ("They set no band on the statistics.", "I", ("They set no band", "The checks set no band")))
add("The fixture's structure checks passed. The inlet's U_H", "Structure checks",
    ("They set no band on the statistics.", "I", ("They set no band", "The checks set no band")))
# Case M
add("One heading and one steady solve: WD 180", "Heading noise floor",
    ("The tunnel's own neighbouring headings are the noise floor of a single heading: ", "I"),
    ("its WD 175 scored as a model of its WD 180", "F", ("its WD 175", "The tunnel's WD 175")))
add("The structure the fixture first asserted is recorded", "Where the model puts the plume",
    (", which Eddy3D reads as a finding", "I", (", which Eddy3D reads ", "Eddy3D reads this ")), ("The peak c* is", "F"))
add("Controls on the same solution", "Controls",
    (": the tracer goes downwind", "I", ": "), ("), and the points mirrored", "F"),
    (": the modelled plume is displaced sideways", "I", ": "))
add("The field campaign (18 runs) is recorded beside the tunnel, not asserted", "Field campaign",
    (", not asserted", "I", (", not asserted", "The field campaign is not asserted")), (": the 10 runs within 10°", "F"))
