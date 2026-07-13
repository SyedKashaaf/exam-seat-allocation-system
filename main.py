"""
========================================================
  EXAM SEAT ALLOCATION SYSTEM
  Analysis of Algorithms — Course Project
  CUST — Mixed Departments (BSAI, BSCS, BSSE, BSIT)
  Algorithms: Merge Sort · Binary Search · Graph Coloring
              Greedy · Constraint Backtracking
========================================================
"""

import sys, os, csv, time

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))   # AA_Project root
sys.path.insert(0, BASE_DIR)
DATA_DIR   = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

from sorting      import sort_students, binary_search_by_course, run_scaling_experiment, print_sort_stats
from graph        import build_halls
from coloring     import greedy_color_assign, detect_conflicts, print_coloring_stats
from backtracking import backtrack_assign, run_stress_test, get_trace, print_backtrack_stats
from visualization import (
    plot_hall_layout, plot_scaling_experiment, plot_algorithm_comparison,
    plot_greedy_vs_backtrack, plot_stress_layout, print_conflict_report
)


def load_students(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def save_seating_plan(final_halls):
    path = os.path.join(OUTPUT_DIR, "seating_plan.csv")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["Hall","Seat","RollNo","Name","Course"])
        w.writeheader()
        for hall_name, alloc, seat_course, hall in final_halls:
            for sid, stu in sorted(alloc.items()):
                w.writerow({"Hall": hall_name, "Seat": hall.get_seat_label(sid),
                            "RollNo": stu["RollNo"], "Name": stu["Name"],
                            "Course": stu["Course"]})
    print(f"\n  ✅ Seating plan → {path}")


def main():
    print("\n" + "█"*62)
    print("█  EXAM SEAT ALLOCATION SYSTEM — AA Course Project       █")
    print("█"*62)

    real_times = {}   # collect real measured times for chart

    # ── 1. LOAD & SORT ────────────────────────────────────────
    print("\n[1/7] Loading & sorting students...")
    students = load_students(os.path.join(DATA_DIR, "students.csv"))
    sorted_stu, sort_stats = sort_students(students, key="RollNo")
    real_times["merge_sort"] = sort_stats["time_ms"]
    print_sort_stats(sort_stats)

    # Binary search (real measured)
    sorted_by_course, _ = sort_students(students, key="Course")
    t0 = time.perf_counter()
    idx, steps = binary_search_by_course(sorted_by_course, "AI3163")
    real_times["binary_search"] = round((time.perf_counter()-t0)*1000, 5)
    print(f"\n  Binary Search → 'AI3163' at index {idx} in {steps} steps | "
          f"Time: {real_times['binary_search']} ms")

    # ── 2. BUILD HALLS ────────────────────────────────────────
    print("\n[2/7] Building hall seat graphs...")
    t0 = time.perf_counter()
    halls = build_halls()
    real_times["graph_build"] = round((time.perf_counter()-t0)*1000, 4)
    for h in halls:
        h.print_stats()
    print(f"\n  Graph build time: {real_times['graph_build']} ms")

    # ── 3. GREEDY GRAPH COLORING ──────────────────────────────
    print("\n[3/7] Running Greedy Graph Coloring...")
    pool = list(sorted_stu)
    halls_data    = []
    greedy_stats  = []
    all_conflicts = []
    t_greedy_total = 0

    for hall in halls:
        chunk = pool[:hall.total_seats]
        pool  = pool[hall.total_seats:]
        alloc, seat_course, unplaced, g_st = greedy_color_assign(hall, chunk)
        conflicts = detect_conflicts(hall, alloc, seat_course)
        t_greedy_total += g_st["time_ms"]
        print(f"  {hall.hall_name}: {g_st['seats_filled']} filled | "
              f"{g_st['unplaced']} unplaced | {len(conflicts)} conflicts")
        greedy_stats.append(g_st)
        all_conflicts.extend(conflicts)
        pool = unplaced + pool
        halls_data.append((hall.hall_name, alloc, seat_course, hall, unplaced, g_st))

    real_times["greedy_color"] = round(t_greedy_total, 4)

    # ── 4. BACKTRACKING ───────────────────────────────────────
    print("\n[4/7] Running Backtracking for remaining students...")
    final_halls    = []
    bt_normal_stats = []
    t_bt_total     = 0

    for hall_name, alloc, seat_course, hall, unplaced, g_st in halls_data:
        _, bt_st = backtrack_assign(hall, alloc, seat_course, unplaced)
        conflicts_after = detect_conflicts(hall, alloc, seat_course)
        t_bt_total += bt_st["time_ms"]
        bt_normal_stats.append(bt_st)
        print_backtrack_stats(bt_st)
        print(f"  {hall_name}: conflicts after backtracking = {len(conflicts_after)}")
        all_conflicts = conflicts_after
        final_halls.append((hall_name, alloc, seat_course, hall))

    real_times["backtrack"] = round(t_bt_total, 4)
    print_conflict_report(all_conflicts)

    # ── 5. STRESS TEST ────────────────────────────────────────
    print("\n[5/7] Running Worst-Case Stress Test (2 courses only)...")
    stress_hall = halls[0]
    stress_alloc, stress_course, stress_stats, stress_trace = run_stress_test(stress_hall)
    stress_conflicts = detect_conflicts(stress_hall, stress_alloc, stress_course)
    print_backtrack_stats(stress_stats)
    print(f"  Stress test conflicts: {len(stress_conflicts)}  "
          f"(proves constraint holds even in worst case)")

    # ── 6. SAVE ───────────────────────────────────────────────
    save_seating_plan(final_halls)

    # ── 7. VISUALIZATIONS ─────────────────────────────────────
    print("\n[6/7] Generating charts & hall layouts...")

    # Hall layouts (normal)
    for hall_name, alloc, seat_course, hall in final_halls:
        plot_hall_layout(hall, alloc, seat_course)

    # Stress test layout
    plot_stress_layout(stress_hall, stress_alloc, stress_course)

    # Scaling experiment (real data)
    scaling_results = run_scaling_experiment()
    plot_scaling_experiment(scaling_results)

    # Algorithm comparison (real measured times)
    plot_algorithm_comparison(real_times)

    # Greedy vs Backtracking (real data)
    plot_greedy_vs_backtrack(greedy_stats, bt_normal_stats, stress_stats)

    # ── RECURSION TRACE ───────────────────────────────────────
    print("\n[7/7] Backtracking Recursion Trace (stress test sample):")
    print(f"\n  {'Step':<5} {'Seat':<16} {'Tried':<12} {'Forbidden':<20} {'Result'}")
    print("  " + "-"*68)
    for row in stress_trace[:20]:
        print(f"  {row['Step']:<5} {row['Seat']:<16} {row['Course Tried']:<12} "
              f"{row['Forbidden']:<20} {row['Result']}")

    # ── SUMMARY ───────────────────────────────────────────────
    total_placed = sum(len(a) for _, a, _, _ in final_halls)
    total_cap    = sum(h.total_seats for h in halls)
    print("\n" + "█"*62)
    print("█  FINAL SUMMARY                                         █")
    print("█"*62)
    print(f"  Students loaded    : {len(students)}")
    print(f"  Students placed    : {total_placed} / {total_cap}")
    print(f"  Final conflicts    : {len(all_conflicts)}")
    print(f"  Stress test placed : {stress_stats['students_placed']} | "
          f"Conflicts: {len(stress_conflicts)}")
    print(f"\n  Real Algorithm Times:")
    for k, v in real_times.items():
        print(f"    {k:<20}: {v} ms")
    print("█"*62 + "\n")

    return real_times, scaling_results, greedy_stats, bt_normal_stats, stress_stats


if __name__ == "__main__":
    main()
