#!/bin/bash
# collect_stats.sh - Extract key metrics from all experiment stats files
RESULTS=$HOME/MSCS531_CompArch/assignment4/results

extract() {
    local dir="$1"
    local label="$2"
    local stats="$dir/stats.txt"
    if [ ! -f "$stats" ]; then echo "$label: NO STATS"; return; fi

    local cycles=$(grep "system.cpu.numCycles " "$stats" | awk '{print $2}')
    local cpi=$(grep "system.cpu.cpi " "$stats" | awk '{print $2}')
    local ipc=$(grep "system.cpu.ipc " "$stats" | awk '{print $2}')
    local insts=$(grep "committedInsts\|thread_0.numInsts" "$stats" | head -1 | awk '{print $2}')
    local ops=$(grep "committedOps\|thread_0.numOps" "$stats" | head -1 | awk '{print $2}')
    # Branch stats (O3CPU)
    local bp_lookups=$(grep "branchPred.lookups_0::total " "$stats" 2>/dev/null | awk '{print $2}')
    local bp_misses=$(grep "branchPred.committed_0::Incorrect::total\|branchMispredicts " "$stats" 2>/dev/null | head -1 | awk '{print $2}')
    local squashes=$(grep "commitStats0.committedInstType_0::total\|squashedInsts " "$stats" 2>/dev/null | head -1 | awk '{print $2}')

    printf "%-30s  cycles=%-10s CPI=%-10s IPC=%-10s insts=%-8s ops=%-8s bp_miss=%-8s\n" \
        "$label" "$cycles" "$cpi" "$ipc" "$insts" "$ops" "${bp_misses:-n/a}"
}

echo "========================================================================"
echo "  TASK 1-2: Basic Pipeline"
echo "========================================================================"
extract "$RESULTS/task1_pipeline"    "MinorCPU (in-order)"
extract "$RESULTS/task1_o3_baseline" "O3CPU width=4 (OoO)"

echo ""
echo "========================================================================"
echo "  TASK 3: Branch Prediction"
echo "========================================================================"
for bp in static local tournament tage; do
    extract "$RESULTS/task3_bp_$bp" "BP=$bp"
done

echo ""
echo "========================================================================"
echo "  TASK 4: Superscalar Width Sweep"
echo "========================================================================"
for bench in int_compute fp_compute mem_compute branch_heavy; do
    echo "--- $bench ---"
    for w in 1 2 4 8; do
        extract "$RESULTS/task4_${bench}_w${w}" "width=$w"
    done
done

echo ""
echo "========================================================================"
echo "  TASK 5: SMT"
echo "========================================================================"
extract "$RESULTS/task5_smt_1thread" "1 thread"
extract "$RESULTS/task5_smt_2thread" "2 threads (SMT)"

# Also get per-thread stats for SMT
echo ""
echo "--- SMT 2-thread per-thread details ---"
for t in 0 1; do
    stats="$RESULTS/task5_smt_2thread/stats.txt"
    insts=$(grep "commitStats${t}.numInsts " "$stats" 2>/dev/null | awk '{print $2}')
    ops=$(grep "commitStats${t}.numOps " "$stats" 2>/dev/null | awk '{print $2}')
    echo "  Thread $t: insts=$insts ops=$ops"
done
