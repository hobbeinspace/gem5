# Copyright (c) 2022 The Regents of the University of California.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met: redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer;
# redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution;
# neither the name of the copyright holders nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
Hands-on Session 1: Modifying the base system.
-------------------------------------------
This is a completed renscript file.

This is a simple script to run the a binary program using the SimpleBoard.
We will use x86 ISA for this example. This script is partly taken from
configs/example/gem5_library/arm-hello.py

* Limitations *
---------------
1. We are only simulating workloads with one CPU core.
2. The binary cannot accept any arguments.

Usage:
------

```
scons build/X86/gem5.opt -j<num_proc>
./build/X86/gem5.opt base-system.py --binary <path/to/binary>
```
"""

# Importing the required python packages here

import os
import argparse
# We need to first determine which ISA that we want to use. Then we have to
# make sure that we are using the correct ISA while executing this script.
from gem5.isas import ISA
from gem5.utils.requires import requires
from gem5.resources.resource import CustomResource
# We import various parameters of the machine.
from gem5.components.cachehierarchies.classic\
    .private_l1_private_l2_cache_hierarchy import (
    PrivateL1PrivateL2CacheHierarchy,
)

from gem5.components.memory.ramulator_2 import Ramulator2System
from gem5.components.processors.cpu_types import CPUTypes
from gem5.components.boards.x86_board import X86Board
from gem5.components.boards.simple_board import SimpleBoard
from gem5.components.processors.simple_switchable_processor import SimpleSwitchableProcessor
from gem5.components.processors.simple_processor import SimpleProcessor
# We will use the new simulator module to simulate this task.
from gem5.simulate.simulator import Simulator
from gem5.simulate.exit_event import ExitEvent
from m5.util import fatal

# import the m5 (gem5) library created when gem5 is built
import m5

# import all of the SimObjects
from m5.objects import *

# Add the common scripts to our path
m5.util.addToPath("../../")

# import the SimpleOpts module
from common import SimpleOpts

# We are using argparse to supply the path to the binary.
thispath = os.path.dirname(os.path.realpath(__file__))
default_binary = os.path.join(
    "../../build/build_base_mytest-m64.0000/lbm_r",
)
default_option="3000 reference.dat 0 0 100_100_130_ldc.of"

# Binary to execute
SimpleOpts.add_option("--binary", nargs="?", default=default_binary)
SimpleOpts.add_option("--maxtime",nargs="?", default="0.1") #100ms
SimpleOpts.add_option("--options", nargs="?", default=default_option)
# Finalize the arguments and grab the args so we can pass it on to our objects
args = SimpleOpts.parse_args()
cache_hierarchy = AbstractThreeLevelCacheHierarchy(
    l1d_size="32kB",
    l1d_assoc=4,
    l1i_assoc=4,
    l1i_size="32kB",
    l2_size="256kB",
    l2_assoc=8,
    l3_size="8MB",
    l3_assoc=8
)

# Use
memory = Ramulator2System("ext/ramulator2/example_config.yaml", "ramulator_out", "16GB")

processor = SimpleProcessor(
    cpu_type=CPUTypes.O3,
    isa=ISA.X86,
    num_cores=4
)

#board = X86Board(
board = SimpleBoard(
    clk_freq = "4.2GHz",
    processor = processor,
    memory = memory,
    cache_hierarchy = cache_hierarchy,
)

# Set SE mode binary workload
print("Start setting binary to board")
board.set_se_binary_workload(
    binary=args.binary,
    args=args.options.split()
)
if(type(args.maxtime)==str):
    args.maxtime = float(args.maxtime)
# Lastly we instantiate the simulator module and simulate the program.
print("set simulator")
simulator = Simulator(board=board)
simulator.set_max_tick(m5.ticks.fromSeconds(args.maxtime))
simulator.run()

# We acknowlwdge the user that the simulation has ended.
print(
    "Exiting @ tick {} because {}.".format(
        simulator.get_current_tick(),
        simulator.get_last_exit_event_cause(),
    )
)