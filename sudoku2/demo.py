
from sudoku_state import set_N, SudokuBoard, SudokuSquare, StatePrinter, SudokuState
set_N(3)
from sudoku_state import N, N_2, N_3, N_4

from sudoku_solver import EliminateValues, ValidatorTechnique, SudokuSolver

#values = "790000300000006900800030076000005002005418700400700000610090008002300000009000054" # noqa

values = "...71....5..............53.16..2.3......3...9.456......9.2...7.6.....2.3.....6.81"  # noqa


values = values.replace('.', '0').replace(' ', '0')

board = SudokuBoard()
squares = [SudokuSquare(value=int(values[i]), id=i) for i in range(N_4)]
print str(squares)
state = SudokuState(squares=squares, board=board)
StatePrinter.print_board_state(state, color=True)

solver = SudokuSolver(state, enable_guess_and_check=True)

for newstate in solver.solve_iter():
    if newstate and newstate.parent:
        print "{} -> {} -> {}".format(
            newstate.parent._id, newstate.transition_technique, newstate._id)
        StatePrinter.print_board_diff(newstate.parent, newstate, color=True)
    else:
        StatePrinter.print_board_state(newstate, color=True)

StatePrinter.print_board_state(solver._current_state, color=True)
StatePrinter.print_playable_state(solver._current_state)

# # for i in range(N_2):
# #     squares[N_2 * i + i].set_value(i+1)
# # state = SudokuState(squares=squares, parent=state)
# # StatePrinter.print_board_state(state)

# for i in range(30):
#     print "EliminateValues {}".format(i)
#     eliminated = EliminateValues.apply(state)
#     # StatePrinter.print_board_state(eliminated)
#     StatePrinter.print_board_diff(eliminated, state)
#     if eliminated == state:
#         break
#     state = eliminated

# # print "EliminateValues"
# # eliminated = EliminateValues.apply(state)
# # StatePrinter.print_board_state(eliminated)

# print "ValidatorTechnique"
# validated = ValidatorTechnique.apply(eliminated)
# StatePrinter.print_board_state(validated)
