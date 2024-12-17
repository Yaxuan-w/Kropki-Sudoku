# Kropki-Sudoku

This project is a Kropki Sudoku solver implemented using a **Constraint Satisfaction Problem (CSP)** framework. The solver employs backtracking search with forward checking and heuristics such as **Minimum Remaining Values (MRV)** and **Degree Heuristics (DH)** to efficiently find solutions to Kropki Sudoku puzzles.

## How It Works

### What is Kropki Sudoku?

Kropki Sudoku combines standard Sudoku rules with additional constraints represented by dots between adjacent cells:

**White Dot:** The values of the two cells differ by 1, which is represented by `+` in this project's inputs.

**Black Dot:** The value of one cell is exactly twice the other, which is represented by `x` in this project's inputs.

**No Dot:** No specific relationship is enforced between the two cells.

### Key Features

#### Constraint Satisfaction Problem (CSP):

**Variables:** Each cell in the Sudoku grid.

**Domains:** Possible values for each cell (1–9).

**Constraints:**
- Sudoku rules (row, column, and subgrid uniqueness).
- Kropki dot rules (white and black dots).

#### Optimization Techniques:

**Forward Checking:** Reduces the domains of unassigned variables after each assignment.

**MRV (Minimum Remaining Values):** Prioritizes variables with the smallest domains.

**Degree Heuristics:** Breaks ties by selecting variables involved in the most constraints.

**Backtracking Search:** Attempts to assign values recursively, reverting decisions when conflicts occur.

## Usage 

### Dependencies

Python 3.7+

### Command 

```sh
python run.py --input_file <input_file_path> --output_file <output_file_path>
```

#### Arguments

`--input_file`: Path to the input file containing the Kropki Sudoku puzzle.

`--output_file`: Path to save the solved puzzle.

## Input Format

The input file should contain:

1. 9x9 Sudoku board:
    - Each row is a space-separated list of integers.
    - Use 0 to represent empty cells.
    - Horizontal Kropki dots:
2. A 9x8 grid where each value represents a constraint:
    - 1: White dot.
    - 2: Black dot.
    - 0: No constraint.
3. Vertical Kropki dots:
    - An 8x9 grid with the same encoding as above.

### Example Input File

Example input files could be found under `input/` folder

```txt
0 1 0 0 8 0 0 2 0
8 7 0 0 0 0 0 1 3
0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0
6 0 0 0 0 0 0 0 7
0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0
7 2 0 0 0 0 0 4 1
0 4 0 0 3 0 0 9 0

0 0 0 1 0 2 0 0 
1 0 2 0 0 1 0 0
0 2 0 0 1 2 0 1
0 0 0 0 0 0 0 1
0 0 2 0 0 0 0 0
0 0 0 0 0 1 0 2
0 0 0 0 2 1 1 0
0 0 0 1 0 0 1 0 
0 0 0 1 0 1 1 0

2 0 0 0 1 2 1 1 0
1 1 1 1 0 0 1 0 0
0 0 0 0 0 2 0 0 0
0 1 0 0 0 1 0 0 1
1 0 0 1 0 0 1 0 0
0 0 0 0 0 0 0 0 2
0 0 1 0 1 1 0 0 2
0 2 0 0 0 0 0 0 0 
```

## Output Format

The output file will contain the solved Sudoku board:

- Each row is a space-separated list of integers.

### Example Output File

```txt
4 1 5 7 8 3 6 2 9
8 7 2 4 9 6 5 1 3
9 6 3 5 1 2 4 7 8
2 8 1 3 7 4 9 5 6
6 9 4 8 2 5 1 3 7
5 3 7 9 6 1 2 8 4
3 5 9 1 4 8 7 6 2
7 2 8 6 5 9 3 4 1
1 4 6 2 3 7 8 9 5
```
