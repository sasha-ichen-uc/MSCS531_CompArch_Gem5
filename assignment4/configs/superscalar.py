"""superscalar.py - Task 4: Multiple-issue (superscalar) simulation.

Configures an O3CPU with variable issue width (1, 2, 4, 8) to measure
the performance gains from superscalar execution.

Usage:
  gem5.opt --outdir=DIR superscalar.py BINARY --width {1,2,4,8}
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
parser = argparse.ArgumentParser(description="Superscalar width comparison")
parser.add_argument("binary")
parser.add_argument("--width", type=int, choices=[1, 2, 4, 8], default=4)
args = parser.parse_args()

# ---------------------------------------------------------------------------
# System
# ---------------------------------------------------------------------------
system = System()
system.clk_domain = SrcClockDomain(clock="1GHz",
                                   voltage_domain=VoltageDomain())
system.mem_mode = "timing"
system.mem_ranges = [AddrRange("512MiB")]

# O3CPU with configurable pipeline widths
system.cpu = X86O3CPU()
w = args.width
system.cpu.fetchWidth = w
system.cpu.decodeWidth = w
system.cpu.renameWidth = w
system.cpu.issueWidth = w
system.cpu.dispatchWidth = w
system.cpu.commitWidth = w

# Scale ROB/LQ/SQ/registers to match width so narrow configs aren't
# bottlenecked by structures sized for width-8
system.cpu.numROBEntries = max(32, 32 * w)
system.cpu.LQEntries = max(16, 8 * w)
system.cpu.SQEntries = max(16, 8 * w)
system.cpu.numPhysIntRegs = max(64, 64 * (w // 2 + 1))
system.cpu.numPhysFloatRegs = max(64, 64 * (w // 2 + 1))

# IQ entries are set on the IQUnit objects (gem5 ≥ 25.1)
for iq in system.cpu.instQueues:
    iq.numEntries = max(16, 16 * w)

# L1 caches
system.cpu.icache = L1ICache()
system.cpu.dcache = L1DCache()

# Interconnect
system.membus = SystemXBar()
system.cpu.icache.cpu_side = system.cpu.icache_port
system.cpu.dcache.cpu_side = system.cpu.dcache_port
system.cpu.icache.mem_side = system.membus.cpu_side_ports
system.cpu.dcache.mem_side = system.membus.cpu_side_ports

# Interrupt controller
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
print(f"Beginning simulation (O3CPU, issue width: {w})...")
exit_event = m5.simulate()
print(f"Exiting @ tick {m5.curTick()} because {exit_event.getCause()}")
