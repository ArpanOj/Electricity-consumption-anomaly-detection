# Sensitivity runs (12 November 2026)

These scripts rerun the cut-off, evaluation and equal-alarm-rate steps (notebooks 04-06) with one design choice changed at a time, then compare with the reported results. They were written for the cloud copy of the project (paths start with /home/claude/rerun/); change the paths at the top before using them on another machine.

| Variant | What changes | Notebooks rerun |
| --- | --- | --- |
| nolabelexcl | labeled validation hours are not excluded when learning m, s and the cut-offs (two lines in notebook 04) | 04, 05, 06 |
| rawscale | errors measured in raw kWh instead of log(1 + kWh) (`USE_LOG = False`) | 04, 05, 06 |
| floor002, floor010 | smallest allowed building variation 0.02 or 0.10 instead of 0.05 (`MAD_FLOOR`) | 04, 05, 06 |
| zr12, zr48 | zero runs of 12 or 48 hours (instead of 24) are treated as missing (`ZERO_RUN_HOURS`) | 01 to 06 (retrains the models, about 25 minutes each) |

- `make_run.sh NAME "sed expression" "zero-run hours" "notebooks"` builds one variant in its own folder, with a copy of the notebooks and the results, and runs the listed notebooks with `run_split.py` (runs every code cell of a notebook in order).
- `all.sh` runs all variants in a row. `summarize.py` prints and saves one table with the reported run and every variant side by side (`sensitivity_variants_summary.csv`).
- Results are summarised in `results/sensitivity/` and in master section 20.15 and 20.16.
