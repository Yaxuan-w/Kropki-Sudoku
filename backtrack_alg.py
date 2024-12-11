from copy import deepcopy
import time

def build_dot_constraints(horizontal_dots, vertical_dots):
    dot_relations = {}

    # Horizontal -- row constraints
    for i, row in enumerate(horizontal_dots):
        for j, value in enumerate(row):
            if value > 0:
                coords = ((i, j), (i, j + 1))
                dot_relations[coords] = value

    # Vertical -- column constraints 
    for i, row in enumerate(vertical_dots):
        for j, value in enumerate(row):
            if value > 0:
                coords = ((i, j), (i+1, j))
                dot_relations[coords] = value

    return dot_relations

def build_constraints(sudoku_board):
    """
    Initialize row, column, and box constraints based on the initial kropki board.
    Combine row/column/box into one function to save runtime because we only need to loop one time 

    - row_constraints: stores the used values for each row.
    - col_constraints: stores the used values for each column.
    - box_constraints: stores the used values for each 3x3 box.
    The key of each dictionary is the row number, column number or box number, and the value is the corresponding set of used values.
    """
    row_constraints = {r: set() for r in range(9)}
    col_constraints = {c: set() for c in range(9)}
    box_constraints = {(r // 3, c // 3): set() for r in range(9) for c in range(9)}

    for row in range(9):
        for col in range(9):
            if sudoku_board[row][col] != 0:
                value = sudoku_board[row][col]
                row_constraints[row].add(value)
                col_constraints[col].add(value)
                box_constraints[(row // 3, col // 3)].add(value)

    return row_constraints, col_constraints, box_constraints

def assign_value(r, c, k, row_constraints, col_constraints, box_constraints):
    row_constraints[r].add(k)
    col_constraints[c].add(k)
    box_constraints[(r // 3, c // 3)].add(k)

def remove_value(r, c, k, row_constraints, col_constraints, box_constraints):
    row_constraints[r].remove(k)
    col_constraints[c].remove(k)
    box_constraints[(r // 3, c // 3)].remove(k)

def check_kropki(relations, domains, changed):
    # Handle Kropki constraints
    for (cell1, cell2), constraint in relations.items():
        # For each value in first cell's domain
        for v1 in list(domains[cell1]):
            valid = False
            # Checking if there's compatible value in second cell's domain
            for v2 in domains[cell2]:
                if constraint == 1 and abs(v1 - v2) == 1:
                    valid = True
                    break
                elif constraint == 2 and (v1 == 2 * v2 or v2 == 2 * v1):
                    valid = True
                    break
            if not valid:
                domains[cell1].remove(v1)
                changed = True

        # Repeat for second cell's domain
        for v2 in list(domains[cell2]):
            valid = False
            for v1 in domains[cell1]:
                if constraint == 1 and abs(v1 - v2) == 1:
                    valid = True
                    break
                elif constraint == 2 and (v1 == 2 * v2 or v2 == 2 * v1):
                    valid = True
                    break
            if not valid:
                domains[cell2].remove(v2)
                changed = True

    return changed

def check_sudoku(sudoku_board, domains, changed):
    # Handling filled cells
    for r in range(9):
        for c in range(9):
            if sudoku_board[r][c] != 0:
                value = sudoku_board[r][c]
                domains[(r, c)] = {value}  # Set domain to the filled value

                # Remove value from same row
                for col in range(9):
                    if col != c and value in domains[(r, col)]:
                        domains[(r, col)].remove(value)
                        changed = True

                # Remove value from same column
                for row in range(9):
                    if row != r and value in domains[(row, c)]:
                        domains[(row, c)].remove(value)
                        changed = True

                # Remove value from same box
                box_r, box_c = (r // 3) * 3, (c // 3) * 3
                for i in range(box_r, box_r + 3):
                    for j in range(box_c, box_c + 3):
                        if (i, j) != (r, c) and value in domains[(i, j)]:
                            domains[(i, j)].remove(value)
                            changed = True
    return changed

def forward_check(sudoku_board, dot_relations, domains):
    """
    Cleans the domains based on all constraints and propagates changes.
    Returns False if any domain becomes empty, True otherwise.
    """
    changed = True
    while changed:
        changed = False

        changed = check_kropki(dot_relations, domains, changed)

        changed = check_sudoku(sudoku_board, domains, changed)

        # Check if any domain is empty
        if any(len(domain) == 0 for domain in domains.values()):
            return False

    return True


def is_valid(kropki, relations, r, c, k, row_constraints, col_constraints, box_constraints):
    # Check row, column, and box constraints
    if k in row_constraints[r] or k in col_constraints[c] or k in box_constraints[(r // 3, c // 3)]:
        return False

    # Check Kropki constraints
    for (cell1, cell2), constraint in relations.items():
        if (r, c) == cell1 or (r, c) == cell2:
            other_r, other_c = cell1 if (r, c) == cell2 else cell2
            other_value = kropki[other_r][other_c]

            if other_value != 0:
                if constraint == 1 and abs(k - other_value) != 1:
                    return False
                if constraint == 2 and (k != 2 * other_value and other_value != 2 * k):
                    return False

    return True


def select_unassigned_variable(kropki, domains, relations):
    """
    Implements Minimum Remaining Values (MRV) and Degree Heuristics.
    Returns (row, col) of the unassigned variable with the smallest domain.
    If tied, chooses the variable involved in the most constraints.
    Returns None if all variables are assigned.
    """
    min_domain_size = float('inf')
    max_degree = -1
    best_cell = None

    for r in range(9):
        for c in range(9):
            if kropki[r][c] == 0:  # Unassigned cell
                domain_size = len(domains[(r, c)])

                if domain_size < min_domain_size:
                    # Update if smaller domain found
                    min_domain_size = domain_size
                    max_degree = count_unassigned_neighbors(kropki, r, c, relations)
                    best_cell = (r, c)

                elif domain_size == min_domain_size:
                    # Break ties with Degree Heuristics
                    degree = count_unassigned_neighbors(kropki, r, c, relations)
                    if degree > max_degree:
                        max_degree = degree
                        best_cell = (r, c)

    return best_cell

def count_unassigned_neighbors(kropki, r, c, relations):
    """
    Counts the number of unassigned neighbors for a cell, based on Kropki relations.
    """
    count = 0
    for (cell1, cell2) in relations:
        if (r, c) == cell1 or (r, c) == cell2:
            other_r, other_c = cell2 if (r, c) == cell1 else cell1
            if kropki[other_r][other_c] == 0:  # Unassigned neighbor
                count += 1
    return count

def order_domain_values(r, c, domains):
    return sorted(domains[(r, c)])

def backtrack(kropki, relations, domains, row_constraints, col_constraints, box_constraints):
    """
    Before trying a value, use the is_valid function to check whether the current assignment satisfies all constraints.
    If an assignment results in a constraint violation, backtrack and try other possible values.
    """
    global backtrack_count

    # Get next unassigned variable using MRV and DH
    next_cell = select_unassigned_variable(kropki, domains, relations)

    # If no unassigned variables remain, puzzle is solved
    if next_cell is None:
        return True

    r, c = next_cell

    for k in order_domain_values(r, c, domains):
        if is_valid(kropki, relations, r, c, k, row_constraints, col_constraints, box_constraints):
            kropki[r][c] = k
            assign_value(r, c, k, row_constraints, col_constraints, box_constraints)

            domains_copy = deepcopy(domains)
            if forward_check(kropki, relations, domains_copy):
                if backtrack(kropki, relations, domains_copy, row_constraints, col_constraints, box_constraints):
                    return True

            kropki[r][c] = 0
            remove_value(r, c, k, row_constraints, col_constraints, box_constraints)
            backtrack_count += 1

    return False

def main():
    global backtrack_count
    backtrack_count = 0
    
    with open('Sample_Input.txt', 'r') as file:
        lines = file.readlines()
    # with open('Input3.txt', 'r') as file:
    #     lines = file.readlines()

    hard_kropki_solution = [list(map(int, line.split())) for line in lines[:9]]  # Board
    # print(board)
    horizontal_dots = [list(map(int, line.split())) for line in lines[10:19]]  # Horizontal
    vertical_dots = [list(map(int, line.split())) for line in lines[20:28]]  # Vertical

    hard_relations = build_dot_constraints(horizontal_dots, vertical_dots)
    
    domains = {(row, col): set(range(1, 10)) for row in range(9) for col in range(9)}

    row_constraints, col_constraints, box_constraints = build_constraints(hard_kropki_solution)

    start_time = time.time()
    # Initial domain cleanup to reduce total searching time 
    if forward_check(hard_kropki_solution, hard_relations, domains):
        if backtrack(hard_kropki_solution, hard_relations, domains, row_constraints, col_constraints, box_constraints):
            print("Solution found:")
            end_time = time.time()
            for row in hard_kropki_solution:
                print(row)
        else:
            print("No solution found.")
    else:
        print("Invalid puzzle - constraints cannot be satisfied")

    print(f"Backtrack steps: {backtrack_count}")
    print(f"Time taken: {end_time - start_time:.6f} seconds")

main()