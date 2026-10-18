"""One look for every figure in validation/: what the plot scripts import instead of styling themselves.

The reference is the house style for publication figures: a bold title, panels lettered a, b, c in bold at
the upper left, a full black frame with minor ticks, major grid lines strong enough to read values off,
units in square brackets, the MEASUREMENT drawn in black and each model in its own fixed colour, and one
frameless legend centred under the panels. It is built on ultraplot 2.7.1 (requirements.txt), and what
"ultraplot standard" means below was MEASURED from that version in the pinned container, not recalled:

  ultraplot's defaults    font TeX Gyre Heros (a Helvetica clone shipped inside the package) at 9 pt; frame
                          0.6 pt, lines 1.5 pt, ticks 4 pt out with minor ticks; grid alpha 0.1; subplots
                          sized by an axes width in inches (refwidth 2.5) and laid out tight; cycle
                          "colorblind" = #0072b2 #d55e00 #009e73 #cc79a7 #f0e442 #56b4e9 (the Wong 2011
                          palette without black and orange); cmap.sequential "Fire" (white to near-black),
                          cmap.diverging "BuRd" (ColorBrewer RdBu reversed, centre #f7f6f6); figure.facecolor
                          #f4f4f4 for screens and savefig.facecolor white; savefig.dpi 1000.

The rules this repository applies, where they depart from those defaults, and why:

  1. Raster figures are written at 1200 dpi (DPI), nothing lower; sizes stay in inches, so a panel keeps its
     physical size and its text stays 10 pt. Vector output (.svg, .pdf) stays vector, with outlined text.
     Every figure is written through save(), which also fixes the metadata so that a rebuild is
     byte-identical (no timestamp; the PNG carries the producing script and the library versions).
  2. One font, TeX Gyre Heros, for text and for maths. Sizes are 10 pt body and 11 pt labels where ultraplot
     has 9, a taste call kept so that the layout of every figure published so far does not move. The grid is
     black at alpha 0.28 (ultraplot: 0.1) so values can be read off, and the legend has no frame.
  3. WHO drew it (categorical): the measurement is ink (MEASURED); each engine takes one colour of
     ultraplot's "colorblind" cycle and keeps it in every figure: OpenFOAM blue, OpenLB vermillion, ML
     bluish green, FluidX3D reddish purple (the hue family each engine already had, so no figure changes
     meaning). The cycle's yellow (1.3:1 against white) and sky blue (2.3:1, and 26 units from the blue)
     are not used for engines; every engine colour is at least 3:1 against the white page.
     check_palette() simulates deuteranopia, protanopia and tritanopia (Machado, Oliveira and Fernandes
     2009, severity 1) and fails apply() if any two of these colours come closer than 15 CIE76 units
     under any of them; `python validation/plotstyle.py` prints the table. The smallest differences are 53.6
     (normal vision), 17.9 (deuteranopia, FluidX3D-ML), 22.7 (protanopia, OpenFOAM-FluidX3D) and 17.0
     (tritanopia, OpenFOAM-ML); the palette this replaced had 12.9, 35.6 and 13.9 for the three.
  4. HOW MUCH (sequential): viridis, not ultraplot's default "Fire". Both are monotone in lightness, but Fire
     starts at #ffffff, which is the page, so the smallest values of a magnitude would vanish; viridis runs
     from L* 15 to 91 in steps within 0.6 to 1.3 times the mean and is built to survive colour blindness.
  5. ABOVE OR BELOW A REFERENCE (diverging): ultraplot's default "BuRd" REVERSED (BIAS_CMAP), centred on zero
     (vmin = -vmax, zero = the neutral #f7f6f6, ends at L* 20, lightness within 5 L* of each other at equal
     distance from the centre). Reversed so that red is "model slower than the tunnel" and blue "faster",
     the sense these figures have had since release 2.0.0. Markers carry a thin grey edge, because the
     neutral centre is the white of the page and the best-agreeing points would otherwise disappear.
  6. Ink and greys, all achromatic so they never tint a colour map: INK for text and frames, REFERENCE
     (#6b6b69, 5.3:1) for 1:1 lines and secondary text, FOOTPRINT and FOOTPRINT_FOCUS for plan-view solids.
     Reference geometry is always thinner than data.
  7. Figures keep the white page (SURFACE). On the site's dark scheme they sit on a white card, which the
     page's CSS provides; a figure never relies on its page for its background.

Public names (keep them stable; other scripts import them): DPI, FIGURES, INK, MEASURED, REFERENCE, SURFACE,
FOOTPRINT, FOOTPRINT_FOCUS, BLUE, VERMILLION, GREEN, PURPLE, OPENFOAM, OPENLB, ML, FLUIDX3D, SEQUENTIAL,
BIAS_CMAP, BIAS_LIM, SLOW, FAST, NEUTRAL, apply, line, marker, stats, one_to_one, outer_ticks, arrow,
bias_scatter, bias_colorbar, finish, save, delta_e, contrast, check_palette, palette_report.

A figure script, complete:

    import numpy as np
    import ultraplot as uplt
    import plotstyle as ps

    ps.apply()
    fig, axs = uplt.subplots(ncols=2, refwidth=2.5, refaspect=1)
    axs[0].scatter(measured, modelled, s=16, color=ps.OPENFOAM, edgecolor=ps.SURFACE, linewidth=0.35)
    ps.one_to_one(axs[0], 0, 1.2)
    sc = ps.bias_scatter(axs[1], x, y, model=modelled, tunnel=measured, s=26)
    ps.bias_colorbar(fig, sc, "Eddy3D speed / tunnel Vs")
    ps.finish(fig, "Title", handles=[ps.marker(ps.OPENFOAM, "Eddy3D"), ps.line(ps.REFERENCE, "1:1")])
    ps.save(fig, "figure-name.png")      # validation/figures/figure-name.png at 1200 dpi

Why arrow() rounds its end points: a FancyArrowPatch whose direction is exactly 45 degrees has a head on a
sub-pixel rounding boundary, and sin and cos of 45 degrees differ in the last bit between libm builds, so
the same script drew a head one 1/256 pixel apart on arm64 and on amd64 (14 pixels, one grey level, in
case-c-openfoam-bias-map.png). Rounded to 1e-6 the input is the same on every CPU.
"""
from __future__ import annotations

import itertools
import os
import struct
import sys

import matplotlib as mpl
import numpy as np
import ultraplot as uplt
from matplotlib import font_manager
from matplotlib.colors import to_hex, to_rgb
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch

HERE = os.path.dirname(os.path.abspath(__file__))
FIGURES = os.path.join(HERE, "figures")

DPI = 1200                    # every raster figure, no exceptions
FONT = "TeX Gyre Heros"       # ultraplot's own default, shipped inside the package

# Ink and greys: achromatic on purpose.
INK = "#1a1a1a"
MEASURED = INK                # the measurement is black, as in every comparison figure of the house style
REFERENCE = "#6b6b69"         # 1:1 and factor-of-two lines, secondary text: recessive, never data
SURFACE = "#ffffff"
FOOTPRINT = "#dadada"         # plan-view buildings
FOOTPRINT_FOCUS = "#a8a8a8"   # the building(s) the case is about

# ultraplot's "colorblind" cycle, in its order; check_palette() fails if the installed ultraplot disagrees.
BLUE = "#0072b2"
VERMILLION = "#d55e00"
GREEN = "#009e73"
PURPLE = "#cc79a7"

# Each engine keeps one colour across every figure in this repository.
OPENFOAM = BLUE
OPENLB = VERMILLION
ML = GREEN
FLUIDX3D = PURPLE

SEQUENTIAL = "viridis"        # magnitudes
BIAS_CMAP = "BuRd_r"          # model/measurement ratios, centred on zero: red = model slow, blue = model fast
BIAS_LIM = 1.0                # log2 units: +-1 is the factor of two

_bias = uplt.Colormap(BIAS_CMAP)
SLOW = to_hex(_bias(0.0))     # the pole of the map where the model is slower than the tunnel
FAST = to_hex(_bias(1.0))
NEUTRAL = to_hex(_bias(0.5))  # zero: model equals measurement


def apply():
    """Set the house style. Call once, before any subplots."""
    check_palette()
    font_manager.findfont(FONT, fallback_to_default=False)   # raises if the font is missing: no silent fallback
    uplt.rc.update({
        "font.family": FONT,
        "mathtext.cal": "sans:italic",    # ultraplot's default asks for a cursive font nobody has, and warns
        "font.size": 10.0,
        "label.size": 11.0,
        "tick.labelsize": 10.0,
        "title.size": 11.5,
        "suptitle.size": 13.0,
        "suptitle.weight": "bold",
        "abc": "a",
        "abc.loc": "ul",
        "abc.size": 12.0,
        "abc.weight": "bold",
        "abc.border": True,
        "abc.borderwidth": 2.5,
        "grid": True,
        "grid.color": "black",
        "grid.alpha": 0.28,
        "grid.linewidth": 0.6,
        "gridminor": False,
        "axes.linewidth": 0.8,
        "tick.width": 0.8,
        "tick.len": 4.5,
        "tick.minor": True,
        "legend.frameon": False,
        "legend.fontsize": 10.5,
        "lines.linewidth": 1.6,
        "cycle": "colorblind",
        "cmap.sequential": SEQUENTIAL,
        "figure.facecolor": SURFACE,
        "savefig.facecolor": SURFACE,
        "savefig.dpi": DPI,
        "svg.hashsalt": "aij",            # vector output: element ids derive from this, not from a random salt
    })


def line(color, label, lw=1.8, ls="-"):
    return Line2D([], [], color=color, lw=lw, ls=ls, label=label)


def marker(color, label, filled=True, size=6.5):
    return Line2D([], [], ls="none", marker="o", markersize=size, label=label,
                  markerfacecolor=color if filled else "none", markeredgecolor=color if not filled else SURFACE,
                  markeredgewidth=1.0 if not filled else 0.4)


def stats(ax, text, loc=(0.05, 0.80)):
    """Scores printed in the panel, under its letter, on a white halo so grid lines never cut them."""
    ax.text(*loc, text, transform=ax.transAxes, va="top", ha="left", fontsize=8.5, color=INK, zorder=10,
            bbox=dict(boxstyle="round,pad=0.25", facecolor=SURFACE, edgecolor="none", alpha=0.85))


def one_to_one(ax, lo, hi, factor_two=True):
    xs = np.array([lo, hi])
    ax.plot(xs, xs, color=REFERENCE, lw=1.0, zorder=1)
    if factor_two:
        pos = np.array([max(lo, 1e-6), hi])
        ax.plot(pos, 2 * pos, color=REFERENCE, lw=0.8, ls=":", zorder=1)
        ax.plot(pos, 0.5 * pos, color=REFERENCE, lw=0.8, ls=":", zorder=1)


def outer_ticks(axs, nrows, ncols):
    """Tick labels on the outer edge of a grid only; the panels share their limits, so inner labels repeat."""
    grid = np.asarray(axs).reshape(nrows, ncols)
    for r in range(nrows):
        for c in range(ncols):
            grid[r, c].tick_params(labelleft=(c == 0), labelbottom=(r == nrows - 1))


def arrow(ax, tail, head, color=INK):
    """A wind arrow in data coordinates. End points are rounded to 1e-6 so every CPU draws the same pixels."""
    ax.add_patch(FancyArrowPatch(tuple(np.round(tail, 6)), tuple(np.round(head, 6)), arrowstyle="-|>",
                                 mutation_scale=11, color=color, lw=1.4, zorder=4))


def bias_scatter(ax, x, y, model, tunnel, s):
    """Markers coloured by log2(model / tunnel), clipped to +-BIAS_LIM; returns the mappable for bias_colorbar."""
    ratio = np.log2(np.asarray(model, float) / np.asarray(tunnel, float))
    return ax.scatter(x, y, c=np.clip(ratio, -BIAS_LIM, BIAS_LIM), cmap=BIAS_CMAP, vmin=-BIAS_LIM, vmax=BIAS_LIM,
                      s=s, edgecolor=REFERENCE, linewidth=0.4, zorder=3)


def bias_colorbar(fig, mappable, what):
    """The colour bar under a grid of bias maps; `what` reads "numerator / denominator"."""
    fig.colorbar(mappable, loc="b", ticks=[-1, -0.5, 0, 0.5, 1], length=0.7,
                 label=f"log$_2$({what}) [–]:  −1 = half the tunnel's speed,  0 = equal,  +1 = twice")


def finish(fig, title, handles=None, ncols=None, **fmt):
    """Bold title, panel letters, and one frameless legend centred under the panels."""
    fig.format(suptitle=title, **fmt)
    if handles:
        fig.legend(handles, loc="b", ncols=ncols or len(handles), frame=False)


def save(fig, name, directory=FIGURES, dpi=DPI):
    """Write `fig` as directory/name; the only place a figure is written.

    .png at `dpi` (1200) on the white page, losslessly optimised, with no timestamp so a rebuild is
    byte-identical; .svg and .pdf stay vector. The PNG's own dpi field is read back and checked.
    """
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, name)
    kind = os.path.splitext(name)[1].lower()
    software = f"Matplotlib {mpl.__version__}, ultraplot {uplt.__version__}"
    script = getattr(sys.modules.get("__main__"), "__file__", None) or __file__
    if kind == ".png":
        fig.savefig(path, dpi=dpi, facecolor=SURFACE, pil_kwargs={"optimize": True},
                    metadata={"Software": software, "Comment": "validation/" + os.path.basename(script)})
        with open(path, "rb") as f:        # the pHYs chunk (pixels per metre) sits before the image data
            head = f.read(4096)
        i = head.index(b"pHYs")
        per_metre = struct.unpack(">II", head[i + 4:i + 12])
        assert all(abs(p * 0.0254 - dpi) < 1 for p in per_metre), (name, per_metre)
    elif kind == ".svg":
        fig.savefig(path, facecolor=SURFACE, metadata={"Date": None, "Creator": software})
    elif kind == ".pdf":
        fig.savefig(path, facecolor=SURFACE, metadata={"CreationDate": None, "Creator": software, "Producer": software})
    else:
        raise ValueError(f"{name}: write .png, .svg or .pdf")
    print("wrote", name)


# ----------------------------------------------------------------------------- colour checks

# Machado, Oliveira and Fernandes (2009), severity 1.0, acting on linear sRGB.
_CVD = {
    "deuteranopia": [[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.011820, 0.042940, 0.968881]],
    "protanopia": [[0.152286, 1.052583, -0.204868], [0.114503, 0.786281, 0.099216], [-0.003882, -0.048116, 1.051998]],
    "tritanopia": [[1.255528, -0.076749, -0.178779], [-0.078411, 0.930809, 0.147602], [0.004733, 0.691367, 0.303900]],
}
_XYZ = np.array([[0.4124564, 0.3575761, 0.1804375], [0.2126729, 0.7151522, 0.0721750], [0.0193339, 0.1191920, 0.9503041]])
VISIONS = ("normal",) + tuple(_CVD)
MIN_DELTA_E = 15.0            # CIE76 units; ~2.3 is a just-noticeable difference, so 15 reads as two colours
MIN_CONTRAST = 3.0            # WCAG 2.2 non-text contrast of a mark against its background

CATEGORICAL = {"measured": MEASURED, "OpenFOAM": OPENFOAM, "OpenLB": OPENLB, "FluidX3D": FLUIDX3D, "ML": ML}


def _linear(colour):
    c = np.array(to_rgb(colour))
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def _lab(rgb_linear):
    t = (_XYZ @ rgb_linear) / (_XYZ @ np.ones(3))
    f = np.where(t > (6 / 29) ** 3, np.cbrt(t), t / (3 * (6 / 29) ** 2) + 4 / 29)
    return np.array([116 * f[1] - 16, 500 * (f[0] - f[1]), 200 * (f[1] - f[2])])


def delta_e(a, b, vision="normal"):
    """CIE76 colour difference between two colours as seen with `vision` (normal, deuteranopia, ...)."""
    lab = []
    for c in (a, b):
        rgb = _linear(c)
        lab.append(_lab(rgb if vision == "normal" else np.clip(np.array(_CVD[vision]) @ rgb, 0, 1)))
    return float(np.linalg.norm(lab[0] - lab[1]))


def contrast(colour, background=SURFACE):
    """WCAG contrast ratio of `colour` against `background`."""
    hi, lo = sorted(((_XYZ @ _linear(c))[1] for c in (colour, background)), reverse=True)
    return float((hi + 0.05) / (lo + 0.05))


def palette_report(colours=None):
    """Print every pair's colour difference under every vision, and each colour's contrast on the page."""
    colours = colours or CATEGORICAL
    for n, c in colours.items():
        print(f"{n:9s} {c}  contrast against white {contrast(c):4.2f}")
    rows = {}
    for (a, ca), (b, cb) in itertools.combinations(colours.items(), 2):
        rows[(a, b)] = {v: delta_e(ca, cb, v) for v in VISIONS}
        print(f"{a:9s} {b:9s} " + "  ".join(f"{v} {d:5.1f}" for v, d in rows[(a, b)].items()))
    print("minimum   " + "  ".join(f"{v} {min((r[v], p) for p, r in rows.items())[0]:.1f}" for v in VISIONS))


def check_palette():
    """The categorical colours must be ultraplot's, tell apart under every vision, and show on the page."""
    cycle = [to_hex(d["color"]) for d in uplt.Cycle("colorblind")]
    assert cycle[:4] == [BLUE, VERMILLION, GREEN, PURPLE], f"ultraplot's colorblind cycle changed: {cycle}"
    for (a, ca), (b, cb) in itertools.combinations(CATEGORICAL.items(), 2):
        for v in VISIONS:
            assert delta_e(ca, cb, v) >= MIN_DELTA_E, (a, b, v, delta_e(ca, cb, v))
    for n, c in CATEGORICAL.items():
        assert contrast(c) >= MIN_CONTRAST, (n, contrast(c))


if __name__ == "__main__":
    check_palette()
    palette_report()
