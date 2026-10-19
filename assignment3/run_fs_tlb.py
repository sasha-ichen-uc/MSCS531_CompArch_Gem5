"""run_fs_tlb.py - boot Linux in gem5 full-system (FS) mode and optionally run
the membench workload inside the guest, with configurable TLB size.

Run from assignment3/ with the gem5 build (X86 or ALL):
  ../gem5/build/X86/gem5.opt run_fs_tlb.py --boot-only
  ../gem5/build/X86/gem5.opt --outdir=runs/fs_boot run_fs_tlb.py --boot-only

The guest receives the benchmark as a base64-encoded file through the m5
readfile script, because this host has no tools to write into the ext4 disk
image.
"""
import argparse
import base64
import os

import m5
from m5.objects import *  # noqa: F401  (ensures gem5 objects are loaded)

from gem5.components.boards.x86_board import X86Board
from gem5.components.cachehierarchies.classic.private_l1_cache_hierarchy import (
    PrivateL1CacheHierarchy,
)
from gem5.components.memory.single_channel import SingleChannelDDR3_1600
from gem5.components.processors.cpu_types import CPUTypes
from gem5.components.processors.simple_processor import SimpleProcessor
from gem5.isas import ISA
from gem5.resources.resource import DiskImageResource, KernelResource

HERE = os.path.dirname(os.path.abspath(__file__))
FS = os.path.join(HERE, "fs")

parser = argparse.ArgumentParser()
parser.add_argument("--boot-only", action="store_true",
                    help="boot the kernel and exit, with no benchmark")
parser.add_argument("--binary", default=os.path.join(FS, "membench.stripped"))
parser.add_argument("--tlb-size", type=int, default=64)
parser.add_argument("--cpu", choices=["atomic", "timing"], default="atomic")
args = parser.parse_args()

processor = SimpleProcessor(
    cpu_type=CPUTypes.ATOMIC if args.cpu == "atomic" else CPUTypes.TIMING,
    isa=ISA.X86,
    num_cores=1,
)
board = X86Board(
    clk_freq="1GHz",
    processor=processor,
    memory=SingleChannelDDR3_1600(size="3GiB"),
    cache_hierarchy=PrivateL1CacheHierarchy(
        l1d_size="32KiB", l1i_size="32KiB"
    ),
)

# TLB size: each core has an MMU with an instruction TLB and a data TLB.
mmu = board.get_processor().get_cores()[0].get_mmu()
mmu.itb.size = args.tlb_size
mmu.dtb.size = args.tlb_size

readfile_contents = None
if not args.boot_only:
    with open(args.binary, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    # Split the encoded binary into lines so the guest shell can read it.
    lines = [encoded[i:i + 76] for i in range(0, len(encoded), 76)]
    readfile_contents = (
        "base64 -d > /root/membench <<'B64EOF'\n"
        + "\n".join(lines)
        + "\nB64EOF\n"
        + "chmod +x /root/membench\n"
        + "m5 resetstats\n"
        + "/root/membench\n"
        + "m5 exit\n"
    )

board.set_kernel_disk_workload(
    kernel=KernelResource(local_path=os.path.join(FS, "vmlinux-5.4.49")),
    disk_image=DiskImageResource(
        local_path=os.path.join(FS, "x86-ubuntu.img"), root_partition="1"
    ),
    readfile_contents=readfile_contents,
)

# gem5's stdlib Simulator class uses Python 3.10 type syntax, which the
# Python 3.9 embedded in this build cannot parse. We perform the same steps it
# does: pre-instantiate the board, instantiate, post-instantiate, then simulate.
root = board._pre_instantiate(full_system=True)
m5.instantiate()
board._post_instantiate()
exit_event = m5.simulate()
print(f"Finished at tick {m5.curTick()}, exit cause: {exit_event.getCause()}")
