
from sudoku_state import set_N, SudokuBoard, SudokuSquare, StatePrinter, SudokuState
set_N(3)
from sudoku_state import N, N_2, N_3, N_4

from sudoku_solver import EliminateValues, ValidatorTechnique

board = SudokuBoard()
squares = [SudokuSquare() for i in range(N_4)]
print str(squares)
state = SudokuState(squares=squares, board=board)
StatePrinter.print_board_state(state)
for v, i in enumerate(range(0, N_4, N_2 + 1)):
    squares[i].set_value(v+1)
state = SudokuState(squares=squares, parent=state)
StatePrinter.print_board_state(state)

print "EliminateValues"
eliminated = EliminateValues.apply(state)
StatePrinter.print_board_state(eliminated)

# print "EliminateValues"
# eliminated = EliminateValues.apply(state)
# StatePrinter.print_board_state(eliminated)

print "ValidatorTechnique"
validated = ValidatorTechnique.apply(eliminated)
StatePrinter.print_board_state(validated)
