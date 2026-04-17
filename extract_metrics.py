#!/usr/bin/env python3
import re, os
import json

def parse_sections(filepath):
    with open(filepath) as f:
        content = f.read()
    raw = re.split(r'-{10} Begin Simulation Statistics -{10}', content)
    sections = []
    for sec in raw[1:]:
        end = re.search(r'-{10} End Simulation Statistics', sec)
        if end:
            sec = sec[:end.start()]
        stats = {}
        for line in sec.strip().splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            m = re.match(r'^(\S+)\s+([\d.\-naninf]+)', line)
            if m:
                try:
                    stats[m.group(1)] = float(m.group(2))
                except:
                    stats[m.group(1)] = m.group(2)
        if stats:
            sections.append(stats)
    return sections

def get(d, *keys, default=0.0):
    for k in keys:
        if k in d:
            return d[k]
    return default

configs = {
    'Baseline':  '/workspace/m5out_baseline/stats.txt',
    'Config 1 (LTAGE)':   '/workspace/m5out_config1/stats.txt',
    'Config 2 (In-Order)':   '/workspace/m5out_config2/stats.txt',
    'Config 3 (512k L2)':  '/workspace/m5out_config3/stats.txt',
    'Config 4 (Prefetch)':   '/workspace/m5out_config4/stats.txt',
}

results = {}

for name, path in configs.items():
    if not os.path.exists(path):
        print(f"Skipping {name}, no stats.txt found at {path}")
        continue
    
    secs = parse_sections(path)
    roi = secs[1] if len(secs) >= 2 else secs[0]

    # Core
    ipc   = get(roi, 'board.processor.cores.core.ipc', 'board.processor.cores.core.commitStats0.ipc')
    cpi   = get(roi, 'board.processor.cores.core.cpi', 'board.processor.cores.core.commitStats0.cpi')
    ticks = get(roi, 'simTicks')
    cycles= get(roi, 'board.processor.cores.core.numCycles')
    insts = get(roi, 'board.processor.cores.core.thread_0.numInsts', 'simInsts')
    kinsts= insts / 1000.0 if insts > 0 else 1.0
    
    # Branches
    committed = get(roi, 'board.processor.cores.core.branchPred.committed_0::total')
    mispred   = get(roi, 'board.processor.cores.core.branchPred.mispredicted_0::total')
    squashes  = get(roi, 'board.processor.cores.core.branchPred.squashes_0::total')
    branch_mpki = mispred / kinsts

    # Caches
    l2_demand_misses = get(roi, 'board.cache_hierarchy.l2cache.demandMisses::total', 'board.cache_hierarchy.l2-cache-0.demandMisses::total')
    l2_demand_accesses = get(roi, 'board.cache_hierarchy.l2cache.demandAccesses::total', 'board.cache_hierarchy.l2-cache-0.demandAccesses::total')
    l2_miss_rate = (l2_demand_misses / l2_demand_accesses * 100.0) if l2_demand_accesses > 0 else 0.0
    l2_mpki = l2_demand_misses / kinsts

    l1d_demand_misses = get(roi, 'board.cache_hierarchy.dcache.demandMisses::total', 'board.cache_hierarchy.l1d-cache-0.demandMisses::total')
    l1d_mpki = l1d_demand_misses / kinsts
    
    # OoO Stalls
    squashed_cycles = get(roi, 'board.processor.cores.core.squashedCycles')
    idle_cycles = get(roi, 'board.processor.cores.core.idleCycles')

    results[name] = {
        "IPC": ipc,
        "CPI": cpi,
        "Ticks_M": ticks / 1e6,
        "Branch_MPKI": branch_mpki,
        "L2_MPKI": l2_mpki,
        "L1D_MPKI": l1d_mpki,
        "L2_Miss_Rate": l2_miss_rate,
        "Squashes": squashes,
        "Squashed_Cycles": squashed_cycles,
        "Idle_Cycles": idle_cycles
    }

    print(f"=== {name} ===")
    print(f"  IPC: {ipc:.4f} | CPI: {cpi:.4f} | Ticks: {ticks/1e6:.1f}M")
    print(f"  Branch MPKI: {branch_mpki:.4f} | L2 MPKI: {l2_mpki:.4f} | L1D MPKI: {l1d_mpki:.4f}")
    print(f"  L2 Miss Rate: {l2_miss_rate:.2f}% | Squashed Cycles: {squashed_cycles}")
    print()

# Save for graphs
with open("/workspace/parsed_metrics.json", "w") as f:
    json.dump(results, f, indent=4)
