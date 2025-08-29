# Copyright (c) 2015 Jason Power
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

"""This file creates a single CPU and a two-level cache system.
This script takes a single parameter which specifies a binary to execute.
If none is provided it executes 'hello' by default (mostly used for testing)

See Part 1, Chapter 3: Adding cache to the configuration script in the
learning_gem5 book for more information about this script.
This file exports options for the L1 I/D and L2 cache sizes.

IMPORTANT: If you modify this file, it's likely that the Learning gem5 book
           also needs to be updated. For now, email Jason <power.jg@gmail.com>

"""

# import the m5 (gem5) library created when gem5 is built
import m5

# import all of the SimObjects
from m5.objects import *

# Add the common scripts to our path
m5.util.addToPath("../../")

# import the caches which we made
from caches import *

# import the SimpleOpts module
from common import SimpleOpts

# Default to running 'hello', use the compiled ISA to find the binary
# grab the specific path to the binary
thispath = os.path.dirname(os.path.realpath(__file__))
# default_binary = os.path.join(
#     thispath,
#     "../../../",
#     "tests/test-progs/hello/bin/x86/linux/hello",
# )
# default_binary = os.path.join(
#     thispath,
#     "../../../../",
#     "cs251a-microbench/spmv",
# )
default_binary = os.path.join(
    "../../build/build_base_mytest-m64.0000/lbm_r",
)
default_option="3000 reference.dat 0 0 100_100_130_ldc.of"

# Binary to execute
SimpleOpts.add_option("--cmd", nargs="?", default=default_binary)
SimpleOpts.add_option("--maxtime",nargs="?", default="0.1") #100ms
SimpleOpts.add_option("--options", nargs="?", default=default_option)
SimpleOpts.add_option("--num-cpus", nargs="?", default=4)
# Finalize the arguments and grab the args so we can pass it on to our objects
args = SimpleOpts.parse_args()
num_cpus = int(args.num_cpus)
# create the system we are going to simulate
system = System()

# Set the clock frequency of the system (and all of its children)
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = "4.2GHz"
system.clk_domain.voltage_domain = VoltageDomain()

# Set up the system
system.mem_mode = "timing"  # Use timing accesses
system.mem_ranges = [AddrRange("16GB")] # Match this value with DRAM capacity specified in the RAMULATOR2 config file

# Create a simple CPU
system.cpu = [DerivO3CPU() for i in range(num_cpus)]

for i in range(num_cpus):
    system.cpu[i].icache = L1ICache()
    system.cpu[i].icache.size="16kB"
    system.cpu[i].dcache = L1DCache()
    system.cpu[i].dcache.size="16kB"
    system.cpu[i].icache.connectCPU(system.cpu[i])
    system.cpu[i].dcache.connectCPU(system.cpu[i])
# Create an L1 instruction and data cache


# system.cpu.icache = L1ICache(args)
# system.cpu.dcache = L1DCache(args)

# # Connect the instruction and data caches to the CPU
# system.cpu.icache.connectCPU(system.cpu)
# system.cpu.dcache.connectCPU(system.cpu)

# Create a memory bus, a coherent crossbar, in this case
system.l2bus = L2XBar()

for i in range(num_cpus):
    system.cpu[i].icache.connectBus(system.l2bus)
    system.cpu[i].dcache.connectBus(system.l2bus)

# # Hook the CPU ports up to the l2bus
# system.cpu.icache.connectBus(system.l2bus)
# system.cpu.dcache.connectBus(system.l2bus)

# Create an L2 cache and connect it to the l2bus
system.l2cache = L2Cache(args)
system.l2cache.connectCPUSideBus(system.l2bus)
system.l2cache.size="512kB"
system.l2cache.assoc=8

# Create a memory bus
system.membus = SystemXBar()

# Connect the L2 cache to the membus
system.l2cache.connectMemSideBus(system.membus)

# # create the interrupt controller for the CPU
for i in range(num_cpus):
    system.cpu[i].createInterruptController()
    system.cpu[i].interrupts[0].pio = system.membus.mem_side_ports
    system.cpu[i].interrupts[0].int_requestor = system.membus.cpu_side_ports
    system.cpu[i].interrupts[0].int_responder = system.membus.mem_side_ports

# Connect the system up to the membus
system.system_port = system.membus.cpu_side_ports

# Create a DDR3 memory controller
system.mem_ctrl = Ramulator2()
system.mem_ctrl.port = system.membus.mem_side_ports
system.mem_ctrl.config_path = "/gem5/gem5/ext/ramulator2/example_config.yaml"
system.mem_ctrl.range= system.mem_ranges[0]  # Match this value with DRAM capacity specified in the RAMULATOR2 config file
# system.dram=DRAMSim2()
# system.dram.port=system.membus.mem_side_ports
# system.dram.deviceConfigFile = "ini/DDR3_micron_16M_8B_x8_sg15.ini"
# system.mem_ctrls = MemCtrl()
# system.mem_ctrls.dram = DDR5_8400_4x8()
# system.mem_ctrls.dram.range = AddrRange("8GB")
# system.mem_ctrls.port = system.membus.mem_side_ports

# system.kvm_vm = KvmVM()
# system.m5ops_base = max(0xFFFF0000, system.mem_ranges[0].size())

procs=[]
# Create a process for a simple "Hello World" application
# process.useArchPT = True
# process.kvmInSE = True
# Set the command
# cmd is a list which begins with the executable (like argv)
# process.maxStackSize = "1MB"  # Set the maximum stack size
# Set the cpu to use the process as its workload and create thread contexts
for i in range(4):
    p = Process(pid=100 + i)
    p.cmd = [args.cmd] + args.options.split()
    procs.append(p)
    system.cpu[i].workload = p
    system.cpu[i].createThreads()


system.workload = SEWorkload.init_compatible(args.cmd)

# set up the root SimObject and start the simulation
root = Root(full_system=False, system=system)
# instantiate all of the objects we've created above
m5.instantiate()
if(type(args.maxtime)==str):
    args.maxtime = float(args.maxtime)

print(f"Beginning simulation!")
print(f"maxticks= {m5.ticks.fromSeconds(args.maxtime)}")
m5.scheduleTickExitAbsolute(m5.ticks.fromSeconds(args.maxtime))
exit_event = m5.simulate()

print(f"Exiting @ tick {m5.curTick()} because {exit_event.getCause()}")
