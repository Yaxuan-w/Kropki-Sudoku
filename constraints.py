def build_dot_constraints(horizontal_dots, vertical_dots):
    """
    Builds the Kropki dot constraints dictionary, representing the relationships between adjacent cells in the Sudoku board.

    Parses horizontal_dots (row-based constraints) and vertical_dots (column-based constraints).
    Creates constraints for white dots (difference of 1) and black dots (value is double).
    Returns a dictionary dot_relations with keys as tuples of adjacent cell coordinates and values as the constraint type.
    """
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
    """
    Updates the constraints when a value is assigned to a cell.
    - Adds value k to the row, column, and subgrid constraints for cell (r, c).
    """
    row_constraints[r].add(k)
    col_constraints[c].add(k)
    box_constraints[(r // 3, c // 3)].add(k)

def remove_value(r, c, k, row_constraints, col_constraints, box_constraints):
    """
    Removes a value from constraints when a cell is unassigned during backtracking.
    - Removes value k from the row, column, and subgrid constraints for cell (r, c).
    """
    row_constraints[r].remove(k)
    col_constraints[c].remove(k)
    box_constraints[(r // 3, c // 3)].remove(k)
    