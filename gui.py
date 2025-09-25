# gui.py
import tkinter as tk
from tkinter import messagebox
import math
from algorithm import EightQueensSolver

N = 8
CELL_SIZE = 60
BOARD_COLOR_1 = "#434343"
BOARD_COLOR_2 = "#ceddbb"
QUEEN_CHAR = "♛"

AUTO_DELAY_MS = 2  # default autoplay delay


def board_from_state(state):
    """Convert 1D state[row] = col to 2D board[row][col] with 1 for queens."""
    board = [[0] * N for _ in range(N)]
    for r, c in enumerate(state):
        if c != -1:
            board[r][c] = 1
    return board


def count_attacking_pairs_state(state):
    """Count conflict pairs among queens in row-first state."""
    queens = [(r, c) for r, c in enumerate(state) if c != -1]
    count = 0
    for i in range(len(queens)):
        r1, c1 = queens[i]
        for j in range(i + 1, len(queens)):
            r2, c2 = queens[j]
            if r1 == r2 or c1 == c2 or abs(r1 - r2) == abs(c1 - c2):
                count += 1
    return count


class EightQueensGUI:
    def __init__(self, master):
        self.master = master
        master.title("8-Queens — Stepper (Backtracking / A*)")

        # solver choice
        self.mode = tk.StringVar(value="Backtracking")
        self.mode_menu = tk.OptionMenu(master, self.mode, "Backtracking", "A*")
        self.mode_menu.grid(row=1, column=6, padx=6)

        self.status_label = tk.Label(master,
                                     text="Choose solver and press Start.")
        self.status_label.grid(row=2, column=0, columnspan=7,
                               sticky="w", padx=6, pady=(4, 6))

        # model state (row -> col)
        self.state = [-1] * N
        self.board = board_from_state(self.state)

        # solver generator
        self.solver = None
        self.gen = None

        # UI canvas
        self.canvas = tk.Canvas(master, width=N * CELL_SIZE, height=N * CELL_SIZE)
        self.canvas.grid(row=0, column=0, columnspan=6, padx=6, pady=6)

        # Controls & labels
        self.heur_label = tk.Label(master, text="Attacking pairs: 0")
        self.heur_label.grid(row=1, column=0, sticky="w", padx=6)

        self.step_label = tk.Label(master, text="Step: 0")
        self.step_label.grid(row=1, column=1, sticky="w", padx=6)

        self.start_bt = tk.Button(master, text="Start", width=12, command=self.start)
        self.start_bt.grid(row=1, column=2, padx=4)

        self.next_bt = tk.Button(master, text="Next Step", width=12, command=self.next_step, state="disabled")
        self.next_bt.grid(row=1, column=3, padx=4)

        self.auto_bt = tk.Button(master, text="Auto Play", width=12, command=self.toggle_auto, state="disabled")
        self.auto_bt.grid(row=1, column=4, padx=4)

        self.reset_bt = tk.Button(master, text="Reset", width=12, command=self.reset_board)
        self.reset_bt.grid(row=1, column=5, padx=4)

        self.status_label = tk.Label(master, text="Press Start to initialize the solver.")
        self.status_label.grid(row=2, column=0, columnspan=6, sticky="w", padx=6, pady=(4, 6))

        # visual markers
        self.attempt = None
        self.reject_mark = None
        self.step_count = 0

        # autoplay state
        self.auto_running = False
        self.auto_delay = AUTO_DELAY_MS

        self.draw_board()
        self.update_heuristic()

    # ---------- drawing ----------
    def draw_board(self):
        self.canvas.delete("all")
        for r in range(N):
            for c in range(N):
                x1 = c * CELL_SIZE
                y1 = r * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE
                color = BOARD_COLOR_1 if (r + c) % 2 == 0 else BOARD_COLOR_2
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='')

                if self.board[r][c] == 1:
                    self.canvas.create_text(x1 + CELL_SIZE / 2, y1 + CELL_SIZE / 2,
                                            text=QUEEN_CHAR, font=("Arial", int(CELL_SIZE / 1.5)))

    # ---------- controls ----------
    def start(self):
        # initialize solver and generator according to selected mode
        self.solver = EightQueensSolver(N)
        if self.mode.get() == "Backtracking":
            self.gen = self.solver.solve_steps(stop_at_first=True)
            init_msg = "Backtracking initialized."
        else:
            self.gen = self.solver.astar_steps()
            init_msg = "A* search initialized."

        self.state = [-1] * N
        self.board = board_from_state(self.state)
        self.step_count = 0
        self.step_label.config(text="Step: 0")
        self.start_bt.config(state="disabled")
        self.next_bt.config(state="normal")
        self.auto_bt.config(state="normal", text="Auto Play")
        self.auto_running = False
        self.status_label.config(text=f"Solver initialized ({self.mode.get()}). {init_msg} Press Next Step or Auto Play.")
        self.update_heuristic()
        self.draw_board()

    def next_step(self):
        if self.gen is None:
            return

        # find next visible event
        while True:
            try:
                ev = next(self.gen)
            except StopIteration:
                # no more events
                self.next_bt.config(state="disabled")
                self.auto_bt.config(state="disabled")
                self.status_label.config(text="No more steps.")
                self.auto_running = False
                return

            typ = ev[0]
            if typ in ('place', 'remove', 'solution'):
                break
            # otherwise (try/reject or other silent events) continue silently

        # visible event: update step count & UI
        self.step_count += 1
        self.step_label.config(text=f"Step: {self.step_count}")

        # compute f/g/h if A* mode (use same heuristic as solver: ceil(conflicts/(N-1)))
        if self.mode.get() == "A*":
            snapshot = ev[-1] if typ != 'solution' else ev[1]
            g = sum(1 for c in snapshot if c != -1)   # queens placed
            raw_conflicts = count_attacking_pairs_state(snapshot)
            h = math.ceil(raw_conflicts / (N - 1)) if raw_conflicts > 0 else 0
            f = g + h

        if typ == 'place':
            _, row, col, snapshot = ev
            self.state = list(snapshot)
            self.board = board_from_state(self.state)
            if self.mode.get() == "A*":
                self.status_label.config(
                    text=f"Placed queen at row {row+1}, col {col+1} | f={f}, g={g}, h={h} (attacks={raw_conflicts})"
                )
            else:
                self.status_label.config(text=f"Placed queen at row {row+1}, col {col+1}")
        elif typ == 'remove':
            _, row, col, snapshot = ev
            self.state = list(snapshot)
            self.board = board_from_state(self.state)
            if self.mode.get() == "A*":
                self.status_label.config(
                    text=f"Backtracked (removed) row {row+1}, col {col+1} | f={f}, g={g}, h={h} (attacks={raw_conflicts})"
                )
            else:
                self.status_label.config(text=f"Backtracked (removed) row {row+1}, col {col+1}")
        elif typ == 'solution':
            snapshot = ev[1]
            self.state = list(snapshot)
            self.board = board_from_state(self.state)
            self.status_label.config(text="Solution found!")
            self.next_bt.config(state="disabled")
            self.auto_bt.config(state="disabled")
            self.auto_running = False
            messagebox.showinfo("Solved", "A full solution was found. Press Reset to start again.")

        self.update_heuristic()
        self.draw_board()

    def toggle_auto(self):
        if not self.auto_running:
            # start auto
            self.auto_running = True
            self.auto_bt.config(text="Stop Auto")
            self.next_bt.config(state="disabled")  # prevent manual stepping while auto
            self._auto_step()
        else:
            # stop auto
            self.auto_running = False
            self.auto_bt.config(text="Auto Play")
            self.next_bt.config(state="normal")

    def _auto_step(self):
        if not self.auto_running:
            return
        # perform one visible step (or stop if finished)
        self.next_step()
        # continue if auto still running
        if self.auto_running:
            self.master.after(self.auto_delay, self._auto_step)

    def reset_board(self):
        # stop auto if running
        self.auto_running = False
        self.auto_bt.config(text="Auto Play")
        # reset model & UI
        self.state = [-1] * N
        self.board = board_from_state(self.state)
        self.solver = None
        self.gen = None
        self.step_count = 0
        self.step_label.config(text="Step: 0")
        self.heur_label.config(text=f"Attacking pairs: 0")
        self.status_label.config(text="Reset. Press Start to initialize the solver.")
        self.start_bt.config(state="normal")
        self.next_bt.config(state="disabled")
        self.auto_bt.config(state="disabled")
        self.draw_board()

    def update_heuristic(self):
        self.heur_label.config(text=f"Attacking pairs: {count_attacking_pairs_state(self.state)}")


if __name__ == '__main__':
    root = tk.Tk()
    app = EightQueensGUI(root)
    root.resizable(False, False)
    root.mainloop()
