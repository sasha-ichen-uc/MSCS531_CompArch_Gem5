"""branch_prediction.py - Task 3: Impact of branch prediction.

Runs the same workload on an O3CPU with different branch predictors
to compare pipeline efficiency with/without effective prediction.

In gem5 25.1 the branch-predictor hierarchy is:
  BranchPredictor  (top-level: BTB + RAS + conditional + indirect)
    └─ conditionalBranchPred = ConditionalPredictor subclass
         (LocalBP, TournamentBP, BiModeBP, TAGE, LTAGE, TAGE_SC_L_64KB...)
  GshareBP is a standalone BranchPredictor (no separate conditional).

For the "static" baseline we use LocalBP with a tiny 1-entry table and
1-bit counters so it effectively always predicts one direction.

Usage:
  gem5.opt --outdir=DIR branch_prediction.py BINARY --bp {static,local,tournament,tage}
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
# Branch predictor factory
# ---------------------------------------------------------------------------
def make_branch_predictor(name):
    """Return a BranchPredictor object configured for the named strategy."""
    if name == "static":
        # Approximate a static "always not-taken" predictor by using a
        # LocalBP with minimal storage (2 entries, 1-bit counters).
        bp = BranchPredictor()
        bp.conditionalBranchPred = LocalBP(
            localPredictorSize=2,
            localCtrBits=1,
        )
        return bp
    elif name == "local":
        bp = BranchPredictor()
        bp.conditionalBranchPred = LocalBP(
            localPredictorSize=2048,
            localCtrBits=2,
        )
        return bp
    elif name == "tournament":
        bp = BranchPredictor()
        bp.conditionalBranchPred = TournamentBP(
            localPredictorSize=2048,
            localCtrBits=2,
            globalPredictorSize=8192,
            globalCtrBits=2,
            choicePredictorSize=8192,
            choiceCtrBits=2,
        )
        return bp
    elif name == "tage":
        bp = BranchPredictor()
        bp.conditionalBranchPred = TAGE_SC_L_64KB()
        return bp
    else:
        raise ValueError(f"Unknown predictor: {name}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
parser = argparse.ArgumentParser(description="Branch prediction comparison")
parser.add_argument("binary")
parser.add_argument("--bp", choices=["static", "local", "tournament", "tage"],
                    default="tournament")
args = parser.parse_args()

# ---------------------------------------------------------------------------
# System
# ---------------------------------------------------------------------------
system = System()
system.clk_domain = SrcClockDomain(clock="1GHz",
                                   voltage_domain=VoltageDomain())
system.mem_mode = "timing"
system.mem_ranges = [AddrRange("512MiB")]

# O3CPU with configurable branch predictor
system.cpu = X86O3CPU()
system.cpu.branchPred = make_branch_predictor(args.bp)

# Keep issue width at 4 for a controlled comparison
system.cpu.fetchWidth = 4
system.cpu.decodeWidth = 4
system.cpu.renameWidth = 4
system.cpu.issueWidth = 4
system.cpu.dispatchWidth = 4
system.cpu.commitWidth = 4

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
print(f"Beginning simulation (O3CPU, branch predictor: {args.bp})...")
exit_event = m5.simulate()
print(f"Exiting @ tick {m5.curTick()} because {exit_event.getCause()}")
