#!/usr/bin/python

import curses
import time
import random
import sys

RATE_OF_4 = 1.0 / 10

class Cursed2048:

    board = {}
    stdscr = None
    retval = None
    COLORS = { '1' : 1, '2' : 2, '3' : 3, '4' : 4, '5' : 5, '6' : 6, '7' : 7, '8' : 8, 'M' : 9, 'F' : 10 }

    def __init__(self):
        self.newboard()
        curses.wrapper(self.newgame)
        self.printboard()
        print self.retval



    def newgame(self, stdscr):
        curses.init_pair(9, curses.COLOR_RED, curses.COLOR_BLUE)
        curses.init_pair(10, curses.COLOR_BLUE, curses.COLOR_RED)
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(8, curses.COLOR_WHITE, curses.COLOR_BLACK)
        self.stdscr = stdscr
        self.stdscr.clear()
        self.printboard()
        key = None
        prev_board = self.board
        while (key != 'q'):
            start_board = self.board
            try:
                key = self.stdscr.getkey()
            except:
                pass
            if (key == 'KEY_LEFT' or key == 'h'):
                self.board = self.collapse_left(self.board)
            elif (key == 'KEY_RIGHT' or key == 'l'):
                self.board = [outrow[::-1] for outrow in self.collapse_left([row[::-1] for row in self.board])]
            elif (key == 'KEY_UP' or key == 'k'):
                trans_board = [list(col) for col in zip(*self.board)]
                trans_board = self.collapse_left(trans_board)
                self.board = [list(row) for row in zip(*trans_board)]
            elif (key == 'KEY_DOWN' or key == 'j'):
                trans_board = [list(col) for col in zip(*self.board)]
                trans_board = [outrow[::-1] for outrow in self.collapse_left([row[::-1] for row in trans_board])]
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
                    x = random.randint(0, 3)
                    y = random.randint(0, 3)
                    if self.board[y][x] == 0:
                        self.board[y][x] = 2 if random.random() < RATE_OF_4 else 1
                        break
            self.printboard()

        self.retval = "Goodbye"

    def collapse_left(self, board):
        out = []
        for y in range(4):
            row = board[y][:]
            for x in range(4):
                sq = row[x]
                if sq == 0:
                    self._clear_zeros(row, x)
                elif x > 0 and row[x - 1] == sq:
                    row[x - 1] += 1
                    row[x] = 0
                    self._clear_zeros(row, x)

            out.append(row)
        return out

    def _clear_zeros(self, row, x):
        while x < len(row) and row[x] == 0:
            del row[x]
        for i in range(4 - len(row)):
            row.append(0)

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
        self.stdscr.addstr(0, 0, '+====+' * 4)
        for y, row in enumerate(board or self.board):
            #print (y, row)
            for x, sq in enumerate(row):
                #print (x, sq)
                self.stdscr.addstr(2 * y, 6 * x, '|{:^4}|'.format(2 ** sq if sq > 0 else ' '), curses.color_pair(sq))
                self.stdscr.addstr(2 * y + 1, 0, '+====+' * 4)
        self.stdscr.refresh()

    def newboard(self):
        self.board = [[0] * 4] + [[0] * 4] + [[0] * 4] + [[0] * 4]
        #print self.board

        for i in range(2):
            x = random.randint(0, 3)
            y = random.randint(0, 3)
            #print (x, y, 1)
            self.board[y][x] = 1
        #print self.board


if __name__ == '__main__':
    game = Cursed2048()
