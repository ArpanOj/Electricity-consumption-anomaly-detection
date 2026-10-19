# The Project Explained: Plain Language First, Technical Detail Underneath

Each numbered point says what we did in plain words. The sub-points under it give the technical description, with the exact settings and numbers.

Main notebook: `Electricity_Anomaly_Detection_Midterm.ipynb`. Action list: `ACTION_POINTS.md`.

---

## 1. What we are trying to find out

**Plain language.** Buildings use electricity in patterns. Sometimes use is strange for the moment: a building that should be quiet at night is busy, or the reverse. We build a tool that points to strange hours, then check how many of the hours that people had already marked as strange our tool also points to.

- 1.1 **Research question.** How well do residual-based flags from an expected-consumption model match labeled anomalies in building electricity data, and which design choices (features, threshold, detector) improve that match?
- 1.2 **Definition of anomaly.** Use that is unusual given its context (hour, weekday, weather, building). It is not proof of waste, a fault or a saving.
- 1.3 **Output.** A ranked list of periods worth a human check, not a list of confirmed problems.
- 1.4 **Method family.** Residual-based detection: predict expected use, take the residual (actual minus expected), score it, flag large scores. This method is standard, so our contribution is the validation against labels and the comparison of design choices.

---

## 2. The data we use

**Plain language.** We use hourly electricity readings from many university buildings during 2016, plus a list of hours that people marked as anomalous. We also use weather and basic building facts.

- 2.1 **GEPIII (ASHRAE Great Energy Predictor III).** Hourly meter readings, building metadata and weather. We use electricity only (meter 0), file `train.csv`, together with `building_metadata.csv` and `weather_train.csv`.
- 2.2 **LEAD 1.0 labels.** Anomaly labels from human inspection of plots, file `train_features.csv`. LEAD derives from GEPIII, so the labels are a check against human judgment, not an independent truth.
- 2.3 **Scope.** 200 labeled buildings, 1,749,494 hourly rows, 37,296 labeled hours (2.1% of hours), 5,811 events.
- 2.4 **Events by length.** 2,780 events of 1 hour, 906 of 2 to 3 hours, 1,302 of 4 to 12 hours, 823 over 12 hours. Labeled hours by length: 2,780 / 2,284 / 9,111 / 23,121.
- 2.5 **Why only 200 buildings.** Only these buildings carry labels. Restricting to them keeps every number comparable to the labels. (An earlier plan document said about 1,413 buildings; that is the number in the LEAD paper, not in the file we hold.)

---

## 3. Cleaning the data so it can be trusted

**Plain language.** Before predicting anything, we fix problems that would mislead us: different units, meters that were switched off, and missing hours.

- 3.1 **Basic checks.** Duplicates, negative readings and missing readings: 0 found in the labeled buildings. About 4.0% of readings are exact zeros.
- 3.2 **Units.** GEPIII site 0 is stored in kBTU; LEAD stores kWh. Site 0 readings are multiplied by 0.2931.
- 3.3 **Zero runs.** A run of 24 or more consecutive exact zeros is treated as missing (a meter or data problem, not real low use). Shorter runs of zeros stay. The same rule is used in the labels part and the predictor part so the hours match.
- 3.4 **Complete hourly table.** Every building crossed with every hour of 2016 (8,784 hours, because 2016 is a leap year). Hours with no reading stay empty and are never invented.
- 3.5 **Weather.** Filled forward in time only, so a value never comes from the future. Building facts that are empty everywhere in training are dropped automatically (for example floor count).
- 3.6 **Features dropped on purpose.** The month feature is removed because the test months never appear in training.

---

## 4. Splitting time fairly

**Plain language.** To test honestly, the tool must be built using the past and judged on the future. We cut the year into three consecutive blocks and never let information flow backwards.

- 4.1 **Split dates.** Train: before 13 Sep 2016. Validation: 13 Sep to 6 Nov. Test: from 7 Nov. One cut for every building and every model.
- 4.2 **What each block is for.** Train: fit models and typical values. Validation: choose settings and cut-offs. Test: report final numbers only.
- 4.3 **Leakage rule.** Every fill value, typical value, model and error scale is learned from training or validation rows only. The earlier submission filled missing values with medians over the whole dataset, which leaked future information; that was removed.
- 4.4 **Test usage.** Cut-offs are written to files before the test block is scored. They are not changed afterwards.

---

## 5. Giving the tool a memory: history features

**Plain language.** Electricity use is repetitive, so the best clue to what a building uses now is what it used just before, a day ago, or a week ago. We test how much each of these clues helps.

- 5.1 **History values.** Use 1 hour earlier, 24 hours earlier and 168 hours earlier (same hour last week), on the log scale `log(1 + kWh)`, built from the cleaned reading.
- 5.2 **Why time-based and not row-based.** Some hours are missing, so shifting by 24 rows can reach back more than 24 hours. In our data, 0.074% of consecutive rows are not exactly one hour apart, and a row-based 24-hour lag would be wrong in 0.89% of rows. Because the complete hourly table has one row per building per hour, a shift of k rows equals k hours.
- 5.3 **Verification.** The notebook looks the lag up again by timestamp and compares. Every value must match, otherwise the run stops.
- 5.4 **Empty history.** Zero-run hours and missing hours give empty history, and predictions that need that history are left empty rather than guessed.

---

## 6. The six ways we guess what a building should use

**Plain language.** We compare simple guesses with smarter guesses. The simplest guess is "same as an hour ago". The smartest uses the calendar, the weather and the recent past.

- 6.1 **Same as last hour.** Prediction = the previous hour's reading. No training. This sets the bar any model must beat.
- 6.2 **Historical typical value.** Training median for the same building, hour of day and weekday-or-weekend. Falls back to building and hour, then to the building.
- 6.3 **Model A.** HistGradientBoosting on `log(1 + kWh)` with calendar (hour, day of week, weekend), building facts (size, use type, site) and weather (air temperature, dew temperature, wind speed and more). No history.
- 6.4 **Model B.** Model A plus use at the same hour yesterday and last week.
- 6.5 **Model C.** Model B plus the previous hour.
- 6.6 **Fixed percentile (comparison method).** Flag any hour where use is above the 99.5th percentile of that building's own training use. No prediction involved.
- 6.7 **Same settings for A, B, C.** Identical model settings and identical training rows, so only the features differ. Settings are pinned: 600 iterations, learning rate 0.05, 127 leaves, 100 samples per leaf, L2 1.0 (chosen earlier by light tuning on validation with model C).
- 6.8 **Accuracy on test.** Same as last hour: R squared 0.993, log error 0.200. Model C: 0.993 and 0.227. Model B: 0.978 and 0.441. Typical value: 0.958 and 0.699. Model A: 0.955 and 0.705. Accuracy alone does not rank detectors: the simple rule is as accurate as the best model.

---

## 7. Turning a gap into a score, and a score into a flag

**Plain language.** A big miss on a quiet building matters more than the same miss on a huge building, so we measure each miss against that building's own usual miss size. Then we pick a line: scores above the line become flags.

- 7.1 **Error.** Measured on the log scale: log(1 + actual) minus log(1 + predicted).
- 7.2 **Per-building normal error.** From clean validation hours (no label, valid reading), take each building's median error and its scaled MAD (median absolute deviation times 1.4826), with a floor of 0.05.
- 7.3 **Score.** `|error - median| / scale`, so every building is on the same footing.
- 7.4 **Buildings with little validation data.** Buildings with fewer than 500 clean validation hours borrow values from similar buildings (same site and use, then the site, then everyone). This affected 4 buildings.
- 7.5 **One cut-off per predictor.** Set at the 0.5% quantile of clean validation scores, so about 0.5% of normal hours would be flagged.
- 7.6 **Freezing.** The cut-offs, the per-building values and the fixed-percentile thresholds are saved to files (`cutoffs.json`, `cut_building_values.csv`, `cut_fixed_thresholds.csv`) before any test scoring. Flags for validation and test are then produced from those saved files only.
- 7.7 **Check.** The notebook confirms the files were written before the flags were made.

---

## 8. Checking the flags against the labeled events

**Plain language.** We ask two questions: how many of the marked events does the tool catch, and how many of its alarms land on marked events? Because about 2% of hours are marked, a random alarm would be right about 2% of the time.

- 8.1 **Event recall (events found).** An event counts as found if at least one hour inside it is flagged.
- 8.2 **Flagged runs.** Consecutive flagged hours form one run. Run precision = share of runs that touch a labeled event. Hour precision = share of flagged hours that are labeled.
- 8.3 **Precision at 50 and 100.** Precision among the 50 or 100 highest-scoring runs, which matters when a person reviews a short list.
- 8.4 **By event length.** Recall is reported separately for 1 hour, 2 to 3 hours, 4 to 12 hours and over 12 hours, and for Education buildings alone.
- 8.5 **Usable events.** Events mostly inside zero runs are dropped (same rule as before). The test period has 587 usable events (212 / 92 / 185 / 98 by length; 173 in Education).
- 8.6 **Intervals.** Wilson 95% intervals are shown, but they are too narrow because events in one building are related.
- 8.7 **A detail to remember.** The same-as-last-hour rule flags the start of an event and the hour after its end, because the reading jumps twice.

---

## 9. Results at the pre-set cut-offs

**Plain language.** With the lines we drew on validation, only two methods catch a meaningful share of events: same as last hour and model C. The others catch very few. But the lines gave unequal numbers of alarms on test, so this comparison is not fair to every method. That is why we did a second comparison.

- 9.1 **Events found (all buildings, 587 events).** Same as last hour 29.1%, model C 29.0%, fixed percentile 7.2%, model B 3.4%, model A 1.5%, typical value 1.4%.
- 9.2 **Alarm rates on normal test hours** (target 0.5%): same as last hour 0.35%, model C 0.48%, typical 0.075%, model A 0.077%, model B 0.106%, fixed 1.87%.
- 9.3 **Precision at 50 flags.** Model C 72%, same as last hour 54%, fixed percentile 28%, model B 22%, typical 14%, model A 12%.
- 9.4 **Why the rates differ.** Pooled scores have heavy tails, so a validation quantile did not carry over to test for the weaker predictors.
- 9.5 **How we handled it.** The frozen cut-offs were not changed. The problem was found after looking at test results, and the report and slides say so.

---

## 10. The fair comparison at equal alarm rates

**Plain language.** To compare methods fairly, we let each one raise the same number of alarms and see who catches more events. We do this at several alarm budgets, and in two ways: one shared line for all buildings, or each building flagging its own top hours.

- 10.1 **Alarm rates.** 0.1%, 0.25%, 0.5%, 1%, 2% and 5% of valid hours. The report rate is 1%.
- 10.2 **Two modes.** Pooled: one global threshold per method. Per building: each building flags its top share of hours by percentile rank.
- 10.3 **No labels used.** Thresholds are set from scores only, so the comparison does not tune on the answers.
- 10.4 **Result at 1% of hours (events found, per building / pooled).** Same as last hour 38.7 / 37.6. Model C 35.1 / 33.2. Typical value 20.8 / 4.8. Model B 18.2 / 10.2. Model A 17.9 / 5.6. Fixed percentile 8.7 / 1.7.
- 10.5 **Result at 5% of hours.** Model C 59.8% and same as last hour 52.6% (per building).
- 10.6 **Precision at 1%.** About 10 to 18% of flagged runs touch a labeled event, against a base rate near 2% of hours.

---

## 11. What the results tell us

**Plain language.** The hour just before is by far the most useful clue. Looking back a day or a week adds almost nothing. A very simple rule is as good as a machine-learning model overall. How the line is drawn matters a lot for the weaker methods. Detection is modest, so the output should be treated as a short list for a person to look at.

- 11.1 **The previous hour roughly doubles recall** at equal alarm rates (35 to 39% against 18 to 21%).
- 11.2 **Longer history adds almost nothing.** Model B is no better than model A.
- 11.3 **Threshold design matters** for predictors without the previous hour: pooled recall for typical value, model A and model B is 5 to 10%, while per building it is 18 to 21%.
- 11.4 **Persistence is hard to beat.** Same as last hour is slightly ahead of model C overall (within noise).
- 11.5 **By event length (1%, per building).** 1 hour: same as last hour 40.6% against model C 25.5%. 2 to 3 hours: 52.2% against 45.7%. 4 to 12 hours: tied at 33.0%. Over 12 hours: model C 50.0% against same as last hour 32.7%. A rule that copies the last hour treats a long event as normal after its first hour, which answers the professor's question about history hiding persistent anomalies.
- 11.6 **Limits on these numbers.** Small groups are noisy (for example 30 to 36 events in the Education-only view), labels are human judgments, and intervals are too narrow.

---

## 12. How we fixed the first submission

**Plain language.** The first version had four problems that made its numbers look better than they were. We fixed each one.

- 12.1 **Median fill before the split.** Test information leaked into training. Now the split comes first and fills use training rows only.
- 12.2 **History by row position.** Shifted rows, not hours. Now history is built by time on a complete hourly table and verified.
- 12.3 **One cut-off for all buildings, set on the data it was used on.** Now scores are per building, and cut-offs come from validation and are saved before test.
- 12.4 **R squared 0.968 as the headline.** High accuracy is not detection. That number is kept only as a record of the submission stage. The new test shows a trivial same-as-last-hour rule reaches 0.993.

---

## 13. How the project is organized and how to run it

**Plain language.** There is one notebook that does everything from the raw files to the final tables. You change the file paths once, press run all, and wait about a minute and a half.

- 13.1 **Notebook.** `Electricity_Anomaly_Detection_Midterm.ipynb`, built from Parts A to E plus a data-checks section.
- 13.2 **Parts.** A: labels and events. Checks: duplicates, plots, row-lag error. B: hourly table and predictors. C: cut-offs and flags. D: evaluation at the pre-set cut-offs. E: equal-alarm-rate comparison.
- 13.3 **Settings.** One master settings cell holds the paths, split dates and rules. Each part also has a small settings cell for its own options.
- 13.4 **Restartable.** Each part saves its files and the next part reads them, so any part can be re-run alone. A memory-freeing cell runs between parts.
- 13.5 **Verified.** The notebook was run on the real data: 131 cells, 0 errors, total run time about 1.5 minutes, and every number matches the report.
- 13.6 **Main outputs** (in `outputs/`): `predictor_accuracy.csv`, `cutoffs.json`, `eval_summary_test.csv`, `eval_by_length_test.csv`, `eval_equal_rate_summary_test.csv`, `eval_equal_rate_by_length_test.csv`, `eval_equal_rate_test.csv`, plus figures.
- 13.7 **Partner's notebook.** Reviewed. Its basic checks, plots and row-lag measurement were folded in. Its numbers are not used because it runs on all 1,413 buildings with different settings.

---

## 14. What we can still do

**Plain language.** The midterm shows that the previous hour is the key clue and that detection is modest. The final project can try to improve detection and to make the claims stronger.

- 14.1 **Choose the cut-off rule using validation labels.** Per building, frozen before test.
- 14.2 **Compare an Isolation Forest.** Answers the "which detector" part of the research question.
- 14.3 **Measure which hours inside an event are found.** Delay and share of event hours.
- 14.4 **Add an explain-away step.** Holidays, weather, neighbouring buildings.
- 14.5 **Use intervals that group by building.** To fix the narrow intervals.
- 14.6 **Look for more labeled buildings and run a synthetic check on CU-BEMS.** A second dataset where the truth is known.
- 14.7 **Test extra history features** from the partner's notebook (2 and 3 hours back, 24-hour average) as an extension.

---

## 15. Honest limits

**Plain language.** The labels are people's opinions, not facts. We have 200 labeled buildings. Our best result still misses about six in ten labeled events at 1% of hours flagged. A flag is a reason to look, not a finding.

- 15.1 **Labels.** Human judgment from plots; LEAD derives from GEPIII.
- 15.2 **Sample.** 200 buildings; events in one building are related.
- 15.3 **Order of discovery.** The unequal alarm rates were found after looking at test results.
- 15.4 **Interpretation.** Low precision (about 10 to 18% of flagged runs) means flags need a human check.
- 15.5 **Wording.** We say "unusual given context" and "worth a human check", and never "waste", "fault" or "savings".