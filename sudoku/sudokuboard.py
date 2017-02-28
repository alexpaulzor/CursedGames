from random import shuffle
import time
from solvable import (Square, ExclusiveSet, N, N_2, N_4, UnsolvableError,
                      ROW_LETTERS)

MIN_CLUES = 19
MAX_CLUES = 24

MAX_LEVEL = N_2 * N  # 27

# TODO: allow increased/decreased verbosity?
YIELD_ITERS = 500


class SudokuBoard(object):
    def __init__(self, x_regions=False, meta_regions=False):
        self.start_time = time.clock()
        self.grid = [[Square(x, y) for x in range(N_2)] for y in range(N_2)]
        self.sets = set()
        self._log = []
        self.cursor_x = 0
        self.cursor_y = 0
        self.go_forward = True
        self.x_regions = x_regions
        self.meta_regions = meta_regions
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
            This state is intended for use mostly internally

            All characters not in
            r'^[xm]?[.1-9]{81}([.1-9]{81}(([0-9]{3}|.[1-9]g){81})?)?'
            are ignored, so whitespace/formatting does not matter.
        """
        if not line:
            line = '.' * N_4

        if not self.original_state:
            self.original_state = line
        if 'x' in line:
            self.set_x_regions(True)
            # line = line.translate(None, 'x')
        else:
            self.set_x_regions(False)
        if 'm' in line:
            self.set_meta_regions(True)
            # line = line.translate(None, 'm')
        else:
            self.set_meta_regions(False)
        # purge irrelevant characters
        line = line.replace('g', '.').replace('|', '')
        for i, ch in enumerate(line):
            if ch not in '0123456789.':
                line2 = line[:i] + line[i+1:]
                self.log('"{}" => "{}"'.format(line, line2))
                line = line2

        if len(line) not in (N_4, 2 * N_4, 5 * N_4):
            self.log("Invalid line: {} ({} ch)".format(line, len(line)))
            raise RuntimeError(
                "Lines (excluding preceding extra region chars) "
                "must be one of length {} (yours was {}: {})".format(
                    (N_4, 2 * N_4, 5 * N_4), len(line), line))

        self.clues = 0
        for y in range(N_2):
            for x in range(N_2):
                char = line[y * N_2 + x]
                sq = self.grid[y][x]
                if char != ".":
                    val = int(char)
                    sq.set_value(val, given=True)
                    self.clues += 1
                elif len(line) >= 2 * N_4 and line[N_4 + y * N_2 + x] != '.':
                    val = int(line[N_4 + y * N_2 + x])
                    self.grid[y][x].set_value(val, given=False)
                elif len(line) >= 5 * N_4:
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
                elif sq.get_value():
                    line3 += '.' + str(sq.get_value()) + (
                        'g' if sq.is_given else '.')
                else:
                    line3 += '{:03d}'.format(self._possible_value_mask(sq))
        if givens_only:
            return line
        if not include_possibles:
            return "{}|{}".format(line, line2)
        return "{}|{}|{}".format(line, line2, line3)

    def _possible_value_mask(self, sq):
        mask = 0
        for i in sq.possible_values:
            mask += 2**(i - 1)
        return mask

    def unsolved_squares(self):
        for row in self.grid:
            for sq in row:
                if not sq.is_solved():
                    yield sq

    def log(self, message, replace=False):
        dt = time.clock() - self.start_time
        message = '[{:02d}:{:02d}] {}'.format(
            int(dt / 60), int(dt % 60), str(message))
        if replace:
            self._log[-1] = message
        else:
            self._log.append(message)
        yield message

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
            row = ExclusiveSet("row_{}".format(ROW_LETTERS[y]))
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
    def freeze_known_or_clear(self):
        for row in self.grid:
            for sq in row:
                if sq.get_value():
                    sq.set_value(sq.get_value(), given=True)
                else:
                    sq.clear()

    def _solve_iter(self, level=0, verbose=False):
        while not self.is_solved():
            if not self.solve_step(verbose=verbose):
                break
        if self.is_solved():
            return
        if level > MAX_LEVEL:
            yield "We're too deep..."
            return
        inferred_state = self.current_state()

        yield ("lev {}: No more progress from solve_step: " +
               inferred_state).format(level)

        for sq in set(self.unsolved_squares()):
            if sq.get_value():
                continue
            pv = list(sq.possible_values)
            if len(pv) + level > MAX_LEVEL:
                continue
            shuffle(pv)
            pv_orig = pv[:]
            for i, v in enumerate(pv_orig):
                self.load_game(inferred_state)
                sq.set_value(v, False)
                yield ("lev {}: Guess and checking with {} ({}/{})".format(
                    level, sq, i+1, len(pv_orig)))
                try:
                    for msg in self._solve_iter(level + 1, verbose=verbose):
                        yield msg
                    if self.is_solved():
                        return
                except UnsolvableError as ue:
                    if verbose:
                        yield str(ue)
                    pv.remove(v)
                    # if not any(pv):
                    #     raise ue
            self.load_game(inferred_state)

            if pv and pv != pv_orig:
                sq.set_possible_values(set(pv))
                inferred_state = self.current_state()

    def solve_iter(self, verbose=False):
        for msg in self._solve_iter(verbose=verbose):
            yield msg
        if self.is_solved():
            state = self.current_state(include_possibles=False)
            yield "Solved! " + state
            return
        else:
            yield "Could not solve!"

    def solve_step(self, verbose=False):
        """return truthy if progress was made"""
        prev_state = self.current_state()
        # self.log("infer_values...")
        for msg in self.solve_step_iter(prev_state, verbose=verbose):
            if verbose:
                self.log(msg)

        return self.current_state() != prev_state

    def solve_step_iter(self, prev_state, verbose=False):
        for sq in self.unsolved_squares():
            sq.infer_values()
        if verbose:
            yield "Infer values complete"
        if self.current_state() != prev_state:
            return
        for s in self.sets:
            for msg in s.try_solve_iter(verbose=verbose):
                if verbose:
                    yield msg
                #print self.current_state()
        if verbose:
            yield "try_solve complete"

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

            return "bf(~{:.2f}%) {} {} at {} -> {}".format(
                pct_complete,
                '>' if self.go_forward else '<',
                start_square,
                square,
                self.current_state())

        yield status(start_square, square)
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

            square = self.grid[self.cursor_y][self.cursor_x]
        # self.log(status(start_square, square), replace=True)
