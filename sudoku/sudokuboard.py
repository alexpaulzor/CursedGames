import sys
from random import shuffle
import time
from solvable import Square, ExclusiveSet

MIN_CLUES = 17
MAX_CLUES = 24

N = 3
N_2 = N * N
N_3 = N_2 * N
N_4 = N_3 * N

class SudokuBoard(object):
    def __init__(self, x_regions=False):
        self.start_time = time.clock()
        self.grid = [[Square(x, y) for x in range(N_2)] for y in range(N_2)]
        self.sets = set()
        self._log = []
        self.cursor_x = 0
        self.cursor_y = 0
        self.go_forward = True
        self.x_regions = x_regions
        self.original_state = None
        self.saved_states = []
        self.redo_states = []
        self.build_rows()
        self.build_columns()
        self.build_sectors()
        self.build_x_regions()

    def load_game(self, line):
        """
            line is an N_4-character representation of the board where
            given values are 1-9 and spaces are .

            If the first character is 'x', enable x-regions.

            Optionally with another N_4 characters representing
            a solution or partial solution.

            Optionally after that, another 3*N_4 characters representing
            a bitmask of 1-shifted possible values as a 3-digit decimal.
            For instance, a square with possible values 1, 3, and 9 would be
            2**(1-1) + 2**(3-1) + 2**(9-1) = 261
        """

        if not line:
            line = 'x' + '.' * N_4
        if not self.original_state:
            self.original_state = line
        if 'x' in line:
            self.set_x_regions(True)
            line = line[1:]
        else:
            self.set_x_regions(False)
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
        line = 'x' if self.x_regions else u''
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


    def generate(self):
        # generate a game
        for row in self.grid:
            for sq in row:
                sq.prepare_for_generate()
        solution = self.compute_solution()
        if not solution:
            self.log("Cannot solve! " + self.current_state(include_possibles=False))
            return

        def given_str(givens):
            return ('x' if self.x_regions else '') + ''.join(givens)

        givens = list(solution)
        if self.x_regions:
            givens = givens[1:]
        givens = ['.'] * N_4 + givens[81:]
        all_squares = reduce(lambda l, row: l + row, self.grid, [])
        shuffle(all_squares)

        self.load_game(given_str(givens))
        self.log("complete: " + solution)
        yield

        sq = all_squares.pop()
        clues = 0
        while True:
            # Pick a random square that is not uncertain
            while any(all_squares) and (sq.is_given or not sq.get_value()):
                sq = all_squares.pop()
            if not any(all_squares) or len(all_squares) + clues <= MIN_CLUES:
                key = 0
                break
            self.cursor_x = sq.x
            self.cursor_y = sq.y
            sq_val = sq.get_value()
            sq.prevent_value(sq_val)
            self.log('[{} togo / {} clues] generate trying without: {}'.format(
                len(all_squares), clues, str(sq)))
            givens[N_2 * sq.y + sq.x] = '.'
            givens[81 + 9 * sq.y + sq.x] = '.'
            new_solution = self.compute_solution(given_str(givens[81:]))
            sq.prevent_value(None)
            if new_solution is False:
                # interrupted, give up
                key = 0

            if new_solution and new_solution != solution:
                # can't remove this square, since it's unsolvable
                # or solvable another way without it
                clues += 1
                self.log("keeping {} ({} clues)".format(sq, clues))
                sq.set_value(sq_val, True)
                givens[N_2 * sq.y + sq.x] = str(sq_val)
                givens[81 + N_2 * sq.y + sq.x] = str(sq_val)

            else:
                # can remove this square
                self.log("removing {}".format(sq))
            self.load_game(given_str(givens))
        self.log('Done! No more squares to try ' + given_str(givens[:81]))
        if self.clues <= MAX_CLUES:
        # if len(all_squares) + clues <= MAX_CLUES:
        #     for sq in all_squares:
        #         sq_val = sq.get_value()
        #         if not sq_val:
        #             continue
        #         sq.set_value(sq_val, True)
        #         givens[N_2 * sq.y + sq.x] = str(sq_val)
        #         givens[81 + N_2 * sq.y + sq.x] = str(sq_val)
        #         clues += 1
            self.log('saving with {} clues'.format(self.clues))
            with open('puzzles/generated.sudoku', 'a') as f:
                f.write(given_str(givens[:81]) + '\n')
        self.load_game(given_str(givens))

    def compute_solution(self, initial_state=None):
        backup_state = self.current_state()
        backup_direction = self.go_forward
        if initial_state is not None:
            self.load_game(initial_state)
        self.log("solving from: " + self.current_state(include_possibles=False))
        self.go_forward = True
        for msg in self.solve():
            pass
        solution = self.current_state(include_possibles=False)
        self.load_game(backup_state)
        self.go_forward = backup_direction
        return solution

    def is_solved(self):
        for s in self.sets:
            if not s.is_solved():
                return False
        for row in self.grid:
            for square in row:
                if not square.is_solved():
                    return False

        self.complete_solution = self.current_state(include_possibles=False)

        return True

    def solve(self):
        """Solve, no matter what."""
        start_square = self.grid[self.cursor_y][self.cursor_x]
        #self.smart_solve()
        for msg in self.bruteforce():
            yield msg
        if self.is_solved():
            state = self.current_state(include_possibles=False)
            self.log("Solved! " + state)
            return
        else:
            if not any(start_square.value_attempts):
                self.log("Unsolvable!")
            return

    # def smart_solve(self):
    #     prev_state = None
    #     while self.current_state() != prev_state:
    #         self.solve_step(False)
    #         # TODO: catch keyboardinterrupt
    #         if self.is_solved():
    #             return self.current_state(include_possibles=False)

    # def solve_step(self, log=True):
    #     prev_state = self.current_state()
    #     if log:
    #         self.log("infer_values...")
    #     for row in self.grid:
    #         for sq in row:
    #             sq.infer_values()
    #     if self.current_state() != prev_state:
    #         return
    #     if log:
    #         self.log("try_solve...")
    #     for s in self.sets:
    #         s.try_solve()
    #     if self.current_state() != prev_state:
    #         return
    #     if log:
    #         self.log("solve_naked_groups...")
    #     self.solve_naked_groups()
    #     if self.current_state() != prev_state:
    #         return

    # def solve_naked_groups(self):
    #     """find groups of 2 or 3 of values in the same set
    #     and remove that group from the rest of the squares in that set

    #     A Naked Pair (also known as a Conjugate Pair) is a set of two candidate numbers sited in two cells that belong to at least one unit in common. That is, they reside in the same row, column or box.
    #     It is clear that the solution will contain those values in those two cells, and all other candidates with those numbers can be removed from whatever unit(s) they have in common.

    #     Naked Triple:
    #     Any group of three cells in the same unit that contain IN TOTAL three candidates is a Naked Triple.
    #     Each cell can have two or three numbers, as long as in combination all three cells have only three numbers.
    #     When this happens, the three candidates can be removed from all other cells in the same unit.

    #     The combinations of candidates for a Naked Triple will be one of the following:

    #     (123) (123) (123) - {3/3/3} (in terms of candidates per cell)
    #     (123) (123) (12) - {3/3/2} (or some combination thereof)
    #     (123) (12) (23) - {3/2/2/}
    #     (12) (23) (13) - {2/2/2}
    #     """
    #     for s in self.sets:
    #         pass

    # def hidden_groups(self):
    #     """ """

    def bruteforce(self):
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

            return "(~{:.2f}%) solve {} {} at {}".format(
                pct_complete,
                '>' if self.go_forward else '<',
                start_square,
                square)

        yield status(start_square, square)
        steps = 0
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

            if steps % 5000 == 0:
                yield status(start_square, square)
            steps += 1

            square = self.grid[self.cursor_y][self.cursor_x]
        self.log(status(start_square, square), replace=True)

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

    # def check_solution(self):
    #     for y in range(N_2):
    #         # check column y
    #         values = filter(
    #             None,
    #             [self.grid[y][i].get_value() for i in range(N_2)])
    #         if len(values) != len(set(values)):
    #             return False
    #         for x in range(N_2):
    #             # check row
    #             values = filter(
    #                 None,
    #                 [self.grid[i][x].get_value() for i in range(N_2)])
    #             if len(values) != len(set(values)):
    #                 return False
    #     # check 3x3 grids
    #     for qy in range(N):
    #         for qx in range(N):
    #             values = filter(
    #                 None,
    #                 [self.grid[N * qy + i % N][N * qx + i / N].get_value()
    #                  for i in range(N_2)])
    #             if len(values) != len(set(values)):
    #                 return False
    #     if self.x_regions:
    #         down_values = filter(
    #             None,
    #             [self.grid[i][i].get_value() for i in range(N_2)])
    #         up_values = filter(
    #             None,
    #             [self.grid[N_2 - 1 - i][i].get_value() for i in range(N_2)])
    #         if len(down_values) != len(set(down_values)):
    #             return False
    #         if len(up_values) != len(set(up_values)):
    #             return False
    #     return True

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

    @property
    def selected_square(self):
        return self.grid[self.cursor_y][self.cursor_x]


