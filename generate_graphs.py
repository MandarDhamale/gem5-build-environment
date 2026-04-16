#!/usr/bin/env python3
"""
generate_graphs.py
==================
Generates 4 publication-quality bar charts from gem5 simulation results
for the Quicksort Performance Characterization midterm project.

Metrics extracted from ROI section (index 1) of each stats.txt:
  Baseline  : O3CPU + TournamentBP + 256kB L2,  n=10,000
  Config 1  : O3CPU + LTAGE         + 256kB L2,  n=10,000
  Config 2  : TimingSimpleCPU        + 256kB L2,  n=10,000
  Config 3a : O3CPU + TournamentBP  + 256kB L2,  n=100,000
  Config 3b : O3CPU + TournamentBP  + 512kB L2,  n=100,000
  Config 4  : O3CPU + TournamentBP  + 8-way L1D + 256kB L2, n=10,000
"""

import matplotlib
matplotlib.use('Agg')          # non-interactive backend (no display needed)
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os

# ── Output directory ──────────────────────────────────────────────────────────
OUT_DIR = "/workspace"

# ── Shared style ──────────────────────────────────────────────────────────────
BG_DARK   = "#0d1117"
BG_PANEL  = "#161b22"
GRID_COL  = "#30363d"
TEXT_COL  = "#e6edf3"
TITLE_COL = "#58a6ff"
SUB_COL   = "#8b949e"

PALETTE = [
    "#58a6ff",   # blue    – Baseline
    "#3fb950",   # green   – Config 1 (LTAGE)
    "#f78166",   # red/ora – Config 2 (InOrder)
    "#d2a8ff",   # purple  – Config 3a (256kB L2)
    "#ffa657",   # orange  – Config 3b (512kB L2)
    "#79c0ff",   # sky     – Config 4 (8-way L1D)
]

def apply_dark_theme(fig, ax):
    fig.patch.set_facecolor(BG_DARK)
    ax.set_facecolor(BG_PANEL)
    ax.tick_params(colors=TEXT_COL, labelsize=10)
    ax.xaxis.label.set_color(TEXT_COL)
    ax.yaxis.label.set_color(TEXT_COL)
    ax.title.set_color(TITLE_COL)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID_COL)
    ax.yaxis.grid(True, color=GRID_COL, linestyle='--', linewidth=0.6, alpha=0.7)
    ax.set_axisbelow(True)

def add_value_labels(ax, rects, fmt="{:.4f}", offset=0.005, color=TEXT_COL, fontsize=9):
    """Annotate each bar with its numeric value."""
    ylim_max = ax.get_ylim()[1]
    for rect in rects:
        h = rect.get_height()
        ax.text(
            rect.get_x() + rect.get_width() / 2.0,
            h + ylim_max * offset,
            fmt.format(h),
            ha='center', va='bottom',
            color=color, fontsize=fontsize, fontweight='bold'
        )

def save(fig, name):
    path = os.path.join(OUT_DIR, name)
    fig.savefig(path, dpi=180, bbox_inches='tight', facecolor=fig.get_facecolor())
    print(f"  [SAVED] {path}")
    plt.close(fig)

# ═══════════════════════════════════════════════════════════════════════════════
# ── GRAPH 1: IPC Comparison – all 6 configs ───────────────────────────────────
# ═══════════════════════════════════════════════════════════════════════════════
print("\n[Graph 1] Generating IPC comparison bar chart...")

configs_ipc = [
    "Baseline\n(O3+Tournament\nn=10k)",
    "Config 1\n(O3+LTAGE\nn=10k)",
    "Config 2\n(InOrder/Timing\nn=10k)",
    "Config 3a\n(O3+256kB L2\nn=100k)",
    "Config 3b\n(O3+512kB L2\nn=100k)",
    "Config 4\n(O3+8-way L1D\nn=10k)",
]
ipc_values = [0.8017, 0.8111, 0.5453, 0.8612, 0.8615, 0.8017]

fig, ax = plt.subplots(figsize=(12, 6))
apply_dark_theme(fig, ax)

x = np.arange(len(configs_ipc))
bars = ax.bar(x, ipc_values, color=PALETTE, width=0.6,
              edgecolor='#21262d', linewidth=0.8, zorder=3)

# Highlight baseline with a dashed reference line
ax.axhline(y=ipc_values[0], color=PALETTE[0], linestyle='--',
           linewidth=1.2, alpha=0.5, label=f"Baseline IPC ({ipc_values[0]:.4f})")

ax.set_xticks(x)
ax.set_xticklabels(configs_ipc, fontsize=8.5, color=TEXT_COL)
ax.set_ylabel("Instructions Per Cycle (IPC)", fontsize=11)
ax.set_title("IPC Comparison — All Configurations\nRecursive Quicksort Benchmark (gem5 ROI)",
             fontsize=13, fontweight='bold', pad=14)
ax.set_ylim(0, max(ipc_values) * 1.20)
ax.legend(fontsize=9, facecolor=BG_PANEL, edgecolor=GRID_COL,
          labelcolor=TEXT_COL, loc='upper left')

add_value_labels(ax, bars, fmt="{:.4f}", fontsize=9)

# Annotation arrows
ax.annotate("Best IPC ↑\n(Config 3b)", xy=(4, 0.8615), xytext=(4, 0.97),
            fontsize=8, color="#ffa657",
            arrowprops=dict(arrowstyle='->', color="#ffa657", lw=1.2),
            ha='center')
ax.annotate("−32% vs Baseline", xy=(2, 0.5453), xytext=(2, 0.45),
            fontsize=8, color="#f78166",
            arrowprops=dict(arrowstyle='->', color="#f78166", lw=1.2),
            ha='center')

fig.text(0.99, 0.02, "gem5 Simulator · x86-64 SE Mode · 3GHz",
         ha='right', va='bottom', color=SUB_COL, fontsize=7.5)

save(fig, "graph_1_ipc_comparison.png")


# ═══════════════════════════════════════════════════════════════════════════════
# ── GRAPH 2: Branch Misprediction Rate – Baseline vs Config 1 (LTAGE) ─────────
# ═══════════════════════════════════════════════════════════════════════════════
print("[Graph 2] Generating branch misprediction rate chart...")

bp_labels = [
    "Baseline\n(TournamentBP)",
    "Config 1\n(LTAGE)",
]
bp_mispredict_pct = [0.795, 0.387]

# Also include raw counts for annotation
bp_mispredict_count = [1290, 627]
bp_committed        = [162171, 162171]
bp_squashes         = [13198, 3964]

fig, ax = plt.subplots(figsize=(7, 6))
apply_dark_theme(fig, ax)

colors_bp = [PALETTE[0], PALETTE[1]]
x = np.arange(len(bp_labels))
bars = ax.bar(x, bp_mispredict_pct, color=colors_bp, width=0.45,
              edgecolor='#21262d', linewidth=0.8, zorder=3)

ax.set_xticks(x)
ax.set_xticklabels(bp_labels, fontsize=11, color=TEXT_COL)
ax.set_ylabel("Branch Misprediction Rate (%)", fontsize=11)
ax.set_title("Branch Misprediction Rate\nTournamentBP vs. LTAGE (n=10k, O3CPU)",
             fontsize=13, fontweight='bold', pad=14)
ax.set_ylim(0, max(bp_mispredict_pct) * 1.55)

add_value_labels(ax, bars, fmt="{:.3f}%", offset=0.02)

# Reduction annotation bracket
y_top = max(bp_mispredict_pct) * 1.25
ax.annotate("", xy=(1, bp_mispredict_pct[1] + 0.03),
            xytext=(0, bp_mispredict_pct[0] + 0.03),
            arrowprops=dict(arrowstyle='<->', color=TEXT_COL, lw=1.2,
                            connectionstyle='arc3,rad=0'))
ax.text(0.5, (bp_mispredict_pct[0] + bp_mispredict_pct[1]) / 2 + 0.13,
        "−51.3%\nreduction", ha='center', va='bottom',
        color="#3fb950", fontsize=10, fontweight='bold')

# Info table below bars
info = [
    ["Committed Branches", f"{bp_committed[0]:,}", f"{bp_committed[1]:,}"],
    ["Mispredicted",       f"{bp_mispredict_count[0]:,}", f"{bp_mispredict_count[1]:,}"],
    ["Pipeline Squashes",  f"{bp_squashes[0]:,}", f"{bp_squashes[1]:,}"],
]
table = ax.table(cellText=info,
                 colLabels=["Metric", "TournamentBP", "LTAGE"],
                 cellLoc='center', loc='lower center',
                 bbox=[0.0, -0.42, 1.0, 0.30])
table.auto_set_font_size(False)
table.set_fontsize(9)
for (row, col), cell in table.get_celld().items():
    cell.set_facecolor(BG_PANEL if row > 0 else "#1c2128")
    cell.set_edgecolor(GRID_COL)
    cell.set_text_props(color=TEXT_COL if row > 0 else TITLE_COL, fontweight='bold' if row == 0 else 'normal')

fig.subplots_adjust(bottom=0.30)
fig.text(0.99, 0.02, "gem5 Simulator · x86-64 SE Mode · 3GHz",
         ha='right', va='bottom', color=SUB_COL, fontsize=7.5)

save(fig, "graph_2_branch_prediction.png")


# ═══════════════════════════════════════════════════════════════════════════════
# ── GRAPH 3: L2 Cache Miss Rate – Baseline vs Config 3a/3b vs Config 4 ────────
# ═══════════════════════════════════════════════════════════════════════════════
print("[Graph 3] Generating L2 cache miss rate chart...")

cache_labels = [
    "Baseline\n(O3+256kB L2\nn=10k)",
    "Config 3a\n(O3+256kB L2\nn=100k)",
    "Config 3b\n(O3+512kB L2\nn=100k)",
    "Config 4\n(O3+8-way L1D\n256kB L2, n=10k)",
]
l2_miss_pct = [61.00, 19.98, 19.61, 61.00]
l1d_miss_pct = [0.192, 0.024, 0.024, 0.192]

fig, ax1 = plt.subplots(figsize=(10, 6))
apply_dark_theme(fig, ax1)

x = np.arange(len(cache_labels))
width = 0.38

colors_l2 = [PALETTE[0], PALETTE[3], PALETTE[4], PALETTE[5]]
colors_l1 = ["#58a6ff55", "#d2a8ff55", "#ffa65755", "#79c0ff55"]

bars_l2 = ax1.bar(x - width/2, l2_miss_pct, width, color=colors_l2,
                  edgecolor='#21262d', linewidth=0.8, zorder=3, label="L2 Miss Rate %")

ax2 = ax1.twinx()
ax2.set_facecolor(BG_PANEL)
bars_l1 = ax2.bar(x + width/2, l1d_miss_pct, width, color=colors_l1,
                  edgecolor='#21262d', linewidth=0.8, zorder=3, label="L1D Miss Rate %",
                  hatch='///')

ax1.set_xticks(x)
ax1.set_xticklabels(cache_labels, fontsize=9, color=TEXT_COL)
ax1.set_ylabel("L2 Miss Rate (%)", fontsize=11, color=TEXT_COL)
ax2.set_ylabel("L1D Miss Rate (%)", fontsize=11, color=SUB_COL)
ax2.tick_params(colors=SUB_COL, labelsize=10)
for spine in ax2.spines.values():
    spine.set_edgecolor(GRID_COL)

ax1.set_title("Cache Miss Rates — Baseline vs. Config 3 vs. Config 4\nL2 (primary axis) and L1D (secondary axis)",
              fontsize=13, fontweight='bold', pad=14)
ax1.set_ylim(0, 85)
ax2.set_ylim(0, 0.40)

# Value labels for L2 bars
for rect, val in zip(bars_l2, l2_miss_pct):
    ax1.text(rect.get_x() + rect.get_width() / 2,
             rect.get_height() + 1.5,
             f"{val:.2f}%", ha='center', va='bottom',
             color=TEXT_COL, fontsize=9, fontweight='bold')

# Value labels for L1D bars
for rect, val in zip(bars_l1, l1d_miss_pct):
    ax2.text(rect.get_x() + rect.get_width() / 2,
             rect.get_height() + 0.008,
             f"{val:.3f}%", ha='center', va='bottom',
             color=SUB_COL, fontsize=8)

# Improvement annotation
ax1.annotate("−67.2%\nvs Baseline",
             xy=(1, l2_miss_pct[1]), xytext=(1, 55),
             fontsize=9, color="#3fb950", ha='center', fontweight='bold',
             arrowprops=dict(arrowstyle='->', color="#3fb950", lw=1.2))

ax1.annotate("3b only −0.4pp\nvs 3a",
             xy=(2, l2_miss_pct[2]), xytext=(2.5, 30),
             fontsize=8, color="#ffa657", ha='center',
             arrowprops=dict(arrowstyle='->', color="#ffa657", lw=1.0))

legend_patches = [
    mpatches.Patch(color=PALETTE[0], label="L2 Miss Rate (primary)"),
    mpatches.Patch(color="#58a6ff55", hatch='///', label="L1D Miss Rate (secondary)", edgecolor=GRID_COL),
]
ax1.legend(handles=legend_patches, fontsize=9, facecolor=BG_PANEL,
           edgecolor=GRID_COL, labelcolor=TEXT_COL, loc='upper right')

fig.text(0.99, 0.02, "gem5 Simulator · x86-64 SE Mode · 3GHz",
         ha='right', va='bottom', color=SUB_COL, fontsize=7.5)

save(fig, "graph_3_cache_misses.png")


# ═══════════════════════════════════════════════════════════════════════════════
# ── GRAPH 4: Total Execution Ticks – all 6 configs ────────────────────────────
# ═══════════════════════════════════════════════════════════════════════════════
print("[Graph 4] Generating execution ticks chart...")

configs_ticks = [
    "Baseline\n(O3+Tournament\nn=10k)",
    "Config 1\n(O3+LTAGE\nn=10k)",
    "Config 2\n(InOrder/Timing\nn=10k)",
    "Config 3a\n(O3+256kB L2\nn=100k)",
    "Config 3b\n(O3+512kB L2\nn=100k)",
    "Config 4\n(O3+8-way L1D\nn=10k)",
]
# Convert to Millions of Ticks for readability
ticks_raw   = [301676355, 298147887, 443556999, 2747101815, 2746143441, 301676355]
ticks_m     = [t / 1e6 for t in ticks_raw]

fig, ax = plt.subplots(figsize=(12, 6))
apply_dark_theme(fig, ax)

x = np.arange(len(configs_ticks))
bars = ax.bar(x, ticks_m, color=PALETTE, width=0.6,
              edgecolor='#21262d', linewidth=0.8, zorder=3)

ax.axhline(y=ticks_m[0], color=PALETTE[0], linestyle='--',
           linewidth=1.2, alpha=0.5, label=f"Baseline ({ticks_m[0]:.1f}M ticks)")

ax.set_xticks(x)
ax.set_xticklabels(configs_ticks, fontsize=8.5, color=TEXT_COL)
ax.set_ylabel("Simulated Execution Time (Millions of Ticks)", fontsize=11)
ax.set_title("Execution Time — All Configurations\nRecursive Quicksort Benchmark (gem5 ROI, 1 tick = 0.333 ns @ 3GHz)",
             fontsize=13, fontweight='bold', pad=14)
ax.set_ylim(0, max(ticks_m) * 1.22)
ax.legend(fontsize=9, facecolor=BG_PANEL, edgecolor=GRID_COL,
          labelcolor=TEXT_COL, loc='upper left')

add_value_labels(ax, bars, fmt="{:.1f}M", offset=0.008, fontsize=9)

# Annotations
ax.annotate("+47.0% vs Baseline", xy=(2, ticks_m[2]), xytext=(2, ticks_m[2] + 35),
            fontsize=8.5, color="#f78166", ha='center',
            arrowprops=dict(arrowstyle='->', color="#f78166", lw=1.2))

ax.annotate("Config 1: −1.17%\n(best for n=10k)", xy=(1, ticks_m[1]),
            xytext=(1.3, ticks_m[1] + 120),
            fontsize=8, color="#3fb950", ha='center',
            arrowprops=dict(arrowstyle='->', color="#3fb950", lw=1.0))

ax.annotate("100k array\n(~9.1× baseline)", xy=(3, ticks_m[3]), xytext=(3.0, ticks_m[3] + 180),
            fontsize=8, color="#d2a8ff", ha='center',
            arrowprops=dict(arrowstyle='->', color="#d2a8ff", lw=1.0))

fig.text(0.99, 0.02, "gem5 Simulator · x86-64 SE Mode · 3GHz  |  1M ticks = 0.333ms",
         ha='right', va='bottom', color=SUB_COL, fontsize=7.5)

save(fig, "graph_4_execution_ticks.png")


# ── Done ──────────────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("All 4 graphs saved successfully to:", OUT_DIR)
print("  graph_1_ipc_comparison.png")
print("  graph_2_branch_prediction.png")
print("  graph_3_cache_misses.png")
print("  graph_4_execution_ticks.png")
print("="*60)
