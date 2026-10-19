"""smt.py - Task 5: Simultaneous Multithreading (SMT) simulation.

Runs one or two threads on an O3CPU with SMT enabled to measure
resource sharing and overall throughput improvement.

Note: gem5 x86 SE mode uses a hardcoded stack base (0x7FFFFFFFF000) for
all processes. Two *different* binaries collide at that address when sharing
the page table (multi_thread=True). We therefore run two copies of the
same binary, which is the standard SMT micro-benchmark approach — it
isolates the effect of resource contention from workload differences.

Usage:
  # Single thread baseline:
  gem5.opt --outdir=DIR smt.py BINARY
  # Two-thread SMT (same binary, two instances):
  gem5.opt --outdir=DIR smt.py BINARY --threads 2
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
parser = argparse.ArgumentParser(description="SMT simulation")
parser.add_argument("binary", help="Static x86-64 ELF to simulate")
parser.add_argument("--threads", type=int, choices=[1, 2], default=1,
                    help="Number of SMT threads (both run the same binary)")
args = parser.parse_args()

num_threads = args.threads

# ---------------------------------------------------------------------------
# System
# ---------------------------------------------------------------------------
system = System()
system.clk_domain = SrcClockDomain(clock="1GHz",
                                   voltage_domain=VoltageDomain())
system.mem_mode = "timing"
system.mem_ranges = [AddrRange("512MiB")]

# Required for multi-threaded (SMT) simulation
if num_threads > 1:
    system.multi_thread = True

# O3CPU with SMT support
system.cpu = X86O3CPU()
system.cpu.numThreads = num_threads

# Use default width-8 for SMT to give both threads room
system.cpu.fetchWidth = 8
system.cpu.decodeWidth = 8
system.cpu.renameWidth = 8
system.cpu.issueWidth = 8
system.cpu.dispatchWidth = 8
system.cpu.commitWidth = 8

# Generous structures for two threads
system.cpu.numROBEntries = 256
system.cpu.LQEntries = 64
system.cpu.SQEntries = 64
system.cpu.numPhysIntRegs = 256
system.cpu.numPhysFloatRegs = 256

# IQ entries (gem5 ≥ 25.1 uses IQUnit objects)
for iq in system.cpu.instQueues:
    iq.numEntries = 128

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
for i in range(num_threads):
    system.cpu.interrupts[i].pio = system.membus.mem_side_ports
    system.cpu.interrupts[i].int_requestor = system.membus.cpu_side_ports
    system.cpu.interrupts[i].int_responder = system.membus.mem_side_ports

# Memory controller
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports
system.system_port = system.membus.cpu_side_ports

# Workload — run the same binary on each thread (avoids x86 stack collision)
system.workload = SEWorkload.init_compatible(args.binary)
workloads = []
for i in range(num_threads):
    process = Process(pid=100 + i, cmd=[args.binary])
    workloads.append(process)
system.cpu.workload = workloads if num_threads > 1 else workloads[0]
system.cpu.createThreads()

# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
root = Root(full_system=False, system=system)
m5.instantiate()
print(f"Beginning simulation (O3CPU SMT, {num_threads} thread(s))...")
exit_event = m5.simulate()
print(f"Exiting @ tick {m5.curTick()} because {exit_event.getCause()}")
