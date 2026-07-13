"""
Module: graph.py
Purpose: Model each exam hall as a seat graph
         Each seat = node; adjacent seats = edges
Time Complexity (Build): O(rows × cols)
Space Complexity: O(V + E) where V = seats, E = adjacency edges
"""


class SeatGraph:
    def __init__(self, hall_name, rows, cols):
        self.hall_name = hall_name
        self.rows = rows
        self.cols = cols
        self.total_seats = rows * cols
        self.adjacency = {}   # node -> list of neighbor nodes
        self.seat_matrix = {} # (r,c) -> seat_id
        self.id_to_rc = {}    # seat_id -> (r,c)
        self._build_graph()

    def _build_graph(self):
        """
        Assign seat IDs and build adjacency list.
        Adjacency: left, right, front, back (4-directional)
        """
        seat_id = 0
        for r in range(self.rows):
            for c in range(self.cols):
                self.seat_matrix[(r, c)] = seat_id
                self.id_to_rc[seat_id] = (r, c)
                self.adjacency[seat_id] = []
                seat_id += 1

        # Build edges
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # up, down, left, right
        for (r, c), sid in self.seat_matrix.items():
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if (nr, nc) in self.seat_matrix:
                    neighbor = self.seat_matrix[(nr, nc)]
                    self.adjacency[sid].append(neighbor)

    def get_neighbors(self, seat_id):
        return self.adjacency.get(seat_id, [])

    def get_seat_label(self, seat_id):
        r, c = self.id_to_rc[seat_id]
        return f"{self.hall_name}-R{r+1}C{c+1}"

    def stats(self):
        total_edges = sum(len(v) for v in self.adjacency.values()) // 2
        return {
            "hall": self.hall_name,
            "rows": self.rows,
            "cols": self.cols,
            "total_seats": self.total_seats,
            "total_edges": total_edges,
            "time_complexity": "O(rows × cols)",
            "space_complexity": "O(V + E)"
        }

    def print_stats(self):
        s = self.stats()
        print(f"\n  Hall: {s['hall']} | Seats: {s['total_seats']} "
              f"({s['rows']}×{s['cols']}) | Edges: {s['total_edges']}")


def build_halls():
    """
    Define 3 exam halls with different capacities.
    """
    halls = [
        SeatGraph("Hall-A", rows=9, cols=10),   # 90 seats
        SeatGraph("Hall-B", rows=8, cols=10),   # 80 seats
        SeatGraph("Hall-C", rows=7, cols=10),   # 70 seats
    ]
    return halls
