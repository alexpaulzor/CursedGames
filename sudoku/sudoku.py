#!/usr/bin/env python

import curses

import sys
from random import shuffle
import time
from solvable import Square, ExclusiveSet

N = 3
N_2 = N * N
N_3 = N_2 * N
N_4 = N_3 * N


COLOR_SELECTED = 10
COLOR_SAME = 12
COLOR_CONFLICT = 13
COLOR_X = 11

MIN_CLUES = 17
MAX_CLUES = 24


class Sudoku:
    def __init__(self, x_regions=False):
        self.start_time = time.clock()
        self.grid = [[Square(x, y) for x in range(N_2)] for y in range(N_2)]
        self.sets = set()
        self.draw_small = False
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

    def help(self):
        self._log += [
            "Commands:",
            "Arrow keys: move",
            "1-9: toggle number",
            "c: clear",
            "s: toggle small board",
            "a: autosolve step",
            "A: autosolve until key press",
            "R: reset board",
            "f: fill in possible values",
            "F: fill in all possible values (board)",
            "w: save (write) current state",
            "o: load last save",
            "u: undo",
            "r: redo",
            "g: generate board (sloooow)",
            "x: toggle x regions",
            "H: this help",
            "q: quit"
        ]
        self.draw_board()

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
            self.steps = 0
        if line[0] == 'x':
            self.set_x_regions(True)
            line = line[1:]
        else:
            self.set_x_regions(False)
        if len(line) not in (N_4, 2 * N_4, 5 * N_4):
            print "Invalid line: {} ({} ch)".format(line, len(line))
            print ("Lines (excluding preceding extra region chars) "
                   "must be one of length {}".format((N_4, 2 * N_4, 5 * N_4)))
            sys.exit(1)
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
                sq.reset()
        solution = self.compute_solution()
        if not solution:
            self.log("Cannot solve! " + self.current_state())
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
        self.draw_board()
        sq = all_squares.pop()
        key = -1
        clues = 0
        while key == -1:
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
            self.draw_board()
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
        if len(all_squares) + clues <= MAX_CLUES:
            for sq in all_squares:
                sq_val = sq.get_value()
                if not sq_val:
                    continue
                sq.set_value(sq_val, True)
                givens[N_2 * sq.y + sq.x] = str(sq_val)
                givens[81 + N_2 * sq.y + sq.x] = str(sq_val)
                clues += 1
            self.log('saving with {} clues'.format(clues))
            with open('puzzles/generated.sudoku', 'a') as f:
                f.write(given_str(givens[:81]) + '\n')
        self.load_game(given_str(givens))
        self.draw_board()

    def compute_solution(self, initial_state=None):
        backup_state = self.current_state()
        backup_steps = self.steps
        backup_direction = self.go_forward
        if initial_state is not None:
            self.load_game(initial_state)
            self.steps = 0
        self.log("solving from: " + self.current_state())
        self.go_forward = True
        solution = self.solve(None)
        self.load_game(backup_state)
        self.go_forward = backup_direction
        self.steps += backup_steps
        return solution

    def _possible_value_mask(self, sq):
        mask = 0
        for i in sq.possible_values:
            mask += 2**(i - 1)
        return mask

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

    def is_solved(self):
        for s in self.sets:
            if not s.is_solved():
                return False
        for row in self.grid:
            for square in row:
                if not square.is_solved():
                    return False

        self.complete_solution = self.current_state()

        return True

    def solve(self, steps=1):
        start_square = self.grid[self.cursor_y][self.cursor_x]
        #self.smart_solve()
        self.bruteforce(start_square, steps=None)
        if self.is_solved():
            state = self.current_state()
            self.log("Solved! " + state)
            return state
        else:
            if not any(start_square.value_attempts):
                self.log("Unsolvable!")
                return None
            else:
                return False

    def smart_solve(self):
        prev_state = None
        while self.current_state() != prev_state:
            if self.is_solved():
                return self.current_state()
            prev_state = self.current_state()
            for row in self.grid:
                for sq in row:
                    sq.infer_values()
            for s in self.sets:
                s.try_solve()

    def naked_groups(self):
        """find groups of 2 or 3 of values in the same set
        and remove that group from the rest of the squares in that set
        """

    def hidden_groups(self):
        """ """

    def bruteforce(self, start_square, steps=1):
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

        self.log(status(start_square, square))
        self.stdscr.nodelay(True)
        key = -1
        while (key == -1 and
               (steps is None or steps > 0) and
               not self.is_solved() and
               any(start_square.value_attempts)):
            self.steps += 1
            if steps:
                steps -= 1
            self.log(status(start_square, square), replace=True)
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

            if self.steps % 5000 == 0:
                self.log(status(start_square, square), replace=True)
                self.draw_board()
                key = self.stdscr.getch()

            square = self.grid[self.cursor_y][self.cursor_x]
        self.stdscr.nodelay(False)
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

    def check_solution(self):
        for y in range(N_2):
            # check column y
            values = filter(
                None,
                [self.grid[y][i].get_value() for i in range(N_2)])
            if len(values) != len(set(values)):
                return False
            for x in range(N_2):
                # check row
                values = filter(
                    None,
                    [self.grid[i][x].get_value() for i in range(N_2)])
                if len(values) != len(set(values)):
                    return False
        # check 3x3 grids
        for qy in range(N):
            for qx in range(N):
                values = filter(
                    None,
                    [self.grid[N * qy + i % N][N * qx + i / N].get_value()
                     for i in range(N_2)])
                if len(values) != len(set(values)):
                    return False
        if self.x_regions:
            down_values = filter(
                None,
                [self.grid[i][i].get_value() for i in range(N_2)])
            up_values = filter(
                None,
                [self.grid[N_2 - 1 - i][i].get_value() for i in range(N_2)])
            if len(down_values) != len(set(down_values)):
                return False
            if len(up_values) != len(set(up_values)):
                return False
        return True

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

    def _get_blank_board_strings(self):
        if self.draw_small:
            value_width = 3
        else:
            value_width = 2 * N + 1

        horiz_v = '-' * value_width
        major_horiz_v = '=' * value_width
        blank_v = ' ' * value_width

        horiz_sep = '#'.join(['+'.join([horiz_v] * N)] * N)
        major_horiz_sep = '#'.join(['+'.join([major_horiz_v] * N)] * N)
        blank_line = '#'.join(['|'.join([blank_v] * N)] * N)

        horiz_sep = '#' + horiz_sep + '#'
        major_horiz_sep = '#' + major_horiz_sep + '#'
        blank_line = '#' + blank_line + '#'

        return (value_width, horiz_sep, major_horiz_sep, blank_line)

    def _get_square_color(self, square):
        conflicts = self.selected_square().conflict_squares()
        if self.cursor_x == square.x and self.cursor_y == square.y:
            return COLOR_SELECTED
        elif (not self.selected_square().is_unknown() and
              square in conflicts):
            return COLOR_CONFLICT
        elif (square.get_value() and
              self.selected_square().get_value() == square.get_value()):
            return COLOR_SAME
        elif (self.x_regions and
              (square.x == square.y or
               square.x == 9 - 1 - square.y)):
            return COLOR_X
        return 0

    def selected_square(self):
        return self.grid[self.cursor_y][self.cursor_x]

    def draw_board(self):
        (value_width, horiz_sep,
         major_horiz_sep, blank_line) = self._get_blank_board_strings()

        liney = 0
        self.stdscr.addstr(liney, 0, major_horiz_sep, curses.A_DIM)
        liney += 1
        for y in range(N_2):
            linex = 0
            for line in range(1 if self.draw_small else N):
                self.stdscr.addstr(liney, 0, blank_line, curses.A_DIM)

                linex = 1
                for x in range(N_2):
                    square = self.grid[y][x]
                    color = self._get_square_color(square)

                    self.stdscr.addstr(liney, linex, " " * value_width,
                                       curses.color_pair(color))
                    if self.draw_small:
                        rng = [square.get_value()]
                    else:
                        rng = range(line * N + 1, line * N + N + 1)
                    for i in rng:
                        attributes = \
                            curses.A_UNDERLINE if square.is_given else 0
                        if (i and (i == square.get_value() or
                                   (not self.draw_small and
                                    i in square.possible_values and
                                    not square.is_unknown()))):

                            self.stdscr.addstr(
                                liney,
                                linex + 1,
                                "{}".format(i),
                                curses.color_pair(i) | attributes)
                        if not self.draw_small:
                            linex += 2
                    linex += 2
                    if self.draw_small:
                            linex += 2
                liney += 1

            if (y+1) % N == 0:
                self.stdscr.addstr(liney, 0, major_horiz_sep, curses.A_DIM)
            else:
                self.stdscr.addstr(liney, 0, horiz_sep, curses.A_DIM)
            liney += 1

        self._draw_value_counts()
        self._draw_log()
        self.stdscr.refresh()

    def _draw_value_counts(self):

        value_counts = {i: 0 for i in range(1, N_2 + 1)}
        for row in self.grid:
            for sq in row:
                v = sq.get_value()
                if v is not None:
                    value_counts[v] += 1

        for i in range(1, N_2 + 1):
            self.stdscr.addstr(i, N_4, str(i), curses.color_pair(i))
            color = COLOR_SAME if value_counts[i] == N_2 else 0
            self.stdscr.addstr(i, N_4 + 1, ": {}     ".format(value_counts[i]),
                               curses.color_pair(color))
        self.stdscr.addstr(N_2 + 1, N_4, "Steps: {}".format(self.steps))

    def _draw_log(self):
        i = 0
        height, width = self.stdscr.getmaxyx()
        start_line_num = N_2 + N
        num_log_lines = height - start_line_num

        if len(self._log) < num_log_lines:
            num_log_lines = len(self._log)
            start_line_num = height - num_log_lines

        for i in range(start_line_num, height - 1):
            line = str(self._log[-(height - i - 1)])
        #while  < height - 1 and len(self._log) > i:
            #line = str(self._log[-1 - i])
            if len(line) < width - N_4:
                line += ' ' * (width - N_4 - len(line))
            self.stdscr.addstr(i, N_4, line[:(width - N_4)])
            #i += 1

    def newgame(self, stdscr):
        self._init_colors()
        self.stdscr = stdscr
        self.stdscr.clear()
        self.draw_board()
        self.draw_small = False
        self.help()

        key = None
        while key != 'q':
            try:
                key = self.stdscr.getkey()
            except:
                # screen was resized or something
                key = None

            self._handle_key(key)

            self.cursor_x = self.cursor_x % N_2
            self.cursor_y = self.cursor_y % N_2
            if self.is_solved():
                self.log("You won!")
            self.draw_board()
        self.draw_board()

    def _handle_key(self, key):
        initial_state = self.current_state()
        if (key == 'KEY_LEFT' or key == 'h'):
            self.cursor_x -= 1
        elif (key == 'KEY_RIGHT' or key == 'l'):
            self.cursor_x += 1
        elif (key == 'KEY_UP' or key == 'k'):
            self.cursor_y -= 1
        elif (key == 'KEY_DOWN' or key == 'j'):
            self.cursor_y += 1
        elif key in map(str, range(1, N_2 + 1)):
            if self.draw_small:
                self.grid[self.cursor_y][self.cursor_x].clear()
            self.grid[self.cursor_y][self.cursor_x].toggle_mark(int(key))
        elif key == 'c':
            self.grid[self.cursor_y][self.cursor_x].clear()
        elif key == 's':
            self.draw_small = not self.draw_small
            self.stdscr.clear()
        elif key == 'a':
            self.smart_solve()
        elif key == 'A':
            self.solve(None)
        elif key == 'R':
            self.log(self.current_state())
            self.log('resetting from:')
            self.load_game(self.original_state)
            self.load_game(self.current_state(True))
        elif key == 'f':
            self.grid[self.cursor_y][self.cursor_x].infer_values()
        elif key == 'F':
            for row in self.grid:
                for square in row:
                    square.infer_values()
        elif key == 'w':    # write
            self.save_state()
        elif key == 'u':    # open
            if any(self.saved_states):
                self.redo_states.append(initial_state)
                new_state = self.saved_states.pop()
                initial_state = new_state
                self.load_game(new_state)
        elif key == 'r':
            if any(self.redo_states):
                self.load_game(self.redo_states.pop())
        elif key == 'g':    # generate
            self.generate()
        elif key == 'H':
            self.help()
        elif key == 'x':
            self.set_x_regions(not self.x_regions)
        if self.current_state() != initial_state:
            self.save_state(log=False)
            self.steps += 1

    def save_state(self, log=True):
        self.saved_states.append(self.current_state())
        if log:
            self.log("saved: " + self.saved_states[-1])

    def set_x_regions(self, enable_x_regions):
        self.x_regions = enable_x_regions
        self.x_down.set_enabled(self.x_regions)
        self.x_up.set_enabled(self.x_regions)

    def _init_colors(self):
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLUE)
        curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(7, curses.COLOR_CYAN, curses.COLOR_BLUE)
        curses.init_pair(8, curses.COLOR_GREEN, curses.COLOR_BLUE)
        curses.init_pair(9, curses.COLOR_MAGENTA, curses.COLOR_BLUE)
        curses.init_pair(COLOR_SELECTED, curses.COLOR_WHITE,
                         curses.COLOR_GREEN)
        curses.init_pair(COLOR_SAME, curses.COLOR_BLACK, curses.COLOR_CYAN)
        curses.init_pair(COLOR_CONFLICT, curses.COLOR_BLACK, curses.COLOR_RED)
        curses.init_pair(COLOR_X, curses.COLOR_WHITE, curses.COLOR_BLUE)


def main():
    s = Sudoku(False)
    game = sys.argv[1] if len(sys.argv) == 2 else None
    s.load_game(game)
    try:
        curses.wrapper(s.newgame)
    # except Exception as e:
    #     print repr(e)
    finally:
        print "\n".join(s._log)
        print s.original_state
        print s.current_state()
        if s.is_solved():
            print "You won!"
        print "({} clues, {} steps)".format(s.clues, s.steps)

if __name__ == "__main__":
    main()
