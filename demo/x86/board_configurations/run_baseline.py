"""
Baseline Configuration: x86 O3CPU @ 3GHz, 16kB L1 I/D, 256kB L2
Array size: 10,000 elements with ROI instrumentation
Branch predictor: TournamentBP (gem5 default)
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

# Cache hierarchy: 16kB L1 I/D, 256kB L2
cache_hierarchy = PrivateL1PrivateL2CacheHierarchy(
    l1d_size="16kB", l1i_size="16kB", l2_size="256kB"
)

# Standard DDR4 memory
memory = SingleChannelDDR4_2400()

# x86 O3CPU processor (uses TournamentBP by default)
processor = SimpleProcessor(cpu_type=CPUTypes.O3, isa=ISA.X86, num_cores=1)

board = SimpleBoard(
    clk_freq="3GHz",
    processor=processor,
    memory=memory,
    cache_hierarchy=cache_hierarchy,
)

# Point to the 10k instrumented binary
binary_path = Path(__file__).parent.parent.parent / "programs" / "quicksort_10k_x86"
board.set_se_binary_workload(binary=BinaryResource(local_path=str(binary_path)))

# Output stats
outdir = m5.options.outdir
simulator = Simulator(board=board)
simulator.add_text_stats_output(os.path.join(outdir, "stats.txt"))

print("=== BASELINE: O3CPU + TournamentBP + 256kB L2 + n=10,000 ===")
simulator.run()
print("Baseline simulation complete!")
