# Unusual electricity use in university buildings
AT82.01 Computer Programming for Data Science and AI, AIT. Barnnita Shrestha and Arpan Ojha. Instructor: Dr. Chantri Polprasert.

We flag hours in which a building's electricity use is unusual for that building at that time, and measure how well the flags match labeled events
(GEPIII/LEAD, 200 buildings) and problems we planted (CU-BEMS). Full explanation: the Project Master Document (not stored here).

## Folder map
| Folder / file | What it is |
| --- | --- |
| notebooks/ | The pipeline: 18 numbered notebooks, config.py (all settings), README.md (run order). Extras: label_excluded/, sensitivity/, audit/ |
| Electricity_Anomaly_Detection_Midterm.ipynb | The frozen midterm notebook (never edited) |
| outputs/ | Frozen midterm results |
| outputs_split/ | Written by notebooks 01 to 10 (empty until you run them) |
| results/ | Results of notebooks 11 to 18 and later checks; results/report/ holds the final tables and figures |
| data/ | CU-BEMS raw (download, see data/cu_bems/README.md) and hourly files |
| ashrae-energy-prediction/ | GEPIII and LEAD files (download from Kaggle, not in git) |
| docs/ | Course requirements, notes; superseded_9Nov2026/ holds outdated PDFs |
| archive/ | Old material, not in git |
| requirements.txt | Python packages |

## How to run
1. `pip install -r requirements.txt`
2. Put the data in place (ashrae-energy-prediction/ and data/cu_bems/).
3. Run notebooks/01 to 12 in order, then 13 to 17, then 18 (details in notebooks/README.md). Notebook 03 is the slow one.
4. Do not edit outputs/ (frozen midterm).
