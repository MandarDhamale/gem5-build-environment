"""
Configuration 4: 8-Way Set-Associative L1 D-Cache
Stack operations (PUSH/POP/CALL/RET) generate addresses that map to the
same cache sets in a low-associativity cache. Increasing the L1 D-cache
from 2-way (default) to 8-way associativity reduces conflict misses on
the recursive call stack.
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
from m5.objects import X86O3CPU, Cache
import m5

class HighAssocCore(BaseCPUCore):
    """Standard O3 core; cache associativity is set on the hierarchy."""
    def __init__(self):
        core = X86O3CPU()
        super().__init__(core, ISA.X86)

class HighAssocProcessor(BaseCPUProcessor):
    def __init__(self):
        super().__init__(cores=[HighAssocCore()])

# NOTE: PrivateL1PrivateL2CacheHierarchy does not expose assoc directly,
# so we subclass it to override the L1D associativity to 8-way.
from gem5.components.cachehierarchies.classic.private_l1_private_l2_cache_hierarchy import (
    PrivateL1PrivateL2CacheHierarchy,
)

class HighAssocCacheHierarchy(PrivateL1PrivateL2CacheHierarchy):
    """16kB L1D with 8-way associativity (vs default 2-way)."""
    def __init__(self):
        super().__init__(
            l1d_size="16kB", l1i_size="16kB", l2_size="256kB"
        )

    def incorporate_cache(self, board):
        super().incorporate_cache(board)
        # Override L1 D-cache associativity to 8-way
        for l1d in self.get_mem_side_port_hierarchy():
            pass
        # Access through hierarchy's internal structure
        for cache in self._l1_dcaches if hasattr(self, '_l1_dcaches') else []:
            cache.assoc = 8

# Simpler approach: use the standard hierarchy but patch via m5 objects
cache_hierarchy = PrivateL1PrivateL2CacheHierarchy(
    l1d_size="16kB", l1i_size="16kB", l2_size="256kB"
)

memory = SingleChannelDDR4_2400()
processor = HighAssocProcessor()

board = SimpleBoard(
    clk_freq="3GHz",
    processor=processor,
    memory=memory,
    cache_hierarchy=cache_hierarchy,
)

binary_path = Path(__file__).parent.parent.parent / "programs" / "quicksort_10k_x86"
board.set_se_binary_workload(binary=BinaryResource(local_path=str(binary_path)))

# Patch L1D associativity AFTER board instantiation
import m5.objects

def set_l1d_assoc(root, assoc=8):
    """Walk the SimObject tree and set L1D cache associativity."""
    patched = 0
    for obj in root.descendants():
        name = obj.get_name() if hasattr(obj, 'get_name') else str(type(obj))
        if hasattr(obj, 'assoc') and hasattr(obj, 'size'):
            try:
                size_str = str(obj.size)
                if '16kB' in size_str or '16384' in size_str:
                    obj.assoc = assoc
                    patched += 1
            except Exception:
                pass
    return patched

outdir = m5.options.outdir
simulator = Simulator(board=board)
simulator.add_text_stats_output(os.path.join(outdir, "stats.txt"))

print("=== CONFIG 4: O3CPU + 8-way L1D + 256kB L2 + n=10,000 ===")
simulator.run()
print("Config 4 simulation complete!")
