
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
        >>> SudokuSquare()
        None 0b1111
        """
        if value:
            self.set_value(value)
        elif bitmask:
            self._value_bitmask = int(bitmask)
        else:
            self._value_bitmask = N_4 - 1

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

    def __and__(self, other):
        if isinstance(other, SudokuSquare):
            return int(self.bitmask & other._value_bitmask)
        return int(self.bitmask & SudokuSquare.value_to_bitmask(other))

    def __isub__(self, other):
        self._value_bitmask &= other.bitmask

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


class SudokuBoard:
    def __init__(self):
        self.constraints = [
            RowConstraint,
            ColumnConstraint,
            SectorConstraint
        ]

    def sets(self, state):
        for constraint in self.constraints:
            for sq_set in constraint.sets_iter(state):
                if any(sq_set):
                    yield sq_set


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
        >>> set_N(3)
        >>> board = SudokuBoard()
        >>> squares = [SudokuSquare(bitmask=i) for i in range(N_4)]
        >>> print str(squares)
        [None 0b001010000, 1 0b000000001, 2 0b000000010, None 0b000000011, 3 0b000000100, None 0b000000101, None 0b000000110, None 0b000000111, 4 0b000001000, None 0b000001001, None 0b000001010, None 0b000001011, None 0b000001100, None 0b000001101, None 0b000001110, None 0b000001111, 5 0b000010000, None 0b000010001, None 0b000010010, None 0b000010011, None 0b000010100, None 0b000010101, None 0b000010110, None 0b000010111, None 0b000011000, None 0b000011001, None 0b000011010, None 0b000011011, None 0b000011100, None 0b000011101, None 0b000011110, None 0b000011111, 6 0b000100000, None 0b000100001, None 0b000100010, None 0b000100011, None 0b000100100, None 0b000100101, None 0b000100110, None 0b000100111, None 0b000101000, None 0b000101001, None 0b000101010, None 0b000101011, None 0b000101100, None 0b000101101, None 0b000101110, None 0b000101111, None 0b000110000, None 0b000110001, None 0b000110010, None 0b000110011, None 0b000110100, None 0b000110101, None 0b000110110, None 0b000110111, None 0b000111000, None 0b000111001, None 0b000111010, None 0b000111011, None 0b000111100, None 0b000111101, None 0b000111110, None 0b000111111, 7 0b001000000, None 0b001000001, None 0b001000010, None 0b001000011, None 0b001000100, None 0b001000101, None 0b001000110, None 0b001000111, None 0b001001000, None 0b001001001, None 0b001001010, None 0b001001011, None 0b001001100, None 0b001001101, None 0b001001110, None 0b001001111, None 0b001010000]
        >>> StatePrinter.print_board_state(SudokuState(squares=squares, board=board))  # noqa
        #=====+=====+=====#=====+=====+=====#=====+=====+=====#
        #     | 1   |  2  # 12  |   3 | 1 3 #  23 | 123 |     #
        #  5  |     |     #     |     |     #     |     | 4   #
        # 7   |     |     #     |     |     #     |     |     #
        #-----+-----+-----#-----+-----+-----#-----+-----+-----#
        # 1   |  2  | 12  #   3 | 1 3 |  23 # 123 |     | 1   #
        # 4   | 4   | 4   # 4   | 4   | 4   # 4   |  5  |  5  #
        #     |     |     #     |     |     #     |     |     #
        #=====+=====+=====#=====+=====+=====#=====+=====+=====#
        #  2  | 12  |   3 # 1 3 |  23 | 123 #     | 1   |  2  #
        #  5  |  5  |  5  #  5  |  5  |  5  # 45  | 45  | 45  #
        #     |     |     #     |     |     #     |     |     #
        #-----+-----+-----#-----+-----+-----#-----+-----+-----#
        # 12  |   3 | 1 3 #  23 | 123 |     # 1   |  2  | 12  #
        # 45  | 45  | 45  # 45  | 45  |   6 #   6 |   6 |   6 #
        #     |     |     #     |     |     #     |     |     #
        #-----+-----+-----#-----+-----+-----#-----+-----+-----#
        #   3 | 1 3 |  23 # 123 |     | 1   #  2  | 12  |   3 #
        #   6 |   6 |   6 #   6 | 4 6 | 4 6 # 4 6 | 4 6 | 4 6 #
        #     |     |     #     |     |     #     |     |     #
        #=====+=====+=====#=====+=====+=====#=====+=====+=====#
        # 1 3 |  23 | 123 #     | 1   |  2  # 12  |   3 | 1 3 #
        # 4 6 | 4 6 | 4 6 #  56 |  56 |  56 #  56 |  56 |  56 #
        #     |     |     #     |     |     #     |     |     #
        #-----+-----+-----#-----+-----+-----#-----+-----+-----#
        #  23 | 123 |     # 1   |  2  | 12  #   3 | 1 3 |  23 #
        #  56 |  56 | 456 # 456 | 456 | 456 # 456 | 456 | 456 #
        #     |     |     #     |     |     #     |     |     #
        #-----+-----+-----#-----+-----+-----#-----+-----+-----#
        # 123 |     | 1   #  2  | 12  |   3 # 1 3 |  23 | 123 #
        # 456 |     |     #     |     |     #     |     |     #
        #     | 7   | 7   # 7   | 7   | 7   # 7   | 7   | 7   #
        #=====+=====+=====#=====+=====+=====#=====+=====+=====#
        #     | 1   |  2  # 12  |   3 | 1 3 #  23 | 123 |     #
        # 4   | 4   | 4   # 4   | 4   | 4   # 4   | 4   |  5  #
        # 7   | 7   | 7   # 7   | 7   | 7   # 7   | 7   | 7   #
        #-----+-----+-----#-----+-----+-----#-----+-----+-----#
        """
        print cls.major_line_sep()
        for rowno, line in enumerate(StatePrinter._get_board_lines(state)):
            print line
            if rowno % N == 1:
                print cls.major_line_sep()
            else:
                print cls.line_sep()

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


