"""pipeline_basic.py - Task 1 & 2: Basic in-order pipeline simulation.

Configures an X86 MinorCPU (in-order, 5-stage pipeline: fetch, decode,
execute, memory, writeback) with L1 caches, runs a workload in SE mode,
and collects throughput / latency metrics from stats.txt.

Usage:
  gem5.opt [--outdir=DIR] pipeline_basic.py BINARY
"""
import argparse
import m5
from m5.objects import *


# ---------------------------------------------------------------------------
# Cache hierarchy
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
parser = argparse.ArgumentParser(description="Basic in-order pipeline sim")
parser.add_argument("binary", help="Static x86-64 ELF to simulate")
args = parser.parse_args()

# ---------------------------------------------------------------------------
# System
# ---------------------------------------------------------------------------
system = System()
system.clk_domain = SrcClockDomain(clock="1GHz",
                                   voltage_domain=VoltageDomain())
system.mem_mode = "timing"
system.mem_ranges = [AddrRange("512MiB")]

# MinorCPU: gem5's in-order pipeline model (fetch → decode → execute → mem → WB)
system.cpu = X86MinorCPU()

# L1 caches
system.cpu.icache = L1ICache()
system.cpu.dcache = L1DCache()

# Interconnect
system.membus = SystemXBar()
system.cpu.icache.cpu_side = system.cpu.icache_port
system.cpu.dcache.cpu_side = system.cpu.dcache_port
system.cpu.icache.mem_side = system.membus.cpu_side_ports
system.cpu.dcache.mem_side = system.membus.cpu_side_ports

# Interrupt controller (required for X86)
system.cpu.createInterruptController()
system.cpu.interrupts[0].pio = system.membus.mem_side_ports
system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
system.cpu.interrupts[0].int_responder = system.membus.mem_side_ports

# Memory controller
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports
system.system_port = system.membus.cpu_side_ports

# Workload
system.workload = SEWorkload.init_compatible(args.binary)
process = Process(cmd=[args.binary])
system.cpu.workload = process
system.cpu.createThreads()

# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
root = Root(full_system=False, system=system)
m5.instantiate()
print("Beginning simulation (MinorCPU in-order pipeline)...")
exit_event = m5.simulate()
print(f"Exiting @ tick {m5.curTick()} because {exit_event.getCause()}")
