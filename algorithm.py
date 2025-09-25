# algorithm.py
import heapq
import math
from typing import Generator, Tuple, List

Event = Tuple  # ('place'|'remove'|'solution', ...)


class EightQueensSolver:
    def __init__(self, size: int = 8):
        self.size = size
        self.state: List[int] = [-1] * self.size

    # ----------------- Backtracking solver (unchanged) -----------------
    def is_safe(self, row: int, col: int) -> bool:
        for r in range(row):
            c = self.state[r]
            if c == -1:
                continue
            if c == col or abs(r - row) == abs(c - col):
                return False
        return True

    def solve_steps(self, stop_at_first: bool = True) -> Generator[Event, None, None]:
        self.state = [-1] * self.size
        yield from self._backtrack_gen(0, stop_at_first)

    def _backtrack_gen(self, row: int, stop_at_first: bool) -> Generator[Event, None, None]:
        if row == self.size:
            yield ('solution', tuple(self.state.copy()))
            return
        for col in range(self.size):
            if self.is_safe(row, col):
                self.state[row] = col
                yield ('place', row, col, tuple(self.state.copy()))
                for step in self._backtrack_gen(row + 1, stop_at_first):
                    yield step
                    if stop_at_first and step[0] == 'solution':
                        return
                self.state[row] = -1
                yield ('remove', row, col, tuple(self.state.copy()))


    # ----------------- A* solver (fixed, pruned, first-solution only) -----------------
    def astar_steps(self, stop_at_first: bool = True) -> Generator[Event, None, None]:
        """
        A* search that fills rows left-to-right.

        State: tuple of length N with -1 for empty rows.
        g(n): number of queens placed so far
        h(n): number of rows still unfilled
        f(n) = g + h

        Yields ('place', row, col, state) when expanding a node,
               ('solution', state) when solved.
        """

        def is_safe_partial(state: Tuple[int, ...], row: int, col: int) -> bool:
            """Check if placing queen at (row, col) is safe wrt previous rows."""
            for r in range(row):
                c = state[r]
                if c == -1:
                    continue
                if c == col or abs(r - row) == abs(c - col):
                    return False
            return True

        def heuristic(state: Tuple[int, ...]) -> int:
            # number of rows left to fill
            return state.count(-1)

        start = tuple([-1] * self.size)
        counter = 0
        pq: List[Tuple[int, int, int, Tuple[int, ...]]] = []
        start_h = heuristic(start)
        heapq.heappush(pq, (start_h, 0, counter, start))
        gscore = {start: 0}

        while pq:
            f, g, _, state = heapq.heappop(pq)
            if g != gscore.get(state, None):
                continue

            # show the placement that led to this state (skip root)
            if g > 0:
                row = g - 1
                col = state[row]
                yield ('place', row, col, tuple(state))

            # goal check
            if -1 not in state:
                yield ('solution', tuple(state))
                if stop_at_first:
                    return

            # expand next row
            row = state.index(-1)
            for col in range(self.size):
                if not is_safe_partial(state, row, col):
                    continue  # prune unsafe moves immediately
                new_state = list(state)
                new_state[row] = col
                new_tup = tuple(new_state)
                g2 = g + 1
                h2 = heuristic(new_tup)
                f2 = g2 + h2

                oldg = gscore.get(new_tup, float('inf'))
                if g2 < oldg:
                    gscore[new_tup] = g2
                    counter += 1
                    heapq.heappush(pq, (f2, g2, counter, new_tup))



            # NOTE: we intentionally DO NOT yield a 'place' for neighbor pushes here.
            # Only yield when a state is actually popped/expanded (above). This prevents
            # the UI from showing many temporary candidate placements and avoids the
            # "first row jumping back" flicker you observed.

        # exhausted without finding a solution
        return
