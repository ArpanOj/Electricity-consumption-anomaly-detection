# Notebooks: one file per task

Each notebook does one job. They run in order. Each one reads files written by the earlier ones and writes its own results into `OUT_DIR` (set in `config.py`; `outputs_split/` on this computer). Notebooks 13 to 17 write report-ready tables into `results/<step>/`. The frozen midterm results in `outputs/` are never touched.

All shared settings (file paths, split dates, rules) are in `config.py`. Edit that file only. Every notebook starts with `from config import *`.

| Run order | File | Data it works on | What it does | Writes |
| --- | --- | --- | --- | --- |
| 1 | `01_lead_labels_and_events.ipynb` | **LEAD** labels, matched to GEPIII readings | Keeps the labeled buildings, checks LEAD against GEPIII, marks zero runs, builds events by length | `labeled_building_ids.csv`, `lead_labels.parquet`, `lead_events.csv`, `table_events_*.csv` |
| 2 | `02_gepiii_data_checks.ipynb` | **GEPIII** readings | Duplicates, negatives, gaps, daily and weekly patterns, why history must be built by time | `table_data_checks.csv`, `eda_profiles.png` |
| 3 | `03_gepiii_predictors.ipynb` | **GEPIII** readings, weather, building facts | Hourly table, features, simple predictors, models A, B, C | `predictions.parquet`, `predictor_accuracy.csv` |
| 4 | `04_cutoffs_and_flags.ipynb` | Predictions and LEAD labels | Scores, one cut-off per predictor, frozen to files, flags | `cutoffs.json`, `flags.parquet` |
| 5 | `05_evaluation_against_events.ipynb` | Flags and LEAD events | Events found, run precision, recall by event length | `eval_summary_test.csv`, `eval_by_length_test.csv` |
| 6 | `06_equal_alarm_rates.ipynb` | Flags and LEAD events | Every method flags the same share of hours | `eval_equal_rate_*.csv` |
| 7 | `07_results_summary.ipynb` | Result tables | Prints all tables in one place and checks they match the midterm results in `outputs/` | nothing |
| 8 | `08_isolation_forest_and_intervals.ipynb` | Scores, flags, events | Isolation Forest (two variants), equal-alarm-rate recall with 95% intervals grouped by building, delay and hour share, check of per-building cut-offs | `flags_ext.csv.gz`, `cutoffs_iforest.json`, `eval_equal_rate_ci_ext.csv`, `eval_equal_rate_diff_ext.csv`, `eval_frozen_rules_test.csv` |
| 9 | `09_persistence_test.ipynb` | Flags and events from notebook 08 | Events found by event length, with 95% intervals; share of hours flagged at each position inside events over 12 h (the professor's question) | `persistence_*.csv`, `persistence_test.png` |
| 10 | `10_unmatched_flags.ipynb` | Flags, predictions, labels | Samples 30 flagged runs that touch no label and draws them; tags all unmatched runs (exactly zero, site-wide, near an event) | `unmatched_flags_review.pdf`, `unmatched_flags_review_sheet.csv`, `unmatched_runs_tagged.csv`, `flagged_runs_model_C_test.csv` |
| 11 | `11_cubems_hourly_series.ipynb` | One-minute CU-BEMS files in `data/cu_bems/` | Converts to hourly kWh per floor (hour valid only if every device has 45+ of 60 minutes); adds the 6-floor total (floors 1, 2, 3, 4, 5, 7; the published floor 6 file stops on 22 Oct 2019) | `data/cu_bems_hourly/cu_bems_hourly_wide.csv.gz`, `device_stats.csv` |
| 12 | `12_cubems_planted_test.ipynb` | Hourly CU-BEMS series | Trains Models A', B', C' and Isolation Forests, plants anomalies in the test period (20 random placements), evaluates at equal alarm rates | `results/cu_bems/` |
| 13 | `13_ranked_review_list.ipynb` | Flags and predictions from 03 and 08 | Describes every run of Model C flags in the test period and ranks them by peak score | `results/review_list/` |
| 14 | `14_permutation_importance.ipynb` | Features from 03 | Scrambles inputs of Model C on the validation hours to see which ones it relies on | `results/importance/` |
| 15 | `15_sitewide_filter.ipynb` | Flags and events | Tests removing hours where many buildings of a site are flagged together (not adopted) | `results/sitewide_filter/` |
| 16 | `16_complexity.ipynb` | Features from 03, predictions | Training time, prediction time and size of every method | `results/complexity/` |
| 17 | `17_leakage_checks.ipynb` | Features from 03, predictions, labels | Future-perturbation test, recomputed cut-offs, random-label test, placebo events | prints only |
| 18 | `18_report_tables_figures.ipynb` | Results of notebooks 05 to 17 | Builds the final report tables (CSV) and figures (PNG), one colour per method; recomputes nothing | `results/report/` |

Other folders: `label_excluded/` (notebook 03 with labeled hours left out of training; results in `results/label_excluded/`), `sensitivity/` (scripts for the design-choice checks; see its README; results in `results/sensitivity/`), `audit/` (the first stand-alone versions of the leakage scripts, superseded by notebook 17).

## First run (reproducing everything)
1. Put the raw files in `ashrae-energy-prediction/` (GEPIII and LEAD) and `data/cu_bems/` (CU-BEMS).
2. Run notebooks 01 to 06, then 08, 09 and 10, then 11 and 12, then 07, then 13 to 17, then 18. Notebook 03 is the slow one (about 25 minutes on a 2-core machine). The large result files (predictions, flags) are not kept in the project folder; they are rebuilt by notebooks 01 to 10 and are identical from run to run (a full rerun on 10 November reproduced every result file exactly).
3. Read the table at the end of notebook 07. Rows that depend only on the data should say `match`. Rows that depend on the three trained models may say `close`, which means within a small allowance, with the methods ranked the same way. If any row says `DIFFERENT` or the ranking changed, stop and check before building anything on top.
4. Notebooks 14, 16 and 17 rebuild the features of notebook 03 and train models again (a few minutes each). Timings in notebook 16 depend on the machine.

## Where the raw data and old files are
- Raw data: `ashrae-energy-prediction/` (`train.csv`, `weather_train.csv`, `building_metadata.csv` are GEPIII; `train_features.csv` is the labeled LEAD file).
- `Electricity_Anomaly_Detection_Midterm.ipynb`: the combined notebook the notebooks here were split from.
- `archive/old_notebooks/` and `archive/old_repo/`: earlier work, superseded by this folder. Do not quote numbers from it.
- `docs/`: the Master Document, the Plain English document and the Complete Task List (PDF copies); the living versions are online.

## For anything new
Put each new step in its own numbered notebook in this folder. Start it with `from config import *`, read the frozen results from `OUT_DIR`, and write only into its own `results/<step>/` folder.
