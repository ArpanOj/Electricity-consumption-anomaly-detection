# Action Points: Electricity Consumption Anomaly Detection

| | |
|---|---|
| **Course** | AT82.01 Computer Programming for Data Science and AI |
| **Instructor** | Dr. Chantri Polprasert |
| **Team** | Barnnita Shrestha, Arpan Ojha |
| **Document owner** | Barnnita Shrestha |
| **Last updated** | Mon 19 Oct 2026 |
| **Midterm submission due** | Mon 19 Oct 2026, 11:59 PM |
| **Presentation** | Tue 20 Oct 2026, 10 min talk + 5 min Q&A |
| **Main notebook** | `Electricity_Anomaly_Detection_Midterm.ipynb` |
| **Companion document** | `PROJECT_EXPLAINED.md` (plain-language and technical description of every step) |

**Status key:** Done, In progress, Open, Blocked. **Priority key:** P1 = needed for the midterm, P2 = needed for the final project, P3 = nice to have.
**Owner column:** names are suggestions based on the slide split (A: slides 1 to 5, B: slides 6 to 9). Please confirm.

---

## 1. Summary

| Area | Status | Next action |
|---|---|---|
| Data cleaning and rules | Done | None |
| Labels (LEAD 1.0) | Done | None |
| Predictors | Done | None |
| Cut-offs and flags | Done | None |
| Evaluation (pre-set cut-offs and equal alarm rates) | Done | None |
| Combined notebook | Done and verified on real data | Push to GitHub |
| Midterm report | Drafted | Update wording, number check, export PDF |
| Presentation slides | Drafted | Update wording, number check, export PDF, rehearse |
| Final project extensions | Open | Plan after the midterm |

**Headline result (test period, 587 labeled events).** At 1% of hours flagged, the same-as-last-hour rule finds 38.7% of events and model C 35.1%, while the models without the previous hour find 18 to 21%. Detection is modest, and the output is a ranked list for a human to check.

---

## 2. Completed actions

### 2.1 Professor feedback

| ID | Feedback | Action taken | Status |
|---|---|---|---|
| F1 | Residual plus threshold is a standard method | Kept it. The contribution is the check against labeled events and the comparison of design choices | Done |
| F2 | No ground-truth validation | Added LEAD 1.0 labels and an event-by-event check | Done |
| F3 | Lag features were never tested | Compared feature sets A, B, C and a same-as-last-hour baseline | Done |
| F4 | Lag alignment | History built by time on a complete hourly table, verified against a timestamp lookup | Done |
| F5 | Data leakage | Time split first, fills from training rows only, month feature dropped | Done |
| F6 | Threshold calibration | Per-building error scores, cut-offs learned on validation and saved before test | Done (see I1) |
| F7 | Does history hide persistent anomalies? | Answered in part by recall by event length | In progress (see A12) |

### 2.2 Build work

| ID | Action | Result | Status |
|---|---|---|---|
| D1 | Clean the data and set the rules | 200 labeled buildings, site 0 converted to kWh, zero runs of 24+ hours treated as missing, complete hourly table | Done |
| D2 | Join LEAD labels and build events | 37,296 labeled hours, 5,811 events, grouped by length | Done |
| D3 | Build five predictors | Same as last hour, typical value, models A, B, C | Done |
| D4 | Set cut-offs on validation, freeze them, produce flags | One cut-off per predictor, saved in `cutoffs.json` before test | Done |
| D5 | Evaluate the flags at the pre-set cut-offs | Events found, precision, results by event length | Done |
| D6 | Add the equal-alarm-rate comparison | Fair comparison at 0.1% to 5% of hours flagged, two threshold modes | Done |
| D7 | Review the partner's cleaning notebook | Good parts folded into the combined notebook | Done |
| D8 | Combine Parts A to E and the partner's checks into one notebook | Ran on real data in about 1.5 minutes, 0 errors, all numbers reproduce | Done |
| D9 | Draft the report | Introduction to remaining work, in Claude Docs | Done (needs updates, see A2) |
| D10 | Draft the slides | 9 main slides, 4 backup slides, speaker notes with timing | Done (needs updates, see A3) |

---

## 3. Open actions: midterm (due tonight)

| ID | Priority | Action | Owner | Due | Depends on | Done when |
|---|---|---|---|---|---|---|
| A1 | P1 | Look at the notebook's own figures in `outputs/` | Barnnita | Mon 19 Oct, evening | None | Figures are readable and match the tables |
| A2 | P1 | Update the report to say "one notebook, run top to bottom" and name `Electricity_Anomaly_Detection_Midterm.ipynb` | Claude with Barnnita | Mon 19 Oct, evening | None | Report text matches the notebook; no result numbers change |
| A3 | P1 | Update the slides with the same wording (method slide and speaker notes) | Claude with Barnnita | Mon 19 Oct, evening | None | Slides match the notebook |
| A4 | P1 | Number check: compare every figure and table value in the report and slides with the CSVs in `outputs/` | Claude, then Barnnita spot-checks | Mon 19 Oct, evening | A2, A3 | Every number traced to a CSV; list of checked values kept |
| A5 | P1 | Wording check: no claims about waste, faults or savings; no overstated conclusions | Claude, then Barnnita | Mon 19 Oct, evening | A2, A3 | Wording rules pass |
| A6 | P1 | Fix old wording that says about 1,413 buildings (plan PDF and older Docs checklist) to say 200 labeled buildings | Barnnita | Mon 19 Oct, evening | None | No document says 1,413 for our data |
| A7 | P1 | Export the report to PDF and open it | Barnnita | Mon 19 Oct, 11:00 PM | A4, A5 | PDF layout checked page by page |
| A8 | P1 | Export the slides to PDF and open it | Barnnita | Mon 19 Oct, 11:00 PM | A4, A5 | PDF layout checked slide by slide |
| A9 | P1 | Submit notebook, report PDF and slides PDF | Barnnita | Mon 19 Oct, 11:59 PM | A7, A8 | Submission confirmed |

---

## 4. Open actions: presentation (Tuesday)

| ID | Priority | Action | Owner | Due | Depends on | Done when |
|---|---|---|---|---|---|---|
| A10 | P1 | Rehearse the talk with a timer (10 minutes) | Both | Tue 20 Oct, morning | A8 | Run-through finishes in 10 minutes or less |
| A11 | P1 | Prepare Q&A answers using the four backup slides (pre-set cut-offs, precision, label lengths, accuracy) | Both | Tue 20 Oct, morning | A10 | Each person can answer the likely questions below |
| A12 | P1 | Prepare a short answer on the professor's history question: the rule that copies the last hour finds 33% of events over 12 hours, model C finds 50% | Arpan | Tue 20 Oct, morning | None | Answer fits in 30 seconds |

**Likely questions to prepare:**
1. Why did the alarm rates differ on test? (Pooled scores have heavy tails. We found it after looking at test results, kept the frozen cut-offs and added an equal-rate comparison.)
2. Why is a simple rule as good as the model? (The previous hour carries almost all the information; the model adds weather and calendar.)
3. Are the labels reliable? (They are human judgments from plots, and LEAD derives from GEPIII.)
4. Does a flag mean waste? (No. It means unusual given context.)

---

## 5. Open actions: repository and teamwork

| ID | Priority | Action | Owner | Due | Depends on | Done when |
|---|---|---|---|---|---|---|
| R1 | P1 | Check `.gitignore` covers `ashrae-energy-prediction/` and large parquet files (`train.csv` 680 MB, `predictions.parquet` 53 MB, `flags.parquet` 21 MB) | Barnnita | Before first push | None | `git status` shows no large files |
| R2 | P1 | Push the combined notebook, `ACTION_POINTS.md`, `PROJECT_EXPLAINED.md`, small result tables and figures from `outputs/` | Barnnita | After A9 | R1 | Partner can clone and see them |
| R3 | P1 | Write a short `README.md` with the run instructions (edit the master settings cell, run top to bottom, about 1.5 minutes) | Barnnita | After A9 | R2 | A new reader can run the notebook |
| R4 | P2 | Move older notebooks into one `archive/` folder (partner's notebook, submitted version, `progress/` parts, `Untitled` copies) | Both | Before final project | R2 | One obvious notebook in the main folder |
| R5 | P2 | Agree who edits which part of the notebook, one person per part at a time | Both | Before final project | R2 | Rule written in the README |

---

## 6. Open actions: final project

Ordered by importance. Each item is a design choice that can be tested against the labels.

| ID | Priority | Action | Why | Done when |
|---|---|---|---|---|
| X1 | P2 | Choose the cut-off rule using validation labeled events (per building) | Current cut-offs use no labels; this may raise recall and removes the alarm-rate mismatch at its source | Rule chosen on validation only, frozen, then scored once on test |
| X2 | P2 | Add an Isolation Forest detector and compare it at equal alarm rates | The research question asks about the detector | Same table as Part E, with Isolation Forest added |
| X3 | P2 | Measure which hours inside an event are found (delay and share of event hours) | Today one flagged hour counts as finding the event | New table of delay and hour share |
| X4 | P2 | Add an explain-away step (holiday, weather, neighbouring buildings) | Reduces flags that have an ordinary explanation | Flags drop without losing labeled events |
| X5 | P2 | Replace confidence intervals with ones that group by building | Events in one building are related, so current intervals are too narrow | New intervals reported |
| X6 | P3 | Look for more labeled buildings | The file we hold labels 200 buildings (the paper describes about 1,413 meters) | Decision recorded |
| X7 | P3 | Run a second check with synthetic anomalies on CU-BEMS | Tests detection where truth is known | Known inserted anomalies scored |
| X8 | P3 | Test extra history features from the partner's notebook (2 and 3 hours back, 24-hour average) and a wider model-settings search | May help, but history beyond the previous hour added little so far | Reported as an extension, not a replacement |

---

## 7. Decisions

| ID | Decision | Reason |
|---|---|---|
| DEC1 | Keep the method frozen for the midterm | The reported numbers came from this method and a rerun reproduced them |
| DEC2 | Report both the pre-set cut-offs (Part D) and the equal alarm rates (Part E) | The first comparison was unfair to some methods; we say openly that this was found after seeing test results |
| DEC3 | Main focus is validating flags against labels; the history analysis is supporting evidence | Agreed framing for the report |
| DEC4 | Use the words "unusual given context" and "worth a human check"; never "waste", "fault" or "savings" | A flag is not proof of any cause |
| DEC5 | Work only on the 200 labeled buildings | Every number stays comparable to the labels |
| DEC6 | Do not mix numbers from the partner's notebook with ours | It runs on all 1,413 buildings and has different settings |

---

## 8. Risks and issues

| ID | Risk or issue | Impact | Mitigation | Owner |
|---|---|---|---|---|
| I1 | Alarm rates at the pre-set cut-offs were uneven on test (0.075% to 1.87% against a 0.5% target) | First comparison is unfair to some methods | Equal-alarm-rate comparison added; the frozen cut-offs were not changed; stated in report and slides | Done |
| I2 | Labels are human judgments and LEAD derives from GEPIII | Results show agreement with human labels, not independent truth | State the limit in report, slides and Q&A | Both |
| I3 | Only 200 buildings are labeled and events in one building are related | Confidence intervals are too narrow | State the limit; see X5 | Both |
| I4 | Small groups (for example 30 to 36 events in the Education-only view) | Differences of a few points are noise | Avoid ranking on small differences | Both |
| I5 | Time pressure before 11:59 PM | Errors in exported PDFs | Export early (A7, A8) and open the PDFs | Barnnita |
| I6 | The partner's notebook has no visible kBTU to kWh conversion for site 0 (as far as could be seen; code read, not run) | Site 0 would be on the wrong scale | Not used for results; confirm with the partner | Arpan |
| I7 | Large files could be pushed to GitHub | Slow or failed push | See R1 | Barnnita |