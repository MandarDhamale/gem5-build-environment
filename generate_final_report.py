#!/usr/bin/env python3
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import io
import base64
from weasyprint import HTML

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

def get_b64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=180, bbox_inches='tight', facecolor=fig.get_facecolor())
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return b64

# ==========================================
# 1) IPC Comparison
# ==========================================
configs_ipc = ["Baseline\n(O3+Tournament)", "Config 1\n(O3+LTAGE)", "Config 2\n(InOrder/Timing)", "Config 3a\n(O3+256kB L2)", "Config 3b\n(O3+512kB L2)", "Config 4\n(O3+8-way L1D)"]
ipc_values = [0.8017, 0.8111, 0.5453, 0.8612, 0.8615, 0.8017]
fig1, ax1 = plt.subplots(figsize=(10, 5))
apply_dark_theme(fig1, ax1)
x = np.arange(len(configs_ipc))
bars = ax1.bar(x, ipc_values, color=PALETTE, width=0.6, edgecolor='#21262d', linewidth=0.8, zorder=3)
ax1.axhline(y=ipc_values[0], color=PALETTE[0], linestyle='--', linewidth=1.2, alpha=0.5, label=f"Baseline IPC ({ipc_values[0]:.4f})")
ax1.set_xticks(x)
ax1.set_xticklabels(configs_ipc, fontsize=8, color=TEXT_COL)
ax1.set_ylabel("Instructions Per Cycle (IPC)")
ax1.set_title("IPC Comparison — All Configurations")
ax1.set_ylim(0, max(ipc_values) * 1.20)
ax1.legend(fontsize=9, facecolor=BG_PANEL, edgecolor=GRID_COL, labelcolor=TEXT_COL, loc='upper left')
add_value_labels(ax1, bars, fmt="{:.4f}", fontsize=9)
g1_b64 = get_b64(fig1)

# ==========================================
# 2) Branch Misprediction Rate
# ==========================================
bp_labels = ["Baseline (TournamentBP)", "Config 1 (LTAGE)"]
bp_mispredict_pct = [0.795, 0.387]
fig2, ax2 = plt.subplots(figsize=(6, 5))
apply_dark_theme(fig2, ax2)
colors_bp = [PALETTE[0], PALETTE[1]]
x = np.arange(len(bp_labels))
bars = ax2.bar(x, bp_mispredict_pct, color=colors_bp, width=0.5, edgecolor='#21262d', linewidth=0.8, zorder=3)
ax2.set_xticks(x)
ax2.set_xticklabels(bp_labels, fontsize=10, color=TEXT_COL)
ax2.set_ylabel("Branch Misprediction Rate (%)")
ax2.set_title("Branch Misprediction Rate")
ax2.set_ylim(0, max(bp_mispredict_pct) * 1.55)
add_value_labels(ax2, bars, fmt="{:.3f}%", offset=0.02)
g2_b64 = get_b64(fig2)

# ==========================================
# 3) Cache Miss Rates
# ==========================================
cache_labels = ["Baseline", "Config 3a (256kB L2)", "Config 3b (512kB L2)", "Config 4 (8-way L1D)"]
l2_miss_pct = [61.00, 19.98, 19.61, 61.00]
l1d_miss_pct = [0.192, 0.024, 0.024, 0.192]
fig3, ax3 = plt.subplots(figsize=(10, 5))
apply_dark_theme(fig3, ax3)
x = np.arange(len(cache_labels))
width = 0.38
bars_l2 = ax3.bar(x - width/2, l2_miss_pct, width, color=[PALETTE[0], PALETTE[3], PALETTE[4], PALETTE[5]], edgecolor='#21262d', linewidth=0.8, zorder=3)
axtwin = ax3.twinx()
axtwin.set_facecolor(BG_PANEL)
bars_l1 = axtwin.bar(x + width/2, l1d_miss_pct, width, color=["#58a6ff55", "#d2a8ff55", "#ffa65755", "#79c0ff55"], edgecolor='#21262d', linewidth=0.8, zorder=3, hatch='///')
ax3.set_xticks(x)
ax3.set_xticklabels(cache_labels, fontsize=9, color=TEXT_COL)
ax3.set_ylabel("L2 Miss Rate (%)")
axtwin.set_ylabel("L1D Miss Rate (%)", color=SUB_COL)
axtwin.tick_params(colors=SUB_COL)
for spine in axtwin.spines.values(): spine.set_edgecolor(GRID_COL)
ax3.set_title("Cache Miss Rates — L2 (primary) and L1D (secondary)")
ax3.set_ylim(0, 85)
axtwin.set_ylim(0, 0.40)
for rect, val in zip(bars_l2, l2_miss_pct): ax3.text(rect.get_x() + rect.get_width() / 2, rect.get_height() + 1.5, f"{val:.2f}%", ha='center', va='bottom', color=TEXT_COL, fontsize=9, fontweight='bold')
for rect, val in zip(bars_l1, l1d_miss_pct): axtwin.text(rect.get_x() + rect.get_width() / 2, rect.get_height() + 0.008, f"{val:.3f}%", ha='center', va='bottom', color=SUB_COL, fontsize=8)
g3_b64 = get_b64(fig3)

# ==========================================
# 4) Total Execution Ticks
# ==========================================
ticks_m = [301.6, 298.1, 443.5, 2747.1, 2746.1, 301.6]
fig4, ax4 = plt.subplots(figsize=(10, 5))
apply_dark_theme(fig4, ax4)
x = np.arange(len(configs_ipc))
bars = ax4.bar(x, ticks_m, color=PALETTE, width=0.6, edgecolor='#21262d', linewidth=0.8, zorder=3)
ax4.axhline(y=ticks_m[0], color=PALETTE[0], linestyle='--', linewidth=1.2, alpha=0.5, label=f"Baseline ({ticks_m[0]:.1f}M ticks)")
ax4.set_xticks(x)
ax4.set_xticklabels(configs_ipc, fontsize=8, color=TEXT_COL)
ax4.set_ylabel("Execution Time (Millions of Ticks)")
ax4.set_title("Simulated Execution Time")
ax4.set_ylim(0, max(ticks_m) * 1.25)
ax4.legend(fontsize=9, facecolor=BG_PANEL, edgecolor=GRID_COL, labelcolor=TEXT_COL, loc='upper left')
add_value_labels(ax4, bars, fmt="{:.1f}M", offset=0.008, fontsize=9)
g4_b64 = get_b64(fig4)

# ==========================================
# Generate HTML and PDF
# ==========================================
html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Final Project Report</title>
    <style>
        body {{ font-family: 'Helvetica', sans-serif; color: #333; line-height: 1.6; margin: 30px; font-size: 13px; }}
        h1 {{ color: #2c3e50; font-size: 20px; font-family: 'Georgia', serif; text-align: center; margin-bottom: 5px; }}
        .header-sub {{ text-align: center; font-style: italic; color: #555; margin-bottom: 25px; border-bottom: 2px solid #2c3e50; padding-bottom: 15px; }}
        h2 {{ color: #2c3e50; font-size: 16px; border-bottom: 1px solid #ddd; padding-bottom: 3px; margin-top: 25px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; font-size: 12px; page-break-inside: avoid; }}
        th, td {{ border: 1px solid #aaa; padding: 6px; text-align: center; }}
        th {{ background-color: #eee; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
        .img-box {{ text-align: center; margin: 20px 0; page-break-inside: avoid; }}
        .img-box img {{ max-width: 80%; border: 1px solid #ccc; }}
        .caption {{ font-style: italic; color: #666; font-size: 11px; margin-top: 5px; }}
    </style>
</head>
<body>
    <h1>Performance Characterization of Recursive Quicksort on Out-of-Order Architectures</h1>
    <div class="header-sub">
        USF Bellini College of Artificial Intelligence, Cybersecurity and Computing<br>
        EEL 6764 - Computer Architecture<br>
        Team: Srikanth Akkaru, Mandar Dhamale, Johnathan Gutierrez-diaz, Sri Satya Sudarshan Varma Indukuri
    </div>

    <h2>1. Executive Summary & Storyline</h2>
    <p>Recursive Quicksort produces a demanding microarchitectural footprint due to unpredictable branch outcomes and volatile stack activity. This project characterizes the bottlenecks of a recursive Quicksort benchmark on a simulated out-of-order x86 processor (gem5). By isolating the sorting Region-of-Interest (ROI) via <code>m5_dump_reset_stats</code>, we precisely measured the stalls originating from branch mispredictions and L2 cache thrashing, and mapped the PPA tradeoffs required to mitigate them.</p>

    <h2>2. Methodology</h2>
    <p>We simulated x86-64 execution in gem5 Syscall Emulation mode. The baseline CPU model was <code>O3CPU</code> at 3 GHz, paired with an 8-way 16kB L1D cache and a 256kB L2. Simulation bounds were precisely managed with inline x86 assembly to reset statistics exactly before and after the <code>quickSort()</code> recursive tree.</p>

    <h2>3. Configuration Iterations</h2>
    <ul>
        <li><strong>Config 1 (LTAGE Predictor):</strong> Replaced TournamentBP to handle recursive branch patterns.</li>
        <li><strong>Config 2 (In-Order CPU):</strong> Swapped O3 for TimingSimpleCPU to establish true out-of-order latency hiding benefits.</li>
        <li><strong>Config 3 (L2 Cache Scaling):</strong> Enlarged array size to 100k, evaluating 256kB vs 512kB L2 sizes.</li>
        <li><strong>Config 4 (L1D Associativity):</strong> Patched to explicitly test 8-way L1D cache geometries.</li>
    </ul>

    <h2>4. Performance Results</h2>
    <table>
        <thead>
            <tr><th>Configuration</th><th>n</th><th>IPC</th><th>Sim Ticks</th><th>Mispredict %</th><th>L2 Miss %</th></tr>
        </thead>
        <tbody>
            <tr><td>Baseline (O3, Tournament, 256k)</td><td>10k</td><td>0.8017</td><td>301M</td><td>0.795%</td><td>61.00%</td></tr>
            <tr><td>Config 1 (O3, LTAGE, 256k)</td><td>10k</td><td>0.8111</td><td>298M</td><td>0.387%</td><td>61.04%</td></tr>
            <tr><td>Config 2 (In-Order, 256k)</td><td>10k</td><td>0.5453</td><td>443M</td><td>N/A</td><td>58.11%</td></tr>
            <tr><td>Config 3a (O3, Tourn, 256k)</td><td>100k</td><td>0.8612</td><td>2,747M</td><td>0.446%</td><td>19.98%</td></tr>
            <tr><td>Config 3b (O3, Tourn, 512k)</td><td>100k</td><td>0.8615</td><td>2,746M</td><td>0.446%</td><td>19.61%</td></tr>
            <tr><td>Config 4 (O3, 8-way L1, 256k)</td><td>10k</td><td>0.8017</td><td>301M</td><td>0.795%</td><td>61.00%</td></tr>
        </tbody>
    </table>

    <div class="img-box">
        <img src="data:image/png;base64,{g1_b64}">
        <div class="caption">Graph 1: Baseline IPC against evaluated architectural modifications.</div>
    </div>
    
    <div class="img-box">
        <img src="data:image/png;base64,{g2_b64}">
        <div class="caption">Graph 2: TournamentBP vs. LTAGE branch misprediction rates.</div>
    </div>

    <div class="img-box">
        <img src="data:image/png;base64,{g3_b64}">
        <div class="caption">Graph 3: L2 (Primary) and L1D (Secondary) miss rate distributions.</div>
    </div>

    <div class="img-box">
        <img src="data:image/png;base64,{g4_b64}">
        <div class="caption">Graph 4: Total simulated execution time (ticks).</div>
    </div>

    <h2>5. Bottleneck Analysis</h2>
    <p><strong>Config 1 (LTAGE):</strong> The predictor successfully halved the branch misprediction rate, verifying that Quicksort's conditional data dependencies heavily benefit from tagged geometric histories. However, IPC only improved by 1.17% overall.</p>
    <p><strong>Config 2 (In-Order):</strong> Performance dropped by 32% (IPC lowered from 0.80 to 0.54), establishing that memory latency hiding is the single biggest performance driver for this workload.</p>
    <p><strong>Config 3 (L2 Size Scaling):</strong> Doubling the L2 cache for a 100k element array provided fewer than 0.4% improvements to L2 misses. The structural random-access pivoting in Quicksort makes the workload completely pattern-limited rather than capacity-limited.</p>

    <h2>6. PPA Analysis & Conclusion</h2>
    <p><strong>Pareto Conclusion:</strong> The optimal configuration is <strong>O3CPU + LTAGE BP + 256kB L2</strong>. The out-of-order core is strictly mandated to tolerate the high ~61% L2 miss penalties. The LTAGE predictor solves the secondary branch bottleneck at almost zero area cost (&lt;0.1 mm²). Conversely, scaling the LLC to 512kB constitutes a poor PPA investment due to its 2x static power overhead with negligible latency reduction. We conclude that algorithmic locality (e.g. Iterative Mergesort) or dedicated hardware stream prefetchers are necessary to completely bypass Quicksort's fundamental architectural ceilings.</p>

</body>
</html>
"""

HTML(string=html).write_pdf("Quicksort_Final_Report.pdf")
print("Successfully generated Quicksort_Final_Report.pdf via weasyprint")
