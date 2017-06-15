
from sudoku_state import set_N, SudokuBoard, SudokuSquare, StatePrinter, SudokuState


class InvalidStateError(Exception):
    def InvalidStateError(
            self, state=None, invalid_sets=None, invalid_squares=None):
        self.state = state
        self.invalid_sets = invalid_sets
        self.invalid_squares = invalid_squares


class DuplicateValueError(InvalidStateError):
    def DuplicateValueError(self, constraint_set):
        super(ImpossibleValueError, self).__init__(invalid_sets=[constraint_set])


class ImpossibleValueError(InvalidStateError):
    def ImpossibleValueError(self, square):
        super(ImpossibleValueError, self).__init__(invalid_squares=[square])


class SudokuSolverTechnique:
    @classmethod
    def apply(cls, state):
        new_state = state.copy(transition_technique=cls)
        cls.apply_to_sets(new_state.sets)
        cls.apply_to_squares(new_state.squares)
        if new_state == state:
            return state
        return new_state

    @classmethod
    def apply_to_sets(cls, sets):
        pass

    @classmethod
    def apply_to_squares(cls, squares):
        pass


class ValidatorTechnique(SudokuSolverTechnique):
    @classmethod
    def apply_to_sets(cls, sets):
        for sq_set in sets:
            values = [sq.known_value for sq in sq_set]
            known_values = [v for v in values if v]
            # no duplicates
            if len(set(known_values)) != len(known_values):
                raise DuplicateValueError(sq_set)

    @classmethod
    def apply_to_squares(cls, squares):
        for sq in squares:
            if sq.bitmask <= 0:
                raise ImpossibleValueError(sq)


class EliminateValues(SudokuSolverTechnique):
    @classmethod
    def apply_to_sets(cls, sets):
        """
        >>> set_N(2)
        >>> from sudoku_state import N, N_2, N_3, N_4
        >>> board = SudokuBoard()
        >>> squares = [SudokuSquare() for i in range(N_4)]
        >>> state = SudokuState(squares=squares, board=board)
        >>> StatePrinter.print_board_state(state)
        #====+====#====+====#
        # 12 | 12 # 12 | 12 #
        # 34 | 34 # 34 | 34 #
        #----+----#----+----#
        # 12 | 12 # 12 | 12 #
        # 34 | 34 # 34 | 34 #
        #====+====#====+====#
        # 12 | 12 # 12 | 12 #
        # 34 | 34 # 34 | 34 #
        #----+----#----+----#
        # 12 | 12 # 12 | 12 #
        # 34 | 34 # 34 | 34 #
        #====+====#====+====#
        >>> for v, i in enumerate(range(0, N_4, N_2 + 1)):
        ...     squares[i].set_value(v+1)
        >>> state = SudokuState(squares=squares, parent=state)
        >>> StatePrinter.print_board_state(state)
        #====+====#====+====#
        # 1  | 12 # 12 | 12 #
        #    | 34 # 34 | 34 #
        #----+----#----+----#
        # 12 |  2 # 12 | 12 #
        # 34 |    # 34 | 34 #
        #====+====#====+====#
        # 12 | 12 #    | 12 #
        # 34 | 34 # 3  | 34 #
        #----+----#----+----#
        # 12 | 12 # 12 |    #
        # 34 | 34 # 34 |  4 #
        #====+====#====+====#
        >>> state = EliminateValues.apply(state)
        >>> StatePrinter.print_board_state(state)
        #====+====#====+====#
        # 1  |    #  2 |  2 #
        #    | 34 #  4 | 3  #
        #----+----#----+----#
        #    |  2 # 1  | 1  #
        # 34 |    #  4 | 3  #
        #====+====#====+====#
        #  2 | 1  #    | 12 #
        #  4 |  4 # 3  |    #
        #----+----#----+----#
        #  2 | 1  # 12 |    #
        # 3  | 3  #    |  4 #
        #====+====#====+====#
        """
        for sq_set in sets:
            for sq in iter(sq_set):
                for sq2 in iter(sq_set):
                    sq.subtract(sq2)


class SudokuSolver:
    TECHNIQUES = [
        ValidatorTechnique,
        EliminateValues
    ]

    def __init__(self, initial_state):
        self._initial_state = initial_state
        self._current_state = initial_state

    def solve_iter(self):
        for t in SudokuSolver.TECHNIQUES:
            prev_state = None
            while prev_state != self._current_state:
                prev_state = self._current_state
                self._current_state = t.apply(prev_state)
                if self._current_state != prev_state:
                    yield self._current_state


if __name__ == "__main__":
    import doctest
    doctest.testmod()


