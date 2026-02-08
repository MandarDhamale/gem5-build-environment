from gem5.components.boards.arm_board import ArmBoard
from gem5.components.cachehierarchies.classic.private_l1_private_l2_cache_hierarchy import (
    PrivateL1PrivateL2CacheHierarchy,
)
from gem5.components.memory.single_channel import SingleChannelDDR3_1600
from gem5.components.processors.cpu_types import CPUTypes
from gem5.components.processors.simple_switchable_processor import (
    SimpleSwitchableProcessor,
)
from gem5.isas import ISA
from gem5.resources.resource import obtain_resource
from gem5.simulate.exit_event import ExitEvent
from gem5.simulate.simulator import Simulator

cache_hierarchy = PrivateL1PrivateL2CacheHierarchy(
    l1d_size="16kB", l1i_size="16kB", l2_size="256kB"
)

memory = SingleChannelDDR3_1600(size="4GB")

processor = SimpleSwitchableProcessor(
    starting_core_type=CPUTypes.TIMING,
    switch_core_type=CPUTypes.O3,
    isa=ISA.ARM,
    num_cores=2,
)

board = ArmBoard(
    clk_freq="3GHz",
    processor=processor,
    memory=memory,
    cache_hierarchy=cache_hierarchy,
)

board.set_workload(obtain_resource("arm64-ubuntu-20.04-boot"))

simulator = Simulator(board=board)
simulator.run()
