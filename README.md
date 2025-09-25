# CS4200-8-Queens
# 8 Queens Puzzle Solver  

This project is a Python implementation of the **8 Queens Puzzle** with a step-by-step **Tkinter GUI visualization**.  
It demonstrates two solving strategies: **Backtracking** and **A\* Search**.  

---

## 📖 The 8 Queens Puzzle  
The challenge is to place 8 queens on a standard chessboard (8×8) so that no two queens threaten each other.  
This means no two queens can share the same row, column, or diagonal.  

---

## 🧮 Methods Implemented  

### 1. Backtracking  
Backtracking is a **depth-first search (DFS)** technique that tries to build a valid solution row by row:  

- Place a queen in a valid column of the current row.  
- Recursively attempt to place the next queen in the next row.  
- If no valid placement is possible, **backtrack** by removing the last queen and trying another column.  
- Continue until all queens are placed or all possibilities are exhausted.  

This guarantees finding a solution if one exists.  

---

### 2. A\* Search  
A\* is a **best-first search algorithm** guided by a cost function:  

- **State:** Board configuration, with queens placed row by row.  
- **g(n):** Number of queens placed so far.  
- **h(n):** Number of rows still unfilled.  
- **f(n) = g(n) + h(n):** Priority used for search expansion.  

The algorithm expands states in order of increasing `f(n)` while pruning invalid moves early.  
It explores only safe placements and stops when a full solution is found. 