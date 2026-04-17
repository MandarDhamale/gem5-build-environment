import m5
from gem5.components.boards.simple_board import SimpleBoard
from gem5.components.processors.simple_processor import SimpleProcessor
from gem5.components.cachehierarchies.classic.private_l1_private_l2_cache_hierarchy import PrivateL1PrivateL2CacheHierarchy
from gem5.components.memory.single_channel import SingleChannelDDR4_2400
from gem5.components.processors.cpu_types import CPUTypes
from gem5.isas import ISA

ch = PrivateL1PrivateL2CacheHierarchy("16kB", "16kB", "256kB")
processor = SimpleProcessor(cpu_type=CPUTypes.O3, isa=ISA.X86, num_cores=1)
board = SimpleBoard("3GHz", processor, SingleChannelDDR4_2400(), ch)
print("Board components:")
for name in dir(board):
    if "cache" in name.lower() or "l2" in name.lower():
        print(name)
print("Hierarchy:")
for name in dir(ch):
    if "l2" in name.lower():
        print(name)
