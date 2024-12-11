from copy import deepcopy
from constraints import *
import counter

def check_kropki(dot_relations, domains, changed):
    """
    Updates domains based on Kropki dot constraints by removing invalid values.
    - For each pair of cells with a Kropki constraint, ensures their domains satisfy the constraint.
    - Removes invalid values and marks changed if a domain is updated.
    - Returns the changed flag.
    """
    # Handle Kropki constraints
    for (cell1, cell2), constraint in dot_relations.items():
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
    """
    Updates domains based on Sudoku rules (row, column, and subgrid uniqueness).
    - For each filled cell in the board, removes its value from the domains of other cells in the same row, column, or subgrid.
    - Marks changed if a domain is updated and returns the flag.
    """
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
    - Iteratively applies check_kropki and check_sudoku until no more changes occur.
    - Returns False if any domain becomes empty, otherwise returns True.
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


def _is_valid(kropki, relations, r, c, k, row_constraints, col_constraints, box_constraints):
    """
    Checks whether assigning a value to a cell satisfies all constraints.
    - Ensures value k does not violate row, column, or subgrid constraints.
    - Validates that k satisfies Kropki dot constraints with adjacent cells.
    """
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
    Use Minimum Remaining Values (MRV) and Degree Heuristics (DH) to select the next unassigned variable:
    - Prefer the variable with the smallest domain size (MRV).
    - If the domain sizes are the same, select the variable that participates in the most constraints (DH)
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
                    max_degree = _count_unassigned_neighbors(kropki, r, c, relations)
                    best_cell = (r, c)

                elif domain_size == min_domain_size:
                    # Break ties with Degree Heuristics
                    degree = _count_unassigned_neighbors(kropki, r, c, relations)
                    if degree > max_degree:
                        max_degree = degree
                        best_cell = (r, c)

    return best_cell

def _count_unassigned_neighbors(kropki, r, c, relations):
    """
    Helper function for select_unassigned_variable:
    Counts the number of unassigned neighbors for a cell, based on Kropki relations.
    - Traverses Kropki constraints and counts the neighbors of cell (r, c) that are not yet assigned.
    """
    count = 0
    for (cell1, cell2) in relations:
        if (r, c) == cell1 or (r, c) == cell2:
            other_r, other_c = cell2 if (r, c) == cell1 else cell1
            if kropki[other_r][other_c] == 0:  # Unassigned neighbor
                count += 1
    return count

def order_domain_values(r, c, domains):
    """
    Try possible values of the current variable in ascending order
    """
    return sorted(domains[(r, c)])

def backtrack(kropki, relations, domains, row_constraints, col_constraints, box_constraints):
    """
    Before trying a value, use the _is_valid function to check whether the current assignment satisfies all constraints.
    If an assignment results in a constraint violation, backtrack and try other possible values.
    """

    # Get next unassigned variable using MRV and DH
    next_cell = select_unassigned_variable(kropki, domains, relations)

    # If no unassigned variables remain, puzzle is solved
    if next_cell is None:
        return True

    r, c = next_cell

    # Selects an unassigned variable using select_unassigned_variable.
    # Iteratively assigns a valid value from the domain, propagates constraints using forward_check, and recursively searches 
    # for a solution.
    # If a conflict occurs, reverts the assignment and tries another value.
    for k in order_domain_values(r, c, domains):
        if _is_valid(kropki, relations, r, c, k, row_constraints, col_constraints, box_constraints):
            kropki[r][c] = k
            assign_value(r, c, k, row_constraints, col_constraints, box_constraints)

            domains_copy = deepcopy(domains)
            if forward_check(kropki, relations, domains_copy):
                if backtrack(kropki, relations, domains_copy, row_constraints, col_constraints, box_constraints):
                    return True

            kropki[r][c] = 0
            remove_value(r, c, k, row_constraints, col_constraints, box_constraints)
            counter.BACKTRACK_COUNTER += 1

    return False
