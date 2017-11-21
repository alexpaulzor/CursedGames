#!/usr/bin/python

import curses
import time
import random

RATE_OF_4 = 1.0 / 10
N = 5


class Cursed2048:

    board = {}
    stdscr = None
    retval = None

    def __init__(self):
        self.newboard()
        curses.wrapper(self.newgame)
        self.printboard()
        print self.retval

    def newgame(self, stdscr):
        curses.init_pair(9, curses.COLOR_GREEN, curses.COLOR_BLUE)
        curses.init_pair(10, curses.COLOR_MAGENTA, curses.COLOR_BLUE)
        curses.init_pair(11, curses.COLOR_RED, curses.COLOR_BLUE)
        curses.init_pair(12, curses.COLOR_YELLOW, curses.COLOR_BLUE)
        curses.init_pair(13, curses.COLOR_WHITE, curses.COLOR_BLUE)
        curses.init_pair(14, curses.COLOR_WHITE, curses.COLOR_GREEN)
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(8, curses.COLOR_CYAN, curses.COLOR_BLUE)
        self.stdscr = stdscr
        self.stdscr.clear()
        self.printboard()
        key = None
        prev_board = self.board

        while (key != 'q'):
            self.new_sq = None
            start_board = self.board
            try:
                key = self.stdscr.getkey()
            except Exception:
                pass
            if (key == 'KEY_LEFT' or key == 'h'):
                self.board = self.collapse_left(self.board)
            elif (key == 'KEY_RIGHT' or key == 'l'):
                self.board = [
                    outrow[::-1]
                    for outrow in
                    self.collapse_left(
                        [row[::-1] for row in self.board])]
            elif (key == 'KEY_UP' or key == 'k'):
                trans_board = [list(col) for col in zip(*self.board)]
                trans_board = self.collapse_left(trans_board)
                self.board = [list(row) for row in zip(*trans_board)]
            elif (key == 'KEY_DOWN' or key == 'j'):
                trans_board = [list(col) for col in zip(*self.board)]
                trans_board = [
                    outrow[::-1]
                    for outrow in
                    self.collapse_left(
                        [row[::-1] for row in trans_board])]
                self.board = [list(row) for row in zip(*trans_board)]
            elif key == 'u':
                self.board = prev_board
            if self.haswon():
                self.retval = "You win!"
            elif self.haslost():
                self.lost()
                return

            if start_board != self.board:
                prev_board = start_board
                while key != 'u':
                    x = random.randint(0, N - 1)
                    y = random.randint(0, N - 1)
                    if self.board[y][x] == 0:
                        self.board[y][x] = (
                            2
                            if random.random() < RATE_OF_4
                            else 1)
                        self.new_sq = (x, y)
                        break
            self.printboard()

        self.retval = "Goodbye"

    def collapse_left(self, board):
        out = []
        for y in range(N):
            row = board[y][:]
            row = self._collapse_sq(row)

            for i in range(N - len(row)):
                row.append(0)

            out.append(row)
        return out

    def _collapse_sq(self, row, x=0):
        row = [sq for sq in row if sq > 0]
        if x >= len(row):
            return row
        if row[x] > 0 and x < len(row) - 1 and row[x + 1] == row[x]:
            row[x] += 1
            row[x + 1] = 0
        row = self._collapse_sq(row, x + 1)

        return row

    def haslost(self):
        for row in self.board:
            for sq in row:
                if sq == 0:
                    return False

    def lost(self):
        self.retval = "Game over."
        self.printboard()
        time.sleep(5)

    def haswon(self):
        # TODO
        return False

    def printboard(self, board=None):
        linesep = ('+' + ('=' * N) + '+') * N
        self.stdscr.addstr(0, 0, linesep)
        for y, row in enumerate(board or self.board):
            for x, sq in enumerate(row):
                color = sq
                self.stdscr.addstr(
                    1 + 2 * y,
                    (N + 2) * x,
                    ('|{:^' + str(N) + '}|').format(
                        2 ** sq if sq > 0 else ' '), curses.color_pair(color))
                self.stdscr.addstr(
                    1 + 2 * y + 1,
                    0,
                    linesep)
        self.stdscr.refresh()

    def newboard(self):
        self.board = []
        for i in range(N):
            self.board.append([0] * N)

        for i in range(2):
            x = random.randint(0, N - 1)
            y = random.randint(0, N - 1)
            self.board[y][x] = 1
            self.new_sq = (x, y)


if __name__ == '__main__':
    game = Cursed2048()
