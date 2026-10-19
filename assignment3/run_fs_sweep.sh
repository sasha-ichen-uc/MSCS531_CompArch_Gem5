#!/bin/bash
# Runs the FS TLB sweep sequentially: one full boot + benchmark per TLB size.
source /opt/miniconda3/etc/profile.d/conda.sh && conda activate gem5
cd /Users/sasha/MSCS531_CompArch/assignment3
for T in 4 16 64; do
  OUT=runs/fs_tlb$T
  rm -rf $OUT; mkdir -p $OUT
  ../gem5/build/X86/gem5.opt --outdir=$OUT run_fs_tlb.py --tlb-size $T > $OUT/run.log 2>&1 &
  PID=$!
  ( sleep 5400; kill -0 $PID 2>/dev/null && kill $PID && echo "WATCHDOG: killed after 90 min" >> $OUT/run.log ) >/dev/null 2>&1 &
  wait $PID
  echo "SWEEP tlb=$T finished with exit $?" >> runs/sweep.log
done
echo "SWEEP COMPLETE" >> runs/sweep.log
