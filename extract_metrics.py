#!/usr/bin/env python3
import re, os

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
    'Baseline':  '/workspace/results/baseline/stats.txt',
    'Config1':   '/workspace/results/config_1/stats.txt',
    'Config2':   '/workspace/results/config_2/stats.txt',
    'Config3a':  '/workspace/results/config_3a/stats.txt',
    'Config3b':  '/workspace/results/config_3b/stats.txt',
    'Config4':   '/workspace/results/config_4/stats.txt',
}

for name, path in configs.items():
    secs = parse_sections(path)
    print("=" * 60)
    print("=== " + name + " --- " + str(len(secs)) + " sections, ROI section idx 1 ===")
    roi = secs[1] if len(secs) >= 2 else secs[0]

    ipc   = get(roi, 'board.processor.cores.core.ipc', 'board.processor.cores.core.commitStats0.ipc')
    cpi   = get(roi, 'board.processor.cores.core.cpi', 'board.processor.cores.core.commitStats0.cpi')
    ticks = get(roi, 'simTicks')
    cycles= get(roi, 'board.processor.cores.core.numCycles')
    insts = get(roi, 'board.processor.cores.core.thread_0.numInsts', 'simInsts')

    committed = get(roi, 'board.processor.cores.core.branchPred.committed_0::total')
    mispred   = get(roi, 'board.processor.cores.core.branchPred.mispredicted_0::total')
    lookups   = get(roi, 'board.processor.cores.core.branchPred.lookups_0::total')
    cond_wrong= get(roi, 'board.processor.cores.core.branchPred.condIncorrect')
    squashes  = get(roi, 'board.processor.cores.core.branchPred.squashes_0::total')

    bp_rate = (mispred / committed * 100) if committed > 0 else 0.0

    l1d = get(roi, 'board.cache_hierarchy.l1d-cache-0.demandMissRate::total')
    l1i = get(roi, 'board.cache_hierarchy.l1i-cache-0.demandMissRate::total')
    l2  = get(roi, 'board.cache_hierarchy.l2-cache-0.demandMissRate::total')

    print("  IPC=" + str(round(ipc,4)) + "  CPI=" + str(round(cpi,4)) +
          "  Ticks=" + str(int(ticks)) + "  Cycles=" + str(int(cycles)) + "  Insts=" + str(int(insts)))
    print("  BP Committed=" + str(int(committed)) + "  Mispredicted=" + str(int(mispred)) +
          "  Mispredict%=" + str(round(bp_rate,3)) + "%")
    print("  CondIncorrect=" + str(int(cond_wrong)) + "  Squashes=" + str(int(squashes)) +
          "  Lookups=" + str(int(lookups)))
    print("  L1D miss=" + str(round(l1d*100,3)) + "%  L1I miss=" + str(round(l1i*100,3)) +
          "%  L2 miss=" + str(round(l2*100,3)) + "%")
    print("")
