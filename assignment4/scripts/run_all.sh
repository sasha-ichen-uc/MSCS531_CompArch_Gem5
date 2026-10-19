#!/bin/bash
# run_all.sh - Run all Part 2 gem5 experiments for Assignment 4.
# Usage: cd assignment4 && bash scripts/run_all.sh
set -euo pipefail

GEM5=$HOME/MSCS531_CompArch/gem5/build/X86/gem5.opt
CONFIGS=$HOME/MSCS531_CompArch/assignment4/configs
WORK=$HOME/MSCS531_CompArch/assignment4/workloads
RESULTS=$HOME/MSCS531_CompArch/assignment4/results

# Activate conda for gem5 Python env
source /opt/miniconda3/etc/profile.d/conda.sh && conda activate gem5

echo "============================================================"
echo "  Assignment 4 Part 2 - ILP Experiments"
echo "============================================================"

run_sim() {
    local label="$1"; shift
    local outdir="$1"; shift
    echo "  [$label]"
    rm -rf "$outdir"; mkdir -p "$outdir"
    $GEM5 --outdir="$outdir" "$@" 2>&1 | tee "$outdir/run.log" | tail -3
}

# ---------------------------------------------------------------
# Task 1 & 2: Basic pipeline simulation (MinorCPU + O3CPU baseline)
# ---------------------------------------------------------------
echo ""
echo ">>> Task 1-2: Basic pipeline"
run_sim "MinorCPU in-order" "$RESULTS/task1_pipeline" \
    "$CONFIGS/pipeline_basic.py" "$WORK/int_compute"
run_sim "O3CPU baseline w4" "$RESULTS/task1_o3_baseline" \
    "$CONFIGS/superscalar.py" "$WORK/int_compute" --width 4

# ---------------------------------------------------------------
# Task 3: Branch prediction comparison
# ---------------------------------------------------------------
echo ""
echo ">>> Task 3: Branch prediction"
for BP in static local tournament tage; do
    run_sim "BP=$BP" "$RESULTS/task3_bp_${BP}" \
        "$CONFIGS/branch_prediction.py" "$WORK/int_compute" --bp "$BP"
done

# ---------------------------------------------------------------
# Task 4: Superscalar width sweep
# ---------------------------------------------------------------
echo ""
echo ">>> Task 4: Superscalar width sweep"
for BENCH in int_compute fp_compute mem_compute branch_heavy; do
    for W in 1 2 4 8; do
        run_sim "${BENCH} w${W}" "$RESULTS/task4_${BENCH}_w${W}" \
            "$CONFIGS/superscalar.py" "$WORK/$BENCH" --width "$W"
    done
done

# ---------------------------------------------------------------
# Task 5: SMT (single thread vs two threads)
# ---------------------------------------------------------------
echo ""
echo ">>> Task 5: SMT"
run_sim "SMT 1 thread" "$RESULTS/task5_smt_1thread" \
    "$CONFIGS/smt.py" "$WORK/int_compute" --threads 1
run_sim "SMT 2 threads" "$RESULTS/task5_smt_2thread" \
    "$CONFIGS/smt.py" "$WORK/int_compute" --threads 2

echo ""
echo "============================================================"
echo "  All experiments complete. Results in: $RESULTS"
echo "============================================================"
