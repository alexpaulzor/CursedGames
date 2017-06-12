
from sudoku_state import set_N, SudokuBoard, SudokuSquare, StatePrinter, SudokuState
set_N(3)
from sudoku_state import N, N_2, N_3, N_4

from sudoku_solver import EliminateValues, ValidatorTechnique

board = SudokuBoard()
squares = [SudokuSquare() for i in range(N_4)]
print str(squares)
state = SudokuState(squares=squares, board=board)
StatePrinter.print_board_state(state)
for i in range(N_2):
    squares[i].set_value(i+1)
state = SudokuState(squares=squares, parent=state)
StatePrinter.print_board_state(state)

for i in range(30):
    print "EliminateValues {}".format(i)
    eliminated = EliminateValues.apply(state)
    # StatePrinter.print_board_state(eliminated)
    StatePrinter.print_board_diff(eliminated, state)
    if eliminated == state:
        break
    state = eliminated

# print "EliminateValues"
# eliminated = EliminateValues.apply(state)
# StatePrinter.print_board_state(eliminated)

print "ValidatorTechnique"
validated = ValidatorTechnique.apply(eliminated)
StatePrinter.print_board_state(validated)
