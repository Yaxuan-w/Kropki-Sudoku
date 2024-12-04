"""
Decalre a data structure for sudokus(entire), data structure contains:
- cells (all cells in this sudokus)
- possibilities
- binary_constraints
- related_cells
"""
import itertools
import sys

# coordinates idea from @ https://github.com/speix/sudoku-solver/blob/master/sudoku.py
rows = "123456789"
cols = "ABCDEFGHI"

class Sudoku:

    """
    INITIALIZATION 
    """
    def __init__(self, grid, horizontal_dots, vertical_dots):
        # generation of all the coords of the grid
        self.cells = list()
        self.cells = self.generate_coords()

        # generation of all the possibilities for each one of these coords
        self.possibilities = dict()
        self.possibilities = self.generate_possibilities(grid)
   
        # generation of the line / row / square constraints
        rule_constraints = self.generate_rules_constraints()

        # convertion of these constraints to binary constraints
        self.binary_constraints = list()
        self.binary_constraints = self.generate_binary_constraints(rule_constraints)

        # generating all constraint-related cells for each of them
        self.related_cells = dict()
        self.related_cells = self.generate_related_cells()

        #prune
        self.pruned = dict()
        self.pruned = {v: [] for v in self.cells}

        # 新增水平和垂直点信息
        self.horizontal_dots = horizontal_dots
        self.vertical_dots = vertical_dots

        # 添加点约束
        self.dot_constraints = self.generate_dot_constraints()


    """
    generates all the coordinates of the cells
    """
    def generate_coords(self):

        all_cells_coords = []

        # for A,B,C, ... ,H,I
        for col in cols:
            #for 1,2,3 ,... ,8,9
            for row in rows:
                # A1, A2, A3, ... , H8, H9
                new_coords = col + row
                all_cells_coords.append(new_coords)

        return all_cells_coords

    """
    generates all possible value remaining for each cell
    """
    def generate_possibilities(self, grid):

        grid_as_list = list(grid)

        possibilities = dict()

        for index, coords in enumerate(self.cells):
            # if value is 0, then the cell can have any value in [1, 9]
            if grid_as_list[index] == "0":
                possibilities[coords] = list(range(1,10))
            # else value is already defined, possibilities is this value
            else:
                possibilities[coords] = [int(grid_as_list[index])]
                print(possibilities[coords])

        print(possibilities)
        return possibilities

    """
    generates the constraints based on the rules of the game:
    value different from any in row, column or square
    """
    def generate_rules_constraints(self):
        
        row_constraints = []
        column_constraints = []
        square_constraints = []

        # get rows constraints
        for row in rows:
            row_constraints.append([col + row for col in cols])

        # get columns constraints
        for col in cols:
            column_constraints.append([col + row for row in rows])

        # get square constraints
        # how to split coords (non static): 
        # https://stackoverflow.com/questions/9475241/split-string-every-nth-character
        rows_square_coords = (cols[i:i+3] for i in range(0, len(rows), 3))
        rows_square_coords = list(rows_square_coords)

        cols_square_coords = (rows[i:i+3] for i in range(0, len(cols), 3))
        cols_square_coords = list(cols_square_coords)

        # for each square
        for row in rows_square_coords:
            for col in cols_square_coords:

                current_square_constraints = []
                
                # and for each value in this square
                for x in row:
                    for y in col:
                        current_square_constraints.append(x + y)

                square_constraints.append(current_square_constraints)

        # all constraints is the sum of these 3 rules
        return row_constraints + column_constraints + square_constraints

    """
    generates the binary constraints based on the rule constraints
    """
    def generate_binary_constraints(self, rule_constraints):
        generated_binary_constraints = list()

        # for each set of constraints
        for constraint_set in rule_constraints:

            binary_constraints = list()

            # 2 because we want binary constraints
            # solution taken from :
            # https://stackoverflow.com/questions/464864/how-to-get-all-possible-combinations-of-a-list-s-elements
            
            #for tuple_of_constraint in itertools.combinations(constraint_set, 2):
            for tuple_of_constraint in itertools.permutations(constraint_set, 2):
                binary_constraints.append(tuple_of_constraint)

            # for each of these binary constraints
            for constraint in binary_constraints:

                # check if we already have this constraint saved
                # = check if already exists
                # solution from https://stackoverflow.com/questions/7571635/fastest-way-to-check-if-a-value-exist-in-a-list
                constraint_as_list = list(constraint)
                if(constraint_as_list not in generated_binary_constraints):
                    generated_binary_constraints.append([constraint[0], constraint[1]])

        return generated_binary_constraints

    """
    generates the the constraint-related cell for each one of them
    """
    def generate_related_cells(self):
        related_cells = dict()

        #for each one of the 81 cells
        for cell in self.cells:

            related_cells[cell] = list()

            # related cells are the ones that current cell has constraints with
            for constraint in self.binary_constraints:
                if cell == constraint[0]:
                    related_cells[cell].append(constraint[1])

        return related_cells
    
    def generate_dot_constraints(self):
        dot_constraints = []

        # 生成水平点约束
        for row in range(9):
            for col in range(8):  # 只需处理相邻单元格
                cell1 = cols[col] + rows[row]
                cell2 = cols[col + 1] + rows[row]
                if self.horizontal_dots[row][col] == 1:  # 白点
                    dot_constraints.append((cell1, cell2, "white"))
                elif self.horizontal_dots[row][col] == 2:  # 黑点
                    dot_constraints.append((cell1, cell2, "black"))

        # 生成垂直点约束
        for row in range(8):  # 只需处理相邻单元格
            for col in range(9):
                cell1 = cols[col] + rows[row]
                cell2 = cols[col] + rows[row + 1]
                if self.vertical_dots[row][col] == 1:  # 白点
                    dot_constraints.append((cell1, cell2, "white"))
                elif self.vertical_dots[row][col] == 2:  # 黑点
                    dot_constraints.append((cell1, cell2, "black"))

        return dot_constraints

    """
    checks if the Sudoku's solution is finished
    we loop through the possibilities for each cell
    if all of them has only one, then the Sudoku is solved
    """
    def isFinished(self):
        for coords, possibilities in self.possibilities.items():
            if len(possibilities) > 1:
                return False
        
        return True
    
    """
    returns a human-readable string
    """
    def __str__(self):

        output = ""
        count = 1
        
        # for each cell, print its value
        for cell in self.cells:

            # trick to get the right print in case of an AC3-finished sudoku
            value = str(self.possibilities[cell])
            if type(self.possibilities[cell]) == list:
                value = str(self.possibilities[cell][0])

            output += "[" + value + "]"

            # if we reach the end of the line,
            # make a new line on display
            if count >= 9:
                count = 0
                output += "\n"
            
            count += 1
        
        return output

"""
is_different
checks if two cells are the same
"""
def is_different(cell_i, cell_j):
    result = cell_i != cell_j
    return result

"""
number of conflicts
counts the number of conflicts for a cell with a specific value
"""
def number_of_conflicts(sudoku, cell, value):

    count = 0

    # for each of the cells that can be in conflict with cell
    for related_c in sudoku.related_cells[cell]:

        # if the value of related_c is not found yet AND the value we look for exists in its possibilities
        if len(sudoku.possibilities[related_c]) > 1 and value in sudoku.possibilities[related_c]:
            
            # then a conflict exists
            count += 1

    return count

"""
is_consistent

checks if the value is consistent in the assignments
"""
def is_consistent(sudoku, assignment, cell, value):
    is_consistent = True
    
    # 原有约束：行、列、小方块内不能重复
    for current_cell, current_value in assignment.items():
        if current_value == value and current_cell in sudoku.related_cells[cell]:
            is_consistent = False

    # 新增点约束检查
    # for constraint in sudoku.dot_constraints:
    #     cell1, cell2, dot_type = constraint

    #     if cell1 == cell or cell2 == cell:
    #         other_cell = cell2 if cell1 == cell else cell1

    #         if other_cell in assignment:
    #             other_value = assignment[other_cell]
    #             if dot_type == "white" and abs(value - other_value) != 1:
    #                 is_consistent = False
    #             if dot_type == "black" and (value != 2 * other_value and other_value != 2 * value):
    #                 is_consistent = False

    return is_consistent


"""
assign
add {cell: val} to assignment
inspired by @ http://aima.cs.berkeley.edu/python/csp.html
"""
def assign(sudoku, cell, value, assignment):
    # add {cell: val} to assignment
    assignment[cell] = value
    if sudoku.possibilities:
        # forward check
        forward_check(sudoku, cell, value, assignment)

"""
unassign
remove {cell: val} from assignment (backtracking)
inspired by @ http://aima.cs.berkeley.edu/python/csp.html
"""
def unassign(sudoku, cell, assignment):
    # if the cell is in assignment
    if cell in assignment:
        # for coord, each value in pruned
        for (coord, value) in sudoku.pruned[cell]:

            # add it to the possibilities
            sudoku.possibilities[coord].append(value)

        # reset pruned for the cell
        sudoku.pruned[cell] = []

        # and delete its assignment
        del assignment[cell]

"""
forward check
domain reduction for the current assignment
idea based on @ https://github.com/ishpreet-singh/Sudoku
"""
def forward_check(sudoku, cell, value, assignment):

    # for each related cell of cell
    for related_c in sudoku.related_cells[cell]:

        # if this cell is not in assignment
        if related_c not in assignment:

            # and if the value remains in the possibilities
            if value in sudoku.possibilities[related_c]:

                # removed it from the possibilities
                sudoku.possibilities[related_c].remove(value)

                # and add it to pruned
                sudoku.pruned[cell].append((related_c, value))

"""
fetch sudokus
fetches sudokus based on user's input
"""
def fetch_sudokus(input_file):
    with open(input_file, 'r') as f:
        lines = f.readlines()

    # 第 1-9 行是初始网格
    grid = ''.join(line.strip().replace(' ', '') for line in lines[:9])

    print(grid)
    # 第 10 行是空行，忽略
    # 第 11-19 行是水平点信息
    horizontal_dots = [list(map(int, line.strip().split())) for line in lines[10:19]]

    # 第 20 行是空行，忽略
    # 第 21-28 行是垂直点信息
    vertical_dots = [list(map(int, line.strip().split())) for line in lines[20:28]]

    return grid, horizontal_dots, vertical_dots


def print_grid(grid):

        output = ""
        count = 1
        
        # for each cell, print its value
        for cell in grid:

            value = cell
            output += "[" + value + "]"

            # if we reach the end of the line,
            # make a new line on display
            if count >= 9:
                count = 0
                output += "\n"
            
            count += 1
        
        return output

"""
Most Constrained Variable (MRV) heuristic

definitions & explanations @ https://www.cs.unc.edu/~lazebnik/fall10/lec08_csp2.pdf
returns the variable with the fewest possible values remaining
"""
def select_unassigned_variable(assignment, sudoku):

    unassigned = []

    # for each of the cells
    for cell in sudoku.cells:

        # if the cell is not in the assignment
        if cell not in assignment:

            # add it
            unassigned.append(cell)

    # the criterion here is the length of the possibilities (MRV)
    criterion = lambda cell: len(sudoku.possibilities[cell])

    # we return the variable with the fewest possible values remaining
    return min(unassigned, key=criterion)


def order_domain_values(sudoku, cell):
    return sorted(sudoku.possibilities[cell])

def recursive_backtrack_algorithm(assignment, sudoku):

    # if assignment is complete then return assignment
    if len(assignment) == len(sudoku.cells):
        return assignment

    # var = select-unassigned-variables(csp)
    cell = select_unassigned_variable(assignment, sudoku)

    # for each value in order-domain-values(csp, var)
    for value in order_domain_values(sudoku, cell):

        # if value is consistent with assignment
        if is_consistent(sudoku, assignment, cell, value):

            # add {cell = value} to assignment
            assign(sudoku, cell, value, assignment)

            # result = backtrack(assignment, csp)
            result = recursive_backtrack_algorithm(assignment, sudoku)

            # if result is not a failure return result
            if result:
                return result

            # remove {cell = value} from assignment
            unassign(sudoku, cell, assignment)
   
    # return failure
    return False

def write_solution(output_file, assignment, sudoku):
    with open(output_file, 'w') as f:
        for row in rows:
            line = []
            for col in cols:
                cell = col + row
                line.append(str(assignment[cell]))
            f.write(' '.join(line) + '\n')

if __name__ == "__main__":
    input_file = "Sample_Input.txt"
    output_file = "output.txt"

    # 读取输入
    grid, horizontal_dots, vertical_dots = fetch_sudokus(input_file)

    # 初始化数独
    sudoku = Sudoku(grid, horizontal_dots, vertical_dots)

    # 求解数独
    assignment = {}
    solution = recursive_backtrack_algorithm(assignment, sudoku)

    if solution:
        write_solution(output_file, solution, sudoku)
        print("Solution written to", output_file)
    else:
        print("No solution found.")