global N, N_2, N_3, N_4

def set_N(n=3):
    global N, N_2, N_3, N_4
    N = n          # 2  # 3
    N_2 = N * N    # 4  # 9
    N_3 = N_2 * N  # 8  # 27
    N_4 = N_3 * N  # 16 # 81

set_N()


class SudokuSquare:
    def __init__(self, value=None, bitmask=None):
        """
        >>> set_N(2)
        >>> global N, N_2, N_3, N_4
        >>> SudokuSquare()
        None 0b1111

        # >>> set_N(3)
        # >>> SudokuSquare()
        # None 0b111111111
        """
        if value:
            self.set_value(value)
        elif bitmask:
            self._value_bitmask = int(bitmask)
        else:
            self._value_bitmask = sum(
                [self.value_to_bitmask(i + 1) for i in range(N_2)])

    @property
    def bitmask(self):
        return int(self._value_bitmask)

    @classmethod
    def value_to_bitmask(cls, value):
        """
        >>> set_N(2)
        >>> bin(SudokuSquare.value_to_bitmask(4))
        '0b1000'
        >>> bin(SudokuSquare.value_to_bitmask(1))
        '0b1'
        >>> int(SudokuSquare.value_to_bitmask(3))
        4
        """
        return int(2 ** (value - 1))

    @classmethod
    def bitmask_to_known_value(cls, bmask):
        """
        >>> SudokuSquare.bitmask_to_known_value(0b0100)
        3
        """
        v = int(bmask).bit_length()
        if cls.value_to_bitmask(v) != bmask:
            return None
        return v

    @property
    def known_value(self):
        return SudokuSquare.bitmask_to_known_value(self.bitmask)

    def set_value(self, value):
        self._value_bitmask = SudokuSquare.value_to_bitmask(value)

    def set_bitmask(self, bitmask):
        self._value_bitmask = bitmask

    def __and__(self, other):
        if isinstance(other, SudokuSquare):
            return int(self.bitmask & other._value_bitmask)
        return int(self.bitmask & SudokuSquare.value_to_bitmask(other))

    def subtract(self, other):
        """
        >>> s = SudokuSquare()
        >>> s.subtract(SudokuSquare(value=3))
        >>> s
        None 0b1011
        >>> s.subtract(SudokuSquare(value=2))
        >>> s
        None 0b1001
        >>> s.subtract(SudokuSquare(value=1))
        >>> s
        4 0b1000
        """
        if (self != other and other.known_value and
            self.value_to_bitmask(other.known_value) & self._value_bitmask > 0):
            self._value_bitmask -= self.value_to_bitmask(other.known_value)

    def __isub__(self, other):
        self.subtract(other)

    def state_lines(self):
        """
        >>> ','.join(list(SudokuSquare(value=1).state_lines()))
        '1 ,  '
        >>> bm_1 = SudokuSquare.value_to_bitmask(1)
        >>> bm_2 = SudokuSquare.value_to_bitmask(2)
        >>> bm_3 = SudokuSquare.value_to_bitmask(3)
        >>> bm_4 = SudokuSquare.value_to_bitmask(4)
        >>> square = SudokuSquare(bitmask=bm_1 | bm_2 | bm_3 | bm_4)
        >>> square
        None 0b1111
        >>> ','.join(square.state_lines())
        '12,34'
        """
        return tuple(self._state_line_iter())

    def _state_line_iter(self):
        for lino in range(N):
            vals = [str(i) if self & i == SudokuSquare.value_to_bitmask(i) else ' '
                    for i in range(1 + N * lino, 1 + N * lino + N)
                    ]
            yield "".join(vals)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return ("{} 0b{:0" + str(N_2) + "b}").format(
            SudokuSquare.bitmask_to_known_value(self._value_bitmask),
            self.bitmask)


class SudokuState:
    def __init__(self, squares=None, parent=None, transition_technique=None,
                 board=None):
        if not squares:
            squares = [SudokuSquare() for i in range(N_4)]
        self.squares = squares
        self.parent = parent
        self.transition_technique = transition_technique

        if parent:
            self.board = parent.board
        elif board:
            self.board = board

    def copy(self, transition_technique=None):
        squares = [SudokuSquare(bitmask=sq.bitmask) for sq in self.squares]
        return SudokuState(
            squares=squares, parent=self,
            transition_technique=transition_technique)

    @classmethod
    def square_index(cls, x, y):
        return y * N_2 + x

    @property
    def sets(self):
        return self.board.sets(self)

    def __eq__(self, other):
        for i, my_sq in enumerate(self.squares):
            if my_sq.bitmask != other.squares[i].bitmask:
                return False
        return True

    def __sub__(self, other):
        diff_state = self.copy()
        for i, my_sq in enumerate(self.squares):
            diff_state.squares[i].set_bitmask(abs(my_sq.bitmask - other.squares[i].bitmask))
        return diff_state


class SudokuBoard:
    def __init__(self):
        self.constraints = [
            RowConstraint,
            ColumnConstraint,
            SectorConstraint
        ]

    def sets(self, state):
        for constraint in self.constraints:
            for sq_set in constraint.groups_iter(state):
                yield set(sq_set)


class SudokuBoardConstraint:
    @classmethod
    def groups_iter(cls, state):
        """Return a list of sets of SudokuSquares"""
        return


class RowConstraint(SudokuBoardConstraint):
    @classmethod
    def groups_iter(cls, state):
        """
        >>> set_N(2)
        >>> board = SudokuBoard()
        >>> squares = [SudokuSquare(value=(i % N_2)) for i in range(N_4)]
        >>> state = SudokuState(squares=squares, board=board)
        >>> StatePrinter.print_board_state(state)
        #====+====#====+====#
        # 12 | 1  #  2 |    #
        # 34 |    #    | 3  #
        #----+----#----+----#
        #    |    #    |    #
        #  4 |    #    |    #
        #====+====#====+====#
        #    | 12 # 1  |  2 #
        #    | 34 #    |    #
        #----+----#----+----#
        #    |    #    |    #
        # 3  |  4 #    |    #
        #====+====#====+====#
        >>> groups = list(RowConstraint.groups_iter(state))
        >>> [StatePrinter.print_square_set(g) for g in groups]
        #====+====#====+====#
        | 12 | 1  |  2 |    |
        | 34 |    |    | 3  |
        #====+====#====+====#
        #====+====#====+====#
        |    |    |    |    |
        |  4 |    |    |    |
        #====+====#====+====#
        #====+====#====+====#
        |    | 12 | 1  |  2 |
        |    | 34 |    |    |
        #====+====#====+====#
        #====+====#====+====#
        |    |    |    |    |
        | 3  |  4 |    |    |
        #====+====#====+====#
        [None, None, None, None]
        """
        for i in range(N_2):
            yield state.squares[
                SudokuState.square_index(0, i):
                SudokuState.square_index(0, i+1)]


class ColumnConstraint(SudokuBoardConstraint):
    @classmethod
    def groups_iter(cls, state):
        """
        >>> set_N(2)
        >>> board = SudokuBoard()
        >>> squares = [SudokuSquare(value=(i % N_2)) for i in range(N_4)]
        >>> state = SudokuState(squares=squares, board=board)
        >>> StatePrinter.print_board_state(state)
        #====+====#====+====#
        # 12 | 1  #  2 |    #
        # 34 |    #    | 3  #
        #----+----#----+----#
        #    |    #    |    #
        #  4 |    #    |    #
        #====+====#====+====#
        #    | 12 # 1  |  2 #
        #    | 34 #    |    #
        #----+----#----+----#
        #    |    #    |    #
        # 3  |  4 #    |    #
        #====+====#====+====#
        >>> groups = list(ColumnConstraint.groups_iter(state))
        >>> [StatePrinter.print_square_set(g) for g in groups]
        #====+====#====+====#
        | 12 |    |    |    |
        | 34 |  4 |    | 3  |
        #====+====#====+====#
        #====+====#====+====#
        | 1  |    | 12 |    |
        |    |    | 34 |  4 |
        #====+====#====+====#
        #====+====#====+====#
        |  2 |    | 1  |    |
        |    |    |    |    |
        #====+====#====+====#
        #====+====#====+====#
        |    |    |  2 |    |
        | 3  |    |    |    |
        #====+====#====+====#
        [None, None, None, None]
        """
        for i in range(N_2):
            yield [state.squares[j] for j in range(N_4) if j % N_2 == i]


class SectorConstraint(SudokuBoardConstraint):
    @classmethod
    def groups_iter(cls, state):
        """
        >>> set_N(2)
        >>> board = SudokuBoard()
        >>> squares = [SudokuSquare(value=(i % N_2)) for i in range(N_4)]
        >>> state = SudokuState(squares=squares, board=board)
        >>> StatePrinter.print_board_state(state)
        #====+====#====+====#
        # 12 | 1  #  2 |    #
        # 34 |    #    | 3  #
        #----+----#----+----#
        #    |    #    |    #
        #  4 |    #    |    #
        #====+====#====+====#
        #    | 12 # 1  |  2 #
        #    | 34 #    |    #
        #----+----#----+----#
        #    |    #    |    #
        # 3  |  4 #    |    #
        #====+====#====+====#
        >>> groups = list(SectorConstraint.groups_iter(state))
        >>> [StatePrinter.print_square_set(g) for g in groups]
        #====+====#====+====#
        | 12 | 1  |    |    |
        | 34 |    |  4 |    |
        #====+====#====+====#
        #====+====#====+====#
        |  2 |    |    |    |
        |    | 3  |    |    |
        #====+====#====+====#
        #====+====#====+====#
        |    | 12 |    |    |
        |    | 34 | 3  |  4 |
        #====+====#====+====#
        #====+====#====+====#
        | 1  |  2 |    |    |
        |    |    |    |    |
        #====+====#====+====#
        [None, None, None, None]
        """
        for i in range(N_2):
            start_y = i / N * N
            start_x = i % N * N

            squares = []
            for y in range(start_y, start_y + N):
                squares += state.squares[
                    SudokuState.square_index(start_x, y):
                    SudokuState.square_index(start_x, y) + N]

            yield squares


ROW_LETTERS = 'ABCDEFGHI'


class StatePrinter:
    @classmethod
    def line_sep(cls):
        return ('#' + '+'.join(['-' * (2 + N)] * N)) * N + '#'

    @classmethod
    def major_line_sep(cls):
        return ('#' + '+'.join(['=' * (2 + N)] * N)) * N + '#'

    @classmethod
    def print_board_state(cls, state):
        """
        >>> set_N(2)
        >>> board = SudokuBoard()
        >>> squares = [SudokuSquare(bitmask=i) for i in range(N_4)]
        >>> StatePrinter.print_board_state(SudokuState(squares=squares, board=board))  # noqa
        #====+====#====+====#
        # 12 | 1  #  2 | 12 #
        # 34 |    #    |    #
        #----+----#----+----#
        #    | 1  #  2 | 12 #
        # 3  | 3  # 3  | 3  #
        #====+====#====+====#
        #    | 1  #  2 | 12 #
        #  4 |  4 #  4 |  4 #
        #----+----#----+----#
        #    | 1  #  2 | 12 #
        # 34 | 34 # 34 | 34 #
        #====+====#====+====#
        """
        print cls.major_line_sep()
        for rowno, line in enumerate(StatePrinter._get_board_lines(state)):
            print line
            if (rowno + 1) % N == 0:
                print cls.major_line_sep()
            else:
                print cls.line_sep()

    @classmethod
    def print_board_diff(cls, state1, state2):
        state3 = state2 - state1
        cls.print_board_state(state3)

    @classmethod
    def _get_board_lines(cls, state):
        """
        >>> set_N(2)
        >>> board = SudokuBoard()
        >>> squares = [SudokuSquare(value=(i % N_2)) for i in range(N_4)]
        >>> list(StatePrinter._get_board_lines(SudokuState(squares=squares, board=board)))  # noqa
        ['# 12 | 1  #  2 |    #\\n# 34 |    #    | 3  #', '#    |    #    |    #\\n#  4 |    #    |    #', '#    | 12 # 1  |  2 #\\n#    | 34 #    |    #', '#    |    #    |    #\\n# 3  |  4 #    |    #']
        """
        for y in range(N_2):
            for row in cls._get_row_lines(
                    state.squares[SudokuState.square_index(0, y):
                                  SudokuState.square_index(0, y + 1)]):
                yield row

    @classmethod
    def print_square_set(cls, squares):
        print cls.major_line_sep()
        for line in cls._get_row_lines(squares, major_sep='|'):
            print line
        print cls.major_line_sep()

    @classmethod
    def _get_row_lines(cls, squares, major_sep='#'):
        row_lines = [''] * N
        for x, sq in enumerate(squares):
            for lino, sqline in enumerate(sq.state_lines()):
                sep = major_sep if x % N == 0 else '|'
                row_lines[lino] += sep + ' {} '.format(sqline)
        yield (major_sep + '\n').join(row_lines) + major_sep


if __name__ == "__main__":
    import doctest
    doctest.testmod()


