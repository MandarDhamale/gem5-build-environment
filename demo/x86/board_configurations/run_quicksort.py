import os
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

# THIS IS THE IMPORT THAT WAS MISSING
from m5.objects import InstCsvTrace

# Set up a Two-Level Cache Hierarchy
cache_hierarchy = PrivateL1PrivateL2CacheHierarchy(
    l1d_size="16kB", l1i_size="16kB", l2_size="256kB"
)

# Set up standard DDR4 Memory
memory = SingleChannelDDR4_2400()

# Set up an x86 Processor using the Timing model
processor = SimpleProcessor(cpu_type=CPUTypes.O3, isa=ISA.X86, num_cores=1)

# --- PROBE CONFIGURATION ---
inst_trace = InstCsvTrace()
inst_trace.trace_file = "inst_trace.csv"
inst_trace.trace_fetch = True

# Attach the probe to the first core of your processor
processor.cores[0].core.probeListener = inst_trace
# --------------------------

# Connect everything to the Motherboard
board = SimpleBoard(
    clk_freq="3GHz",
    processor=processor,
    memory=memory,
    cache_hierarchy=cache_hierarchy,
)

# Point the board to the compiled Quick Sort binary
binary_path = Path(__file__).parent.parent.parent / "programs" / "quicksort_x86"
board.set_se_binary_workload(binary=BinaryResource(local_path=str(binary_path)))

# Instantiate and run the simulator
simulator = Simulator(board=board)
print("Starting gem5 simulation...")
simulator.run()
print("Simulation complete!")