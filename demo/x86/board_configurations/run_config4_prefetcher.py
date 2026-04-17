import os
from pathlib import Path
from gem5.components.boards.simple_board import SimpleBoard
from gem5.components.processors.simple_processor import SimpleProcessor
from gem5.components.cachehierarchies.classic.private_l1_private_l2_cache_hierarchy import PrivateL1PrivateL2CacheHierarchy
from gem5.components.memory.single_channel import SingleChannelDDR4_2400
from gem5.components.processors.cpu_types import CPUTypes
from gem5.isas import ISA
from gem5.simulate.simulator import Simulator
from gem5.resources.resource import BinaryResource
from m5.objects import StridePrefetcher
import m5

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

# Instead of checking names, just check the python class name
for obj in board.descendants():
    if type(obj).__name__ == "Cache": # gem5 stdlib caches are mostly just 'Cache' class but we can attach it to the L2 by checking its size
        try:
            if getattr(obj, "size", None) == "256kB":
                obj.prefetcher = StridePrefetcher()
        except:
            pass

binary_path = Path(__file__).parent.parent.parent / "programs" / "quicksort_100k_x86"
board.set_se_binary_workload(binary=BinaryResource(local_path=str(binary_path)))

outdir = m5.options.outdir
simulator = Simulator(board=board)
simulator.add_text_stats_output(os.path.join(outdir, "stats.txt"))

print("=== CONFIG 4: O3CPU + 256kB L2 + StridePrefetcher + n=100k ===")
simulator.run()
print("Config 4 simulation complete!")
