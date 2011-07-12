#!/usr/bin/python

import curses
import random

class maze:
    board = {}

    def __init__(self, width, height):
        self.width = width
        self.height = height

    def newboard(self, width, height):
        self.board = {}

        for x in range(width):
            board[x] = {}
            for y in range(height):
                self.board[x][y] = Square(x, y)

        rand = random.Random()
        # out will be either right or bottom wall
        self.enter_square = self.board[0][0]
        if rand.randint(0, 1) == 0:
            self.exit_square = self.board[width - 1][rand.randint(0, height - 1)]
        else:
            self.exit_square = self.board[rand.randint(0, width - 1)][height - 1]

        tovisit = [self.exit_square]

        while len(tovisit) > 0:
             current = tovisit.pop()
             if not current.visited:
                 current.visited = True
                 tovisit += self.explore_neighbors(current)

    def explore_neighbors(self, square):
        nbrs = []
        if square.x > 0:
            if square.y > 0:
                s = self.board[square.x - 1][square.y - 1]
                if not s.visited:
                    nbrs.append(s)
            s = self.board[square.x - 1][square.y]
            if not s.visited:
                nbrs.append(s)
            if square.y < self.height - 1:
                s = self.board[square.x - 1][square.y + 1]
                if not s.visited:
                    nbrs.append(s)
        if square.y > 0:
            s = self.board[square.x][square.y - 1]
            if not s.visited:
                nbrs.append(s)
        if square.y < self.height - 1:
            s = self.board[square.x][square.y + 1]
            if not s.visited:
                nbrs.append(s)
        if square.x < self.width - 1:
            if square.y > 0:
                s = self.board[square.x + 1][square.y - 1]
                if not s.visited:
                    nbrs.append(s)
            s = self.board[square.x + 1][square.y]
            if not s.visited:
                nbrs.append(s)
            if square.y < self.height - 1:
                s = self.board[square.x + 1][square.y + 1]
                if not s.visited:
                    nbrs.append(s)
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
