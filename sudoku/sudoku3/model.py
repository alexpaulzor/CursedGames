COLUMN_NAMES = 'ABCDEFGHIJKLMNOPQ'
ROW_NAMES = COLUMN_NAMES.lower()
VALUE_NAMES = '123456789abcdef'

N = 3
N_2 = N * N
N_3 = N_2 * N
N_4 = N_3 * N

ROW_NAMES = list(ROW_NAMES[:N_2])
COLUMN_NAMES = list(COLUMN_NAMES[:N_2])
VALUE_NAMES = list(VALUE_NAMES[:N_2])


class Value(object):
    """Represents a single value, which individual squares may lay claim to.
    """
    def __init__(self, val, groups=None, squares=None):
        self.value = str(val)
        self.groups = set(groups or [])
        self.squares = set(squares or [])

    def add_square(self, sq):
        self.squares.add(sq)

    def remove_square(self, sq):
        self.squares.discard(sq)
        self.update_groups()

    def update_groups(self):
        old_groups = self.groups
        self.groups = set([g for s in self.squares for g in s.groups])
        for removed_group in self.groups - old_groups:
            removed_group.values.discard(self)

    def try_collapse(self):
        if len(self.squares) != 1:
            return
        # solved, collapse equivalent values into this one
        sq = self.squares[0]
        # TODO: necessary?
        sq.set_value(self.value)

    def absorb_value(self, other):
        for sq in list(other.squares):
            sq.values.add(self)
            sq.values.discard(other)
            other.squares.discard(sq)
        for group in list(other.groups):
            group.values.add(self)
            group.values.discard(other)
            other.update_groups()
        self.update_groups()

    def __str__(self):
        # return "{v}.{c}.{g}".format(
        #     v=str(self.value), c=len(self.squares), g=len(self.groups))
        return str(self.value)

    def __lt__(self, o):
        return self.value < o.value


class Square(object):
    def __init__(self, col, row):
        self.col = str(col)
        self.row = str(row)
        self.values = set()
        self.groups = set()

    def set_value(self, val):
        the_one_val = None
        for v in list(self.values):
            if v.value != str(val):
                print("Removing s{} from v{}".format(self, v))
                v.remove_square(self)
                self.values.discard(v)
            elif not the_one_val:
                the_one_val = v
            else:
                the_one_val.absorb_value(v)
                self.values.discard(v)
            v.update_groups()
        for g in self.groups:
            for v in list(g.values):
                if v.value == the_one_val.value and v != the_one_val:
                    g.values.remove(v)

    def add_group(self, group):
        self.groups.add(group)
        self.values |= group.values
        for v in group.values:
            v.add_square(self)

    def __repr__(self):
        return "Square({col}, {row}, {values}, {groups})".format(
            col=repr(self.col), row=repr(self.row), values=repr(self.values),
            groups=repr(self.groups))

    def __str__(self):
        return "{col}{row}={vals}".format(
            col=self.col, row=self.row, vals=''.join(
                [str(v) for v in sorted(self.values)]))
        # return "{col}{row}={vals}".format(
        #     col=self.col, row=self.row, vals='|'.join(
        #         [str(v) for v in sorted(self.values)]))


class Group(object):
    def __init__(self, squares=None, name=None):
        self.name = name
        self.squares = squares
        self.values = self.create_values()
        for s in self.squares:
            s.add_group(self)

    def create_values(self):
        return set([
            Value(i, groups=[self], squares=self.squares)
            for i in VALUE_NAMES])

    def __repr__(self):
        return "Group({squares}, {name})".format(
            squares=repr(self.squares), name=self.name)


class Grid(object):
    def __init__(self):
        self.squares = [
            Square(col, row)
            for row in ROW_NAMES
            for col in COLUMN_NAMES
        ]
        self.create_groups()

    def _get_sq(self, col, row):
        return self.squares[
            ROW_NAMES.index(row) * N_2 + COLUMN_NAMES.index(col)
        ]

    def set_value(self, col, row, value):
        sq = self._get_sq(col, row)
        sq.set_value(value)

    def create_groups(self):
        group_names = (
            COLUMN_NAMES +
            ROW_NAMES +
            self._square_sector_names()
        )

        print(group_names)

        self.groups = {
            name: Group(
                squares=set([
                    s for s in self.squares
                    if ((len(name) == 1
                        and (name == s.row or name == s.col))
                        or (len(name) > 1
                            and s.row in name and s.col in name))]),
                name=name)
            for name in group_names
        }

    def _square_sector_names(self):
        """Returns sectors like ABCghi"""
        # TODO: name sector like 'AgBgCgAhBhChAiBiCi'
        return [
            ''.join(COLUMN_NAMES[col:col+N]) +
            ''.join(ROW_NAMES[row:row+N])
            for col in range(0, N_2, N)
            for row in range(0, N_2, N)
        ]

    def __str__(self):
        return '\n\n'.join([
            ' # '.join([
                str(s) for s in self.squares
                for col in COLUMN_NAMES
                if s.row == row and s.col == col
            ])
            for row in ROW_NAMES
        ])


# fiendish standard
#   ABCDEFGHI
# a    5   6
# b 8 9    1
# c 16  87
# d 3   26
# e   7 1 6
# f    85   3
# g    47  21
# h  4    9 8
# i  8   3

if __name__ == '__main__':
    grid = Grid()
    # Test game
    vals = [
        ('Da', 5),
        ('Ha', 6),
        ('Ab', 8),
        ('Cb', 9),
        ('Hb', 1),
        ('Ac', 1),
        ('Bc', 6),
        ('Ec', 8),
        ('Fc', 7),
        ('Ad', 3),
        ('Ed', 2),
        ('Fd', 6),
        ('Ce', 7),
        ('Ee', 1),
        ('Ge', 6),
        ('Df', 8),
        ('Ef', 5),
        ('If', 3),
        ('Dg', 4),
        ('Eg', 7),
        ('Hg', 2),
        ('Ig', 1),
        ('Bh', 4),
        ('Gh', 9),
        ('Ih', 8),
        ('Bi', 8),
        ('Fi', 3),
    ]
    for name, v in vals:
        print("Setting {}={}".format(name, v))
        grid.set_value(name[0], name[1], v)

    print(grid)
