
def set_N(n=3):
    global N, N_2, N_3, N_4
    N = n          # 2  # 3
    N_2 = N * N    # 4  # 9
    N_3 = N_2 * N  # 8  # 27
    N_4 = N_3 * N  # 16 # 81

set_N()

class SudokuSquare:
    def __init__(self, value=None, bitmask=None):
        if value:
            self.set_value(value)
        elif bitmask:
            self._value_bitmask = int(bitmask)
        else:
            self._value_bitmask = N_4 - 1

    @classmethod
    def value_to_bitmask(cls, value):
        """
        >>> bin(SudokuSquare.value_to_bitmask(4))
        '0b1000'
        >>> bin(SudokuSquare.value_to_bitmask(1))
        '0b1'
        >>> int(SudokuSquare.value_to_bitmask(3))
        4
        """
        return int(2 ** (value - 1))

    @classmethod
    def bitmask_to_value(cls, bmask):
        """
        >>> SudokuSquare.bitmask_to_value(0b0100)
        3
        """
        v = int(bmask).bit_length()
        if cls.value_to_bitmask(v) != bmask:
            return None
        return v

    def set_value(self, value):
        self._value_bitmask = SudokuSquare.value_to_bitmask(value)

    @property
    def int_value(self):
        return int(self._value_bitmask)

    def __and__(self, other):
        if isinstance(other, SudokuSquare):
            return int(self._value_bitmask & other._value_bitmask)
        return int(self._value_bitmask & SudokuSquare.value_to_bitmask(other))

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
        return "{} 0b{:04b}".format(
            SudokuSquare.bitmask_to_value(self._value_bitmask),
            self.int_value)


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

    @classmethod
    def square_index(cls, x, y):
        return y * N_2 + x


class SudokuBoard:
    def __init__(self):
        self.constraints = [
            RowConstraint(),
            ColumnConstraint(),
            SectorConstraint()
        ]

    def sets(self, state):
        return [s
                for constraint in self.constraints
                for s in constraint.sets_iter()]


class SudokuBoardConstraint:
    def sets_iter(cls, state):
        """Return a list of sets of SudokuSquares"""
        return []


class RowConstraint(SudokuBoardConstraint):
    def sets_iter(cls, state):
        for i in range(N_2):
            yield set(state.squares[i * N_2:(i + 1) * N_2])


class ColumnConstraint(SudokuBoardConstraint):
    def sets_iter(cls, state):
        for i in range(N_2):
            yield set([state.squares[j] for j in range(N_4) if j % N_2 == i])


class SectorConstraint(SudokuBoardConstraint):
    def sets_iter(cls, state):
        for i in range(N_2):
            start_y = i / N * N
            start_x = i % N * N

            squares = []
            for y in range(start_y, start_y + N):
                squares += state.squares[
                    SudokuState.square_index(start_x, y):
                    SudokuState.square_index(start_x, y) + N]

            yield set(squares)


class BoardPrinter:
    @classmethod
    def print_board(cls, state):
        """
        # >>> board = SudokuBoard()
        # >>> squares = [SudokuSquare(value=(i % N_2)) for i in range(N_4)]
        # >>> BoardPrinter.print_board(SudokuState(squares=squares, board=board))  # noqa
        """
        line_sep = ('#' + '+'.join(['-' * (2 + N)] * N)) * N + '#'
        major_line_sep = ('#' + '+'.join(['=' * (2 + N)] * N)) * N + '#'
        print major_line_sep
        for rowno, line in enumerate(BoardPrinter._get_board_lines(state)):
            print line
            if rowno % N == 1:
                print major_line_sep
            else:
                print line_sep

    @classmethod
    def _get_board_lines(cls, state):
        """
        >>> set_N(2)
        >>> board = SudokuBoard()
        >>> squares = [SudokuSquare(value=(i % N_2)) for i in range(N_4)]
        >>> list(BoardPrinter._get_board_lines(SudokuState(squares=squares, board=board)))  # noqa
        ['# 12 | 1  #  2 |    #\\n# 34 |    #    | 3  #', '#    |    #    |    #\\n#  4 |    #    |    #', '#    | 12 # 1  |  2 #\\n#    | 34 #    |    #', '#    |    #    |    #\\n# 3  |  4 #    |    #']
        """
        for y in range(N_2):
            # print [sq.state_lines() for sq in state.squares[N_2 * y:N_2 * (y + 1)]]
            row_lines = [''] * N
            for x, sq in enumerate(
                state.squares[SudokuState.square_index(0, y):
                              SudokuState.square_index(0, y + 1)]):

                for lino, sqline in enumerate(sq.state_lines()):
                    sep = '#' if x % N == 0 else '|'
                    row_lines[lino] += sep + ' {} '.format(sqline)
            yield '#\n'.join(row_lines) + '#'


if __name__ == "__main__":
    import doctest
    doctest.testmod()

    board = SudokuBoard()
    squares = [SudokuSquare(bitmask=i) for i in range(N_4)]
    print str(squares)
    BoardPrinter.print_board(SudokuState(squares=squares, board=board))  # noqa
