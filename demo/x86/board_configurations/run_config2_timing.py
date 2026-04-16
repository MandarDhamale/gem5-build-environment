"""
Configuration 2: TimingSimpleCPU (In-Order)
Replaces O3CPU with TimingSimpleCPU to measure how much OOO execution
benefits the branch-heavy recursive Quicksort workload.
TimingSimpleCPU models every instruction sequentially with no speculation.
"""
import os
import sys
from pathlib import Path
from gem5.components.boards.simple_board import SimpleBoard
from gem5.components.processors.simple_processor import SimpleProcessor
from gem5.components.cachehierarchies.classic.private_l1_private_l2_cache_hierarchy import (
    PrivateL1PrivateL2CacheHierarchy,
)
from gem5.components.memory.single_channel import SingleChannelDDR4_2400
from gem5.components.processors.cpu_types import CPUTypes
from gem5.isas import ISA
from gem5.simulate.simulator import Simulator
from gem5.resources.resource import BinaryResource
import m5

cache_hierarchy = PrivateL1PrivateL2CacheHierarchy(
    l1d_size="16kB", l1i_size="16kB", l2_size="256kB"
)
memory = SingleChannelDDR4_2400()

# TimingSimpleCPU: single-issue in-order processor
processor = SimpleProcessor(cpu_type=CPUTypes.TIMING, isa=ISA.X86, num_cores=1)

board = SimpleBoard(
    clk_freq="3GHz",
    processor=processor,
    memory=memory,
    cache_hierarchy=cache_hierarchy,
)

binary_path = Path(__file__).parent.parent.parent / "programs" / "quicksort_10k_x86"
board.set_se_binary_workload(binary=BinaryResource(local_path=str(binary_path)))

outdir = m5.options.outdir
simulator = Simulator(board=board)
simulator.add_text_stats_output(os.path.join(outdir, "stats.txt"))

print("=== CONFIG 2: TimingSimpleCPU (In-Order) + 256kB L2 + n=10,000 ===")
simulator.run()
print("Config 2 simulation complete!")
