"""
================================================================
  Module: space_complexity.py
  Purpose: Measure ACTUAL memory usage of every algorithm
           using Python's built-in tracemalloc profiler.

  Methods:
    measure_merge_sort(sizes)   → real peak KB per n
    measure_graph_build(sizes)  → real peak KB per V
    measure_greedy(sizes)       → real peak KB per V
    measure_backtrack(sizes)    → real peak KB per n
    measure_binary_search()     → real peak KB (single call)
    run_all()                   → full dict of results

  All values are PEAK memory in kilobytes (KB).
================================================================
"""

import tracemalloc
import random
import math
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def _kb(peak_bytes):
    return round(peak_bytes / 1024, 4)


def measure_merge_sort(sizes=None):
    """
    Measure peak memory of Merge Sort for each n in sizes.
    Theoretical: O(n) — auxiliary array during merge step.
    Returns list of {n, peak_kb, theoretical_kb}
    """
    from sorting import merge_sort
    if sizes is None:
        sizes = [10, 30, 50, 100, 150, 200, 300, 500]
    random.seed(42)
    courses = ["AI3163","CS2512","SE2523","IT2301","AI3812"]
    results = []
    for n in sizes:
        sample = [{"RollNo": f"S{i:04d}", "Name": f"N{i}",
                   "Course": random.choice(courses)} for i in range(n)]
        # Run 3 times, take max peak for stability
        peaks = []
        for _ in range(3):
            tracemalloc.start()
            merge_sort(list(sample))
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            peaks.append(peak)
        peak_kb = _kb(max(peaks))
        # Theoretical O(n): scale by measured value at n=100 as anchor
        theoretical_kb = round(n * peak_kb / max(n, 1) * 0.98, 4)
        results.append({
            "n": n,
            "peak_kb": peak_kb,
            "label": f"n={n}"
        })
    return results


def measure_graph_build():
    """
    Measure peak memory of graph construction for different hall sizes.
    Theoretical: O(V + E) — adjacency list.
    Returns list of {V, E, peak_kb}
    """
    from graph import SeatGraph
    configs = [
        (3, 4),   # V=12
        (5, 6),   # V=30
        (6, 8),   # V=48
        (7, 10),  # V=70
        (8, 10),  # V=80
        (9, 10),  # V=90
        (10,12),  # V=120
        (12,14),  # V=168
    ]
    results = []
    for rows, cols in configs:
        tracemalloc.start()
        g = SeatGraph("T", rows, cols)
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        V = rows * cols
        E = g.stats()["total_edges"]
        results.append({
            "V": V, "E": E,
            "VE": V + E,
            "peak_kb": _kb(peak),
            "label": f"V={V}"
        })
    return results


def measure_greedy(sizes=None):
    """
    Measure peak memory of Greedy Graph Coloring for different hall sizes.
    Theoretical: O(V) — seat_course dict.
    Returns list of {V, peak_kb}
    """
    from graph import SeatGraph
    from coloring import greedy_color_assign
    if sizes is None:
        sizes = [12, 30, 48, 70, 80, 90, 120]
    random.seed(42)
    courses = ["AI3163","CS2512","SE2523","IT2301","AI3812",
               "SE3201","IT3101","CS3301","AI3301","SE2101"]
    results = []
    for V in sizes:
        rows = max(int(V**0.5), 2)
        cols = math.ceil(V / rows)
        hall  = SeatGraph("T", rows, cols)
        stus  = [{"RollNo": f"S{i:04d}", "Name": f"N{i}",
                  "Course": random.choice(courses)}
                 for i in range(hall.total_seats)]
        tracemalloc.start()
        greedy_color_assign(hall, stus)
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        results.append({
            "V": hall.total_seats,
            "peak_kb": _kb(peak),
            "label": f"V={hall.total_seats}"
        })
    return results


def measure_backtrack(sizes=None):
    """
    Measure peak memory of Backtracking for different n values.
    Theoretical: O(n) — recursion stack + course index.
    Returns list of {n, peak_kb}
    """
    from graph import SeatGraph
    from backtracking import backtrack_assign
    if sizes is None:
        sizes = [4, 8, 12, 20, 30, 40, 50]
    random.seed(42)
    results = []
    for n in sizes:
        rows  = max(int(n**0.5), 2)
        cols  = math.ceil(n / rows) + 1
        hall  = SeatGraph("T", rows, cols)
        stus  = [{"RollNo": f"R{i:03d}", "Name": f"N{i}",
                  "Course": f"C{i % 5}"}
                 for i in range(n)]
        alloc, sc = {}, {}
        tracemalloc.start()
        backtrack_assign(hall, alloc, sc, stus, max_depth=500)
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        results.append({
            "n": n,
            "peak_kb": _kb(peak),
            "label": f"n={n}"
        })
    return results


def measure_binary_search():
    """
    Measure peak memory of Binary Search (single call).
    Theoretical: O(1) — only low/high/mid variables.
    """
    from sorting import sort_students, binary_search_by_course
    import csv
    try:
        data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "students.csv")
        with open(data_path) as f:
            students = list(csv.DictReader(f))
    except:
        students = [{"RollNo":f"S{i:04d}","Name":f"N{i}","Course":"AI3163"}
                    for i in range(240)]
    sorted_by_course, _ = sort_students(students, key="Course")
    tracemalloc.start()
    binary_search_by_course(sorted_by_course, "AI3163")
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {"peak_kb": _kb(peak), "note": "O(1) — only 3 pointer variables"}


def run_all():
    """
    Run all memory measurements and return a unified results dict.
    Called by GUI and visualization modules.
    """
    print("  Measuring Merge Sort memory...", flush=True)
    ms   = measure_merge_sort()
    print("  Measuring Graph Build memory...", flush=True)
    gb   = measure_graph_build()
    print("  Measuring Greedy memory...", flush=True)
    gr   = measure_greedy()
    print("  Measuring Backtracking memory...", flush=True)
    bt   = measure_backtrack()
    print("  Measuring Binary Search memory...", flush=True)
    bs   = measure_binary_search()
    return {
        "merge_sort":    ms,
        "graph_build":   gb,
        "greedy":        gr,
        "backtrack":     bt,
        "binary_search": bs,
    }


if __name__ == "__main__":
    print("\n" + "="*55)
    print("  SPACE COMPLEXITY MEASUREMENTS (tracemalloc)")
    print("="*55)

    print("\n[Merge Sort — O(n)]")
    for r in measure_merge_sort():
        print(f"  n={r['n']:<5} → Peak: {r['peak_kb']} KB")

    print("\n[Graph Build — O(V+E)]")
    for r in measure_graph_build():
        print(f"  V={r['V']:<5} E={r['E']:<5} → Peak: {r['peak_kb']} KB")

    print("\n[Greedy Coloring — O(V)]")
    for r in measure_greedy():
        print(f"  V={r['V']:<5} → Peak: {r['peak_kb']} KB")

    print("\n[Backtracking — O(n)]")
    for r in measure_backtrack():
        print(f"  n={r['n']:<5} → Peak: {r['peak_kb']} KB")

    print("\n[Binary Search — O(1)]")
    bs = measure_binary_search()
    print(f"  Peak: {bs['peak_kb']} KB  ({bs['note']})")
    print("="*55)
