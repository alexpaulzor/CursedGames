import random
import logging

logging.basicConfig(level=logging.DEBUG)
log = logging

"""
Generate squigly (and standard) boards

A `Board` is a set of `SquareGroup`s.
A `SquareGroup` is a set of `Square`s and a dict index of values
    * Row
    * Column
    * Region
A `Square` has attributes:
    * row
    * column
    * value

"""
N = 3
N_2 = 9


class InvalidBoardException(RuntimeError):
    pass


class Square:
    def __init__(self, row_i, column_i, value=None, region=None):
        self.row_i = row_i
        self.column_i = column_i
        self.value = value
        self.region = region

    def set_region(self, region):
        self.region = region

    def __repr__(self):
        return (
            f"Square(row_i={self.row_i}, column_i={self.column_i}, "
            f"value={self.value}, region={self.region})")


class SquareGroup:
    def __init__(self, name='??'):
        self.squares = set()
        self.refresh_values()
        self.name = name

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name})"

    def set_squares(self, squares):
        self.squares = set(squares)
        self.refresh_values()

    def refresh_values(self):
        values = {i: None for i in range(1, N_2 + 1)}
        for s in self.squares:
            if s.value:
                values[s.value] = s
        self.values = values

    def is_solved(self):
        return set(self.values.values()) == self.squares

    def is_valid(self):
        known_squares = [sq.value for sq in self.squares if sq.value]
        return len(set(known_squares)) == len(known_squares)

    def unknown_values(self):
        for v, sq in self.values.items():
            if not sq:
                yield v


class RowGroup(SquareGroup):
    pass


class ColumnGroup(SquareGroup):
    pass


class Region(SquareGroup):
    pass


class SquareRegion(Region):
    pass


class SquiggleRegion(Region):
    def add_square(self, sq):
        self.squares.add(sq)
        sq.set_region(self)


# class RegionSet:
#     def __init__(self):


class Board:
    def __init__(self):
        self.grid = [
            [Square(row_i=row_i, column_i=col_i)
                for col_i in range(N_2)]
            for row_i in range(N_2)]
        self.regions = set()
        self.add_rows_and_cols()
        self.add_regions()

    def add_regions(self):
        """Default square impl"""
        for brow in range(N):
            for bcol in range(N):
                r = SquareRegion()
                for drow in range(N):
                    for dcol in range(N):
                        sq = self.grid[brow * N + drow][bcol * N + dcol]
                        r.squares.add(sq)
                        sq.set_region(r)
                self.regions.add(r)

    def add_rows_and_cols(self):
        for i in range(N_2):
            r = RowGroup()
            r.set_squares(self.grid[i])
            self.regions.add(r)
            c = ColumnGroup()
            c.set_squares([self.grid[j][i] for j in range(N_2)])
            self.regions.add(r)

    def print(self):
        """
            A Square displays as 2 lines:

            a b
            c v

            in context:

            a1 b1 a2 b2
            c1 d1 c2 d2
            a3 b3  a b
            c3 d3  c d

            a1 = '#'
            b1 = '==='
            a2 = '=' if r1 == r2
               = '#' otherwise
            b2 = '==='
            a3 = '#'
            b3 = '...'  if r1 == r3
               = '===' otherwise
            c3 = '#'
            a = '.' if all of 1, 2, 3, and 4 are in the same region
              = '=' if r1 == r2 and r3 == r but r1 != r
              = '|' if r1 == r3 and r2 == r but r1 != r
              = '#' otherwise
            b = '...' if r2 == r
              = '===' otherwise
            c = ':' if r3 == r
              = '#' otherwise
            d = ' v ' if square has value v
              = '   ' otherwise
        """
        prev_row = None
        for row_i, row in enumerate(self.grid):
            above_line = ''
            line = ""
            prev_sq = None
            for col_i, sq in enumerate(row):
                a = '#'
                b = '==='
                c = '#'
                sq1 = sq2 = sq3 = None
                if prev_row:
                    sq2 = prev_row[col_i]
                    if prev_sq:
                        sq1 = prev_row[col_i - 1]
                        sq3 = prev_sq
                else:
                    # Top row
                    if prev_sq:
                        sq3 = prev_sq

                if sq2:
                    if sq.region == sq2.region:
                        b = '...'
                        if sq3:
                            if sq.region == sq3.region:
                                c = ':'
                                if sq1 and sq.region == sq1.region:
                                    a = ' '
                else:
                    a = '='
                if sq3 and sq.region == sq3.region:
                    c = ':'
                # if prev_sq.region == sq.region:
                #     a = '='
                #     c = ':'
                # if sq.region == sq2.region:
                #     b = '...'
                # if sq.region == sq3.region:
                #     c = ':'
                #     if sq.region == sq2.region:
                #         if sq.region == sq1.region:
                #             a = ' '
                #         else:
                #             a = '='

                if sq.value:
                    d = f' {sq.value} '
                # elif not sq.region:
                #     d = ' ? '
                else:
                    # d = sq.region.name + ' '
                    d = '   '
                above_line += a + b
                line += c + d
                prev_sq = sq
            print(above_line + '#')
            print(line + '#')
            prev_row = row
        print(' ' + '====' * N_2)

    def is_valid(self):
        for r in self.regions:
            if not r.is_valid():
                return False
        return True

    def is_solved(self):
        for r in self.regions:
            if not r.is_solved():
                return False
        return True

    def unset_squares(self):
        for row in self.grid:
            for sq in row:
                if not sq.value:
                    yield sq


class SquiggleBoard(Board):
    CARDINAL_DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def add_regions(self):
        """
        Starting with the center square, symmetrically build the first region.
        """
        center = self.generate_center_region()
        corners = self.generate_corner_regions()
        NW, NE, SW, SE = corners
        cardinals = self.generate_cardinal_regions()
        W, N, S, E = cardinals
        regions = [NW, N, NE, W, center, E, SW, S, SE]
        # self.fill_regions(corners)
        # self.fill_regions(cardinals)
        self.fill_regions(regions)
        self.regions = set(regions)

    def generate_corner_regions(self):
        NW = SquiggleRegion('NW')
        NW.add_square(self.grid[0][0])
        NE = SquiggleRegion('NE')
        NE.add_square(self.grid[0][N_2 - 1])
        SW = SquiggleRegion('SW')
        SW.add_square(self.grid[N_2 - 1][0])
        SE = SquiggleRegion('SE')
        SE.add_square(self.grid[N_2 - 1][N_2 - 1])
        return [NW, NE, SW, SE]

    def fill_regions(self, regions):
        while min([len(r.squares) for r in regions]) < N_2:
            changed = False
            region_is = list(range(len(regions)))
            random.shuffle(region_is)
            for c_i in region_is:
                c = regions[c_i]
                if not c.squares:
                    # TODO: Deal with empty cardinal regions
                    continue
                elif len(c.squares) == N_2:
                    continue
                # 0 -> 3, 1 -> 2, 2 -> 1, 3 -> 0
                mir_c_i = len(regions) - c_i - 1
                mir_c = regions[mir_c_i]
                for sq in random.sample(c.squares, len(c.squares)):
                    # log.info(f"Examining {sq}")
                    nbrs = self._get_unvisited_neighbor_pair(sq)
                    if not nbrs:
                        continue
                    nbr, mir_nbr = nbrs
                    c.add_square(nbr)
                    mir_c.add_square(mir_nbr)
                    changed = True
                    break
            # self.print()
            if not changed:
                # Impossible, we broke it
                raise InvalidBoardException()

    def generate_cardinal_regions(self):
        W = SquiggleRegion(' W')
        E = SquiggleRegion(' E')
        w_sq, e_sq = self._get_unvisited_square_pair(max_col=N_2 // 2 - 1)
        W.add_square(w_sq)
        E.add_square(e_sq)

        N = SquiggleRegion(' N')
        S = SquiggleRegion(' S')
        n_sq, s_sq = self._get_unvisited_square_pair(max_row=N_2 // 2 - 1)
        N.add_square(n_sq)
        S.add_square(s_sq)

        return [W, N, S, E]

    def _get_unvisited_square_pair(self, max_row=N_2-1, max_col=N_2-1):
        while True:
            row_i = random.randint(0, max_row)
            col_i = random.randint(0, max_col)
            sq = self.grid[row_i][col_i]
            if sq.region:
                continue
            mir_row, mir_col = _mirror_coords(row_i, col_i)
            mir_sq = self.grid[mir_row][mir_col]
            if mir_sq.region:
                continue
            return sq, mir_sq

    def _get_unvisited_neighbor_pair(self, sq):
        # pick random cardinal neighbor of sq until we find one unassinged
        dirs = self.CARDINAL_DIRS
        random.shuffle(dirs)
        for drow, dcol in dirs:
            row_i = sq.row_i + drow
            col_i = sq.column_i + dcol
            if not (0 <= row_i < N_2 and 0 <= col_i < N_2):
                continue
            neighbor = self.grid[row_i][col_i]
            # log.info(f"Checking {neighbor}")
            if neighbor.region:
                continue
            # log.info(f"Checking {row_i}, {col_i}")
            # also make sure the mirror hasn't been taken
            row_i, col_i = _mirror_coords(
                neighbor.row_i, neighbor.column_i)
            # log.info(f"MirChecking {row_i}, {col_i}")
            # if not (0 <= row_i < N_2 and 0 <= col_i < N_2):
            #     continue
            mir_neighbor = self.grid[row_i][col_i]
            # log.info(f"Checking mir {mir_neighbor}")
            if mir_neighbor.region:
                continue
            return neighbor, mir_neighbor
        return None

    def generate_center_region(self):
        c = SquiggleRegion(' C')
        row_i = N_2 // 2
        col_i = N_2 // 2
        sq = self.grid[row_i][col_i]
        # log.info(f"Starting with {sq}")
        c.add_square(sq)
        while len(c.squares) < N_2:
            # pick a random square already included
            sq = random.sample(c.squares, 1)[0]
            # log.info(f"Examining {sq}")
            nbrs = self._get_unvisited_neighbor_pair(sq)
            if not nbrs:
                continue
            nbr, mir_nbr = nbrs
            c.add_square(nbr)
            c.add_square(mir_nbr)
        return c

    @classmethod
    def generate_valid_board(cls):
        while True:
            try:
                return cls()
            except InvalidBoardException:
                pass


def _mirror_coords(row_in, col_in):
    row_i = N_2 // 2 + (N_2 // 2 - row_in)
    col_i = N_2 // 2 + (N_2 // 2 - col_in)
    # log.info(f"mirror({row_in}, {col_in}) = {row_i}, {col_i}")
    return row_i, col_i


def solve(board):
    if board.is_solved():
        return True
    # unset_squares = board.unset_squares()


def main():
    b = generate_board()
    b.print()


def generate_board(squiggles=True):
    if squiggles:
        b = SquiggleBoard.generate_valid_board()
    else:
        b = Board()
    return b


if __name__ == "__main__":
    main()
