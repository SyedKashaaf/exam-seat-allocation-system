"""
Module: coloring.py
Algorithm: Greedy Graph Coloring
Purpose: Assign students to seats such that no two adjacent seats
         have students from the same course (course = color)
Time Complexity: O(V + E) where V = seats, E = adjacency edges
Space Complexity: O(V)
"""

import time


def greedy_color_assign(hall, student_pool):
    """
    Greedy seat allocation using graph coloring principle.
    - Each course acts as a 'color'
    - For each seat, pick a student whose course differs from all neighbors
    - Returns (allocation dict, unplaced students, stats)

    allocation: {seat_id: student_dict}
    """
    allocation = {}           # seat_id -> student
    seat_course = {}          # seat_id -> course string
    unplaced = []
    steps = 0

    # Build index: course -> list of students (queue)
    from collections import defaultdict, deque
    course_queue = defaultdict(deque)
    for s in student_pool:
        course_queue[s["Course"]].append(s)

    start = time.perf_counter()

    for seat_id in range(hall.total_seats):
        steps += 1
        neighbors = hall.get_neighbors(seat_id)
        neighbor_courses = {seat_course[n] for n in neighbors if n in seat_course}

        # Find a course not used by any neighbor
        placed = False
        for course, queue in course_queue.items():
            if course not in neighbor_courses and queue:
                student = queue.popleft()
                allocation[seat_id] = student
                seat_course[seat_id] = course
                placed = True
                break

        # If no valid course found, skip seat (backtracking will handle it)
        if not placed:
            pass  # seat left empty for backtracking phase

    end = time.perf_counter()

    # Collect remaining unplaced students
    for course, queue in course_queue.items():
        unplaced.extend(list(queue))

    stats = {
        "algorithm": "Greedy Graph Coloring",
        "seats_filled": len(allocation),
        "unplaced": len(unplaced),
        "steps": steps,
        "time_ms": round((end - start) * 1000, 4),
        "time_complexity": "O(V + E)",
        "space_complexity": "O(V)"
    }

    return allocation, seat_course, unplaced, stats


def detect_conflicts(hall, allocation, seat_course):
    """
    Scan all adjacent seat pairs and report same-course conflicts.
    Time Complexity: O(V + E)
    """
    conflicts = []
    checked = set()

    for seat_id, student in allocation.items():
        for neighbor in hall.get_neighbors(seat_id):
            pair = tuple(sorted((seat_id, neighbor)))
            if pair in checked:
                continue
            checked.add(pair)

            if neighbor in allocation:
                if seat_course.get(seat_id) == seat_course.get(neighbor):
                    conflicts.append({
                        "seat1": hall.get_seat_label(seat_id),
                        "seat2": hall.get_seat_label(neighbor),
                        "student1": allocation[seat_id]["RollNo"],
                        "student2": allocation[neighbor]["RollNo"],
                        "course": seat_course[seat_id]
                    })

    return conflicts


def print_coloring_stats(stats):
    print("\n" + "="*50)
    print("  COLORING MODULE — GREEDY GRAPH COLORING")
    print("="*50)
    print(f"  Seats filled    : {stats['seats_filled']}")
    print(f"  Unplaced        : {stats['unplaced']}")
    print(f"  Steps taken     : {stats['steps']}")
    print(f"  Time taken      : {stats['time_ms']} ms")
    print(f"  Time Complexity : {stats['time_complexity']}")
    print(f"  Space Complexity: {stats['space_complexity']}")
    print("="*50)
