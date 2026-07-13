"""
Module: backtracking.py
Algorithm: Constraint-Satisfaction Backtracking
Purpose:   Place students that greedy coloring skipped.
           Also handles STRESS TEST where greedy is bypassed entirely.
Time Complexity:  O(n!) worst case  |  O(n) average with pruning
Space Complexity: O(n) recursion stack
"""

import time
from collections import defaultdict

call_count     = 0
backtrack_count = 0
trace_log       = []   # global trace for report/GUI


def backtrack_assign(hall, allocation, seat_course, remaining_students, max_depth=2000):
    global call_count, backtrack_count, trace_log
    call_count = backtrack_count = 0
    trace_log  = []

    empty_seats = [sid for sid in range(hall.total_seats) if sid not in allocation]
    if not remaining_students or not empty_seats:
        return True, _make_stats(0)

    course_index = defaultdict(list)
    for s in remaining_students:
        course_index[s["Course"]].append(s)

    placed_pool = []
    t0 = time.perf_counter()

    _bt_recursive(hall, allocation, seat_course,
                  course_index, empty_seats, 0, placed_pool, max_depth)

    elapsed = (time.perf_counter() - t0) * 1000
    stats = {
        "algorithm":        "Constraint-Satisfaction Backtracking",
        "recursive_calls":  call_count,
        "backtracks":       backtrack_count,
        "students_placed":  len(placed_pool),
        "time_ms":          round(elapsed, 4),
        "time_complexity":  "O(n!) worst, O(n) avg with pruning",
        "space_complexity": "O(n) recursion stack"
    }
    return True, stats


def _bt_recursive(hall, allocation, seat_course,
                  course_index, empty_seats, seat_idx,
                  placed_pool, max_depth):
    global call_count, backtrack_count, trace_log
    call_count += 1
    if call_count > max_depth or seat_idx >= len(empty_seats):
        return True

    seat_id  = empty_seats[seat_idx]
    forbidden = {seat_course[n] for n in hall.get_neighbors(seat_id) if n in seat_course}

    for course, pool in course_index.items():
        if not pool:
            continue
        result_label = "BACKTRACK" if course in forbidden else "PLACED"
        if len(trace_log) < 30:          # cap trace at 30 rows
            trace_log.append({
                "Step":         len(trace_log) + 1,
                "Seat":         hall.get_seat_label(seat_id),
                "Course Tried": course,
                "Forbidden":    ", ".join(sorted(forbidden)) if forbidden else "None",
                "Result":       result_label
            })
        if course in forbidden:
            backtrack_count += 1
            continue

        student = pool.pop()
        allocation[seat_id]  = student
        seat_course[seat_id] = course
        placed_pool.append(student)

        if _bt_recursive(hall, allocation, seat_course,
                         course_index, empty_seats, seat_idx + 1,
                         placed_pool, max_depth):
            return True

        # Undo
        backtrack_count += 1
        del allocation[seat_id]
        del seat_course[seat_id]
        placed_pool.pop()
        pool.append(student)

    return _bt_recursive(hall, allocation, seat_course,
                         course_index, empty_seats, seat_idx + 1,
                         placed_pool, max_depth)


# ── STRESS TEST ───────────────────────────────────────────────────────────────
def run_stress_test(hall):
    """
    Worst-case: only 2 courses for all seats.
    Forces the backtracking algorithm to work hard.
    Returns allocation, seat_course, stats, and trace.
    """
    global call_count, backtrack_count, trace_log
    call_count = backtrack_count = 0
    trace_log  = []

    courses = ["STRESS-A", "STRESS-B"]
    students = []
    per = hall.total_seats // 2 + 5   # slightly over to stress it
    for i in range(per):
        students.append({"RollNo": f"SA{i:03d}", "Name": f"StudentA{i}", "Course": "STRESS-A"})
    for i in range(per):
        students.append({"RollNo": f"SB{i:03d}", "Name": f"StudentB{i}", "Course": "STRESS-B"})

    allocation  = {}
    seat_course = {}
    course_index = defaultdict(list)
    for s in students:
        course_index[s["Course"]].append(s)

    placed_pool = []
    empty_seats = list(range(hall.total_seats))

    t0 = time.perf_counter()
    _bt_recursive(hall, allocation, seat_course,
                  course_index, empty_seats, 0, placed_pool, max_depth=5000)
    elapsed = (time.perf_counter() - t0) * 1000

    stats = {
        "algorithm":        "Backtracking — WORST CASE (2 courses)",
        "recursive_calls":  call_count,
        "backtracks":       backtrack_count,
        "students_placed":  len(placed_pool),
        "time_ms":          round(elapsed, 4),
        "time_complexity":  "O(n!) worst, pruned by adjacency constraints",
        "space_complexity": "O(n) recursion stack"
    }
    return allocation, seat_course, stats, list(trace_log)


def _make_stats(elapsed):
    return {
        "algorithm": "Backtracking", "recursive_calls": 0,
        "backtracks": 0, "students_placed": 0,
        "time_ms": elapsed,
        "time_complexity": "O(n!) worst, O(n) avg with pruning",
        "space_complexity": "O(n) recursion stack"
    }


def get_trace():
    return list(trace_log)


def print_backtrack_stats(stats):
    print("\n" + "="*52)
    print(f"  {stats['algorithm'].upper()}")
    print("="*52)
    print(f"  Recursive calls  : {stats['recursive_calls']}")
    print(f"  Backtracks       : {stats['backtracks']}")
    print(f"  Students placed  : {stats['students_placed']}")
    print(f"  Time taken       : {stats['time_ms']} ms")
    print(f"  Time Complexity  : {stats['time_complexity']}")
    print(f"  Space Complexity : {stats['space_complexity']}")
    print("="*52)
