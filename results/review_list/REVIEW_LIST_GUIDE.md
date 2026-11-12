# Ranked review list: how to read it

File: `ranked_review_list_model_C_test.csv` (made by `ranked_list.py`). One row per flagged run of Model C in the test period (7 Nov to 31 Dec 2016): 911 runs, from 200 buildings. A run is consecutive flagged hours in one building. Runs are ranked by their highest score (peak_score), largest first. Cut-off: score above 9.4469 (frozen, 0.5% of clean validation hours).

Columns
- rank, building_id, site_id, primary_use: which building.
- start, end, hours: when the run began and ended and how many hours it lasted.
- peak_score, peak_hour: the largest score in the run and the hour it happened (score = size of the gap between real and expected use, in units of that building's normal gap).
- actual_kwh_at_peak, expected_kwh_at_peak, ratio_actual_to_expected: real and expected use at the peak hour.
- direction: "below expected" if at least half the flagged hours were under the expected value, otherwise "above expected". It is decided by the majority of hours, so the peak hour can point the other way.
- mean_air_temp_c: average outdoor temperature at the building's site during the run.
- all_zero: every flagged hour has a reading of exactly 0.
- sitewide: at least 3 buildings on the same site and at least 30% of its buildings were flagged in the same hour (same rule as notebook 10).
- touches_label / hours_to_nearest_label: whether a hand-marked event overlaps the run, and how many hours away the closest one is. These come from labels and are for checking the tool, not part of the ranking.

How to use it: start at rank 1 and look at the building's readings around the run. Ask whether use was unusual for that building at that time. Runs marked all_zero or sitewide are often a meter or data problem or an outage affecting a whole site, so check those first as "data or site problem" before treating them as building behaviour.

What the list can and cannot say: it points to hours that are unusual for the building's context. It does not say why, and it does not say anything about waste, faults or savings.

How well the ranking lines up with the labels (test period, descriptive only): 197 of 911 runs (21.6%) overlap a labeled event. Among the top 10, 25, 50, 100 and 200 runs: 80%, 76%, 74%, 65% and 53% overlap a labeled event. Labels are hand-marked and incomplete, so runs that overlap none are not necessarily false alarms.
