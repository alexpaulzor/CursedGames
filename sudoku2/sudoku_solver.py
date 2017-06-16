import random

from sudoku_state import set_N, N_2, SudokuSquare, StatePrinter, SudokuState, SudokuBoard


class InvalidStateError(Exception):
    def __init__(
            self, state=None, invalid_sets=None, invalid_squares=None):
        self.state = state
        self.invalid_sets = invalid_sets
        self.invalid_squares = invalid_squares


class DuplicateValueError(InvalidStateError):
    def __init__(self, constraint_set):
        super(DuplicateValueError, self).__init__(invalid_sets=[constraint_set])


class ImpossibleValueError(InvalidStateError):
    def __init__(self, square):
        super(ImpossibleValueError, self).__init__(invalid_squares=[square])


class Winner(Exception):
    pass
    # def __init__(self):
    #     super(Winner, self).__init__("You won! {}".format(state))


class SudokuSolverTechnique:
    @classmethod
    def apply(cls, state):
        new_state = state.copy(transition_technique=cls)
        new_state = cls.apply_to_state(new_state)
        if not new_state or new_state == state:
            return state
        return new_state

    @classmethod
    def apply_to_state(cls, state):
        cls.apply_to_sets(state.sets)
        cls.apply_to_squares(state.squares)
        return state

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


class WinnerTechnique(SudokuSolverTechnique):
    @classmethod
    def apply(cls, state):
        if cls.check_sets(state.sets):
            return state
        return None

    @classmethod
    def check_sets(cls, sets):
        for sq_set in sets:
            values = [sq.known_value for sq in sq_set]
            known_values = [v for v in values if v]
            # no duplicates
            if len(set(known_values)) != N_2:
                return False
        return True


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
                    sqs[0].set_value(val)

            for bm, sqs in sqs_by_bitmask.iteritems():
                if len(sqs) > 1:
                    pvals = list(SudokuSquare.bitmask_to_possible_values(bm))
                    if len(sqs) == len(pvals):
                        for sq in iter(sq_set):
                            if sq not in sqs:
                                sq.eliminate(sqs[0])


class GuessAndCheck(SudokuSolverTechnique):
    @classmethod
    def apply_to_state(cls, state):
        shuffled_sqs = list(state.squares)
        random.shuffle(shuffled_sqs)
        for sq in sorted(shuffled_sqs, key=lambda s: len(list(s.possible_values()))):
            pvals = list(sq.possible_values())
            if len(pvals) > 1:
                random.shuffle(pvals)
                for pval in pvals:
                    finstate = cls.try_pval(state, sq, pval)
                    if finstate:
                        if WinnerTechnique.apply(finstate):
                            return finstate
                    else:
                        print "Determined {!r} != {}".format(sq, pval)
                        sq.eliminate(SudokuSquare(value=pval))
                        print "(now {!r})".format(sq, pval)
        return state

    @classmethod
    def try_pval(cls, state, sq, value):
        original_bitmask = sq.bitmask
        try:
            print "Trying {!r} = {}".format(sq, value)
            sq.set_value(value)
            solver = SudokuSolver(state)
            final_state = solver.solve()
            return final_state
        except InvalidStateError:
            return None
        finally:
            sq.set_bitmask(original_bitmask)
            print "Reverted {!r}".format(sq)


class SudokuSolver:
    def __init__(self, initial_state, enable_guess_and_check=False):
        self._initial_state = initial_state
        self._current_state = initial_state
        self._techniques = [
            ValidatorTechnique,
            EliminateValues
        ]
        if enable_guess_and_check:
            self._techniques.append(GuessAndCheck)

    def solve(self):
        for state in self.solve_iter():
            pass
        return self._current_state

    def solve_iter(self):
        prev_state = None
        while prev_state != self._current_state:
            prev_state = self._current_state
            self._current_state = self._solve_step()
            yield self._current_state
        yield self._current_state

    def _solve_step(self):
        prev_state = self._current_state
        for t in self._techniques:
            self._current_state = t.apply(prev_state)
            if self._current_state != prev_state:
                return self._current_state
        return self._current_state


if __name__ == "__main__":
    import doctest
    doctest.testmod()
