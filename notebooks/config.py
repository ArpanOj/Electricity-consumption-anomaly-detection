"""Shared settings for every notebook in this folder.
Edit THIS file only if a path or a rule changes. Every notebook starts with:  from config import *
"""
from pathlib import Path
import json, time, datetime, gc
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ---- folders ----
ROOT = Path(__file__).resolve().parent.parent          # the Project folder (one level above notebooks/)
DATA = ROOT / "ashrae-energy-prediction"               # the raw GEPIII and LEAD files

# ---- raw data files (CHANGE only if your files have other names) ----
GEPIII_TRAIN   = str(DATA / "train.csv")                    # GEPIII hourly readings
GEPIII_META    = str(DATA / "building_metadata.csv")        # GEPIII building facts
GEPIII_WEATHER = str(DATA / "weather_train.csv")            # GEPIII weather
LEAD_FILE      = str(DATA / "train_features.csv")           # the labeled LEAD 1.0 file

# ---- where this set of notebooks writes its results ----
# "outputs_split" keeps the midterm results in "outputs" untouched.
# Notebook 07 compares the two. Change to ROOT / "outputs" only when you want to replace the midterm files.
OUT_DIR = ROOT / "outputs_split"
OUT_DIR.mkdir(parents=True, exist_ok=True)
MIDTERM_DIR = ROOT / "outputs"                           # the frozen midterm results (read only)
RESULTS = ROOT / "results"                         # one subfolder per new step (results/step_T23, ...); never write into outputs/

# ---- time split (one cut in time for every building and every model) ----
GRID_START = pd.Timestamp("2016-01-01 00:00")
GRID_END   = pd.Timestamp("2016-12-31 23:00")
TRAIN_END  = pd.Timestamp("2016-09-13")      # train: before this
VAL_END    = pd.Timestamp("2016-11-07")      # validation: up to here; test: from here

# ---- data rules ----
ZERO_RUN_HOURS = 24            # a run of exact zeros this long is treated as missing, not as real low use
CONVERT_SITE0_TO_KWH = True    # GEPIII site 0 is in kBTU; LEAD stores it in kWh
KBTU_TO_KWH = 0.2931

# ---- which period the evaluation notebooks (05 and 06) score ----
EVAL_SPLIT = "test"            # "test" for the final numbers, "val" while exploring

T_START = time.time()
print("settings loaded | data:", DATA, "| results go to:", OUT_DIR)
