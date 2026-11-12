#!/bin/bash
cd /home/claude/rerun/ProjectVar
F="04_cutoffs_and_flags 05_evaluation_against_events 06_equal_alarm_rates"
./make_run.sh rawscale 's/USE_LOG = True /USE_LOG = False/' '' "$F"
./make_run.sh floor002 's/MAD_FLOOR = 0.05 /MAD_FLOOR = 0.02 /' '' "$F"
./make_run.sh floor010 's/MAD_FLOOR = 0.05 /MAD_FLOOR = 0.10 /' '' "$F"
ALL="01_lead_labels_and_events 02_gepiii_data_checks 03_gepiii_predictors $F"
./make_run.sh zr12 '' 12 "$ALL"
./make_run.sh zr48 '' 48 "$ALL"
echo ALL_END >> chain.log
