"""
Module: sorting.py
Algorithms: Merge Sort (primary), Binary Search

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DIVIDE & CONQUER PARADIGM
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Merge Sort is a classic Divide & Conquer algorithm.
It follows the three-step D&C structure:

  DIVIDE  : Split the list into two halves
              → left  = students[0 : n//2]
              → right = students[n//2 : n]

  CONQUER : Recursively sort each half
              → merge_sort(left)
              → merge_sort(right)

  COMBINE : Merge two sorted halves into one
              → _merge(left, right)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RECURRENCE RELATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  T(n) = 2T(n/2) + Θ(n)
         ───────   ────
         2 subproblems  merge step cost
         each of size n/2

Solved using Master Theorem — Case 2:
  a = 2,  b = 2,  f(n) = Θ(n)
  log_b(a) = log_2(2) = 1
  f(n) = Θ(n^1) = Θ(n^log_b(a))  → Case 2 applies

  ∴  T(n) = Θ(n log n)   ← applies to ALL cases (best, avg, worst)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
COMPLEXITY SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Time Complexity  : O(n log n) — Best, Average, Worst
  Space Complexity : O(n)       — Auxiliary merge array
  Binary Search    : O(log n)   — Time | O(1) Space
"""

import time, math

comparisons = 0


def merge_sort(students, key="RollNo"):
    global comparisons
    if len(students) <= 1:
        return students
    mid = len(students) // 2
    left  = merge_sort(students[:mid], key)
    right = merge_sort(students[mid:], key)
    return _merge(left, right, key)


def _merge(left, right, key):
    global comparisons
    result, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        comparisons += 1
        if left[i][key] <= right[j][key]:
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


def sort_students(students, key="RollNo"):
    global comparisons
    comparisons = 0
    t0 = time.perf_counter()
    sorted_s = merge_sort(list(students), key)
    elapsed = (time.perf_counter() - t0) * 1000
    return sorted_s, {
        "comparisons": comparisons,
        "time_ms": round(elapsed, 4),
        "n": len(students),
        "algorithm": "Merge Sort",
        "time_complexity": "O(n log n)",
        "space_complexity": "O(n)"
    }


def binary_search_by_course(students, target_course):
    low, high, result, steps = 0, len(students)-1, -1, 0
    while low <= high:
        steps += 1
        mid = (low + high) // 2
        if students[mid]["Course"] == target_course:
            result = mid; high = mid - 1
        elif students[mid]["Course"] < target_course:
            low = mid + 1
        else:
            high = mid - 1
    return result, steps


def run_scaling_experiment():
    """
    Run Merge Sort on n = 10..500 and return REAL measured timings.
    Used by visualization to produce accurate complexity charts.
    """
    import random
    random.seed(0)
    courses = ["AI3163","CS2512","SE2523","IT2301","AI3812"]
    sizes   = [10, 30, 50, 100, 150, 200, 300, 500]
    results = []
    for n in sizes:
        sample = [{"RollNo": f"S{i:04d}", "Name": f"N{i}",
                   "Course": random.choice(courses)} for i in range(n)]
        # Run 5 times, take median for stability
        times, comps = [], []
        for _ in range(5):
            _, st = sort_students(sample)
            times.append(st["time_ms"])
            comps.append(st["comparisons"])
        times.sort()
        results.append({
            "n": n,
            "time_ms":    round(times[2], 5),   # median
            "comparisons": comps[0],
            "theoretical": round(n * math.log2(max(n,2)), 1)
        })
    return results


def print_sort_stats(stats):
    print("\n" + "="*52)
    print("  SORTING MODULE — MERGE SORT")
    print("="*52)
    print(f"  Students sorted  : {stats['n']}")
    print(f"  Comparisons      : {stats['comparisons']}")
    print(f"  Time taken       : {stats['time_ms']} ms")
    print(f"  Time Complexity  : {stats['time_complexity']}")
    print(f"  Space Complexity : {stats['space_complexity']}")
    print("="*52)
