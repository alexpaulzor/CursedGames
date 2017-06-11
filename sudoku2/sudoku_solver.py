
from sudoku_state import set_N, N, N_4, SudokuBoard, SudokuSquare, StatePrinter, SudokuState


class InvalidStateError(Exception):
    def InvalidStateError(
            self, state=None, invalid_sets=None, invalid_squares=None):
        self.state = state
        self.invalid_sets = invalid_sets
        self.invalid_squares = invalid_squares


class DuplicateValueError(InvalidStateError):
    pass


class SudokuSolverTechnique:
    @classmethod
    def apply(cls, state):
        new_state = state.copy(transition_technique=cls)
        cls.apply_to_sets(new_state.sets)
        return new_state

    @classmethod
    def apply_to_sets(cls, sets):
        pass


class ValidatorTechnique(SudokuSolverTechnique):
    @classmethod
    def apply_to_sets(cls, sets):
        for sq_set in sets:
            values = [sq.known_value for sq in sq_set]
            known_values = [v for v in values if v]
            # no duplicates
            if len(set(known_values)) != len(known_values):
                raise DuplicateValueError(sets=[sq_set])


class EliminateValues(SudokuSolverTechnique):
    @classmethod
    def apply_to_sets(cls, sets):
        for sq_set in sets:
            for sq in sq_set:
                for sq2 in sq_set:
                    if sq != sq2:
                        sq -= sq2

if __name__ == "__main__":
    import doctest
    doctest.testmod()

    set_N(3)
    board = SudokuBoard()
    squares = [SudokuSquare(bitmask=i) for i in range(N_4)]
    print str(squares)
    state = SudokuState(squares=squares, board=board)
    StatePrinter.print_board_state(state)

    print "EliminatieValues"
    eliminated = EliminateValues.apply(state)
    StatePrinter.print_board_state(eliminated)

    print "EliminatieValues"
    validated = ValidatorTechnique.apply(state)
    StatePrinter.print_board_state(validated)


