# Exam Seat Allocation System
### Analysis of Algorithms — Course Project | CUST

---

## Project Overview
Automatically assigns 240 students from 4 departments to seats across 3 exam halls.
Core constraint: no two adjacent seats may contain students from the same course.

**Algorithms used:** Merge Sort · Binary Search · Graph Construction · Greedy Graph Coloring · Constraint-Satisfaction Backtracking

---

## Requirements
```
pip install matplotlib networkx pandas numpy customtkinter pillow
```
Python 3.8+. Tkinter must be installed (comes with standard Python on Windows/macOS).
On Ubuntu/Debian: `sudo apt-get install python3-tk`

---

## How to Run

### Option 1 — Interactive GUI (Recommended for demo)
```bash
python gui.py
```
Click **"Run All Steps"** in the sidebar. Everything runs automatically.

### Option 2 — Command Line (Full pipeline)
```bash
python generate_data.py     # Step 1: generate dataset
python main.py              # Step 2: run all algorithms + generate charts
```

---

## File Structure
```
ExamSeatAllocation/
├── code/
│   ├── main.py             # Master pipeline (7 stages)
│   ├── sorting.py          # Merge Sort + Binary Search
│   ├── graph.py            # Seat graph construction
│   ├── coloring.py         # Greedy graph coloring
│   ├── backtracking.py     # Backtracking + stress test
│   ├── visualization.py    # All charts
│   └── gui.py              # Interactive GUI
├── data/
│   ├── generate_data.py    # Dataset generator
│   └── students.csv        # 240-student dataset
├── output/
│   └── seating_plan.csv    # Final seat assignments
├── charts/                 # All generated PNG charts
└── README.md
```

---

## GUI Tabs
| Tab | What it shows |
|-----|--------------|
| Hall Layout | Colour-coded seat grid per hall |
| Complexity | Scaling experiment + algorithm comparison charts |
| Trace Table | Backtracking recursion trace (green=PLACED, red=BACKTRACK) |
| Student Table | Searchable/sortable table of all placed students |
| Stress Test | Worst-case 2-course test with analysis charts |

---

## Results Summary
| Hall | Seats | Placed | Conflicts |
|------|-------|--------|-----------|
| Hall-A | 90 | 90 | 0 |
| Hall-B | 80 | 78 | 0 |
| Hall-C | 70 | 67 | 0 |
| **Stress Test** | **90** | **90** | **0** |

---

## Complexity Summary
| Algorithm | Time | Space |
|-----------|------|-------|
| Merge Sort | O(n log n) all cases | O(n) |
| Binary Search | O(log n) | O(1) |
| Graph Build | O(V+E) | O(V+E) |
| Greedy Coloring | O(V+E) | O(V) |
| Backtracking | O(n) avg / O(n!) worst | O(n) |
