"""run_membench.py - run a static x86 binary in gem5 SE mode with
configurable L1 data cache and TLB parameters.

Usage (from assignment3/):
  ../gem5/build/X86/gem5.opt run_membench.py BINARY \
      [--l1d-size 32KiB] [--l1d-assoc 2] [--block-size 64] [--tlb-size 64]
"""
import argparse

import m5
from m5.objects import *


class L1Cache(Cache):
    assoc = 2
    tag_latency = 2
    data_latency = 2
    response_latency = 2
    mshrs = 4
    tgts_per_mshr = 20


class L1ICache(L1Cache):
    size = "32KiB"


class L1DCache(L1Cache):
    size = "32KiB"


parser = argparse.ArgumentParser()
parser.add_argument("binary")
parser.add_argument("--l1d-size", default="32KiB")
parser.add_argument("--l1d-assoc", type=int, default=2)
parser.add_argument("--block-size", type=int, default=64)
parser.add_argument("--tlb-size", type=int, default=64)
args = parser.parse_args()

system = System()
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = "1GHz"
system.clk_domain.voltage_domain = VoltageDomain()
system.cache_line_size = args.block_size
system.mem_mode = "timing"
system.mem_ranges = [AddrRange("512MiB")]

system.cpu = TimingSimpleCPU()
system.cpu.icache = L1ICache()
system.cpu.dcache = L1DCache(size=args.l1d_size, assoc=args.l1d_assoc)
system.cpu.itb = X86TLB(size=args.tlb_size, entry_type="instruction")
system.cpu.dtb = X86TLB(size=args.tlb_size, entry_type="data")

system.membus = SystemXBar()
system.cpu.icache.cpu_side = system.cpu.icache_port
system.cpu.dcache.cpu_side = system.cpu.dcache_port
system.cpu.icache.mem_side = system.membus.cpu_side_ports
system.cpu.dcache.mem_side = system.membus.cpu_side_ports

system.cpu.createInterruptController()
system.cpu.interrupts[0].pio = system.membus.mem_side_ports
system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
system.cpu.interrupts[0].int_responder = system.membus.mem_side_ports

system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports
system.system_port = system.membus.cpu_side_ports

system.workload = SEWorkload.init_compatible(args.binary)
process = Process()
process.cmd = [args.binary]
system.cpu.workload = process
system.cpu.createThreads()

root = Root(full_system=False, system=system)
m5.instantiate()
print("Beginning simulation!")
exit_event = m5.simulate()
print("Exiting @ tick {} because {}".format(m5.curTick(), exit_event.getCause()))
