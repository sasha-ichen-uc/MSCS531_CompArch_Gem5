"""run_hello.py - run a "Hello, World!" x86 binary in gem5 (SE mode).

Adapted from the assignment handout for gem5 v25.1. Usage (from this folder):
    ../gem5/build/X86/gem5.opt run_hello.py [path/to/binary]
"""
import sys

import m5
from m5.objects import *


class L1Cache(Cache):
    """Simple L1 cache; L1_ICache / L1_DCache are not part of m5.objects."""

    assoc = 2
    tag_latency = 2
    data_latency = 2
    response_latency = 2
    mshrs = 4
    tgts_per_mshr = 20


class L1_ICache(L1Cache):
    pass


class L1_DCache(L1Cache):
    pass


binary = sys.argv[1] if len(sys.argv) > 1 else "hello"

# Create the system
system = System()
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = "1GHz"
system.clk_domain.voltage_domain = VoltageDomain()

# Memory configuration
system.mem_mode = "timing"
system.mem_ranges = [AddrRange("512MiB")]

# CPU configuration
system.cpu = TimingSimpleCPU()
system.cpu.icache = L1_ICache(size="32KiB")
system.cpu.dcache = L1_DCache(size="32KiB")

# Memory bus
system.membus = SystemXBar()

# CPU -> L1 caches -> memory bus
system.cpu.icache.cpu_side = system.cpu.icache_port
system.cpu.dcache.cpu_side = system.cpu.dcache_port
system.cpu.icache.mem_side = system.membus.cpu_side_ports
system.cpu.dcache.mem_side = system.membus.cpu_side_ports

# x86 needs its interrupt controller wired to the memory bus
system.cpu.createInterruptController()
system.cpu.interrupts[0].pio = system.membus.mem_side_ports
system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
system.cpu.interrupts[0].int_responder = system.membus.mem_side_ports

# DDR3 memory controller behind the memory bus
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports

# Let gem5 itself access memory (loads the program image)
system.system_port = system.membus.cpu_side_ports

# Workload: syscall-emulation of the x86 binary
system.workload = SEWorkload.init_compatible(binary)
process = Process()
process.cmd = [binary]
system.cpu.workload = process
system.cpu.createThreads()

# Run
root = Root(full_system=False, system=system)
m5.instantiate()
print("Beginning simulation!")
exit_event = m5.simulate()
print("Exiting @ tick {} because {}".format(m5.curTick(), exit_event.getCause()))
