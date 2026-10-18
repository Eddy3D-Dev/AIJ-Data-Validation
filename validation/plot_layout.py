"""Where the tunnel measured: one layout figure per case, validation/figures/case-<x>-layout.png.

Each figure shows the measurement lines and planes of one case, grouped and lettered as layout.py groups them: (a) the elevation
with the dotted vertical profiles and the horizontal planes, (b) the plan with every measured position. The groups colour the scatter
dots of the case's agreement figure, so a dot there is found here by its colour and letter. Case I, whose lines run from the cube
to 27 heights downwind, adds a pair of panels on the near field. The district cases C, D, E, F and M, which measure at one height or a
few on a plan, are drawn by layout.district_figure: (a) the plan with the buildings and the points, (b) the elevation under it, or for
Case F the heights above ground at the 13 points beside it.

Inputs: clean/cases/<x>/points.csv, geometry.json and approach_flow.csv (through layout.py, whose docstring has the rules).
"""
import plotstyle as ps
import layout

ps.apply()
for case in layout.SPECS:
    ps.save(layout.district_figure(case) if case in layout.DISTRICT else layout.layout_figure(case), f"case-{case.lower()}-layout.png")
