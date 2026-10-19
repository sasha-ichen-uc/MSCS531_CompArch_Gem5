#!/usr/bin/env python3
"""Generate all charts for Assignment 4 report as PNG images."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os

OUT = os.path.expanduser("~/MSCS531_CompArch/assignment4/images")
os.makedirs(OUT, exist_ok=True)

# ── Common style ──────────────────────────────────────────────────
plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 11,
    'axes.titlesize': 13,
    'axes.labelsize': 12,
    'figure.dpi': 150,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.2,
})

COLORS = ['#4472C4', '#ED7D31', '#A5A5A5', '#FFC000', '#5B9BD5', '#70AD47']

# ═══════════════════════════════════════════════════════════════════
# Chart 1: Task 1-2 — In-order vs Out-of-order
# ═══════════════════════════════════════════════════════════════════
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

labels = ['MinorCPU\n(In-Order)', 'O3CPU\n(Out-of-Order)']
cpis = [34.19, 0.93]
ipcs = [0.029, 1.078]

bars1 = ax1.bar(labels, cpis, color=[COLORS[2], COLORS[0]], width=0.5, edgecolor='black', linewidth=0.5)
ax1.set_ylabel('CPI (Cycles Per Instruction)')
ax1.set_title('CPI: In-Order vs. Out-of-Order')
for bar, val in zip(bars1, cpis):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, f'{val}', ha='center', fontweight='bold')

bars2 = ax2.bar(labels, ipcs, color=[COLORS[2], COLORS[0]], width=0.5, edgecolor='black', linewidth=0.5)
ax2.set_ylabel('IPC (Instructions Per Cycle)')
ax2.set_title('IPC: In-Order vs. Out-of-Order')
for bar, val in zip(bars2, ipcs):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02, f'{val}', ha='center', fontweight='bold')

fig.suptitle('Task 1–2: Basic Pipeline Performance', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(f'{OUT}/task1_2_pipeline.png')
plt.close()
print(f'✅ {OUT}/task1_2_pipeline.png')

# ═══════════════════════════════════════════════════════════════════
# Chart 2: Task 3 — Branch Prediction
# ═══════════════════════════════════════════════════════════════════
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5))

predictors = ['Static\n(minimal)', 'Local\n(2 KB)', 'Tournament', 'TAGE-SC-L\n(64 KB)']
bp_ipc = [0.607, 0.498, 1.078, 1.082]
bp_miss = [6438, 9397, 264, 210]

bars = ax1.bar(predictors, bp_ipc, color=[COLORS[2], COLORS[1], COLORS[0], COLORS[4]],
               edgecolor='black', linewidth=0.5)
ax1.set_ylabel('IPC')
ax1.set_title('IPC by Branch Predictor')
ax1.set_ylim(0, 1.3)
for bar, val in zip(bars, bp_ipc):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02, f'{val:.3f}',
             ha='center', fontsize=9, fontweight='bold')

bars2 = ax2.bar(predictors, bp_miss, color=[COLORS[2], COLORS[1], COLORS[0], COLORS[4]],
                edgecolor='black', linewidth=0.5)
ax2.set_ylabel('Mispredictions')
ax2.set_title('Branch Mispredictions')
for bar, val in zip(bars2, bp_miss):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 100, f'{val:,}',
             ha='center', fontsize=9, fontweight='bold')

fig.suptitle('Task 3: Impact of Branch Prediction (O3CPU, width 4)', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(f'{OUT}/task3_branch_prediction.png')
plt.close()
print(f'✅ {OUT}/task3_branch_prediction.png')

# ═══════════════════════════════════════════════════════════════════
# Chart 3: Task 4 — Superscalar IPC
# ═══════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(9, 5))

widths = [1, 2, 4, 8]
data = {
    'int_compute':  [0.390, 0.673, 1.078, 1.508],
    'fp_compute':   [0.669, 1.202, 2.006, 2.931],
    'mem_compute':  [0.307, 0.379, 0.390, 0.392],
    'branch_heavy': [0.522, 0.817, 1.087, 1.256],
}

for i, (bench, ipcs) in enumerate(data.items()):
    ax.plot(widths, ipcs, 'o-', label=bench, color=COLORS[i], linewidth=2, markersize=7)

ax.set_xlabel('Issue Width')
ax.set_ylabel('IPC (Instructions Per Cycle)')
ax.set_title('Task 4: Superscalar IPC vs. Issue Width', fontsize=14, fontweight='bold')
ax.set_xticks(widths)
ax.legend(loc='upper left', framealpha=0.9)
ax.grid(True, alpha=0.3)
ax.set_xlim(0.5, 8.5)
plt.tight_layout()
plt.savefig(f'{OUT}/task4_superscalar_ipc.png')
plt.close()
print(f'✅ {OUT}/task4_superscalar_ipc.png')

# ═══════════════════════════════════════════════════════════════════
# Chart 4: Task 4 — Superscalar Speedup
# ═══════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(9, 5))

speedups = {
    'int_compute':  [1.00, 1.73, 2.77, 3.87],
    'fp_compute':   [1.00, 1.80, 3.00, 4.38],
    'mem_compute':  [1.00, 1.24, 1.27, 1.28],
    'branch_heavy': [1.00, 1.57, 2.08, 2.41],
}

for i, (bench, sp) in enumerate(speedups.items()):
    ax.plot(widths, sp, 'o-', label=bench, color=COLORS[i], linewidth=2, markersize=7)

# Ideal linear speedup line
ax.plot(widths, widths, 'k--', alpha=0.3, label='Ideal (linear)')

ax.set_xlabel('Issue Width')
ax.set_ylabel('Speedup (relative to width 1)')
ax.set_title('Task 4: Superscalar Speedup vs. Issue Width', fontsize=14, fontweight='bold')
ax.set_xticks(widths)
ax.legend(loc='upper left', framealpha=0.9)
ax.grid(True, alpha=0.3)
ax.set_xlim(0.5, 8.5)
ax.set_ylim(0.5, 8.5)
plt.tight_layout()
plt.savefig(f'{OUT}/task4_superscalar_speedup.png')
plt.close()
print(f'✅ {OUT}/task4_superscalar_speedup.png')

# ═══════════════════════════════════════════════════════════════════
# Chart 5: Task 5 — SMT
# ═══════════════════════════════════════════════════════════════════
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5))

configs = ['1 Thread', '2 Threads\n(SMT)']
total_ipc = [1.508, 1.566]
per_thread_cpi = [0.663, 1.278]

bars1 = ax1.bar(configs, total_ipc, color=[COLORS[0], COLORS[1]], width=0.45, edgecolor='black', linewidth=0.5)
ax1.set_ylabel('Total IPC')
ax1.set_title('Total Throughput (IPC)')
ax1.set_ylim(0, 2.0)
for bar, val in zip(bars1, total_ipc):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.03, f'{val:.3f}',
             ha='center', fontweight='bold')
ax1.annotate('+3.8%', xy=(1, 1.566), xytext=(1.3, 1.75),
             arrowprops=dict(arrowstyle='->', color='red'), color='red', fontweight='bold', fontsize=12)

bars2 = ax2.bar(configs, per_thread_cpi, color=[COLORS[0], COLORS[1]], width=0.45, edgecolor='black', linewidth=0.5)
ax2.set_ylabel('Per-Thread CPI')
ax2.set_title('Per-Thread Latency (CPI)')
ax2.set_ylim(0, 1.6)
for bar, val in zip(bars2, per_thread_cpi):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.03, f'{val:.3f}',
             ha='center', fontweight='bold')
ax2.annotate('1.93× slower', xy=(1, 1.278), xytext=(1.3, 1.45),
             arrowprops=dict(arrowstyle='->', color='red'), color='red', fontweight='bold', fontsize=10)

fig.suptitle('Task 5: SMT Performance (O3CPU, width 8)', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(f'{OUT}/task5_smt.png')
plt.close()
print(f'✅ {OUT}/task5_smt.png')

print(f'\nAll charts saved to {OUT}/')
