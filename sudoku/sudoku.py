#!/usr/bin/env python

import curses

import sys
from random import shuffle
import time
from solvable import Square, ExclusiveSet
from sudokuboard import (SudokuBoard, SudokuBoardSolver, SudokuBoardGenerator,
    N, N_2, N_4, MIN_CLUES, MAX_CLUES)

COLOR_SELECTED = 10
COLOR_SAME = 12
COLOR_CONFLICT = 13
COLOR_X = 11

class Sudoku:
    def __init__(self, x_regions=False):
        self.start_time = time.clock()
        self.draw_small = False
        self.saved_states = []
        self.undo_states = []
        self.redo_states = []
        self.steps = 0
        self.board = SudokuBoardSolver(x_regions)

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
        conflicts = self.board.selected_square.conflict_squares()
        if self.board.cursor_x == square.x and self.board.cursor_y == square.y:
            return COLOR_SELECTED
        elif (not self.board.selected_square.is_unknown() and
              square in conflicts):
            return COLOR_CONFLICT
        elif (square.get_value() and
              self.board.selected_square.get_value() == square.get_value()):
            return COLOR_SAME
        elif (self.board.x_regions and
              (square.x == square.y or
               square.x == 9 - 1 - square.y)):
            return COLOR_X
        return 0

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
        #while  < height - 1 and len(self.board._log) > i:
            #line = str(self.board._log[-1 - i])
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

            self.board.cursor_x = self.board.cursor_x % N_2
            self.board.cursor_y = self.board.cursor_y % N_2
            self.draw_board()
        self.draw_board()

    def help(self):
        self.board._log += [
            "Commands:",
            "Arrow keys: move",
            "1-9: toggle number",
            "c: clear",
            "s: toggle small board",
            "a: autosolve step",
            "A: autosolve until pressed again",
            "R: reset board",
            "f: fill in possible values (current sq)",
            "F: fill in all possible values (board)",
            "w: save (write) current state",
            "o: load last save",
            "u: undo",
            "r: redo",
            "g: generate board until pressed again",
            "x: toggle x regions",
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
        elif key == 's':
            self.draw_small = not self.draw_small
            self.stdscr.clear()
        elif key == 'a':
            self.board.solve_step()
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
            self.board.load_game(self.board.current_state(givens_only=True, include_possibles=False))
        elif key == 'f':
            self.board.grid[self.board.cursor_y][self.board.cursor_x].infer_values()
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
            self.stdscr.nodelay(True)
            self.board = SudokuBoardGenerator(self.board.x_regions)
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
        elif key == 'H':
            self.help()
        elif key == 'x':
            self.board.set_x_regions(not self.board.x_regions)
        if self.board.current_state() != initial_state:
            self.save_state(log=False)
            self.steps += 1

    def save_state(self, log=True):
        state = self.board.current_state()
        self.undo_states.append(state)
        if log:
            self.log("saved: " + state)
            self.saved_states.append(state)

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
    game = sys.argv[1] if len(sys.argv) >= 2 else None
    s.board.load_game(game)

    try:
        if sys.argv[-1] in ('-s', '--solve'):
            last_status_clock = time.clock()
            for msg in s.board.solve_iter():
                if time.clock() - last_status_clock > 1:
                    last_status_clock = time.clock()
                    print msg
        else:
            curses.wrapper(s.newgame)
    # except Exception as e:
    #     print repr(e)
    finally:
        print "\n".join(s.board._log)
        print s.board.original_state
        print s.board.current_state()
        if s.board.is_solved():
            print "You won!"
        print "({} clues, {} steps)".format(s.board.clues, s.steps)

if __name__ == "__main__":
    main()
