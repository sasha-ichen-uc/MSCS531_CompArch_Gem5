#!/usr/bin/env python3
"""Extract key metrics from all experiment stats.txt files into CSVs."""
import csv, os, re, sys

RESULTS = os.path.expanduser("~/MSCS531_CompArch/assignment4/results")
OUT = os.path.expanduser("~/MSCS531_CompArch/assignment4/results")

def get_stat(path, pattern):
    """Return the first numeric value matching pattern in stats.txt."""
    stats = os.path.join(path, "stats.txt")
    if not os.path.exists(stats):
        return None
    with open(stats) as f:
        for line in f:
            if re.search(pattern, line):
                parts = line.split()
                if len(parts) >= 2:
                    try:
                        return float(parts[1])
                    except ValueError:
                        return parts[1]
    return None

def extract(dirname):
    path = os.path.join(RESULTS, dirname)
    return {
        "cycles":    get_stat(path, r"system\.cpu\.numCycles "),
        "cpi":       get_stat(path, r"system\.cpu\.cpi "),
        "ipc":       get_stat(path, r"system\.cpu\.ipc "),
        "insts":     get_stat(path, r"commitStats0\.numInsts "),
        "ops":       get_stat(path, r"commitStats0\.numOps "),
        "bp_misses": get_stat(path, r"branchPred\.committed_0::Incorrect::total"),
    }

# Task 1-2
rows = []
for label, d in [("MinorCPU in-order", "task1_pipeline"),
                  ("O3CPU width=4", "task1_o3_baseline")]:
    s = extract(d)
    rows.append({"experiment": label, **s})

with open(f"{OUT}/task1_2_stats.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["experiment","cycles","cpi","ipc","insts","ops","bp_misses"])
    w.writeheader(); w.writerows(rows)

# Task 3
rows = []
for bp in ["static", "local", "tournament", "tage"]:
    s = extract(f"task3_bp_{bp}")
    rows.append({"predictor": bp, **s})

with open(f"{OUT}/task3_bp_stats.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["predictor","cycles","cpi","ipc","insts","ops","bp_misses"])
    w.writeheader(); w.writerows(rows)

# Task 4
rows = []
for bench in ["int_compute", "fp_compute", "mem_compute", "branch_heavy"]:
    for width in [1, 2, 4, 8]:
        s = extract(f"task4_{bench}_w{width}")
        rows.append({"benchmark": bench, "width": width, **s})

with open(f"{OUT}/task4_superscalar_stats.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["benchmark","width","cycles","cpi","ipc","insts","ops","bp_misses"])
    w.writeheader(); w.writerows(rows)

# Task 5
rows = []
for label, d in [("1 thread", "task5_smt_1thread"),
                  ("2 threads SMT", "task5_smt_2thread")]:
    s = extract(d)
    # For 2-thread SMT, also get thread 1 stats
    path = os.path.join(RESULTS, d)
    t1_insts = get_stat(path, r"commitStats1\.numInsts ")
    rows.append({"experiment": label, "thread1_insts": t1_insts, **s})

with open(f"{OUT}/task5_smt_stats.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["experiment","cycles","cpi","ipc","insts","ops","bp_misses","thread1_insts"])
    w.writeheader(); w.writerows(rows)

print("CSVs written to", OUT)
for f in ["task1_2_stats.csv", "task3_bp_stats.csv", "task4_superscalar_stats.csv", "task5_smt_stats.csv"]:
    print(f"  {f}")
