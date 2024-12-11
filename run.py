from backtrack_alg import *
import argparse, time

def extract_input(args):
    input_file = args.input_file

    with open(input_file, 'r') as file:
        lines = file.readlines()

    sudoku_board = [list(map(int, line.split())) for line in lines[:9]]  # Board
    horizontal_dots = [list(map(int, line.split())) for line in lines[10:19]]  # Horizontal (Row)
    vertical_dots = [list(map(int, line.split())) for line in lines[20:28]]  # Vertical (Col)

    return sudoku_board, horizontal_dots, vertical_dots
    
def run_cps(sudoku_board, horizontal_dots, vertical_dots):
    # Initialize domains 
    domains = {(row, col): set(range(1, 10)) for row in range(9) for col in range(9)}
    # Build constraints for row / column / box / dot
    row_constraints, col_constraints, box_constraints = build_constraints(sudoku_board)
    dot_constraints = build_dot_constraints(horizontal_dots, vertical_dots)

    start_time = time.time()

    # Before solving, the domain is dynamically updated through constraint propagation to reduce the search space.
    if forward_check(sudoku_board, dot_constraints, domains):
        if backtrack(sudoku_board, dot_constraints, domains, row_constraints, col_constraints, box_constraints):
            print("Solution found:")
            end_time = time.time()
            for row in sudoku_board:
                print(row)
        else:
            print("No solution found.")
    else:
        print("Invalid sudoku - constraints cannot be satisfied")

    print(f"Backtrack steps: {backtrack_count}")
    print(f"Time taken: {end_time - start_time:.6f} seconds")

    return sudoku_board

def generate_output(args, sudoku_board):
    filename = args.output_file
    try:
        with open(filename, 'w') as f:
            for row in sudoku_board:
                # Join integers in the row with spaces and write to the file
                f.write(' '.join(map(str, row)) + '\n')
        print(f"Sudoku board successfully written to {filename}")
    except Exception as e:
        print(f"An error occurred while writing the file: {e}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_file",
        type=str,
        required=True,
        help="The input file that contains the puzzle."
    )
    parser.add_argument(
        "--output_file",
        type=str,
        required=True,
        help="The output file that contains the solution."
    )

    args = parser.parse_args()

    global backtrack_count
    backtrack_count = 0

    sudoku_board, horizontal_dots, vertical_dots = extract_input(args)

    sudoku_board = run_cps(sudoku_board, horizontal_dots, vertical_dots)

    generate_output(args, sudoku_board)
    

main()