#!/usr/bin/env python3
import io
import base64
import json
from weasyprint import HTML

def get_b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

with open("/workspace/parsed_metrics.json", "r") as f:
    data = json.load(f)

graphs = {
    'g1': get_b64("/workspace/graph_1_ipc_comparison.png"),
    'g2': get_b64("/workspace/graph_2_branch_prediction.png"),
    'g3': get_b64("/workspace/graph_3_cache_misses.png"),
    'g4': get_b64("/workspace/graph_4_execution_ticks.png"),
}

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
        .alert {{ background-color: #e8f4f8; border-left: 4px solid #3498db; padding: 10px; margin: 15px 0; }}
    </style>
</head>
<body>
    <h1>Performance Characterization of Recursive Quicksort on Out-of-Order Architectures</h1>
    <div class="header-sub">
        Course: EEL 6764 - Computer Architecture<br>
        Institution: USF Bellini College of Artificial Intelligence, Cybersecurity and Computing<br>
        Team: Srikanth Akkaru, Mandar Dhamale, Johnathan Gutierrez-diaz, Sri Satya Sudarshan Varma Indukuri
    </div>

    <h2>1. Executive Summary & Hypothesis</h2>
    <p>Recursive Quicksort is a canonical divide-and-conquer algorithm with O(n log n) average-case time complexity. While elegant in software, it produces irregular execution and memory access patterns in hardware. Specifically, Quicksort alternates between sequential array scans during the <code>partition()</code> phase and non-contiguous memory bounds adjustments during the recursive tree descent. Furthermore, the <code>if (arr[j] &lt; pivot)</code> instruction creates dense, data-dependent conditional branches leading to frequent branch divergence.</p>
    
    <p><strong>Hypotheses:</strong></p>
    <ul>
        <li><strong>Control Flow:</strong> Branch mispredictions will be frequent due to random pivot selections and unpredictable data-dependent comparisons, creating pipeline flushes.</li>
        <li><strong>Memory Locality:</strong> Cache performance will suffer due to mixed locality—while the partition phase exhibits sequential locality, the recursive jumps reduce temporal locality across recursive subproblems and introduce irregular access patterns.</li>
        <li><strong>Scaling Constraints:</strong> Within the evaluated cache size range, performance will show minimal sensitivity to capacity, suggesting limited benefit from increasing L2 size for this workload.</li>
    </ul>

    <h2>2. Experimental Methodology</h2>
    <p>To ensure accurate, single-variable evaluations, simulations were executed using the <strong>gem5 architectural simulator</strong> (Syscall Emulation Mode). We standardized on uniformly random arrays of <strong>n = 100,000 integers</strong>. This dataset (~400kB footprint) was explicitly chosen to purposefully exceed the baseline L2 cache size (256kB), ensuring realistic capacity pressure.</p>
    
    <p>To filter out initialization noise, we injected x86 inline assembly (<code>m5_dump_reset_stats</code>) directly into the C benchmark. This created a strict Region-of-Interest that captured metrics <em>only</em> during the sorting execution.</p>
    
    <p><strong>Limitations & Future Work:</strong> This evaluation is limited to uniformly random input distributions. Future work should evaluate the microarchitectural behavior of sorted, reverse-sorted, or heavily skewed arrays, which alter the predictability of branches and the recursion depth.</p>

    <h2>3. Metric Definitions & Clarifications</h2>
    <p>To formally evaluate the architectures, we utilized the following standardized metrics:</p>
    <ul>
        <li><strong>IPC (Instructions Per Cycle):</strong> The average number of instructions retired per clock cycle. Higher is better.</li>
        <li><strong>CPI (Cycles Per Instruction):</strong> The average number of clock cycles required to execute one instruction. For single-core systems, CPI is the inverse of IPC (CPI ≈ 1 / IPC). Both are reported to provide intuition on execution efficiency versus stall latency.</li>
        <li><strong>Branch MPKI (Mispredictions Per Kilo-Instruction):</strong> The number of branch mispredictions per 1,000 committed instructions. Normalizing by instruction count standardizes comparisons across different runs.</li>
        <li><strong>L2 Demand MPKI (Misses Per Kilo-Instruction):</strong> The number of L2 demand cache misses per 1,000 committed instructions.</li>
        <li><strong>L2 Miss Rate (%):</strong> The ratio of L2 demand misses to total L2 demand accesses.</li>
    </ul>

    <h2>4. Configuration & Isolation Strategy</h2>
    <p>To provide causal attribution, we established a Baseline and varied exactly <strong>one parameter at a time</strong>.</p>
    <ul>
        <li><strong>Baseline:</strong> <code>O3CPU</code> (x86, 3GHz), <code>TournamentBP</code>, 256kB L2 Cache, Standard Memory</li>
        <li><strong>Config 1 (Control Flow):</strong> Same as Baseline, but swapped branch predictor to <code>LTAGE</code></li>
        <li><strong>Config 2 (Compute Pipeline):</strong> Same as Baseline, but swapped processor to <code>TimingSimple</code> (In-Order)</li>
        <li><strong>Config 3 (LLC Capacity):</strong> Same as Baseline, but doubled L2 cache to <strong>512kB</strong></li>
        <li><strong>Config 4 (Spatial Prefetching):</strong> Same as Baseline, but attached a <strong>StridePrefetcher</strong> to the L2 Cache</li>
    </ul>

    <h2>5. Performance Results & Metric Breakdown</h2>
    <table>
        <thead>
            <tr><th>Configuration</th><th>IPC</th><th>CPI</th><th>Exec Ticks (M)</th><th>Branch MPKI</th><th>L2 Demand MPKI</th><th>L2 Miss %</th></tr>
        </thead>
        <tbody>
            <tr><td>Baseline (O3, 256k)</td><td>{data['Baseline']['IPC']:.4f}</td><td>{data['Baseline']['CPI']:.3f}</td><td>{data['Baseline']['Ticks_M']:.1f}</td><td>{data['Baseline']['Branch_MPKI']:.3f}</td><td>{data['Baseline']['L2_MPKI']:.3f}</td><td>{data['Baseline']['L2_Miss_Rate']:.2f}%</td></tr>
            <tr><td>Config 1 (LTAGE)</td><td>{data['Config 1 (LTAGE)']['IPC']:.4f}</td><td>{data['Config 1 (LTAGE)']['CPI']:.3f}</td><td>{data['Config 1 (LTAGE)']['Ticks_M']:.1f}</td><td>{data['Config 1 (LTAGE)']['Branch_MPKI']:.3f}</td><td>{data['Config 1 (LTAGE)']['L2_MPKI']:.3f}</td><td>{data['Config 1 (LTAGE)']['L2_Miss_Rate']:.2f}%</td></tr>
            <tr><td>Config 2 (In-Order)</td><td>{data['Config 2 (In-Order)']['IPC']:.4f}</td><td>{data['Config 2 (In-Order)']['CPI']:.3f}</td><td>{data['Config 2 (In-Order)']['Ticks_M']:.1f}</td><td>N/A</td><td>N/A</td><td>{data['Config 2 (In-Order)']['L2_Miss_Rate']:.2f}%</td></tr>
            <tr><td>Config 3 (512k L2)</td><td>{data['Config 3 (512k L2)']['IPC']:.4f}</td><td>{data['Config 3 (512k L2)']['CPI']:.3f}</td><td>{data['Config 3 (512k L2)']['Ticks_M']:.1f}</td><td>{data['Config 3 (512k L2)']['Branch_MPKI']:.3f}</td><td>{data['Config 3 (512k L2)']['L2_MPKI']:.3f}</td><td>{data['Config 3 (512k L2)']['L2_Miss_Rate']:.2f}%</td></tr>
            <tr><td>Config 4 (Prefetch)</td><td>{data['Config 4 (Prefetch)']['IPC']:.4f}</td><td>{data['Config 4 (Prefetch)']['CPI']:.3f}</td><td>{data['Config 4 (Prefetch)']['Ticks_M']:.1f}</td><td>{data['Config 4 (Prefetch)']['Branch_MPKI']:.3f}</td><td>{data['Config 4 (Prefetch)']['L2_MPKI']:.3f}</td><td>{data['Config 4 (Prefetch)']['L2_Miss_Rate']:.2f}%</td></tr>
        </tbody>
    </table>

    <div class="img-box">
        <img src="data:image/png;base64,{graphs['g1']}">
        <div class="caption">Figure 1: Baseline IPC against evaluated architectural modifications. The graph illustrates that switching to an In-Order core causes a severe IPC drop, while other configurations yield minimal IPC variance.</div>
    </div>
    
    <div class="img-box">
        <img src="data:image/png;base64,{graphs['g2']}">
        <div class="caption">Figure 2: Branch Mispredictions Per Kilo-Instruction. The graph shows a significant reduction in Branch MPKI when using LTAGE, confirming improved prediction accuracy. However, the modest IPC gain suggests branch misprediction is not the dominant bottleneck.</div>
    </div>

    <div class="img-box">
        <img src="data:image/png;base64,{graphs['g3']}">
        <div class="caption">Figure 3: L2 Demand MPKI (O3 configurations only). The graph demonstrates that doubling L2 capacity or adding a stride prefetcher has a nearly imperceptible impact on L2 misses per instruction.</div>
    </div>

    <div class="img-box">
        <img src="data:image/png;base64,{graphs['g4']}">
        <div class="caption">Figure 4: Total simulated execution time (millions of ticks). The graph mirrors the IPC trends, confirming that Config 2 suffers massive execution time penalties due to a lack of latency hiding capabilities.</div>
    </div>

    <h2>6. Architectural Bottleneck Analysis</h2>
    <p><strong>A. The Control Flow Bottleneck (Branch Prediction)</strong><br>
    The data-dependent swaps during Quicksort's array partitioning act as a control flow hurdle. The Baseline <code>TournamentBP</code> suffered a Branch MPKI of ~1.00. Upgrading to the <strong>LTAGE Predictor (Config 1)</strong> dropped the Branch MPKI to 0.10. LTAGE successfully leverages long geometric histories to decipher complex, data-dependent loops. However, despite a substantial drop in Branch MPKI, overall IPC only increased from {data['Baseline']['IPC']:.3f} to {data['Config 1 (LTAGE)']['IPC']:.3f}. This firmly establishes that while branch prediction improves execution efficiency, it is <strong>not the dominant bottleneck</strong>.</p>
    
    <p><strong>B. The Memory Latency Bottleneck (Compute Pipeline)</strong><br>
    To measure exactly how heavily the architecture relies on masking memory latency, we removed the Out-of-Order capabilities (Config 2). Without OoO scheduling, IPC plummeted to {data['Config 2 (In-Order)']['IPC']:.3f} and execution time spiked by roughly 45%. <strong>Out-of-order execution significantly improves performance by enabling latency hiding through instruction-level parallelism (ILP) and memory-level parallelism (MLP).</strong> The O3 CPU allows the processor to overlap cache misses and maintain pipeline throughput while waiting on slow DRAM responses.</p>
    
    <p><strong>C. The L2 Cache Capacity Sensitivity</strong><br>
    Doubling the L2 cache size from 256kB to 512kB (Config 3) dropped the L2 MPKI by an imperceptible margin, yielding effectively identical IPC. <strong>Within the evaluated cache size range (256kB–512kB), performance shows minimal sensitivity to capacity, suggesting limited benefit from increasing L2 size for this workload.</strong> The recursive bounds swapping reduces temporal locality across recursive subproblems and introduces irregular access patterns that cache capacity scaling cannot resolve.</p>

    <p><strong>D. The Efficacy of Spatial Prefetching</strong><br>
    We attached a standard <code>StridePrefetcher</code> to the L2 Cache (Config 4) to exploit the sequential scans during the <code>partition()</code> loop. The IPC and L2 MPKI remained identical to the Baseline. We note that an identical IPC may indicate prefetcher ineffectiveness or underlying configuration limitations within the simulation. <strong>We hypothesize that stride prefetchers may fail here due to short sequential regions and irregular recursion boundaries.</strong> The sequential scans within <code>partition()</code> may be too short-lived to effectively train the prefetcher. Furthermore, the L1D cache naturally filters sequential accesses, meaning the L2 cache observes primarily the unpredictable, erratic bounds updates with limited spatial locality.</p>

    <h2>7. Qualitative PPA Analysis & Conclusion</h2>
    <p>Because synthesis tools (e.g., McPAT or CACTI) were not utilized, this is a qualitative assessment of Power, Performance, and Area (PPA) tradeoffs:</p>
    <ul>
        <li><strong>The 512kB L2 Upgrade:</strong> Doubling LLC capacity likely increases area and power due to larger SRAM structures. Given the near-zero performance gain, this is a poor architectural tradeoff for this specific workload.</li>
        <li><strong>The StridePrefetcher:</strong> Consumes area for tracking tables but provided zero measurable performance utility here, meaning it provides poor efficiency in this scenario.</li>
        <li><strong>The LTAGE Predictor:</strong> Demands an increase in SRAM storage for its history tables. However, by significantly reducing the Branch MPKI, it mitigates the dynamic power waste associated with flushing the pipeline and executing wrong-path instructions.</li>
    </ul>

    <div class="alert">
        <strong>Conclusion:</strong> The optimal architecture for executing Recursive Quicksort among the tested configurations is the <strong>O3CPU + LTAGE Predictor + 256kB L2 Cache</strong>. Out-of-order execution is highly effective at hiding the unavoidable L2 miss penalties through ILP and MLP. The LTAGE predictor stabilizes control flow, while the 256kB L2 avoids the diminishing returns of capacity over-scaling. Attempting to solve memory delays through brute-force cache scaling or simple spatial prefetching is ineffective for algorithms characterized by such mixed locality.
    </div>

</body>
</html>
"""

HTML(string=html).write_pdf("/workspace/Quicksort_Final_Report.pdf")
print("Successfully generated Quicksort_Final_Report.pdf with strict academic rigor!")
