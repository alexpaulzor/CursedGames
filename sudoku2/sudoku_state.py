import sys
from termcolor import colored

global N, N_2, N_3, N_4


def set_N(n=3):
    global N, N_2, N_3, N_4
    N = n          # 2  # 3
    N_2 = N * N    # 4  # 9
    N_3 = N_2 * N  # 8  # 27
    N_4 = N_3 * N  # 16 # 81

set_N()


class SudokuSquare:
    def __init__(self, value=None, bitmask=None, id=None, frozen=False):
        """
        >>> set_N(2)
        >>> global N, N_2, N_3, N_4
        >>> SudokuSquare()
        sq#None 1234
        """
        self._id = id

        if value:
            self.set_value(value)
        elif bitmask:
            self._value_bitmask = int(bitmask)
        else:
            self._value_bitmask = self.full_bitmask()
        self.frozen = frozen and self.known_value

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

    @classmethod
    def full_bitmask(cls):
        return sum([SudokuSquare.value_to_bitmask(i + 1) for i in range(N_2)])

    @property
    def known_value(self):
        return SudokuSquare.bitmask_to_known_value(self.bitmask)

    def set_value(self, value):
        if value > 0:
            self._value_bitmask = SudokuSquare.value_to_bitmask(value)
        else:
            self._value_bitmask = self.full_bitmask()

    def set_bitmask(self, bitmask):
        self._value_bitmask = bitmask

    def __and__(self, other):
        if isinstance(other, SudokuSquare):
            return int(self.bitmask & other._value_bitmask)
        return int(self.bitmask & SudokuSquare.value_to_bitmask(other))

    @classmethod
    def bitmask_to_possible_values(cls, bmask):
        for i in range(N_2):
            mask = SudokuSquare.value_to_bitmask(i + 1)
            if mask & bmask == mask:
                yield i + 1

    def possible_values(self):
        return self.bitmask_to_possible_values(self.bitmask)

    def eliminate(self, other):
        """
        >>> s = SudokuSquare()
        >>> s.eliminate(SudokuSquare(value=3))
        >>> s
        sq#None 124
        >>> s.eliminate(SudokuSquare(value=2))
        >>> s
        sq#None 14
        >>> s.eliminate(SudokuSquare(value=1))
        >>> s
        sq#None 4
        >>> s2 = SudokuSquare()
        >>> s2.eliminate(SudokuSquare(bitmask=0b1101))
        >>> s2
        sq#None 2
        """
        if (self != other and
                other.bitmask & self._value_bitmask > 0):
            self._value_bitmask -= other.bitmask & self._value_bitmask

    def __isub__(self, other):
        self.eliminate(other)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return ("sq#{} {}").format(
            self._id,
            ''.join([str(v) for v in self.possible_values()]))


class SudokuState:
    def __init__(self, squares=None, parent=None, transition_technique=None,
                 board=None):
        if not squares:
            squares = [SudokuSquare(id=i) for i in range(N_4)]
        self.squares = squares
        self.parent = parent
        self.transition_technique = transition_technique

        self._id = 0

        if parent:
            self.board = parent.board
            self._id = parent._id + 1
        elif board:
            self.board = board

    def copy(self, transition_technique=None):
        squares = [SudokuSquare(bitmask=sq.bitmask, id=sq._id)
                   for sq in self.squares]
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
        if not other:
            return False
        for i, my_sq in enumerate(self.squares):
            if my_sq.bitmask != other.squares[i].bitmask:
                return False
        return True

    def __neq__(self, other):
        return not self == other

    def __sub__(self, other):
        diff_state = self.copy()
        for i, my_sq in enumerate(self.squares):
            diff_state.squares[i].set_bitmask(
                abs(my_sq.bitmask - other.squares[i].bitmask))
        return diff_state

    def __str__(self):
        return "st#{} {}".format(self._id, self.squares)


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
        #    | 1  #  2 |    #
        #    |    #    | 3  #
        #----+----#----+----#
        #    |    #    |    #
        #  4 |    #    |    #
        #====+====#====+====#
        #    |    # 1  |  2 #
        #    |    #    |    #
        #----+----#----+----#
        #    |    #    |    #
        # 3  |  4 #    |    #
        #====+====#====+====#
        >>> groups = list(RowConstraint.groups_iter(state))
        >>> [StatePrinter.print_square_set(g) for g in groups]
        #====+====#====+====#
        |    | 1  |  2 |    |
        |    |    |    | 3  |
        #====+====#====+====#
        #====+====#====+====#
        |    |    |    |    |
        |  4 |    |    |    |
        #====+====#====+====#
        #====+====#====+====#
        |    |    | 1  |  2 |
        |    |    |    |    |
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
        #    | 1  #  2 |    #
        #    |    #    | 3  #
        #----+----#----+----#
        #    |    #    |    #
        #  4 |    #    |    #
        #====+====#====+====#
        #    |    # 1  |  2 #
        #    |    #    |    #
        #----+----#----+----#
        #    |    #    |    #
        # 3  |  4 #    |    #
        #====+====#====+====#
        >>> groups = list(ColumnConstraint.groups_iter(state))
        >>> [StatePrinter.print_square_set(g) for g in groups]
        #====+====#====+====#
        |    |    |    |    |
        |    |  4 |    | 3  |
        #====+====#====+====#
        #====+====#====+====#
        | 1  |    |    |    |
        |    |    |    |  4 |
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
        #    | 1  #  2 |    #
        #    |    #    | 3  #
        #----+----#----+----#
        #    |    #    |    #
        #  4 |    #    |    #
        #====+====#====+====#
        #    |    # 1  |  2 #
        #    |    #    |    #
        #----+----#----+----#
        #    |    #    |    #
        # 3  |  4 #    |    #
        #====+====#====+====#
        >>> groups = list(SectorConstraint.groups_iter(state))
        >>> [StatePrinter.print_square_set(g) for g in groups]
        #====+====#====+====#
        |    | 1  |    |    |
        |    |    |  4 |    |
        #====+====#====+====#
        #====+====#====+====#
        |  2 |    |    |    |
        |    | 3  |    |    |
        #====+====#====+====#
        #====+====#====+====#
        |    |    |    |    |
        |    |    | 3  |  4 |
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
    def print_board_state(cls, state, color=False):
        """
        >>> set_N(2)
        >>> board = SudokuBoard()
        >>> squares = [SudokuSquare(bitmask=i) for i in range(N_4)]
        >>> StatePrinter.print_board_state(
        ...     SudokuState(squares=squares, board=board))
        #====+====#====+====#
        #    | 1  #  2 | 12 #
        #    |    #    |    #
        #----+----#----+----#
        #    | 1  #  2 | 12 #
        # 3  | 3  # 3  | 3  #
        #====+====#====+====#
        #    | 1  #  2 | 12 #
        #  4 |  4 #  4 |  4 #
        #----+----#----+----#
        #    | 1  #  2 |    #
        # 34 | 34 # 34 |    #
        #====+====#====+====#
        """
        print cls.major_line_sep()
        for rowno, line in enumerate(StatePrinter._get_board_lines(
                state, color=color)):
            print line
            if (rowno + 1) % N == 0:
                print cls.major_line_sep()
            else:
                print cls.line_sep()

    @classmethod
    def print_board_diff(cls, state1, state2, color=False):
        diff_state = state2 - state1
        state1_lines = '\n'.join(
            StatePrinter._get_board_lines(state1, color=color)).split('\n')
        state2_lines = '\n'.join(
            StatePrinter._get_board_lines(state2, color=color)).split('\n')
        diff_state_lines = '\n'.join(
            StatePrinter._get_board_lines(
                diff_state, prefix='-', color=color)).split('\n')

        sys.stdout.write(' -> '.join([cls.major_line_sep() for i in range(3)]))
        sys.stdout.write('\n')

        for rowno, line in enumerate(state1_lines):
            sys.stdout.write(' -> '.join(
                [line, diff_state_lines[rowno], state2_lines[rowno]]))
            sys.stdout.write('\n')
            if (rowno + 1) % N == 0 and (rowno / N + 1) % N == 0:
                sep = cls.major_line_sep()
            elif (rowno + 1) % N == 0:
                sep = cls.line_sep()
            else:
                sep = None

            if sep:
                sys.stdout.write(' -> '.join([sep for i in range(3)]))
                sys.stdout.write('\n')

    @classmethod
    def _get_board_lines(cls, state, prefix=' ', color=False):
        r"""
        >>> set_N(2)
        >>> board = SudokuBoard()
        >>> squares = [SudokuSquare(value=(i % N_2)) for i in range(N_4)]
        >>> list(StatePrinter._get_board_lines(SudokuState(squares=squares, board=board)))  # noqa
        ['#    | 1  #  2 |    #\n#    |    #    | 3  #', '#    |    #    |    #\n#  4 |    #    |    #', '#    |    # 1  |  2 #\n#    |    #    |    #', '#    |    #    |    #\n# 3  |  4 #    |    #']
        """
        for y in range(N_2):
            for row in cls._get_row_lines(
                    state.squares[SudokuState.square_index(0, y):
                                  SudokuState.square_index(0, y + 1)],
                    prefix=prefix, color=color):
                yield row

    @classmethod
    def print_square_set(cls, squares):
        print cls.major_line_sep()
        for line in cls._get_row_lines(squares, major_sep='|'):
            print line
        print cls.major_line_sep()

    @classmethod
    def _get_row_lines(cls, squares, major_sep='#', prefix=' ', color=False):
        row_lines = [''] * N
        for x, sq in enumerate(squares):
            for lino, sqline in enumerate(cls._state_lines(sq, color=color)):
                sep = major_sep if x % N == 0 else '|'
                pfix = prefix if any(sqline.strip()) else ' '
                row_lines[lino] += sep + '{}{} '.format(pfix, sqline)
        yield (major_sep + '\n').join(row_lines) + major_sep

    @classmethod
    def _state_lines(cls, sq, color=False):
        """
        >>> ','.join(list(StatePrinter.state_lines(SudokuSquare(value=1)))
        '1 ,  '
        >>> bm_1 = SudokuSquare.value_to_bitmask(1)
        >>> bm_2 = SudokuSquare.value_to_bitmask(2)
        >>> bm_3 = SudokuSquare.value_to_bitmask(3)
        >>> bm_4 = SudokuSquare.value_to_bitmask(4)
        >>> square = SudokuSquare(bitmask=bm_1 | bm_2 | bm_3 | bm_4)
        >>> square
        sq#None 1234
        >>> ','.join(StatePrinter.state_lines(square))
        '  ,  '
        """
        if sq.bitmask == SudokuSquare.full_bitmask():
            return [' ' * N] * N
        return tuple(cls._state_line_iter(sq, color=color))

    @classmethod
    def _state_line_iter(cls, sq, color=False):
        for lino in range(N):
            vals = [str(i)
                    if sq & i == SudokuSquare.value_to_bitmask(i) else ' '
                    for i in range(1 + N * lino, 1 + N * lino + N)
                    ]
            yield "".join(cls._color_vals(sq, vals, color))

    """Text colors:

        grey
        red
        green
        yellow
        blue
        magenta
        cyan
        white
        Text highlights:

        on_grey
        on_red
        on_green
        on_yellow
        on_blue
        on_magenta
        on_cyan
        on_white
        Attributes:

        bold
        dark
        underline
        blink
        reverse
        concealed"""

    VALUE_TO_COLOR = {
        '1': dict(color='white', on_color=None, attrs=[]),
        '2': dict(color='red', on_color=None, attrs=[]),
        '3': dict(color='green', on_color=None, attrs=[]),
        '4': dict(color='yellow', on_color=None, attrs=[]),
        '5': dict(color='green', on_color='on_blue', attrs=[]),
        '6': dict(color='magenta', on_color=None, attrs=[]),
        '7': dict(color='cyan', on_color=None, attrs=[]),
        '8': dict(color='blue', on_color=None, attrs=[]),
        '9': dict(color='white', on_color='on_blue', attrs=[]),
        ' ': dict(),
    }

    @classmethod
    def _color_vals(cls, sq, vals, color=False):
        if not color:
            return vals
        return [colored(str(v), **cls.VALUE_TO_COLOR[str(v)]) for v in vals]

    @classmethod
    def print_playable_state(cls, state):
        """
            line is an N_4-character representation of the board where
            given values are 1-9 and spaces are .

            If the first character is 'x', enable x-regions.
            If the first character is 'm', enable meta-regions.

            Optionally with another N_4 characters representing
            a solution or partial solution.

            Optionally after that, another 3*N_4 characters representing
            a bitmask of 1-shifted possible values as a 3-digit decimal.
            For instance, a square with possible values 1, 3, and 9 would be
            2**(1-1) + 2**(3-1) + 2**(9-1) = 261
            This state is intended for use mostly internally

            All characters not in
            r'^[xm]?[.1-9]{81}([.1-9]{81}(([0-9]{3}|.[1-9]g){81})?)?'
            are ignored, so whitespace/formatting does not matter.
        """
        print ''.join([str(sq.known_value or '.') for sq in state.squares] * 2
                      + ["{:03d}".format(sq.bitmask) for sq in state.squares])

if __name__ == "__main__":
    import doctest
    doctest.testmod()
