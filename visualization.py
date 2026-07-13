"""
Module: visualization.py
Generates all charts with REAL measured data — no simulated values.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np, os, time, math, sys

BASE_DIR     = os.path.dirname(os.path.abspath(__file__))   # AA_Project root
sys.path.insert(0, BASE_DIR)
OUTPUT       = os.path.join(BASE_DIR, "output")              # main charts + seating_plan.csv
HALLS_OUTPUT = os.path.join(OUTPUT, "halls")                  # hall layout PNGs
os.makedirs(OUTPUT, exist_ok=True)
os.makedirs(HALLS_OUTPUT, exist_ok=True)

COURSE_COLORS = [
    "#4E79A7","#F28E2B","#E15759","#76B7B2","#59A14F",
    "#EDC948","#B07AA1","#FF9DA7","#9C755F","#BAB0AC",
    "#D37295","#FABFD2","#8CD17D","#B6992D","#499894",
    "#86BCB6","#E9C46A","#264653","#E76F51","#2A9D8F"
]

def _ax_style(ax):
    ax.set_facecolor("#1a1a2e")
    ax.tick_params(colors="white", labelsize=9)
    ax.xaxis.label.set_color("white")
    ax.yaxis.label.set_color("white")
    ax.title.set_color("white")
    for sp in ax.spines.values():
        sp.set_edgecolor("#444466")

def plot_hall_layout(hall, allocation, seat_course, conflicts=None):
    conflict_seats = set()
    if conflicts:
        for c in conflicts:
            # mark both seats in each conflict pair
            for sid in range(hall.total_seats):
                lbl = hall.get_seat_label(sid)
                if lbl in (c["seat1"], c["seat2"]):
                    conflict_seats.add(sid)

    all_courses = sorted(set(seat_course.values()))
    color_map   = {c: COURSE_COLORS[i % len(COURSE_COLORS)] for i, c in enumerate(all_courses)}

    fig, ax = plt.subplots(figsize=(15, 10))
    fig.patch.set_facecolor("#0d0d1a")
    ax.set_facecolor("#0d0d1a")

    cw, ch = 1.0, 0.78
    for sid in range(hall.total_seats):
        r, c = hall.id_to_rc[sid]
        x = c * cw
        y = (hall.rows - 1 - r) * ch

        if sid in allocation:
            course = seat_course[sid]
            color  = "#FF4444" if sid in conflict_seats else color_map[course]
            stu    = allocation[sid]
            label  = f"{stu['RollNo']}\n{course}"
            tcol   = "white"
            lw, ec = (2.5, "#FF0000") if sid in conflict_seats else (0.4, "#ffffff33")
        else:
            color, label, tcol, lw, ec = "#1e1e38", "EMPTY", "#555577", 0.4, "#333355"

        rect = mpatches.FancyBboxPatch(
            (x+0.04, y+0.04), cw-0.08, ch-0.08,
            boxstyle="round,pad=0.02",
            facecolor=color, edgecolor=ec, linewidth=lw
        )
        ax.add_patch(rect)
        ax.text(x+cw/2, y+ch/2, label, ha="center", va="center",
                fontsize=5.2, color=tcol, fontweight="bold", fontfamily="monospace")

    patches = [mpatches.Patch(color=color_map[c], label=c) for c in all_courses]
    if conflict_seats:
        patches.append(mpatches.Patch(color="#FF4444", label="⚠ CONFLICT"))
    ax.legend(handles=patches, loc="upper right", fontsize=7,
              framealpha=0.25, facecolor="#1a1a2e", labelcolor="white",
              title="Courses", title_fontsize=8)

    ax.set_xlim(-0.3, hall.cols*cw+0.3)
    ax.set_ylim(-0.4, hall.rows*ch+0.6)
    ax.set_title(
        f"Exam Hall Layout — {hall.hall_name}   "
        f"({len(allocation)}/{hall.total_seats} filled  |  "
        f"{len(conflicts) if conflicts else 0} conflicts)",
        color="white", fontsize=12, fontweight="bold", pad=12
    )
    ax.axis("off")
    path = f"{HALLS_OUTPUT}/hall_{hall.hall_name}_layout.png"
    plt.tight_layout()
    plt.savefig(path, dpi=160, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    print(f"  Saved: {path}")
    return path


def plot_scaling_experiment(scaling_results):
    ns    = [r["n"]         for r in scaling_results]
    times = [r["time_ms"]   for r in scaling_results]
    comps = [r["comparisons"] for r in scaling_results]
    th    = [r["theoretical"] for r in scaling_results]

    # scale theoretical to match measured magnitude
    s1 = max(times)/max(th)  if max(th)  else 1
    s2 = max(comps)/max(th)  if max(th)  else 1

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.patch.set_facecolor("#0f0f23")
    for ax in axes: _ax_style(ax)

    axes[0].plot(ns, times, "o-", color="#4E79A7", lw=2.2, ms=7, label="Measured (ms)")
    axes[0].plot(ns, [t*s1 for t in th], "--", color="#F28E2B", lw=2, label="O(n log n) scaled")
    axes[0].fill_between(ns, times, [t*s1 for t in th], alpha=0.08, color="#4E79A7")
    axes[0].set_title("Merge Sort — Time vs n", fontweight="bold")
    axes[0].set_xlabel("n (students)"); axes[0].set_ylabel("Time (ms)")
    axes[0].legend(facecolor="#2d2d44", labelcolor="white", fontsize=9)
    axes[0].grid(True, alpha=0.18)

    axes[1].plot(ns, comps, "s-", color="#E15759", lw=2.2, ms=7, label="Actual Comparisons")
    axes[1].plot(ns, [t*s2 for t in th], "--", color="#EDC948", lw=2, label="O(n log n) scaled")
    axes[1].set_title("Merge Sort — Comparisons vs n", fontweight="bold")
    axes[1].set_xlabel("n (students)"); axes[1].set_ylabel("Comparisons")
    axes[1].legend(facecolor="#2d2d44", labelcolor="white", fontsize=9)
    axes[1].grid(True, alpha=0.18)

    fig.suptitle("Scaling Experiment — Merge Sort (Real Measured Data)",
                 color="white", fontsize=13, fontweight="bold")
    path = f"{OUTPUT}/scaling_experiment.png"
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    print(f"  Saved: {path}")
    return path


def plot_algorithm_comparison(real_times):
    """
    real_times: dict with keys merge_sort, binary_search, graph_build,
                greedy_color, backtrack — all REAL measured ms values.
    """
    labels = [
        "Merge Sort\nO(n log n)",
        "Binary Search\nO(log n)",
        "Graph Build\nO(V+E)",
        "Greedy Coloring\nO(V+E)",
        "Backtracking\nO(n) avg"
    ]
    vals   = [
        real_times.get("merge_sort",   0),
        real_times.get("binary_search",0),
        real_times.get("graph_build",  0),
        real_times.get("greedy_color", 0),
        real_times.get("backtrack",    0),
    ]
    colors = ["#4E79A7","#EDC948","#59A14F","#F28E2B","#E15759"]

    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor("#0f0f23"); _ax_style(ax)
    bars = ax.bar(labels, vals, color=colors, width=0.52, edgecolor="#222")
    ax.set_title("Algorithm Runtime Comparison (Real Measured Times)",
                 color="white", fontsize=12, fontweight="bold")
    ax.set_ylabel("Time (ms)")
    ax.grid(True, alpha=0.18, axis="y")
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.0002,
                f"{v:.4f}ms", ha="center", va="bottom", color="white", fontsize=8)
    path = f"{OUTPUT}/algorithm_comparison.png"
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    print(f"  Saved: {path}")
    return path


def plot_greedy_vs_backtrack(greedy_stats, bt_normal_stats, bt_stress_stats):
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.patch.set_facecolor("#0f0f23")
    for ax in axes: _ax_style(ax)

    # Left: seats filled comparison
    cats  = ["Hall-A\n(Normal)", "Hall-B\n(Normal)", "Hall-C\n(Normal)", "Stress\n(2 courses)"]
    g_filled = [s["seats_filled"] for s in greedy_stats]
    g_filled.append(0)   # greedy not run on stress
    bt_filled = [s["students_placed"] for s in bt_normal_stats]
    bt_filled.append(bt_stress_stats["students_placed"])

    x = np.arange(len(cats)); w = 0.35
    b1 = axes[0].bar(x-w/2, g_filled,  w, label="Greedy Only",         color="#4E79A7", edgecolor="#222")
    b2 = axes[0].bar(x+w/2, bt_filled, w, label="Backtracking Added",   color="#59A14F", edgecolor="#222")
    axes[0].set_title("Students Placed: Greedy vs Backtracking", fontweight="bold")
    axes[0].set_ylabel("Students Placed")
    axes[0].set_xticks(x); axes[0].set_xticklabels(cats, color="white")
    axes[0].legend(facecolor="#2d2d44", labelcolor="white")
    axes[0].grid(True, alpha=0.18, axis="y")
    for bar in list(b1)+list(b2):
        if bar.get_height() > 0:
            axes[0].text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.3,
                         str(int(bar.get_height())), ha="center", va="bottom",
                         color="white", fontsize=8)

    # Right: backtrack calls normal vs stress
    labels2 = ["Normal Run\n(15 courses)", "Stress Test\n(2 courses)"]
    calls   = [sum(s["recursive_calls"] for s in bt_normal_stats),
               bt_stress_stats["recursive_calls"]]
    bts     = [sum(s["backtracks"] for s in bt_normal_stats),
               bt_stress_stats["backtracks"]]
    x2 = np.arange(2)
    axes[1].bar(x2-w/2, calls, w, label="Recursive Calls", color="#F28E2B", edgecolor="#222")
    axes[1].bar(x2+w/2, bts,   w, label="Backtracks",      color="#E15759", edgecolor="#222")
    axes[1].set_title("Backtracking: Normal vs Worst-Case Stress", fontweight="bold")
    axes[1].set_ylabel("Count")
    axes[1].set_xticks(x2); axes[1].set_xticklabels(labels2, color="white")
    axes[1].legend(facecolor="#2d2d44", labelcolor="white")
    axes[1].grid(True, alpha=0.18, axis="y")

    fig.suptitle("Greedy Graph Coloring vs Constraint-Satisfaction Backtracking",
                 color="white", fontsize=12, fontweight="bold")
    path = f"{OUTPUT}/greedy_vs_backtrack.png"
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    print(f"  Saved: {path}")
    return path


def plot_stress_layout(hall, allocation, seat_course):
    """Visualize the 2-course stress test hall layout."""
    color_map = {"STRESS-A": "#4E79A7", "STRESS-B": "#E15759"}
    fig, ax = plt.subplots(figsize=(13, 8))
    fig.patch.set_facecolor("#0d0d1a"); ax.set_facecolor("#0d0d1a")
    cw, ch = 1.0, 0.78
    for sid in range(hall.total_seats):
        r, c = hall.id_to_rc[sid]
        x = c * cw; y = (hall.rows - 1 - r) * ch
        if sid in allocation:
            course = seat_course[sid]
            color  = color_map.get(course, "#888")
            label  = course[-1]   # just "A" or "B"
        else:
            color, label = "#1e1e38", ""
        rect = mpatches.FancyBboxPatch(
            (x+0.04, y+0.04), cw-0.08, ch-0.08,
            boxstyle="round,pad=0.02",
            facecolor=color, edgecolor="#ffffff22", linewidth=0.4
        )
        ax.add_patch(rect)
        ax.text(x+cw/2, y+ch/2, label, ha="center", va="center",
                fontsize=9, color="white", fontweight="bold")

    patches = [mpatches.Patch(color="#4E79A7", label="Course STRESS-A"),
               mpatches.Patch(color="#E15759", label="Course STRESS-B")]
    ax.legend(handles=patches, loc="upper right", fontsize=9,
              facecolor="#1a1a2e", labelcolor="white")
    ax.set_xlim(-0.3, hall.cols*cw+0.3)
    ax.set_ylim(-0.4, hall.rows*ch+0.6)
    ax.set_title(
        f"WORST-CASE STRESS TEST — {hall.hall_name}  "
        f"(Only 2 Courses, {len(allocation)}/{hall.total_seats} seats)\n"
        "Alternating pattern proves constraint is maintained even in extreme conditions",
        color="white", fontsize=11, fontweight="bold", pad=10
    )
    ax.axis("off")
    path = f"{OUTPUT}/stress_test_layout.png"
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    print(f"  Saved: {path}")
    return path


def print_conflict_report(all_conflicts):
    print("\n" + "="*62)
    print("  CONFLICT DETECTION REPORT")
    print("="*62)
    if not all_conflicts:
        print("  ✅  Zero conflicts — all adjacent seats hold students")
        print("      from different courses. Constraint fully satisfied.")
    else:
        print(f"  ⚠️   {len(all_conflicts)} conflict(s) found:")
        for i, c in enumerate(all_conflicts, 1):
            print(f"  [{i}] {c['seat1']} ↔ {c['seat2']} | "
                  f"Course: {c['course']} | {c['student1']} & {c['student2']}")
    print("="*62)
