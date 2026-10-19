# Electricity Consumption Anomaly Detection: Project Status and Action Points

Course: AT82.01 Computer Programming for Data Science and AI (Dr. Chantri Polprasert)
Team: Barnnita Shrestha, Arpan Ojha
Last updated: Mon 19 Oct 2026 (midterm deadline: Mon 19 Oct, 11:59 PM; presentation: Tue 20 Oct, 10 min + 5 min Q&A)

---

## 1. The project in one minute

**Question we answer.** How well do residual-based flags from an expected-consumption model match labeled anomalies in building electricity data, and which design choices (features, threshold, detector) improve that match?

**What "anomaly" means here.** Use that is unusual given its context (hour, weekday, weather, building). It is not proof of waste, a fault or a saving. The output is a ranked list of periods worth a human check.

**How it works.**
1. Predict what each building should use in each hour.
2. Compare the real reading with the prediction. A large gap gets a high score.
3. Flag hours whose score is above a cut-off.
4. Check the flags against hours that people labeled as anomalous (LEAD 1.0 labels).

**The story our results tell (one sentence).** Detection quality depends strongly on design choices: the previous hour matters most, longer history (yesterday, last week) adds almost nothing, how the threshold is set matters a lot for predictors without the previous hour, and a same-as-last-hour baseline is hard to beat.

---

## 2. Where everything lives

| What | File or folder |
|---|---|
| **The notebook (use this one)** | `Electricity_Anomaly_Detection_Midterm.ipynb` |
| Results the notebook writes | `outputs/` (tables as CSV, figures as PNG) |
| Data (not pushed to GitHub) | `ashrae-energy-prediction/` (train.csv, building_metadata.csv, weather_train.csv, train_features.csv) |
| Earlier separate notebooks (kept for the record) | `progress/` (Parts A to E), `Electricity_comsumption_anomaly_detection.ipynb` (submitted version), `Mid-progress.ipynb` (partner's cleaning notebook), `outputs_progress/` (partner's outputs) |
| Midterm report | Claude Docs artifact "Midterm Progress Report: Anomaly Flags Checked Against Labeled Events" |
| Presentation | Claude Slides artifact (9 slides plus 4 backup slides) |

**How to run the notebook.** Edit only the "Master settings" cell (file paths), then run all cells from top to bottom. It takes about 1.5 minutes on the real data. Each part saves its files and the next part reads them, so any part can be re-run alone.

---

## 3. What has been done

### 3.1 Feedback from the professor: all seven points handled

| Comment | What we did | Status |
|---|---|---|
| Residual plus threshold is a standard method | Kept it. Our contribution is the check against labeled events and the comparison of design choices | Done |
| No ground-truth validation | Added LEAD 1.0 labels and a check event by event | Done |
| Lag features never tested | Compared feature sets A, B, C and a same-as-last-hour baseline | Done |
| Lag alignment | History is built by time on a complete hourly table, and verified against a timestamp lookup | Done |
| Data leakage | Time split first, all fills from training rows only, month feature dropped | Done |
| Threshold calibration | Per-building error scores, cut-offs learned on validation and saved before test | Done, with a finding (see 3.5) |
| Does history hide persistent anomalies? | Partly answered by results by event length. Long events are found less by the rule that copies the last hour | In progress |

### 3.2 Data cleaning and rules

- **Electricity only** (meter 0), for the **200 buildings** that LEAD labels.
- **Units.** GEPIII site 0 is stored in kBTU and LEAD in kWh, so site 0 is converted (multiply by 0.2931).
- **Checks.** 0 duplicates, 0 negatives, 0 missing readings. About 4.0% of readings are exact zeros.
- **Zero runs.** 24 or more hours of exact zeros in a row are treated as missing (a meter problem, not real low use). Short zero runs stay.
- **Complete hourly table.** Every building crossed with every hour of 2016 (8,784 hours). Missing hours stay empty and are never invented.
- **Why this matters.** 0.074% of consecutive rows are not one hour apart. A row-based 24-hour lag would be wrong in 0.89% of rows. Building history by time removes that error.
- **Weather.** Filled forward only (never backward), so no future information is used.
- **One cut in time.** Train: before 13 Sep 2016. Validation: 13 Sep to 6 Nov. Test: from 7 Nov. Everything learned uses training or validation rows only.

### 3.3 The labels (LEAD 1.0)

- 200 labeled buildings, 1,749,494 hourly rows, 37,296 labeled hours (2.1% of hours), 5,811 events.
- Events by length: 2,780 of 1 hour, 906 of 2 to 3 hours, 1,302 of 4 to 12 hours, 823 over 12 hours.
- Test period: 587 usable events (212 / 92 / 185 / 98 by length; 173 in Education buildings).
- Limits: labels come from people inspecting plots, and LEAD comes from the same source as GEPIII, so this is a check against human judgment, not an independent truth.

### 3.4 The six methods compared

| Method | What it is |
|---|---|
| Same as last hour | Predict the previous hour's reading. No training |
| Historical typical value | Training median for the same building, hour and weekday-or-weekend |
| Model A | Tree model (HistGradientBoosting): calendar, building facts, weather, **no history** |
| Model B | Model A plus use at the same hour yesterday and last week |
| Model C | Model B plus the previous hour |
| Fixed percentile | Flag use above the 99.5th percentile of the building's own training use (simple comparison method) |

All models use identical settings and the same training rows. Model settings are pinned (600 iterations, learning rate 0.05, 127 leaves, 100 samples per leaf, L2 1.0).

### 3.5 Results (test period, 587 events)

**Accuracy of the predictors.** Same as last hour and Model C are tied (R squared 0.993). Typical value and Model A are lowest (0.958 and 0.955). Accuracy alone does not rank detectors.

**Flags at the pre-set cut-offs (events found).** Same as last hour 29.1%, Model C 29.0%, fixed percentile 7.2%, Model B 3.4%, Model A 1.5%, typical value 1.4%. Alarm rates on normal hours were uneven (0.075% to 1.87% against a 0.5% target).

**The finding that led to Part E.** The pooled cut-offs did not carry over equally from validation to test, so the first comparison was not fair. We found this after looking at test results. We did not change the frozen cut-offs. We added a second comparison at equal alarm rates and report both.

**Equal alarm rates, 1% of hours flagged (events found, each building / one shared threshold).**

| Method | Each building | Shared |
|---|---|---|
| Same as last hour | 38.7% | 37.6% |
| Model C | 35.1% | 33.2% |
| Typical value | 20.8% | 4.8% |
| Model B | 18.2% | 10.2% |
| Model A | 17.9% | 5.6% |
| Fixed percentile | 8.7% | 1.7% |

**Reading the results.**
- The previous hour roughly doubles recall at equal alarm rates (35 to 39% against 18 to 21%).
- Yesterday and last week add almost nothing (Model B is no better than Model A).
- The way the threshold is set matters a lot for predictors without the previous hour.
- Same as last hour matches Model C overall, wins on short events (1 to 3 hours), Model C wins on events over 12 hours (50% against 33%).
- Detection is modest: about 4 in 10 events at 1% of hours flagged, 53 to 60% at 5%.
- Precision is low (about 10 to 18% of flagged runs fall on labeled events, against a base rate of about 2% of hours). The output is a ranked list for a human to check.

### 3.6 Deliverables built so far

- **Notebooks.** Parts A to E, now combined into one notebook that was run on the real data (0 errors, all numbers reproduce).
- **Report** (Claude Docs): introduction, feedback summary, methodology, experiments and results, earlier results and known issues, limitations, remaining work.
- **Slides** (Claude Slides): 9 main slides and 4 backup slides, with speaker notes, timing and a Person A / Person B split (A: slides 1 to 5, B: slides 6 to 9).
- **Partner's cleaning notebook.** Reviewed. Its good parts (basic checks, daily and weekly plots, the row-lag check, zero-run plot) were folded into the combined notebook.

---

## 4. What is left to do

### 4.1 Tonight (before the 11:59 PM deadline)

1. **Update the report and slides** to say "one notebook, run top to bottom" and point to `Electricity_Anomaly_Detection_Midterm.ipynb`. No result numbers change, because the rerun reproduced them.
2. **Number check.** Compare every figure and table value in the report and slides against the CSVs in `outputs/`. Check wording: no claims about waste or savings, no overstated conclusions.
3. **Look at the figures** in `outputs/` (the notebook's own PNGs) and confirm they are readable.
4. **Export to PDF** and open the PDFs to check layout. The report exports from Docs, the deck from Slides.
5. **Submit** the notebook, the report PDF and the slides PDF.
6. **Fix old wording.** The plan PDF and the older Docs checklist still say about 1,413 buildings. It should say 200 labeled buildings.

### 4.2 Tuesday 20 Oct: the presentation

1. Rehearse with a timer: 10 minutes, Person A on slides 1 to 5, Person B on slides 6 to 9.
2. Prepare for Q&A using the backup slides (pre-set cut-offs, precision, label lengths, accuracy).
3. Be ready to say plainly: detection is modest, the alarm-rate problem was found after seeing test results, and labels are human judgments.

### 4.3 Repository and teamwork (when pushing to GitHub)

1. **Do not push the data or the large output files.** `train.csv` is 680 MB. `outputs/predictions.parquet` is 53 MB and `outputs/flags.parquet` is 21 MB. Check `.gitignore` covers `ashrae-energy-prediction/` and the large parquet files.
2. **Push:** the combined notebook, the small result tables and figures in `outputs/`, this file, and a short README with the run instructions in section 2.
3. **Move older work** into one folder (for example `archive/`) so there is one obvious notebook to open: the partner's notebook, the submitted version, the `progress/` parts, the duplicate `Untitled` notebooks.
4. **Agree who edits what** in the notebook to avoid merge conflicts: keep one person per part at a time.

### 4.4 After the midterm: the final project

Listed from most to least important. Each item is a design choice we can test against the labels.

1. **Choose the cut-off rule using validation labels.** Today cut-offs are set without labels. A per-building rule chosen on validation labeled events could raise recall. This also removes the alarm-rate mismatch at its source.
2. **Isolation Forest comparison.** The research question asks about the detector. Add one unsupervised detector and compare it at equal alarm rates.
3. **Which hours inside an event are found.** Today an event counts as found if one hour is flagged. Measure the delay and the share of event hours found.
4. **Explain-away step.** Check whether a flag is explained by something else (holiday, weather, nearby buildings), and drop it from the ranked list if so.
5. **Wider intervals.** Our confidence intervals are too narrow because events in one building are related. Use intervals that group by building.
6. **Fuller LEAD labels.** The file we hold labels 200 buildings (the paper describes about 1,413 meters). Check whether more labeled buildings can be obtained.
7. **Second check with synthetic anomalies (CU-BEMS).** Insert known anomalies into a second dataset and see which method finds them.
8. **Ideas from the partner's notebook** worth testing: extra history features (2 and 3 hours back, 24-hour average), and a wider search of model settings. Test them as extensions, not as replacements.

---

## 5. Decisions we made (so we do not argue about them later)

- **Keep the method frozen for the midterm.** The combined notebook uses exactly what produced the reported results.
- **Report both comparisons.** Pre-set cut-offs (Part D) and equal alarm rates (Part E), with the reason for adding the second one stated openly.
- **Primary focus:** validating flags against labels. The study of how much history helps is supporting evidence.
- **Wording.** We say "unusual given context" and "worth a human check". We do not say "waste", "fault" or "savings".
- **Work on the 200 labeled buildings only**, so every number is comparable to the labels.

## 6. Known issues and honest limits

- Alarm rates at the pre-set cut-offs were uneven on test. Found after looking at test results. The equal-rate comparison is an added analysis.
- Labels are human judgments and LEAD derives from GEPIII (not independent).
- Only 200 buildings are labeled, and events in one building are related, so intervals are optimistic.
- Some length groups are small in the Education-only view (for example 30 to 36 events), so differences of a few points are noise.
- The partner's notebook runs on all 1,413 buildings and, as far as I could see, has no kBTU to kWh conversion for site 0. Do not mix its numbers with ours.
- The old submission-stage numbers (R squared 0.968 with row-position history and a global threshold) are kept in the report only as a record of what was fixed.