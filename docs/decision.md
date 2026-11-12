1. the final deadline - 17th November and submission format: 

Introduction -Describe the background of your work, why you want to do this, business understanding, and possible impacts)
Problem statement
Related works
Datasets (At least 3 datasets)
Methodology (EDA, data pre-processing, Machine learning model, Pipeline)
Model Evaluation results
Discussions (comparison with others in terms of performance, interpretability, and complexity)
Conclusions (Summary of your contributions)
Properly cite any figures or datasets that you obtain from the Internet. Using Chatgpt or any genAI tools to improve your writing is encouraged.

Submit both the report and presentation in this assignment.
For the report, use the AIT thesis template from the AIT Language Center.
Provide a detailed explanation of how your system outperforms others in the Kaggle/huggingfaces, highlighting the unique features, advantages, and user benefits that make it more attractive and preferable compared to competing solutions.
Describe the baseline model that you want to compare with your proposed model.

2. any comments from the professor after the midterm - None
3. test protection (I recommend: choose designs on validation, score the test once per design, and say in the report that the test was seen at the midterm)
4. whether CU-BEMS stays in: Yes, we plan to use CUBEMS for the test run. Do you think this is a good idea? 
5. how to word the holiday limitation: You decide this, give me your best solution
6. how to word the BDG2 line: You decide this, give me your best solution
7. Also ask the professor about the explain-away filter: build the simple version, or drop it and say so. : lets do the simple version for now

---

# Answers and notes added on 2 Nov 2026 (the lines above are yours, unchanged)

## Summary of the decisions

| # | Question | Decision | Status |
| --- | --- | --- | --- |
| 1 | Deadline and format | **17 November 2026.** Report (AIT thesis template) plus presentation. Sections and rules are listed above. | Settled |
| 2 | Professor's comments after the midterm | None | Settled |
| 3 | Test protection | **Option A**: choose every design on validation, score the test once per frozen design, and say in the report that the test period was seen at the midterm. | Assumed. You left my recommendation in place without choosing, so I recorded A. Tell me if you want B. |
| 4 | CU-BEMS stays in | **Yes. Keep it.** It is also what gives the report its required third dataset. See the note below. | Settled |
| 5 | Wording of the holiday limitation | See the wording below. | Written, ready to paste |
| 6 | Wording of the BDG2 line | See the wording below. | Written, ready to paste |
| 7 | Explain-away filter | **Build the simple version** (task T38). Reword it as a limitation if it does not work. | Settled |

## Item 4: is using CU-BEMS "for the test run" a good idea?

Yes, keep it, with one correction to how it is described.

- **Why it is a good idea.** The submission format asks for **at least 3 datasets**. GEPIII, LEAD and CU-BEMS make three. CU-BEMS is also a different building (an office tower in Bangkok), so it shows whether the methods work outside the university buildings in GEPIII.
- **The correction.** CU-BEMS cannot be a plain test set for models trained on GEPIII. It has no outdoor weather, minute-level readings, and no anomaly labels. So we do not train on GEPIII and test on CU-BEMS. We run the same methods on CU-BEMS using its **own** train, validation and test split, with anomalies of known size and position planted in its validation and test periods. Call it "a second-dataset check", not "the test set".
- **What it can and cannot show.** It shows the methods can find problems of known size in another building. It does not show they find real faults, because planted problems are artificial. Say so in the report.
- **Honest caveat on "three datasets".** LEAD labels are made on top of GEPIII, so two of the three are linked. Say that in one sentence rather than hiding it.

## Item 5: wording for the holiday limitation (my solution)

**Report, Limitations section (use this if the simple filter, task T38, is built):**

> The datasets give no holiday calendar or class schedule, and GEPIII does not disclose where its sites are, so a calendar could not be attached to the data. The models therefore know the hour, the day of the week, whether it is a weekend, and the weather, but not whether a day is a holiday or an exam period. To reduce the effect, we added a simple filter that marks a flag as *explained by a site-wide event* when most buildings on the same site deviate from normal at the same time. This identifies days when something affected a whole site. It does not identify which day is a holiday, and a holiday that changes only a few buildings may still produce false alarms.

**Report, if the filter does not work or is not finished (fallback):**

> The datasets give no holiday calendar or class schedule, and GEPIII does not disclose where its sites are, so no calendar information could be used. The models know the hour, weekday and weather only. Flags on holidays, exam periods and other scheduled changes may therefore be false alarms. A calendar-based explain-away step is left for future work.

**One sentence for the slides:** "We have no holiday or class-schedule data, so flags on those days may be false alarms; a simple site-wide filter reduces this."

**Why this wording:** it says exactly what is missing and why, it does not claim the filter finds holidays, and it tells the reader what could still go wrong.

## Item 6: wording for the BDG2 line (my solution)

The proposal said we would compare with BDG2. GEPIII is a subset of BDG2, so BDG2 is not independent evidence. The honest fix is to say so and not to pretend BDG2 is a separate fourth dataset.

**Report, Datasets section:**

> We use three datasets. (1) GEPIII, from the ASHRAE Great Energy Predictor III competition, gives hourly electricity readings, weather and building facts for 2016. GEPIII's buildings come from the Building Data Genome Project 2 (BDG2) collection, so BDG2 is the source of GEPIII and not a separate dataset; we do not use it as independent evidence. (2) LEAD 1.0 gives human-marked anomaly labels for 200 GEPIII buildings. LEAD is built on GEPIII, so the labels check our flags against human judgment and are not independent of the readings. (3) CU-BEMS gives minute-level readings from one office building in Bangkok. It has no labels, so we plant anomalies of known size and position to check the methods on a second building.

**Where the proposal line changes:** replace "compare with BDG2" with "BDG2 is the source collection of GEPIII; we use GEPIII from it."

## What the submission format means for the remaining work

Your format asks for more than the experiments. These are added to the task tracker.

| New task | Why |
| --- | --- |
| T44 Put the report into the **AIT thesis template** and map our sections to the required ones (Introduction, Problem statement, Related works, Datasets, Methodology, Model evaluation results, Discussions, Conclusions) | The format requires this template and these sections. |
| T45 Related works section with citations for every dataset and figure | Required, and we need at least 3 datasets stated. |
| T46 A **Discussions comparison** of the methods on **performance, interpretability and complexity** (for example: events found; whether a person can see why an hour was flagged; number of features, training time) | The format asks for these three comparisons. The feature-importance task (T39) feeds the interpretability part. |
| T47 A section on **how our system compares with other approaches**, written honestly | See the warning below. |
| Baseline description | Already have it: same-as-last-hour, historical typical value, fixed percentile. Describe them in the Methodology section. |

**Warning about "explain how your system outperforms others".** Our results do not support saying that we outperform everything. At the same flag rate, copying the last hour (38.7%) finds slightly more events than Model C (35.1%). What we can honestly say:

- The GEPIII Kaggle competition was about predicting use accurately, not flagging anomalies. Its solutions give no flags, no ranked list and no check against labels.
- Our approach checks flags against human labels, compares against honest baselines at equal flag rates, and produces a ranked list for review.
- Model C ranks the top 50 alerts better (72% touch a labeled event, against 54% for the last-hour rule) and finds more events longer than 12 hours (50.0% against 32.7%).
- Where a simple rule is as good as a model, we say so.

Write the comparison section around these points. Do not claim to beat all other systems.

## Schedule to the 17 November deadline

Today is 2 Nov, so there are 15 days. The core work is about 13 to 17 person-days (the 43 tracked tasks plus the four above), so with two people it fits only if writing starts early and the optional tasks are dropped.

| Dates | Work |
| --- | --- |
| 3 to 4 Nov | Correct documents (done), start T23 (more history features), T25 (Isolation Forest), T31 (CU-BEMS prepare). Open the thesis template and set up the report skeleton (T44). |
| 5 to 7 Nov | T24 (persistence test), T40 (train without labeled hours), T38 (explain-away filter), T32 (CU-BEMS evaluate). |
| 8 to 10 Nov | T27, T28 (bootstrap), T39 (feature importance), T30 (the ranked review list). |
| 11 to 12 Nov | T33 (final tables and figures), T46 (comparison table), write Methodology and Results. |
| 13 to 15 Nov | Write the rest of the report, Discussion, Conclusion; make the slides and script (T34, T35, T47). |
| 16 Nov | Buffer: read the whole report, check numbers against `results/final/`, tidy the folder (T36). |
| 17 Nov | Submit report and presentation. |

**Drop first if time runs short:** T41, T42, T43, then T29, then T26. Keep T24, T28, T30, T38, T32.
