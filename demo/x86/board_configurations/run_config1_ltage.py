"""
Configuration 1: LTAGE Branch Predictor
Same as baseline but with LTAGE predictor instead of TournamentBP.
Hypothesis: LTAGE's longer history tables should better predict the
recursive branches in Quicksort.
"""
import os
import sys
from pathlib import Path
from gem5.components.boards.simple_board import SimpleBoard
from gem5.components.cachehierarchies.classic.private_l1_private_l2_cache_hierarchy import (
    PrivateL1PrivateL2CacheHierarchy,
)
from gem5.components.memory.single_channel import SingleChannelDDR4_2400
from gem5.resources.resource import BinaryResource
from gem5.simulate.simulator import Simulator
from gem5.isas import ISA

from gem5.components.processors.base_cpu_core import BaseCPUCore
from gem5.components.processors.base_cpu_processor import BaseCPUProcessor
from m5.objects import X86O3CPU, LTAGE
import m5

class LTAGECore(BaseCPUCore):
    """O3 CPU core with LTAGE branch predictor."""
    def __init__(self):
        core = X86O3CPU()
        core.branchPred = LTAGE()
        super().__init__(core, ISA.X86)

class LTAGEProcessor(BaseCPUProcessor):
    def __init__(self):
        super().__init__(cores=[LTAGECore()])

cache_hierarchy = PrivateL1PrivateL2CacheHierarchy(
    l1d_size="16kB", l1i_size="16kB", l2_size="256kB"
)
memory = SingleChannelDDR4_2400()
processor = LTAGEProcessor()

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

print("=== CONFIG 1: O3CPU + LTAGE Branch Predictor + 256kB L2 + n=10,000 ===")
simulator.run()
print("Config 1 simulation complete!")
