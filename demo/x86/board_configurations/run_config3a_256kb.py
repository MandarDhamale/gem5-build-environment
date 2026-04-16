"""
Configuration 3a: L2 Cache Thrashing - 256kB L2, n=100,000
Large array (100k elements = ~400kB) exceeds the 256kB L2 cache,
causing significant cache thrashing during the recursive partition passes.
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

# Baseline L2 size of 256kB (too small for 100k int array = 400kB)
cache_hierarchy = PrivateL1PrivateL2CacheHierarchy(
    l1d_size="16kB", l1i_size="16kB", l2_size="256kB"
)
memory = SingleChannelDDR4_2400()
processor = SimpleProcessor(cpu_type=CPUTypes.O3, isa=ISA.X86, num_cores=1)

board = SimpleBoard(
    clk_freq="3GHz",
    processor=processor,
    memory=memory,
    cache_hierarchy=cache_hierarchy,
)

# Use the 100k element binary
binary_path = Path(__file__).parent.parent.parent / "programs" / "quicksort_100k_x86"
board.set_se_binary_workload(binary=BinaryResource(local_path=str(binary_path)))

outdir = m5.options.outdir
simulator = Simulator(board=board)
simulator.add_text_stats_output(os.path.join(outdir, "stats.txt"))

print("=== CONFIG 3a: O3CPU + 256kB L2 (thrashing) + n=100,000 ===")
simulator.run()
print("Config 3a simulation complete!")
