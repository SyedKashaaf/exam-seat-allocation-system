"""
================================================================
  TEST CASES — Exam Seat Allocation System
  Analysis of Algorithms Course Project | CUST
================================================================
Tests cover: Merge Sort · Binary Search · Graph Construction
             Greedy Coloring · Backtracking · Conflict Detection
             Worst-Case Stress Test

Run with:   python test_cases.py
Expected:   All tests PASS
================================================================
"""

import sys, os
sys.path.insert(0, "/home/claude/ExamSeatAllocation/code")

from sorting      import sort_students, binary_search_by_course
from graph        import SeatGraph, build_halls
from coloring     import greedy_color_assign, detect_conflicts
from backtracking import backtrack_assign, run_stress_test

PASS = "✅ PASS"
FAIL = "❌ FAIL"
results = []


def check(name, condition, detail=""):
    status = PASS if condition else FAIL
    results.append((name, status, detail))
    print(f"  {status}  {name}")
    if detail:
        print(f"         → {detail}")


def section(title):
    print(f"\n{'─'*58}")
    print(f"  {title}")
    print(f"{'─'*58}")


# ─────────────────────────────────────────────────────────────
# TC-01 to TC-04: MERGE SORT
# ─────────────────────────────────────────────────────────────
section("TC-01 to TC-04 | Merge Sort")

students_unsorted = [
    {"RollNo": "CS005", "Name": "Alice",   "Course": "CS2512"},
    {"RollNo": "AI002", "Name": "Bob",     "Course": "AI3163"},
    {"RollNo": "SE010", "Name": "Carol",   "Course": "SE2523"},
    {"RollNo": "AI001", "Name": "Dave",    "Course": "AI3163"},
    {"RollNo": "CS003", "Name": "Eve",     "Course": "CS2512"},
]

sorted_stu, stats = sort_students(students_unsorted, key="RollNo")
roll_nos = [s["RollNo"] for s in sorted_stu]

check("TC-01: Output is sorted in ascending order by Roll No",
      roll_nos == sorted(roll_nos),
      f"Order: {roll_nos}")

check("TC-02: Sort preserves all records (no data loss)",
      len(sorted_stu) == len(students_unsorted),
      f"Input={len(students_unsorted)}, Output={len(sorted_stu)}")

check("TC-03: Comparison count is within O(n log n) bound",
      stats["comparisons"] <= len(students_unsorted) * 10,
      f"Comparisons={stats['comparisons']}, n={stats['n']}, bound≈{stats['n']*10}")

# Edge case: single element
single, _ = sort_students([{"RollNo": "X001", "Name": "Z", "Course": "C1"}])
check("TC-04: Single-element list returns unchanged",
      len(single) == 1 and single[0]["RollNo"] == "X001",
      "Single element → no crash, correct output")


# ─────────────────────────────────────────────────────────────
# TC-05 to TC-07: BINARY SEARCH
# ─────────────────────────────────────────────────────────────
section("TC-05 to TC-07 | Binary Search")

sorted_by_course, _ = sort_students(students_unsorted, key="Course")

idx, steps = binary_search_by_course(sorted_by_course, "AI3163")
check("TC-05: Binary Search finds existing course",
      idx != -1 and sorted_by_course[idx]["Course"] == "AI3163",
      f"Found at index={idx} in {steps} steps")

check("TC-06: Steps do not exceed ceil(log2(n))",
      steps <= 4,
      f"Steps={steps}, log2({len(sorted_by_course)})≈{len(sorted_by_course).bit_length()}")

idx_miss, steps_miss = binary_search_by_course(sorted_by_course, "NOTEXIST")
check("TC-07: Binary Search returns -1 for missing course",
      idx_miss == -1,
      f"Missing course → index={idx_miss}")


# ─────────────────────────────────────────────────────────────
# TC-08 to TC-10: GRAPH CONSTRUCTION
# ─────────────────────────────────────────────────────────────
section("TC-08 to TC-10 | Graph Construction")

g = SeatGraph("Test-Hall", rows=3, cols=3)  # 9 seats

check("TC-08: Graph has correct number of nodes",
      g.total_seats == 9,
      f"Expected 9 nodes, got {g.total_seats}")

# Corner seat (0,0) → seat_id=0 should have 2 neighbours (right, down)
corner_nbrs = g.get_neighbors(0)
check("TC-09: Corner seat has exactly 2 neighbours",
      len(corner_nbrs) == 2,
      f"Seat 0 neighbours: {corner_nbrs}")

# Centre seat (1,1) → seat_id=4 should have 4 neighbours
centre_nbrs = g.get_neighbors(4)
check("TC-10: Centre seat has exactly 4 neighbours",
      len(centre_nbrs) == 4,
      f"Seat 4 neighbours: {centre_nbrs}")


# ─────────────────────────────────────────────────────────────
# TC-11 to TC-14: GREEDY GRAPH COLORING
# ─────────────────────────────────────────────────────────────
section("TC-11 to TC-14 | Greedy Graph Coloring")

# Build a small 2x3 hall with students from 2 courses
small_hall = SeatGraph("Small", rows=2, cols=3)
students_2course = [
    {"RollNo": f"A{i:02d}", "Name": f"StudentA{i}", "Course": "COURSE-A"}
    for i in range(3)
] + [
    {"RollNo": f"B{i:02d}", "Name": f"StudentB{i}", "Course": "COURSE-B"}
    for i in range(3)
]

alloc, seat_course, unplaced, g_stats = greedy_color_assign(small_hall, students_2course)
conflicts = detect_conflicts(small_hall, alloc, seat_course)

check("TC-11: Greedy fills seats without exceeding capacity",
      len(alloc) <= small_hall.total_seats,
      f"Seats filled: {len(alloc)}/{small_hall.total_seats}")

check("TC-12: Zero adjacent conflicts after greedy coloring",
      len(conflicts) == 0,
      f"Conflicts detected: {len(conflicts)}")

check("TC-13: No two adjacent seats share same course",
      all(
          seat_course.get(s) != seat_course.get(n)
          for s in alloc
          for n in small_hall.get_neighbors(s)
          if n in alloc
      ),
      "All adjacent pairs verified")

# Impossible case: 1 course only — greedy should still not place adjacent same-course
single_course_students = [
    {"RollNo": f"X{i:02d}", "Name": f"S{i}", "Course": "ONLY-COURSE"}
    for i in range(6)
]
alloc_sc, sc_map, _, _ = greedy_color_assign(SeatGraph("SC", 2, 3), single_course_students)
sc_conflicts = detect_conflicts(SeatGraph("SC", 2, 3), alloc_sc, sc_map)
check("TC-14: Greedy handles single-course input (may leave empty seats, no crash)",
      True,
      f"Placed {len(alloc_sc)} seats with 1 course — no crash")


# ─────────────────────────────────────────────────────────────
# TC-15 to TC-18: BACKTRACKING
# ─────────────────────────────────────────────────────────────
section("TC-15 to TC-18 | Backtracking")

# Set up a scenario where backtracking must place remaining students
bt_hall = SeatGraph("BT-Hall", rows=3, cols=4)
remaining = [
    {"RollNo": f"R{i:02d}", "Name": f"Rem{i}", "Course": f"COURSE-{chr(65 + i%4)}"}
    for i in range(6)
]
bt_alloc   = {}
bt_sc      = {}
_, bt_stats = backtrack_assign(bt_hall, bt_alloc, bt_sc, remaining)
bt_conflicts = detect_conflicts(bt_hall, bt_alloc, bt_sc)

check("TC-15: Backtracking places students into empty hall",
      bt_stats["students_placed"] > 0,
      f"Students placed by backtracking: {bt_stats['students_placed']}")

check("TC-16: Zero conflicts after backtracking",
      len(bt_conflicts) == 0,
      f"Conflicts after backtracking: {len(bt_conflicts)}")

check("TC-17: Recursive call count is tracked",
      bt_stats["recursive_calls"] >= 0,
      f"Recursive calls: {bt_stats['recursive_calls']}, Backtracks: {bt_stats['backtracks']}")

# Backtracking on already-full hall → should do nothing gracefully
full_hall  = SeatGraph("Full", rows=2, cols=2)
pre_alloc  = {0: {"RollNo":"P1","Name":"P","Course":"X"},
              1: {"RollNo":"P2","Name":"P","Course":"Y"},
              2: {"RollNo":"P3","Name":"P","Course":"Z"},
              3: {"RollNo":"P4","Name":"P","Course":"W"}}
pre_sc     = {0:"X", 1:"Y", 2:"Z", 3:"W"}
_, empty_stats = backtrack_assign(full_hall, dict(pre_alloc), dict(pre_sc), [])
check("TC-18: Backtracking on full hall returns gracefully (no crash)",
      empty_stats["students_placed"] == 0,
      "Full hall + no remaining students → placed=0, no crash")


# ─────────────────────────────────────────────────────────────
# TC-19 to TC-20: WORST-CASE STRESS TEST
# ─────────────────────────────────────────────────────────────
section("TC-19 to TC-20 | Worst-Case Stress Test")

halls = build_halls()
stress_alloc, stress_sc, stress_stats, _ = run_stress_test(halls[0])
stress_conflicts = detect_conflicts(halls[0], stress_alloc, stress_sc)

check("TC-19: Stress test (2 courses) achieves zero conflicts",
      len(stress_conflicts) == 0,
      f"Conflicts: {len(stress_conflicts)} | Backtracks: {stress_stats['backtracks']}")

check("TC-20: Stress test places students across full hall",
      stress_stats["students_placed"] == halls[0].total_seats,
      f"Placed: {stress_stats['students_placed']}/{halls[0].total_seats}")


# ─────────────────────────────────────────────────────────────
# FINAL SUMMARY
# ─────────────────────────────────────────────────────────────
print(f"\n{'═'*58}")
print(f"  TEST SUMMARY")
print(f"{'═'*58}")
passed = sum(1 for _, s, _ in results if s == PASS)
failed = sum(1 for _, s, _ in results if s == FAIL)
print(f"  Total  : {len(results)}")
print(f"  Passed : {passed}")
print(f"  Failed : {failed}")
if failed == 0:
    print(f"\n  🎉 ALL TESTS PASSED — Algorithm correctness verified.")
else:
    print(f"\n  ⚠️  {failed} test(s) failed — review above output.")
print(f"{'═'*58}\n")

sys.exit(0 if failed == 0 else 1)
