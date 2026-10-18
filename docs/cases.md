---
title: "Cases"
nav_order: 2
has_children: true
has_toc: false
description: "The AIJ UWE benchmark cases: what each is, what was measured, the frame and unit its cleaned data is served in, and which engines were scored."
---

# Cases

Each case has three pages. The **case page** has the geometry render, the engine status and the numbers that matter;
its **Reference data** page has the configuration, the frame and units, the inflow fit, the known data issues and
the files; its **Validation** page has the scores by engine and the figures. The same facts are served by the API as
`/api/cases/{id}.json`.

{% include cases-table.md %}

## Frames and units

Each case has its own frame and unit. The API's `points.json` and STL files of a case share its frame.

{% include cases-frames.md %}
