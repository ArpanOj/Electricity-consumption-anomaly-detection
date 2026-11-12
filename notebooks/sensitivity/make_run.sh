#!/bin/bash
# usage: make_run.sh NAME "sed-expr for nb04 or ''" "ZR hours or ''" "notebooks to run"
set -e
cd /home/claude/rerun/ProjectVar
N=$1; ED=$2; ZR=$3; NBS=$4
rm -rf $N && mkdir $N && cp -r ../ProjectFull/notebooks $N/ && cp -r ../ProjectFull/outputs_full $N/out_$N && cp run_split.py $N/
ln -s /home/claude/rerun/ProjectFull/ashrae-energy-prediction $N/ashrae-energy-prediction
ln -s /home/claude/rerun/ProjectFull/outputs $N/outputs
sed -i "s#ROOT / \"outputs_full\"#ROOT / \"out_$N\"#" $N/notebooks/config.py
[ -n "$ED" ] && sed -i "$ED" $N/notebooks/04_cutoffs_and_flags.ipynb
[ -n "$ZR" ] && sed -i "s/^ZERO_RUN_HOURS = 24/ZERO_RUN_HOURS = $ZR/" $N/notebooks/config.py
for nb in $NBS; do
  echo "$N start $nb $(date +%T)" >> chain.log
  (cd $N && python3 -I -u run_split.py notebooks/$nb.ipynb > log_$nb.txt 2>&1) || { echo "$N FAILED $nb" >> chain.log; exit 1; }
  echo "$N done $nb $(date +%T)" >> chain.log
done
