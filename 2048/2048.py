#!/usr/bin/python

import curses
import time
import random
from square import Square
import sys

class Cursed2048:
    board = {}
    stdscr = None
    retval = None
    COLORS = { '1' : 1, '2' : 2, '3' : 3, '4' : 4, '5' : 5, '6' : 6, '7' : 7, '8' : 8, 'M' : 9, 'F' : 10 }

    def __init__(self):
        self.newboard()
        curses.wrapper(self.newgame)
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
        self.stdscr.refresh()
        key = None
        while (key != 'q'):

            key = self.stdscr.getkey()
            if (key == 'KEY_LEFT' or key == 'h'):
                pass
            elif (key == 'KEY_RIGHT' or key == 'l'):
                pass
            elif (key == 'KEY_UP' or key == 'k'):
                pass
            elif (key == 'KEY_DOWN' or key == 'j'):
                pass
            if self.haswon():
                self.retval = "You win!"
                return

            self.printboard()
            self.stdscr.refresh()
        self.retval = "Goodbye"

    def lost(self):
        self.printboard()
        self.stdscr.refresh()
        time.sleep(5)

    def haswon(self):
        # TODO
        return False

    def printboard(self):
        for y, row in self.board.iteritems():
            for x, sq in enumerate(row):
                self.stdscr.addstr(i, 2 * (x + 1), char, curses.color_pair(sq))

    def newboard(self):
        self.board = {}
        for i in range(0, 4):
            self.board[i] = {}
            for j in range(0, 4):
                self.board[i][j] = 0

        rand = random.Random()

        for i in range(0, 2):
            j = rand.randint(0, height - 1)
            k = rand.randint(0, width - 1)
            self.board[j][k] = 1


if __name__ == '__main__':
    game = Cursed2048()
