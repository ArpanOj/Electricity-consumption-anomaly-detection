# Label-excluded training (task T40)
`03_gepiii_predictors_label_excluded.ipynb` is notebook 03 with one change: hours that LEAD labels as anomalous are left out when the models A, B, C are trained and when the typical-value baseline is computed.
To run it: in `config.py` set `OUT_DIR = ROOT / "outputs_nolabel"`, copy `labeled_building_ids.csv`, `labeled_buildings_info.csv`, `lead_events.csv` and `lead_labels.csv.gz` from `outputs_split/` into `outputs_nolabel/`, run this notebook, then notebooks 04, 05 and 06. Results from our run are in `results/label_excluded/`.
