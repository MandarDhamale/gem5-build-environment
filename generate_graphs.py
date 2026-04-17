#!/usr/bin/env python3
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import json

OUT_DIR = "/workspace"

BG_DARK   = "#0d1117"
BG_PANEL  = "#161b22"
GRID_COL  = "#30363d"
TEXT_COL  = "#e6edf3"
TITLE_COL = "#58a6ff"
SUB_COL   = "#8b949e"

PALETTE = ["#58a6ff", "#3fb950", "#f78166", "#d2a8ff", "#ffa657", "#79c0ff"]

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
    ylim_max = ax.get_ylim()[1]
    for rect in rects:
        h = rect.get_height()
        ax.text(rect.get_x() + rect.get_width() / 2.0, h + ylim_max * offset,
                fmt.format(h), ha='center', va='bottom', color=color, fontsize=fontsize, fontweight='bold')

def save(fig, name):
    fig.savefig(f"{OUT_DIR}/{name}", dpi=180, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)

with open("/workspace/parsed_metrics.json", "r") as f:
    data = json.load(f)

# Arrays for plotting
configs = ["Baseline\n(O3, 256k)", "Config 1\n(LTAGE)", "Config 2\n(In-Order)", "Config 3\n(512k L2)", "Config 4\n(Prefetcher)"]
keys = ["Baseline", "Config 1 (LTAGE)", "Config 2 (In-Order)", "Config 3 (512k L2)", "Config 4 (Prefetch)"]

ipc = [data[k]["IPC"] for k in keys]
ticks = [data[k]["Ticks_M"] for k in keys]
branch_mpki = [data[k]["Branch_MPKI"] for k in keys[:2]]
l2_mpki = [data[k]["L2_MPKI"] for k in keys]

# Graph 1: IPC
fig, ax = plt.subplots(figsize=(10, 5))
apply_dark_theme(fig, ax)
x = np.arange(len(configs))
bars = ax.bar(x, ipc, color=PALETTE[:5], width=0.6, edgecolor='#21262d', linewidth=0.8)
ax.axhline(y=ipc[0], color=PALETTE[0], linestyle='--', alpha=0.5, label=f"Baseline IPC")
ax.set_xticks(x)
ax.set_xticklabels(configs, fontsize=9, color=TEXT_COL)
ax.set_ylabel("Instructions Per Cycle (IPC)")
ax.set_title("IPC Comparison (n=100k)")
ax.set_ylim(0, max(ipc) * 1.2)
add_value_labels(ax, bars, fmt="{:.4f}", fontsize=9)
save(fig, "graph_1_ipc_comparison.png")

# Graph 2: Branch MPKI (Baseline vs Config 1)
fig, ax = plt.subplots(figsize=(6, 5))
apply_dark_theme(fig, ax)
x = np.arange(2)
bars = ax.bar(x, branch_mpki, color=PALETTE[:2], width=0.5, edgecolor='#21262d', linewidth=0.8)
ax.set_xticks(x)
ax.set_xticklabels(configs[:2], fontsize=10, color=TEXT_COL)
ax.set_ylabel("Branch Mispredictions Per Kilo-Instruction (MPKI)")
ax.set_title("Branch MPKI")
ax.set_ylim(0, max(branch_mpki) * 1.5)
add_value_labels(ax, bars, fmt="{:.2f}", offset=0.02)
save(fig, "graph_2_branch_prediction.png")

# Graph 3: L2 MPKI
fig, ax = plt.subplots(figsize=(10, 5))
apply_dark_theme(fig, ax)
x = np.arange(len(configs))
# Note: Config 2 (In-Order) has an inflated MPKI due to simple CPU counting differences. 
# We'll plot all, but scale y to ignore the simple CPU anomaly, or just plot O3 configs.
o3_configs = ["Baseline\n(O3, 256k)", "Config 1\n(LTAGE)", "Config 3\n(512k L2)", "Config 4\n(Prefetcher)"]
o3_keys = ["Baseline", "Config 1 (LTAGE)", "Config 3 (512k L2)", "Config 4 (Prefetch)"]
o3_l2_mpki = [data[k]["L2_MPKI"] for k in o3_keys]
x_o3 = np.arange(len(o3_configs))
colors_o3 = [PALETTE[0], PALETTE[1], PALETTE[3], PALETTE[4]]

bars = ax.bar(x_o3, o3_l2_mpki, color=colors_o3, width=0.6, edgecolor='#21262d', linewidth=0.8)
ax.set_xticks(x_o3)
ax.set_xticklabels(o3_configs, fontsize=9, color=TEXT_COL)
ax.set_ylabel("L2 Demand Misses Per Kilo-Instruction (MPKI)")
ax.set_title("L2 Cache Demand MPKI (O3 CPU configs only)")
ax.set_ylim(0, max(o3_l2_mpki) * 1.25)
add_value_labels(ax, bars, fmt="{:.3f}")
save(fig, "graph_3_cache_misses.png")

# Graph 4: Execution Ticks
fig, ax = plt.subplots(figsize=(10, 5))
apply_dark_theme(fig, ax)
x = np.arange(len(configs))
bars = ax.bar(x, ticks, color=PALETTE[:5], width=0.6, edgecolor='#21262d', linewidth=0.8)
ax.axhline(y=ticks[0], color=PALETTE[0], linestyle='--', alpha=0.5)
ax.set_xticks(x)
ax.set_xticklabels(configs, fontsize=9, color=TEXT_COL)
ax.set_ylabel("Simulated Execution Time (Millions of Ticks)")
ax.set_title("Execution Time")
ax.set_ylim(0, max(ticks) * 1.25)
add_value_labels(ax, bars, fmt="{:.1f}M", offset=0.01)
save(fig, "graph_4_execution_ticks.png")

print("Generated 4 updated graphs.")
