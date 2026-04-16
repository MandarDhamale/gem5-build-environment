#!/usr/bin/env python3
"""
Parse gem5 stats.txt files and extract key metrics from each ROI section.
When m5_dump_reset_stats is called, gem5 creates multiple stat sections:
  Section 1: Pre-sorting initialization
  Section 2: The quickSort ROI (the one we care about)
  Section 3: Post-sorting cleanup
"""
import re
import sys
import os

def parse_stats_sections(filepath):
    """Parse stats.txt into discrete sections separated by headers."""
    sections = []
    current = {}
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Split by Begin Simulation Statistics
    raw_sections = re.split(r'-{10} Begin Simulation Statistics -{10}', content)
    
    for sec in raw_sections[1:]:  # skip first empty piece
        # Only process until End Simulation Statistics
        end_match = re.search(r'-{10} End Simulation Statistics', sec)
        if end_match:
            sec = sec[:end_match.start()]
        
        stats = {}
        for line in sec.strip().splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            # Match: stat_name   value   # comment
            m = re.match(r'^(\S+)\s+([\d.\-naninf]+)', line)
            if m:
                key, val = m.group(1), m.group(2)
                try:
                    stats[key] = float(val)
                except ValueError:
                    stats[key] = val
        if stats:
            sections.append(stats)
    
    return sections

def extract_roi_stats(stats_dict):
    """Extract key metrics from a stats section dict."""
    def get(keys, default=0.0):
        for k in keys:
            if k in stats_dict:
                return stats_dict[k]
        return default
    
    ipc = get(['board.processor.cores.core.ipc',
                'board.processor.cores.core.commitStats0.ipc'])
    cpi = get(['board.processor.cores.core.cpi',
                'board.processor.cores.core.commitStats0.cpi'])
    ticks = get(['simTicks'])
    cycles = get(['board.processor.cores.core.numCycles'])
    insts = get(['board.processor.cores.core.thread_0.numInsts',
                  'simInsts'])
    
    branch_mispredict = get([
        'board.processor.cores.core.commit.branchMispredicts',
        'board.processor.cores.core.iew.branchMispredicts'
    ])
    total_branches = get([
        'board.processor.cores.core.commit.branches',
        'board.processor.cores.core.commitStats0.numBranchInsts'
    ])
    branch_mispredict_rate = (branch_mispredict / total_branches 
                               if total_branches > 0 else float('nan'))
    
    l1d_miss_rate = get(['board.cache_hierarchy.l1d-cache-0.demandMissRate::total'])
    l1i_miss_rate = get(['board.cache_hierarchy.l1i-cache-0.demandMissRate::total'])
    l2_miss_rate = get(['board.cache_hierarchy.l2-cache-0.demandMissRate::total'])
    
    return {
        'ipc': ipc, 'cpi': cpi, 'ticks': ticks, 'cycles': cycles,
        'insts': insts,
        'branch_mispredict': int(branch_mispredict),
        'total_branches': int(total_branches),
        'branch_mispredict_rate': branch_mispredict_rate,
        'l1d_miss_rate': l1d_miss_rate,
        'l1i_miss_rate': l1i_miss_rate,
        'l2_miss_rate': l2_miss_rate,
    }

# Configurations to analyze
configs = {
    'Baseline (O3+Tournament, n=10k)': '/workspace/results/baseline/stats.txt',
    'Config1 (O3+LTAGE, n=10k)':       '/workspace/results/config_1/stats.txt',
    'Config2 (Timing/InOrder, n=10k)': '/workspace/results/config_2/stats.txt',
    'Config3a (O3+256kL2, n=100k)':    '/workspace/results/config_3a/stats.txt',
    'Config3b (O3+512kL2, n=100k)':    '/workspace/results/config_3b/stats.txt',
    'Config4 (O3+8wayL1D, n=10k)':     '/workspace/results/config_4/stats.txt',
}

print("=" * 90)
print("gem5 Quicksort Simulation Results - ROI Section Analysis")
print("=" * 90)

all_results = {}
for name, path in configs.items():
    if not os.path.exists(path):
        print(f"\n[MISSING] {name}: {path}")
        continue
    
    sections = parse_stats_sections(path)
    print(f"\n[{name}] - {len(sections)} stat sections found")
    
    # The ROI sorting phase is typically the 2nd section
    # (section 1 = init, section 2 = sort ROI, section 3 = cleanup)
    roi_idx = 1 if len(sections) >= 2 else 0
    roi = extract_roi_stats(sections[roi_idx])
    all_results[name] = roi
    
    print(f"  IPC:                     {roi['ipc']:.4f}")
    print(f"  CPI:                     {roi['cpi']:.4f}")
    print(f"  Sim Ticks (total):       {roi['ticks']:,.0f}")
    print(f"  Cycles:                  {roi['cycles']:,.0f}")
    print(f"  Branch Mispredicts:      {roi['branch_mispredict']:,}")
    if roi['total_branches'] > 0:
        print(f"  Branch Mispredict Rate:  {roi['branch_mispredict_rate']:.4f} ({roi['branch_mispredict_rate']*100:.2f}%)")
    print(f"  L1D Miss Rate:           {roi['l1d_miss_rate']:.4f} ({roi['l1d_miss_rate']*100:.2f}%)")
    print(f"  L1I Miss Rate:           {roi['l1i_miss_rate']:.4f} ({roi['l1i_miss_rate']*100:.2f}%)")
    print(f"  L2 Miss Rate:            {roi['l2_miss_rate']:.4f} ({roi['l2_miss_rate']*100:.2f}%)")

print("\n" + "=" * 90)
print("SUMMARY TABLE")
print("=" * 90)
print(f"{'Config':<40} {'IPC':>7} {'Ticks':>14} {'BranchMis%':>12} {'L1D%':>8} {'L2%':>8}")
print("-" * 90)
for name, roi in all_results.items():
    bmp = roi['branch_mispredict_rate']*100 if roi['total_branches'] > 0 else float('nan')
    print(f"{name:<40} {roi['ipc']:>7.4f} {roi['ticks']:>14,.0f} {bmp:>11.2f}% {roi['l1d_miss_rate']*100:>6.2f}% {roi['l2_miss_rate']*100:>6.2f}%")
print("=" * 90)
