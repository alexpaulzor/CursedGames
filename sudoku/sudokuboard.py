from random import shuffle
import time
from solvable import Square, ExclusiveSet, N, N_2, N_4

MIN_CLUES = 20
MAX_CLUES = 24

# TODO: allow increased/decreased verbosity?
YIELD_ITERS = 500


class SudokuBoard(object):
    def __init__(self):
        self.start_time = time.clock()
        self.grid = [[Square(x, y) for x in range(N_2)] for y in range(N_2)]
        self.sets = set()
        self._log = []
        self.cursor_x = 0
        self.cursor_y = 0
        self.go_forward = True
        self.x_regions = False
        self.meta_regions = False
        self.original_state = None
        self.clues = 0
        self.saved_states = []
        self.redo_states = []
        self.build_rows()
        self.build_columns()
        self.build_sectors()
        self.build_x_regions()
        self.build_meta_regions()

    def load_game(self, line):
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
        """
        if not line:
            line = '.' * N_4
        if not self.original_state:
            self.original_state = line
        if 'x' in line:
            self.set_x_regions(True)
            line = line.translate(None, 'x')
        else:
            self.set_x_regions(False)
        if 'm' in line:
            self.set_meta_regions(True)
            line = line.translate(None, 'm')
        else:
            self.set_meta_regions(False)
        if len(line) not in (N_4, 2 * N_4, 5 * N_4):
            self.log("Invalid line: {} ({} ch)".format(line, len(line)))
            raise RuntimeError(
                "Lines (excluding preceding extra region chars) "
                "must be one of length {}".format((N_4, 2 * N_4, 5 * N_4)))

        self.clues = 0
        for y in range(N_2):
            for x in range(N_2):
                char = line[y * N_2 + x]
                sq = self.grid[y][x]
                if char != ".":
                    val = int(char)
                    sq.set_value(val, given=True)
                    self.clues += 1
                elif len(line) == 2 * N_4 and line[N_4 + y * N_2 + x] != '.':
                    val = int(line[N_4 + y * N_2 + x])
                    self.grid[y][x].set_value(val, given=False)
                elif len(line) == 5 * N_4:
                    mask_start = 2 * N_4 + 3 * (y * N_2 + x)
                    mask_str = line[mask_start:mask_start+3]
                    if mask_str == '...':
                        continue
                    value_mask = int(mask_str)
                    values = set()
                    for i in range(N_2):
                        if 2**i & value_mask == 2**i:
                            values.add(i + 1)
                    sq.set_possible_values(values)
                else:
                    self.grid[y][x].clear()
                self.grid[y][x].reset_values_to_attempt()

    def current_state(self, givens_only=False, include_possibles=True):
        # return the state of the board as would be loaded
        line = ''
        line += 'x' if self.x_regions else ''
        line += 'm' if self.meta_regions else ''
        line2 = ''
        line3 = ''
        for y in range(N_2):
            for x in range(N_2):
                sq = self.grid[y][x]
                if sq.get_value():
                    if sq.is_given:
                        line += str(sq.get_value())
                    else:
                        line += '.'
                    line2 += str(sq.get_value())
                else:
                    line += '.'
                    line2 += '.'
                if sq.is_unknown():
                    line3 += '...'
                else:
                    line3 += '{:03d}'.format(self._possible_value_mask(sq))
        if givens_only:
            return line
        if not include_possibles:
            return line + line2
        return line + line2 + line3

    def _possible_value_mask(self, sq):
        mask = 0
        for i in sq.possible_values:
            mask += 2**(i - 1)
        return mask

    def log(self, message, replace=False):
        dt = time.clock() - self.start_time
        message = '[{:02d}:{:02d}] {}'.format(
            int(dt / 60), int(dt % 60), str(message))
        if replace:
            self._log[-1] = message
        else:
            self._log.append(message)

    def is_solved(self):
        for s in self.sets:
            if not s.is_solved():
                return False
        return True

    def select_next_square(self):
        # advance
        if self.cursor_x == N_2 - 1:
            self.cursor_y += 1
            self.cursor_x = 0
            if self.cursor_y == N_2:
                self.cursor_y = 0
        else:
            self.cursor_x += 1

    def select_prev_square(self):
        # go back
        if self.cursor_x > 0:
            self.cursor_x -= 1
        elif self.cursor_y > 0:
            self.cursor_y -= 1
            self.cursor_x = N_2 - 1
        else:
            # back at 0,0
            self.cursor_x = N_2 - 1
            self.cursor_y = N_2 - 1

    def build_rows(self):
        for y in range(N_2):
            row = ExclusiveSet("row_{}".format(y))
            for x in range(N_2):
                row.add_square(self.grid[y][x])
            self.sets.add(row)

    def build_columns(self):
        for x in range(N_2):
            column = ExclusiveSet("col_{}".format(x))
            for y in range(N_2):
                column.add_square(self.grid[y][x])
            self.sets.add(column)

    def build_sectors(self):
        for i in range(N):
            for j in range(N):
                sector = ExclusiveSet("sector_{},{}".format(j, i))
                for y in range(N * i, N * i + N):
                    for x in range(N * j, N * j + N):
                        sector.add_square(self.grid[y][x])
                self.sets.add(sector)

    def build_x_regions(self):
        self.x_down = ExclusiveSet('x_down', enabled=self.x_regions)
        self.x_up = ExclusiveSet('x_up', enabled=self.x_regions)
        for x in range(N_2):
            self.x_down.add_square(self.grid[x][x])
            self.x_up.add_square(self.grid[N_2 - 1 - x][x])
        self.sets.add(self.x_down)
        self.sets.add(self.x_up)

    def set_x_regions(self, enable_x_regions):
        self.x_regions = enable_x_regions
        self.x_down.set_enabled(self.x_regions)
        self.x_up.set_enabled(self.x_regions)

    def build_meta_regions(self):
        self.meta_0 = ExclusiveSet('meta_0', enabled=self.meta_regions)
        self.meta_1 = ExclusiveSet('meta_1', enabled=self.meta_regions)
        self.meta_2 = ExclusiveSet('meta_2', enabled=self.meta_regions)
        self.meta_3 = ExclusiveSet('meta_3', enabled=self.meta_regions)

        for dx in range(N):
            for dy in range(N):
                self.meta_0.add_square(self.grid[1+dy][1+dx])
                self.meta_1.add_square(self.grid[1+dy][5+dx])
                self.meta_2.add_square(self.grid[5+dy][1+dx])
                self.meta_3.add_square(self.grid[5+dy][5+dx])

        self.sets.add(self.meta_0)
        self.sets.add(self.meta_1)
        self.sets.add(self.meta_2)
        self.sets.add(self.meta_3)

    def set_meta_regions(self, enable_meta_regions):
        self.meta_regions = enable_meta_regions
        self.meta_0.set_enabled(self.meta_regions)
        self.meta_1.set_enabled(self.meta_regions)
        self.meta_2.set_enabled(self.meta_regions)
        self.meta_3.set_enabled(self.meta_regions)

    @property
    def selected_square(self):
        return self.grid[self.cursor_y][self.cursor_x]


class SudokuBoardSolver(SudokuBoard):
    def solve_iter(self):
        """Solve, no matter what."""

        for msg in self.smart_solve_iter():
            yield msg
        if self.is_solved():
            state = self.current_state(include_possibles=False)
            yield "Solved! " + state
            return
        else:
            yield "Could not solve!"

    def smart_solve_iter(self):
        while not self.is_solved():
            if not self.solve_step():
                break
            # TODO: catch keyboardinterrupt
        if self.is_solved():
            return
        self.log("No more progress from solve_step, bruteforcing...")

        start_square = self.selected_square
        for msg in self.bruteforce_iter():
            yield msg
        if not any(start_square.value_attempts):
            yield "Unsolvable!"

    def solve_step(self):
        """return truthy if progress was made"""
        prev_state = self.current_state()
        # self.log("infer_values...")
        for row in self.grid:
            for sq in row:
                sq.infer_values()
        if self.current_state() != prev_state:
            return True
        # self.log("try_solve...")
        for s in self.sets:
            s.try_solve()
        if self.current_state() != prev_state:
            return True
        # self.log("solve_naked_groups...")
        self.solve_naked_groups()

        return self.current_state() != prev_state

    def solve_naked_groups(self):
        """find groups of 2 or 3 of values in the same set
        and remove that group from the rest of the squares in that set

        A Naked Pair (also known as a Conjugate Pair) is a set of two candidate
        numbers sited in two cells that belong to at least one unit in common.
        That is, they reside in the same row, column or box.
        It is clear that the solution will contain those values in those two
        cells, and all other candidates with those numbers can be removed from
        whatever unit(s) they have in common.

        Naked Triple:
        Any group of three cells in the same unit that contain IN TOTAL three
        candidates is a Naked Triple.
        Each cell can have two or three numbers, as long as in combination all
        three cells have only three numbers.
        When this happens, the three candidates can be removed from all other
        cells in the same unit.

        The combinations of candidates for a Naked Triple will be one of the
        following:

        (123) (123) (123) - {3/3/3} (in terms of candidates per cell)
        (123) (123) (12) - {3/3/2} (or some combination thereof)
        (123) (12) (23) - {3/2/2/}
        (12) (23) (13) - {2/2/2}
        """
        for s in self.sets:
            pass

    def hidden_groups(self):
        """ """

    def bruteforce_iter(self):
        start_square = self.selected_square
        while start_square.is_given:
            self.select_prev_square()
            start_square = self.grid[self.cursor_y][self.cursor_x]
        start_square.clear()
        start_square.reset_values_to_attempt()
        square = start_square

        def status(start_square, square):
            start_i = N_2 * start_square.y + start_square.x
            current_i = N_2 * square.y + square.x
            # I have no idea how I came up with this as the percent complete,
            # but it gives satisfyingish numbers to give you hope as it
            # crunches the solution
            pct_complete = (
                (N_2 - len(start_square.value_attempts)) * 100.0 / N_2 +
                ((current_i - start_i) % N_4) * 100.0 / N_4 / N_2)

            return "bf(~{:.2f}%) {} {} at {}".format(
                pct_complete,
                '>' if self.go_forward else '<',
                start_square,
                square)

        yield status(start_square, square)
        i = 0
        while (not self.is_solved() and
               any(start_square.value_attempts)):
            yield status(start_square, square)
            if not square.is_given:
                if not square.get_value():
                    square.clear()
                    square.reset_values_to_attempt()
                    square.set_value(square.value_attempts.pop())
                    self.go_forward = True
                if not self.go_forward:
                    if any(square.value_attempts):
                        square.set_value(square.value_attempts.pop())
                        self.go_forward = True
                while self.go_forward and any(square.conflict_squares()):
                    if not any(square.value_attempts):
                        self.go_forward = False
                    else:
                        square.set_value(square.value_attempts.pop())

            if self.go_forward:
                self.select_next_square()
            else:
                if square != start_square:
                    square.clear()
                    self.select_prev_square()
            i += 1
            if i % YIELD_ITERS == 0:
                yield status(start_square, square)

            square = self.grid[self.cursor_y][self.cursor_x]
        # self.log(status(start_square, square), replace=True)


class SudokuBoardGenerator(SudokuBoardSolver):
    def generate_iter(self):
        # generate a game
        for row in self.grid:
            for sq in row:
                sq.prepare_for_generate()
        self.log("gen: Computing solution...")
        for msg in self.solve_iter():
            yield msg
        solution = self.current_state(include_possibles=False)
        if not self.is_solved():
            self.log("gen: Cannot solve! " + solution)
            return

        def given_str(givens):
            return (('x' if self.x_regions else '') +
                    ('m' if self.meta_regions else '') +
                    ''.join(givens))

        givens = list(solution.translate(None, 'xm'))
        givens = ['.'] * N_4 + givens[81:]
        all_squares = reduce(lambda l, row: l + row, self.grid, [])
        shuffle(all_squares)

        self.load_game(given_str(givens))
        self.log("gen: complete: " + solution)

        sq = None
        given_squares = set()
        while True:
            sq = all_squares.pop()
            # Pick a random square that is not uncertain
            while any(all_squares) and (sq.is_given or not sq.get_value()):
                sq = all_squares.pop()
            if not any(all_squares) or (
                    len(all_squares) + len(given_squares) <= MIN_CLUES):
                break
            self.cursor_x = sq.x
            self.cursor_y = sq.y
            sq_val = sq.get_value()
            sq.prevent_value(sq_val)
            msg = 'gen: [{} togo / {} clues] gen trying without: {}'.format(
                len(all_squares), len(given_squares), str(sq))
            self.log(msg)
            givens[sq.id] = '.'
            givens[N_4 + sq.id] = '.'

            self.load_game(given_str(givens[81:]))
            for msg in self.solve_iter():
                yield msg
            sq.prevent_value(None)
            if self.is_solved() and self.current_state() != solution:
                # can't remove this square, since it's unsolvable
                # or solvable another way without it
                given_squares.add(sq)
                msg = "gen: keeping {} ({} clues)".format(
                    sq, len(given_squares))
                self.log(msg)
                sq.set_value(sq_val, True)
                givens[sq.id] = str(sq_val)
                givens[N_4 + sq.id] = str(sq_val)

            else:
                # can remove this square
                msg = "gen: removing {}".format(sq)
                self.log(msg)

            self.load_game(given_str(givens))
            yield "ggg"
        self.log('gen: Done! ' + given_str(givens[:81]))
        while any(all_squares) and len(given_squares) < MAX_CLUES:
            sq = all_squares.pop()
            sq_val = sq.get_value()
            if not sq_val:
                continue
            sq.set_value(sq_val, True)
            givens[sq.id] = str(sq_val)
            givens[N_4 + sq.id] = str(sq_val)
            given_squares.add(sq)
        self.load_game(given_str(givens))
        if MIN_CLUES <= self.clues <= MAX_CLUES:
            self.write_to_generated_log()
        else:
            self.log('gen: Interrupted with {} clues'.format(
                len(given_squares)))

    def write_to_generated_log(self):
        givens = self.current_state(givens_only=True)
        self.log('saving with {} clues: {}'.format(self.clues, givens))
        with open('puzzles/generated.sudoku', 'a') as f:
            f.write(givens + '\n')
