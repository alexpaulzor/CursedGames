
from sudoku_state import set_N, N_2, SudokuSquare, StatePrinter, SudokuState, SudokuBoard


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
        >>> squares = [SudokuSquare(id=i) for i in range(N_4)]
        >>> state = SudokuState(squares=squares, board=board)
        >>> StatePrinter.print_board_state(state)
        #====+====#====+====#
        #    |    #    |    #
        #    |    #    |    #
        #----+----#----+----#
        #    |    #    |    #
        #    |    #    |    #
        #====+====#====+====#
        #    |    #    |    #
        #    |    #    |    #
        #----+----#----+----#
        #    |    #    |    #
        #    |    #    |    #
        #====+====#====+====#
        >>> for v, i in enumerate(range(0, N_4, N_2 + 1)):
        ...     squares[i].set_value(v+1)
        >>> state = SudokuState(squares=squares, parent=state)
        >>> StatePrinter.print_board_state(state)
        #====+====#====+====#
        # 1  |    #    |    #
        #    |    #    |    #
        #----+----#----+----#
        #    |  2 #    |    #
        #    |    #    |    #
        #====+====#====+====#
        #    |    #    |    #
        #    |    # 3  |    #
        #----+----#----+----#
        #    |    #    |    #
        #    |    #    |  4 #
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
            sqs_with_val = {}
            sqs_by_bitmask = {}
            for sq in iter(sq_set):
                for sq2 in iter(sq_set):
                    if sq2.known_value:
                        sq.eliminate(sq2)

                pvals = sq.possible_values()

                if sq.bitmask not in sqs_by_bitmask:
                    sqs_by_bitmask[sq.bitmask] = []
                sqs_by_bitmask[sq.bitmask].append(sq)

                for val in pvals:
                    if val not in sqs_with_val:
                        sqs_with_val[val] = []
                    sqs_with_val[val].append(sq)

            for val, sqs in sqs_with_val.iteritems():
                if len(sqs) == 1:
                    #print "Found unique value {} for {}".format(val, sqs[0])
                    sqs[0].set_value(val)

            for bm, sqs in sqs_by_bitmask.iteritems():
                if len(sqs) > 1:
                    pvals = list(SudokuSquare.bitmask_to_possible_values(bm))
                    if len(sqs) == len(pvals):
                        for sq in iter(sq_set):
                            if sq not in sqs:
                                sq.eliminate(sqs[0])





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
        yield self._current_state


if __name__ == "__main__":
    import doctest
    doctest.testmod()


