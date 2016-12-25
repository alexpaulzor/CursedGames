#!/usr/bin/env python

import curses
import click

import sys
import time
from sudokuboard import SudokuBoardSolver, SudokuBoardGenerator, N, N_2, N_4
import threading

COLOR_SELECTED = 10
COLOR_SAME = 12
COLOR_CONFLICT = 13
COLOR_X = 11
COLOR_META = 14


class SudokuDisplay:
    def __init__(self, x_regions=False, meta_regions=False):
        self.start_time = time.clock()
        self.draw_small = False
        self.saved_states = []
        self.undo_states = []
        self.redo_states = []
        self.steps = 0
        self._computed_solution = None
        self.show_all_conflicts = False
        self.board = SudokuBoardSolver(x_regions=x_regions,
                                       meta_regions=meta_regions)

    def _get_square_color(self, sq):
        conflicts = self.board.selected_square.conflict_squares()

        if self.show_all_conflicts and self._computed_solution:
            correct_value = int(self._computed_solution[sq.id - N_4])
            if correct_value not in sq.possible_values:
                return COLOR_CONFLICT
        if sq == self.board.selected_square:
            return COLOR_SELECTED
        elif (not self.board.selected_square.is_unknown() and
              sq in conflicts):
            return COLOR_CONFLICT
        elif (sq.get_value() and
              self.board.selected_square.get_value() == sq.get_value()):
            return COLOR_SAME
        elif (self.board.x_regions and
              (sq.x == sq.y or
               sq.x == 9 - 1 - sq.y)):
            return COLOR_X
        elif (self.board.meta_regions and
              sq.x not in (0, N_2 / 2, N_2 - 1) and
              sq.y not in (0, N_2 / 2, N_2 - 1)):
            return COLOR_META
        # elif self.board.meta_regions:
        #     for s in (self.board.meta_0, self.board.meta_1,
        #               self.board.meta_2, self.board.meta_3):
        #         if sq in s.squares:
        #             return COLOR_META
        return 0

    def _get_blank_board_strings(self):
        horiz_v = '-' * self.value_width
        major_horiz_v = '=' * self.value_width
        blank_v = ' ' * self.value_width

        horiz_sep = '#'.join(['+'.join([horiz_v] * N)] * N)
        major_horiz_sep = '#'.join(['+'.join([major_horiz_v] * N)] * N)
        blank_line = '#'.join(['|'.join([blank_v] * N)] * N)

        horiz_sep = '#' + horiz_sep + '#'
        major_horiz_sep = '#' + major_horiz_sep + '#'
        blank_line = '#' + blank_line + '#'

        return (self.value_width, horiz_sep, major_horiz_sep, blank_line)

    @property
    def value_width(self):
        if self.draw_small:
            return 3
        else:
            return 2 * N + 1

    @property
    def value_height(self):
        if self.draw_small:
            return 2
        else:
            return 2 * N + 1

    def _draw_blank_board(self):
        self._draw_top_horiz_sep(0, 0)

    def _draw_blank_line(self, y, x):
        pass

    def _draw_major_horiz_sep(self, y, x):
        self.stdscr.addch(y, x, curses.ACS_LTEE)
        x += 1

        while x < self.value_width - 1:
            self.stdscr.addch(y, x, curses.ACS_HLINE)
            x += 1
        self.stdscr.addch(y, x, curses.ACS_RTEE)

    def _draw_top_horiz_sep(self, y, x):
        self._draw_major_horiz_sep(y, x)

    # def _draw_line(self, y, x, left_ch=curses.ACS_VLINE, value_ch=ord(' '),
    #                minor_sep_ch=curses.ACS_PLUS, major_sep_ch=curses.ACS_BLOCK,
    #                right_ch=curses.ACS_RTEE):
    #     self.stdscr.addch(y, x, left_ch)
    #     x += 1
    #     for i in range(N):
    #         while x < self.value_width:
    #             self.stdscr.addch(y, x, value_ch)
    #             x += 1
    #         self.stdscr.addch(y, x, curses.ACS_RTEE)

    def draw_square(self, sq):
        # assume the square is a regular sq in the middle of a 3-grid
        y = sq.y * self.value_height
        x = sq.x * (self.value_width + 1)
        v = sq.get_value()
        color = self._get_square_color(sq)

        if self.draw_small:
            self.stdscr.addch(y, x, curses.ACS_PLUS)
            self.stdscr.addch(y+1, x, curses.ACS_VLINE)
            #self.stdscr.addch(y+2, x, curses.ACS_PLUS)
            for dx in range(x, x + self.value_width):
                self.stdscr.addch(y, dx, curses.ACS_HLINE)
                #self.stdscr.addch(y+2, dx, curses.ACS_HLINE)
            self.stdscr.addch(y, x+self.value_width, curses.ACS_PLUS)
            self.stdscr.addch(y+1, x+self.value_width, curses.ACS_VLINE)
            #self.stdscr.addch(y+2, x+self.value_width, curses.ACS_PLUS)
            self.stdscr.addstr(y+1, x+1, " " * self.value_width, curses.color_pair(color))
            attributes = curses.A_UNDERLINE if sq.is_given else 0
            if v:
                self.stdscr.addstr(
                    y + 1,
                    x + 2,
                    "{}".format(v),
                    curses.color_pair(v) | attributes)

    def draw_board(self):
        # if self.draw_small:
        #     for row in self.board.grid:
        #         for sq in row:
        #             self.draw_square(sq)
        #     self._draw_value_counts()
        #     self._draw_log()
        #     self.stdscr.refresh()
        #     return

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
                    square = self.board.grid[y][x]
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
        for row in self.board.grid:
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

        if len(self.board._log) < num_log_lines:
            num_log_lines = len(self.board._log)
            start_line_num = height - num_log_lines

        for i in range(start_line_num, height - 1):
            line = str(self.board._log[-(height - i - 1)])
            if len(line) < width - N_4:
                line += ' ' * (width - N_4 - len(line))
            self.stdscr.addstr(i, N_4, line[:(width - N_4)])

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

            self.board.cursor_x = self.board.cursor_x % N_2
            self.board.cursor_y = self.board.cursor_y % N_2
            self.draw_board()
        self.draw_board()

    def help(self):
        self.board._log += [
            "Commands:",
            "Arrow keys/hjkl: move",
            "1-9: toggle number",
            "c: clear",
            "C: Check board (toggle)",
            "s: toggle Small board",
            "a: autosolve step",
            "A: Autosolve until pressed again",
            "R: reset board",
            "f: fill in possible values (current sq)",
            "F: Fill in all possible values (board)",
            "w: save (write) current state",
            "o: load (open) last save",
            "u: undo",
            "r: redo",
            "g: generate board until pressed again",
            "x: toggle x regions",
            "m: toggle meta regions",
            ".: step through solver",
            "H: this help",
            "q: quit"
        ]
        self.draw_board()

    def log(self, msg, replace=False):
        self.board.log(msg, replace=replace)

    def _handle_key(self, key):
        initial_state = self.board.current_state()
        if (key == 'KEY_LEFT' or key == 'h'):
            self.board.cursor_x -= 1
        elif (key == 'KEY_RIGHT' or key == 'l'):
            self.board.cursor_x += 1
        elif (key == 'KEY_UP' or key == 'k'):
            self.board.cursor_y -= 1
        elif (key == 'KEY_DOWN' or key == 'j'):
            self.board.cursor_y += 1
        elif key in map(str, range(1, N_2 + 1)):
            if self.draw_small:
                self.board.selected_square.clear()
            self.board.selected_square.toggle_mark(int(key))
        elif key == 'c':
            self.board.selected_square.clear()
        elif key == 'C':
            thread = threading.Thread(target=self._toggle_conflicts, args=())
            thread.daemon = True
            thread.start()
        elif key == 's':
            self.draw_small = not self.draw_small
            self.stdscr.clear()
        elif key == 'a':
            self.board.solve_step()
        elif key == '.':
            self._solve_step_slowly()
        elif key == 'A':
            self.stdscr.nodelay(True)
            last_status_clock = time.clock()
            for msg in self.board.solve_iter():
                if time.clock() - last_status_clock > 1:
                    last_status_clock = time.clock()
                    self.log(msg, replace=True)
                    key = self.stdscr.getch()
                    if key == ord('A'):
                        self.log(chr(key))
                        break
                    self.draw_board()
            self.stdscr.nodelay(False)
            if not self.board.is_solved():
                self.log("Unsolvable!")
        elif key == 'R':
            self.log('resetting from: ' + self.board.current_state())
            self.board.load_game(self.board.current_state(
                givens_only=True, include_possibles=False))
        elif key == 'f':
            self.board.selected_square.infer_values()
        elif key == 'F':
            for row in self.board.grid:
                for square in row:
                    square.infer_values()
        elif key == 'w':    # write
            self.save_state()
        elif key == 'o':    # open
            if any(self.saved_states):
                new_state = self.saved_states.pop()
                initial_state = new_state
                self.board.load_game(new_state)
                self.log('loaded: ' + new_state)
        elif key == 'u':    # undo
            if any(self.undo_states):
                self.redo_states.append(initial_state)
                new_state = self.undo_states.pop()
                initial_state = new_state
                self.board.load_game(new_state)
        elif key == 'r':
            if any(self.redo_states):
                self.board.load_game(self.redo_states.pop())
        elif key == 'g':    # generate
            self._generate()
        elif key == 'H':
            self.help()
        elif key == 'x':
            self.board.set_x_regions(not self.board.x_regions)
        elif key == 'm':
            self.board.set_meta_regions(not self.board.meta_regions)
        if self.board.current_state() != initial_state:
            self.save_state(log=False)
            self.steps += 1

    def _generate(self):
        self.stdscr.nodelay(True)
        start = self.board.current_state(include_possibles=False)
        self.board = SudokuBoardGenerator()
        self.board.load_game(start)
        gi = self.board.generate_iter()
        self.log(next(gi))
        last_status_clock = time.clock()
        for msg in gi:
            if 'gen' in msg or time.clock() - last_status_clock > 1:
                last_status_clock = time.clock()
                self.log(msg, replace=('gen' not in msg))
                self.draw_board()
                key = self.stdscr.getch()
                if key == ord('g'):
                    self.log('Generate stopped.')
                    break
        self.stdscr.nodelay(False)

    def _solve_step_slowly(self):
        if self.board.is_solved():
            self.log('Solved!')
            return
        self.stdscr.nodelay(False)
        wait = None
        last_state = self.board.current_state()
        last_msg_ineffective = False
        step_msgs = self.board.solve_step_iter(last_state, verbose=True)
        for msg in step_msgs:
            state = self.board.current_state()
            if state == last_state:
                msg += '...ineffective'
                self.log(msg, replace=last_msg_ineffective)
                last_msg_ineffective = True
            else:
                msg += '...success!'
                self.log(msg)
                last_msg_ineffective = False
                if wait:
                    key = self.stdscr.getkey()
                    if key != '.':
                        wait = False
                elif wait is None:
                    wait = True
            last_state = state

            self.draw_board()

    def save_state(self, log=True):
        state = self.board.current_state()
        self.undo_states.append(state)
        if log:
            self.log("saved: " + state)
            self.saved_states.append(state)

    def _compute_solution(self):
        if self._computed_solution:
            return self._computed_solution
        solver = SudokuBoardSolver()
        solver.load_game(self.board.current_state(givens_only=True))
        self.log("Computing solution...")
        last_status_clock = time.clock()
        for msg in solver.solve_iter():
            if time.clock() - last_status_clock > 1:
                last_status_clock = time.clock()
                self.log(msg, replace=True)
                self.draw_board()
        if not solver.is_solved():
            self.log("Unsolvable puzzle!")
            return None
        self._computed_solution = solver.current_state(
            include_possibles=False)
        self._log_check_solution()
        return self._computed_solution

    def _log_check_solution(self):
        if self.show_all_conflicts and self._computed_solution:
            for row in self.board.grid:
                for sq in row:
                    correct_value = int(self._computed_solution[sq.id - N_4])
                    if correct_value not in sq.possible_values:
                        self.log("Checking solution...Errors exist")
                        return
            self.log('Checking solution...ok')

    def _toggle_conflicts(self):
        self._compute_solution()
        self.show_all_conflicts = not self.show_all_conflicts
        self._log_check_solution()

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
        curses.init_pair(COLOR_META, curses.COLOR_WHITE, curses.COLOR_MAGENTA)
