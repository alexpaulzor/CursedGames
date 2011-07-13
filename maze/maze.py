#!/usr/bin/python

import curses
import random

class Maze:
    board = {}

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.newboard(width, height)
        curses.wrapper(self.newgame)


    def newgame(self, stdscr):
        
        self.stdscr = stdscr
        self.stdscr.clear()
        self.printboard()
        self.stdscr.refresh()
        key = None
        while key != 'q':
            key = self.stdscr.getkey()


    def printboard(self):
        for y in self.board:
            for x in self.board[y]:
                square = self.board[y][x]
                if square.down_wall and square.right_wall:
                    self.stdscr.addstr(y, x * 2, "_|")
                elif square.right_wall:
                    self.stdscr.addstr(y, x * 2 + 1, "|")
                elif square.down_wall:
                    self.stdscr.addstr(y, x * 1, "__")




    def newboard(self, width, height):
        self.board = {}

        for y in range(height):
            self.board[y] = {}
            for x in range(width):
                self.board[y][x] = Square(x, y)

        rand = random.Random()
        # out will be either right or bottom wall
        self.enter_square = self.board[0][0]
        if rand.randint(0, 1) == 0:
            self.exit_square = self.board[height - 1][rand.randint(0, width - 1)]
        else:
            self.exit_square = self.board[rand.randint(0, height - 1)][width - 1]
        self.exit_square.visited = True

        tovisit = [self.exit_square]

        while len(tovisit) > 0:
            current = tovisit.pop()
            print "CURRENT: %s" % current
            tovisit += self.explore_neighbors(current)

    def explore_neighbors(self, square):
        nbrs = []
        if square.y > 0:
            s = self.board[square.y - 1][square.x]
            if not s.visited:
                s.visited = True
                s.down_wall = False
                nbrs.append(s)
                print s
        if square.x > 0:
            s = self.board[square.y][square.x - 1]
            if not s.visited:
                s.visited = True
                s.right_wall = False
                nbrs.append(s)
                print s
        if square.y < self.height - 1:
            s = self.board[square.y + 1][square.x]
            if not s.visited:
                s.visited = True
                square.down_wall = False
                nbrs.append(s)
                print s
        if square.x < self.width - 1:
            s = self.board[square.y][square.x + 1]
            if not s.visited:
                s.visited = True
                square.right_wall = False
                nbrs.append(s)
                print s
        rand = random.Random()
        rand.shuffle(nbrs)
        return nbrs











class Square:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.right_wall = True
        self.down_wall = True
        self.visible = False
        self.visited = False
    
    def __str__(self):
        if self.down_wall:
            d = "_"
        else:
            d = " "
        if self.right_wall:
            r = "|"
        else:
            r = " "

        return "(%d,%d)%s%s" % (self.x, self.y, d, r)


if __name__ == "__main__":
    m = Maze(5, 5)
