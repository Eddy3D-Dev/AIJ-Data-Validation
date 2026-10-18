---
title: "Cases"
nav_order: 2
has_children: true
has_toc: false
description: "The AIJ UWE benchmark cases: what each is, what was measured, the frame and unit its cleaned data is served in, and which engines were scored."
---

# Cases

Each case has three pages: the case page (geometry render, engine status, key numbers), **Data** (configuration, frame
and units, inflow fit, known data issues, files) and **Validation** (scores by engine, figures). The API serves the same
facts as `/api/cases/{id}.json`.

{% include cases-table.md %}

## Frames and units

Each case has its own frame and unit. The API's `points.json` and STL files of a case share its frame.

{% include cases-frames.md %}
