#!/usr/bin/env python3
"""Generate the merged Assignment 4 report (Parts 1 + 2) as a .docx file."""
from docx import Document
from docx.shared import Pt, Inches, Cm, RGBColor, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn
import os

doc = Document()

# ── Page setup (US Letter, 1″ margins) ─────────────────────────────
for section in doc.sections:
    section.page_width = Inches(8.5)
    section.page_height = Inches(11)
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)

# ── Style setup (APA: Times New Roman 12pt, double-spaced) ─────────
style = doc.styles['Normal']
style.font.name = 'Times New Roman'
style.font.size = Pt(12)
style.paragraph_format.space_after = Pt(0)
style.paragraph_format.line_spacing = 2.0

for level in range(1, 4):
    hs = doc.styles[f'Heading {level}']
    hs.font.name = 'Times New Roman'
    hs.font.size = Pt(12)
    hs.font.bold = True
    hs.font.color.rgb = RGBColor(0, 0, 0)
    hs.paragraph_format.space_before = Pt(12)
    hs.paragraph_format.space_after = Pt(6)
    hs.paragraph_format.line_spacing = 2.0
    if level == 1:
        hs.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if level == 3:
        hs.font.italic = True

def add_body(text):
    """Add a body paragraph with first-line indent."""
    p = doc.add_paragraph(text)
    p.paragraph_format.first_line_indent = Inches(0.5)
    return p

def add_center(text, bold=False):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    run.bold = bold
    return p

def add_ref(text):
    """APA hanging-indent reference."""
    p = doc.add_paragraph(text)
    p.paragraph_format.first_line_indent = Inches(-0.5)
    p.paragraph_format.left_indent = Inches(0.5)
    return p

def add_table(headers, rows, caption=None):
    """Add a formatted table with caption."""
    if caption:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(12)
        run = p.add_run("Table. ")
        run.bold = True
        run.italic = True
        run2 = p.add_run(caption)
        run2.italic = True

    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = 'Table Grid'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    # Header row
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = h
        for paragraph in cell.paragraphs:
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in paragraph.runs:
                run.bold = True
                run.font.size = Pt(10)
                run.font.name = 'Times New Roman'
        # Light blue shading
        shading = cell._element.get_or_add_tcPr()
        shading_elem = shading.makeelement(qn('w:shd'), {
            qn('w:val'): 'clear',
            qn('w:color'): 'auto',
            qn('w:fill'): 'D9E2F3',
        })
        shading.append(shading_elem)

    # Data rows
    for r_idx, row_data in enumerate(rows):
        for c_idx, val in enumerate(row_data):
            cell = table.rows[r_idx + 1].cells[c_idx]
            cell.text = str(val)
            for paragraph in cell.paragraphs:
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx > 0 else WD_ALIGN_PARAGRAPH.LEFT
                for run in paragraph.runs:
                    run.font.size = Pt(10)
                    run.font.name = 'Times New Roman'

    doc.add_paragraph()  # spacing after table
    return table

def add_numbered_item(number, bold_text, rest_text):
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Inches(0.5)
    run1 = p.add_run(f"{number}. {bold_text} ")
    run1.bold = True
    p.add_run(rest_text)
    return p

def add_bullet_item(bold_text, rest_text):
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Inches(0.5)
    run1 = p.add_run(f"{bold_text}: ")
    run1.bold = True
    p.add_run(rest_text)
    return p

# ════════════════════════════════════════════════════════════════════
# TITLE PAGE
# ════════════════════════════════════════════════════════════════════
for _ in range(6):
    doc.add_paragraph()

add_center("Exploring Instruction-Level Parallelism in Modern Processors:", bold=True)
add_center("A Literature Review and Practical Exploration with gem5", bold=True)
for _ in range(2):
    doc.add_paragraph()
add_center("I Chen (Sasha Chen)")
add_center("University of the Cumberlands")
add_center("MSCS 531: Advanced Computer Architecture")
add_center("October 2026")

doc.add_page_break()

# ════════════════════════════════════════════════════════════════════
# PART 1: LITERATURE REVIEW
# ════════════════════════════════════════════════════════════════════
doc.add_heading("Part 1: Understanding Instruction-Level Parallelism", level=1)
doc.add_heading("Literature Review", level=2)

add_body("Instruction-level parallelism (ILP)—the overlap among instructions that allows multiple operations to proceed simultaneously—has been the primary mechanism for improving uniprocessor performance since the 1980s (Hennessy & Patterson, 2019). Through pipelining, dynamic scheduling, branch prediction, and speculation, modern processors extract significant parallelism from sequential instruction streams. However, power constraints and diminishing returns have shifted attention toward multicore designs, heterogeneous architectures, and machine learning-based optimizations (Muralidhar et al., 2022). This review traces ILP’s evolution, analyzes its core concepts, critiques contemporary challenges, and synthesizes future directions drawn from five recent peer-reviewed studies.")

doc.add_heading("Historical Evolution of ILP", level=2)

add_body("The foundational era of ILP (1960s–1980s) produced concepts central to modern processors. The CDC 6600 (1964) introduced scoreboarding for out-of-order execution, and the IBM 360/91 (1967) implemented Tomasulo’s algorithm with reservation stations and register renaming to resolve data hazards dynamically (Hennessy & Patterson, 2019). During the 1980s, RISC architectures facilitated efficient pipelining, and compilers began exposing ILP through loop unrolling and software scheduling. The superscalar revolution (1990s–2000s) then brought processors issuing multiple instructions per cycle, with reorder buffers enabling precise exceptions. Branch prediction evolved from 2-bit counters to correlating and tournament predictors, and eventually to tagged hybrid (TAGE) predictors using multiple history lengths (Hennessy & Patterson, 2019).")

add_body("The power wall era (2004–present) forced a paradigm shift. Dennard scaling ended, making power the primary constraint. Intel’s Pentium 4, with its 31-stage pipeline, exemplified the diminishing returns of extreme pipeline depth, and the Itanium’s VLIW approach failed commercially. The industry pivoted to multicore designs, trading single-thread ILP for thread-level parallelism (Muralidhar et al., 2022). ILP research now focuses on efficient exploitation within tight power budgets.")

doc.add_heading("Analysis of Core ILP Concepts", level=2)
doc.add_heading("Parallelism Detection and Exploitation", level=3)

add_body("Modern processors detect ILP through hardware and software mechanisms. Tomasulo’s algorithm uses reservation stations to rename destinations, eliminating WAR and WAW hazards and enabling out-of-order execution while preserving correct data flow (Hennessy & Patterson, 2019). Hardware speculation extends this by executing past unresolved branches, with the reorder buffer enabling in-order commitment. On the software side, loop unrolling remains effective: a four-times unrolled, scheduled loop achieves 3.5 cycles per element versus 8 cycles unscheduled. For VLIW architectures, Deng et al. (2024) proposed a two-dimensional constrained dynamic programming approach that jointly optimizes execution time and resource utilization, outperforming traditional list scheduling.")

doc.add_heading("ILP Limitations and Performance Trade-offs", level=3)

add_body("Three dependence types constrain ILP: true data dependences (RAW hazards) reflecting actual data flow; name dependences (WAR/WAW) from register reuse, eliminated by renaming; and control dependences from branches, addressed through prediction and speculation (Hennessy & Patterson, 2019). Practical limits include finite resources, memory latency, and the power cost of speculative structures. Muralidhar et al. (2022) identified the power wall as the most critical constraint. ILP effectiveness is measured through IPC, CPI decomposition, and MPKI; wider issue increases power superlinearly, deeper pipelines amplify misprediction penalties, and larger speculation windows waste energy on squashed instructions.")

doc.add_heading("Critique of Current Challenges", level=2)

add_body("Branch prediction accuracy remains a bottleneck. Schall et al. (2024) found that TAGE-SC-L with a 64 KB budget still wastes 3.6%–20% of execution cycles on mispredictions in server workloads, and scaling storage yields diminishing returns. Their Last-Level Branch Predictor (LLBP) adds a 512 KB backing store behind TAGE with context-based prefetching, reducing MPKI by 8.9%. Zangeneh et al. (2020) applied convolutional neural networks to hard-to-predict branches, demonstrating that ML can complement traditional predictors by learning non-linear patterns in branch history, though latency constraints remain a tension.")

add_body("Power consumption is the dominant design constraint. Muralidhar et al. (2022) noted that speculative execution wastes energy when incorrect, and dark silicon further limits available structures. Extending ILP to constrained domains also poses challenges: Hu et al. (2022) demonstrated that scaled-down out-of-order techniques benefit even microcontrollers, with their RISC-V design quadrupling pipelined instructions at only 18.37% additional FPGA LUT utilization.")

doc.add_heading("Synthesis of Future Directions", level=2)

add_body("Machine learning-based optimization represents the most transformative opportunity. BranchNet (Zangeneh et al., 2020) demonstrated viable neural prediction, and hierarchical organizations like LLBP (Schall et al., 2024) offer a pragmatic path by applying cache-hierarchy concepts to prediction. Heterogeneous architectures with cores optimized for different ILP profiles are another avenue; Muralidhar et al. (2022) advocated energy-aware heterogeneity matching workloads to core capabilities at runtime. Compiler-hardware co-design also shows promise: Deng et al.’s (2024) VLIW scheduling improvements suggest that sophisticated compile-time analysis could narrow the gap with dynamic scheduling while avoiding its power overhead. The open RISC-V ecosystem provides a natural experimentation platform, as Hu et al.’s (2022) microcontroller work demonstrates.")

doc.add_page_break()

# ════════════════════════════════════════════════════════════════════
# PART 2: PRACTICAL EXPLORATION
# ════════════════════════════════════════════════════════════════════
doc.add_heading("Part 2: Practical Exploration of ILP Techniques", level=1)

doc.add_heading("Experimental Setup", level=2)

add_body("All experiments were conducted using the gem5 simulator version 25.1.0.1, built for the X86 ISA in optimized mode (gem5.opt). The simulator ran on an Apple Silicon Mac (macOS Darwin 25.4.0) under Syscall Emulation (SE) mode. Workloads were written in C, cross-compiled to static x86-64 Linux ELF binaries using Zig 0.16.0 with musl libc (zig cc -target x86_64-linux-musl -static -O1), and executed without modification inside gem5. The system was configured with a 1 GHz clock, 512 MiB DDR3-1600 main memory, and 32 KiB L1 instruction and data caches (2-way associative, 2-cycle latency).")

add_body("Four benchmark workloads were designed to stress different aspects of the pipeline:")

add_bullet_item("int_compute", "An integer-heavy workload with conditional branches (if/else chains based on modular arithmetic over 10,000 iterations), exercising the ALU and control-flow logic.")
add_bullet_item("fp_compute", "A floating-point workload performing multiply, divide, add, and iterative Newton-Raphson square root across 500-element arrays over 20 passes, stressing the FP pipeline.")
add_bullet_item("mem_compute", "A memory-intensive workload combining strided access (64-byte stride over 256 KiB) and pseudo-random pointer chasing, stressing the cache hierarchy and load/store pipeline.")
add_bullet_item("branch_heavy", "A branch-intensive workload using data-dependent, unpredictable branches (modulo-7, 11, 13 tests on pseudo-random data over 40,000 iterations) designed to maximize misprediction.")

add_body("The GitHub repository containing all configuration files, workloads, scripts, and results is available at: https://github.com/sasha-ichen-uc/MSCS531_CompArch_Gem5.git")

# ── Task 1-2 ──────────────────────────────────────────────────────
doc.add_heading("Task 1–2: Basic Pipeline Simulation and Performance Metrics", level=2)

add_body("The first experiment compared an in-order pipeline (MinorCPU) against an out-of-order superscalar pipeline (O3CPU, width 4) running the int_compute workload. MinorCPU models a classic 5-stage pipeline (fetch, decode, execute, memory, writeback), while O3CPU implements dynamic scheduling with register renaming, a reorder buffer, and speculative execution.")

add_table(
    ["CPU Model", "Cycles", "CPI", "IPC", "Instructions", "Micro-ops"],
    [
        ["MinorCPU (in-order)", "3,671,399", "34.19", "0.029", "107,374", "237,387"],
        ["O3CPU (OoO, w=4)", "99,579", "0.93", "1.078", "107,374", "237,387"],
    ],
    "Task 1–2: In-Order vs. Out-of-Order Pipeline Performance",
)

add_body("The O3CPU completed the same workload in 36.8× fewer cycles than MinorCPU. The MinorCPU’s CPI of 34.19 reflects the severe penalty of serializing x86 micro-ops through an in-order pipeline: each complex x86 instruction decomposes into approximately 2.2 micro-ops (237,387 / 107,374), and the in-order pipeline stalls on every data dependency, unable to execute independent instructions out of order. The O3CPU’s CPI of 0.93 (IPC > 1.0) demonstrates that out-of-order execution, register renaming, and speculative execution effectively exploit instruction-level parallelism even within a single thread.")

add_body("The pipeline visualization, generated using gem5’s O3PipeView trace and the o3-pipeview.py utility, shows the progression of instructions through fetch (f), decode (d), rename (n), dispatch (p), issue (i), complete (c), and retire (r) stages. The trace reveals multiple instructions in-flight simultaneously, overlapping across pipeline stages—a direct visualization of ILP exploitation. Store completions (s) appear after retirement, reflecting the write-buffer mechanism.")

# ── Task 3 ────────────────────────────────────────────────────────
doc.add_heading("Task 3: Impact of Branch Prediction", level=2)

add_body("The branch prediction experiment compared four predictors on the O3CPU (width 4) running int_compute: a near-static predictor (LocalBP with only 2 entries and 1-bit counters), a standard local predictor (2,048 entries, 2-bit counters), a tournament predictor (combining local and global history), and TAGE-SC-L with a 64 KB budget.")

add_table(
    ["Predictor", "CPI", "IPC", "Mispredictions", "Lookups", "Squashed Insts"],
    [
        ["Static (minimal)", "1.648", "0.607", "6,438", "47,576", "17,538"],
        ["Local (2 KB)", "2.007", "0.498", "9,397", "55,077", "25,039"],
        ["Tournament", "0.927", "1.078", "264", "30,757", "719"],
        ["TAGE-SC-L 64 KB", "0.924", "1.082", "210", "30,615", "577"],
    ],
    "Task 3: Branch Prediction Comparison (O3CPU, width 4, int_compute)",
)

add_body("The results reveal a dramatic performance gap. Tournament and TAGE predictors achieved CPI near 0.93, while the static predictor suffered CPI of 1.65—a 1.78× slowdown. The static predictor caused 6,438 mispredictions and 17,538 squashed instructions, wasting pipeline work on incorrectly speculated paths. TAGE achieved the fewest mispredictions (210) and the highest IPC (1.082), confirming the theoretical advantage of tagged geometric-length history tables discussed in the literature review (Schall et al., 2024).")

add_body("Notably, the simple local predictor performed worse than the static baseline, with 9,397 mispredictions. This counterintuitive result arises because the int_compute workload’s branches follow patterns that the local predictor’s limited history cannot capture, causing it to oscillate and mispredict more often than a naïve not-taken assumption. This finding aligns with Zangeneh et al.’s (2020) observation that certain hard-to-predict branches defeat simple table-based predictors.")

add_body("The misprediction penalty is severe: each misprediction triggers a pipeline flush, squashing all speculatively fetched instructions. With the static predictor, 17,538 instructions were squashed—equivalent to 16% of total committed instructions wasted. Accurate prediction is therefore critical for pipeline efficiency, as the cost of misprediction scales with pipeline depth and issue width.")

# ── Task 4 ────────────────────────────────────────────────────────
doc.add_heading("Task 4: Multiple Issue (Superscalar) Simulation", level=2)

add_body("The superscalar experiment varied the O3CPU’s issue width (1, 2, 4, 8) across all four benchmarks. Fetch, decode, rename, dispatch, issue, and commit widths were set uniformly. The reorder buffer, load/store queues, and physical register files were scaled proportionally to prevent structural bottlenecks from masking the width effect.")

add_table(
    ["Benchmark", "Width 1", "Width 2", "Width 4", "Width 8"],
    [
        ["int_compute", "0.390", "0.673", "1.078", "1.508"],
        ["fp_compute", "0.669", "1.202", "2.006", "2.931"],
        ["mem_compute", "0.307", "0.379", "0.390", "0.392"],
        ["branch_heavy", "0.522", "0.817", "1.087", "1.256"],
    ],
    "Task 4: Superscalar IPC Across Benchmarks and Issue Widths",
)

add_table(
    ["Benchmark", "w1→w2", "w1→w4", "w1→w8", "Limiting Factor"],
    [
        ["int_compute", "1.73×", "2.77×", "3.87×", "Data dependencies"],
        ["fp_compute", "1.80×", "3.00×", "4.38×", "High ILP in FP ops"],
        ["mem_compute", "1.24×", "1.27×", "1.28×", "Memory latency"],
        ["branch_heavy", "1.57×", "2.08×", "2.41×", "Misprediction penalties"],
    ],
    "Task 4: Speedup Relative to Single-Issue (Width 1)",
)

add_body("The fp_compute workload scaled best with issue width, achieving 4.38× speedup at width 8. Floating-point multiply, add, and divide operations exhibit high instruction-level parallelism because successive loop iterations operate on independent array elements, allowing the processor to issue multiple FP operations simultaneously. This confirms the theoretical prediction that compute-bound workloads with independent operations benefit most from wider issue.")

add_body("In stark contrast, mem_compute gained only 1.28× at width 8. The memory-bound workload’s performance is dominated by cache miss latency: once the pipeline stalls waiting for data from main memory, additional issue width provides no benefit because there are no ready instructions to fill the empty slots. The cycles per instruction remained above 2.5 regardless of width, reflecting the fundamental memory wall.")

add_body("The branch_heavy workload showed moderate scaling (2.41× at width 8), limited by misprediction penalties. With over 21,000 mispredictions across all width configurations, each misprediction flushes more in-flight instructions in a wider pipeline, partially offsetting the throughput gains. This interaction between issue width and misprediction cost illustrates why Schall et al. (2024) emphasize that branch prediction accuracy becomes more critical as pipelines grow wider.")

add_body("The int_compute workload achieved good scaling (3.87×) despite its branchy control flow, because the tournament predictor handles its branch patterns well (only ~190 mispredictions). The data dependencies within the loop body limit perfect scaling but still allow significant ILP extraction.")

# ── Task 5 ────────────────────────────────────────────────────────
doc.add_heading("Task 5: Simultaneous Multithreading (SMT)", level=2)

add_body("The SMT experiment ran one versus two threads of int_compute on an O3CPU with width 8, a 256-entry ROB, and 128-entry issue queues. Due to a gem5 x86 SE-mode limitation (hardcoded stack base address preventing different binaries from coexisting), both threads executed the same binary, isolating the effect of resource contention from workload differences.")

add_table(
    ["Configuration", "Cycles", "Per-Thread CPI", "Total Insts", "Total IPC"],
    [
        ["1 Thread", "71,209", "0.663", "107,374", "1.508"],
        ["2 Threads (SMT)", "137,161", "1.278", "214,748", "1.566"],
    ],
    "Task 5: SMT Performance (O3CPU, Width 8, int_compute)",
)

add_body("With SMT, two threads completed 214,748 total instructions in 137,161 cycles, yielding a total IPC of 1.566 compared to 1.508 for a single thread—a modest 3.8% throughput improvement. Alternatively, SMT completed double the work in only 1.93× the time, giving an effective speedup of 1.04× over sequential execution of both threads.")

add_body("The limited improvement stems from resource contention: both threads execute identical integer-heavy code, competing for the same ALU functional units, ROB entries, and issue queue slots. When one thread stalls, the other can use the freed resources, but because both threads have similar stall patterns, there is little complementary behavior to exploit. Muralidhar et al. (2022) note that SMT throughput gains are highest when threads have complementary resource demands (e.g., one compute-bound and one memory-bound). In production processors, Intel’s Hyper-Threading typically yields 15–30% throughput improvement with diverse workload mixes.")

add_body("Per-thread performance degraded significantly: each thread’s CPI increased from 0.663 to 1.278 (1.93× slowdown) due to resource sharing. This trade-off—higher total throughput at the cost of individual thread latency—is the fundamental SMT design tension. For latency-sensitive single-threaded workloads, SMT can be counterproductive.")

# ── Key Questions ──────────────────────────────────────────────────
doc.add_heading("Discussion: Key Questions", level=2)
doc.add_heading("How Do Different ILP Techniques Interact?", level=3)

add_body("The experiments reveal significant interactions between ILP techniques. Wider superscalar issue amplifies the cost of branch misprediction: at width 1, a misprediction flushes at most one in-flight instruction per cycle, but at width 8, up to eight instructions per cycle may be squashed. This is visible in the branch_heavy results, where the speedup from width 1 to 8 (2.41×) is the lowest among the non-memory-bound benchmarks. Similarly, SMT compounds the branch prediction challenge because the predictor must serve multiple threads, increasing aliasing in its tables (the 2-thread run showed 6,901 mispredictions versus 197 for a single thread). Out-of-order execution mitigates some memory latency by executing independent instructions while loads are pending, but as mem_compute shows, this only helps when independent instructions exist.")

doc.add_heading("What Are the Limitations of These Techniques?", level=3)

add_body("Each technique faces diminishing returns. Superscalar width beyond 4–6 yields progressively smaller gains because true data dependencies limit the available ILP in most code (Hennessy & Patterson, 2019). Branch prediction accuracy plateaus with table size—our TAGE predictor (64 KB) only marginally improved over tournament, echoing Schall et al.’s (2024) finding that scaling storage alone yields diminishing returns. SMT is limited by physical resource contention and works best when threads have complementary profiles. Out-of-order execution’s benefit is bounded by the instruction window size and the program’s inherent data-flow parallelism.")

doc.add_heading("How Can Complexity Be Balanced Against Performance?", level=3)

add_body("The results support a balanced approach to ILP exploitation. A width-4 O3CPU with tournament prediction captures the majority of available ILP (2.77× speedup for int_compute) at far lower complexity than width 8 (which adds only 1.4× more). This aligns with the industry trend toward moderate-width cores in heterogeneous designs (Muralidhar et al., 2022), where power-efficient mid-range cores handle most workloads and high-performance cores activate only when needed. The memory wall (mem_compute’s 1.28× ceiling) and misprediction wall (branch_heavy’s 2.41× ceiling) suggest that future performance gains require co-optimization of cache hierarchies and prediction accuracy alongside pipeline width.")

# ── Troubleshooting ────────────────────────────────────────────────
doc.add_heading("Troubleshooting", level=2)

add_body("Several technical challenges were encountered and resolved during the gem5 experiments:")

add_numbered_item(1, "gem5 25.1 deprecation of se.py.",
    "The standard SE configuration script was moved to configs/deprecated/example/se.py in gem5 25.1, causing initial path errors. Custom configuration scripts were written instead, following gem5’s new-style API patterns.")

add_numbered_item(2, "IQ parameter API change.",
    "The numIQEntries parameter was removed from O3CPU in gem5 25.1 and replaced with per-IQUnit configuration via the instQueues vector. The superscalar and SMT configs were updated to iterate over instQueues and set numEntries on each IQUnit object.")

add_numbered_item(3, "x86 SMT stack address collision.",
    "gem5’s x86 SE mode hardcodes the stack base at 0x7FFFFFFFF000 for all processes. Running two different binaries under SMT (multi_thread=True) caused a “Tried to write unmapped address” panic because both processes attempted to map the same stack region. The solution was to run two instances of the same binary, which avoids the collision since both share identical memory layout.")

add_numbered_item(4, "musl libc FP printf stack overflow.",
    "The musl libc implementation of printf(\"%.6f\") allocates a large stack buffer for floating-point formatting, exceeding gem5 SE mode’s default stack mapping. This caused all FP workloads using floating-point format specifiers to crash. The fix was to output FP results as scaled integers using printf(\"%ld\"), avoiding the stack-heavy FP formatting path.")

add_numbered_item(5, "Cross-compilation on Apple Silicon.",
    "Running on an ARM64 Mac required cross-compiling workloads to x86-64 Linux. The Zig compiler (zig cc -target x86_64-linux-musl -static) provided a reliable cross-compilation toolchain, producing statically linked ELF binaries compatible with gem5 SE mode.")

# ── Conclusion ─────────────────────────────────────────────────────
doc.add_page_break()
doc.add_heading("Conclusion", level=1)

add_body("This assignment explored instruction-level parallelism from both theoretical and practical perspectives. The literature review (Part 1) traced ILP’s evolution from Tomasulo’s algorithm through modern TAGE predictors and identified key challenges: the power wall, misprediction overhead, and the memory wall. The gem5 experiments (Part 2) empirically validated these concepts:")

add_body("Out-of-order execution provides a transformative 36.8× speedup over in-order pipelines by dynamically exploiting ILP that the hardware discovers at runtime. Branch prediction accuracy is critical for pipeline efficiency: TAGE achieved 97% fewer mispredictions than the static baseline, translating to 1.78× higher IPC. Superscalar gains are workload-dependent: FP-heavy code scaled to 4.38× at width 8, while memory-bound code plateaued at 1.28×, illustrating the memory wall. SMT provides marginal throughput improvement (3.8%) with identical workloads but offers greater benefit with complementary thread mixes. The interaction between techniques matters: wider issue amplifies misprediction costs, and SMT increases predictor aliasing.")

add_body("These findings reinforce the contemporary research direction identified in the literature review: future processor performance requires co-optimization across prediction accuracy (Schall et al., 2024; Zangeneh et al., 2020), energy-efficient execution (Muralidhar et al., 2022), compiler-hardware co-design (Deng et al., 2024), and workload-adaptive heterogeneous architectures. ILP remains the foundation upon which all modern processor performance is built.")

# ── References ─────────────────────────────────────────────────────
doc.add_page_break()
doc.add_heading("References", level=1)

add_ref("Deng, C., Chen, Z., Shi, Y., Ma, Y., Wen, M., & Luo, L. (2024). Optimizing VLIW instruction scheduling via a two-dimensional constrained dynamic programming. ACM Transactions on Design Automation of Electronic Systems, 29(5). https://doi.org/10.1145/3643135")
doc.add_paragraph()
add_ref("Hennessy, J. L., & Patterson, D. A. (2019). Computer architecture: A quantitative approach (6th ed.). Morgan Kaufmann.")
doc.add_paragraph()
add_ref("Hu, Y., Chen, J., Zhu, K., Xing, Q., Liu, W., Shen, J., & Gao, G. (2022). Specially-designed out-of-order processor architecture for microcontrollers. Electronics, 11(19), Article 2989. https://doi.org/10.3390/electronics11192989")
doc.add_paragraph()
add_ref("Muralidhar, R., Borovica-Gajic, R., & Buyya, R. (2022). Energy efficient computing systems: Architectures, abstractions and modeling to techniques and standards. ACM Computing Surveys, 54(11s), Article 236. https://doi.org/10.1145/3511094")
doc.add_paragraph()
add_ref("Schall, D., Sandberg, A., & Grot, B. (2024). The last-level branch predictor. In Proceedings of the 57th IEEE/ACM International Symposium on Microarchitecture (MICRO ’24). IEEE. https://doi.org/10.1109/MICRO61859.2024.00069")
doc.add_paragraph()
add_ref("Zangeneh, S., Pruett, S., Lym, S., & Patt, Y. N. (2020). BranchNet: A convolutional neural network to predict hard-to-predict branches. In Proceedings of the 53rd Annual IEEE/ACM International Symposium on Microarchitecture (MICRO ’53), 118–130. https://doi.org/10.1109/MICRO50266.2020.00022")

# ── Save ───────────────────────────────────────────────────────────
out_path = os.path.expanduser("~/MSCS531_CompArch/assignment4/Assignment4_ILP_Report.docx")
doc.save(out_path)
print(f"Wrote {out_path} ({os.path.getsize(out_path) // 1024} KB)")
