#!/usr/bin/python

import curses
import random

class Maze:
    board = {}

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.newboard(width, height)
        #curses.wrapper(self.newgame)


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
    
    def outputboard(self):
        print
        print "Current: %s" % self.current_square
        line = ""
        for x in range(len(self.board[0])):
            line += "__"
        print line
        for y in self.board:
            line = ""
            if self.board[y][0] == self.enter_square:
                line += "S"
            else:
                line += "|"
            for x in self.board[y]:
                square = self.board[y][x]
                if square.down_wall and square.right_wall:
                    line += "_|"
                elif square.right_wall:
                    line += " |"
                elif square.down_wall:
                    line += "__"
            print line
        print





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
            self.exit_square.down_wall = False
        else:
            self.exit_square = self.board[rand.randint(0, height - 1)][width - 1]
            self.exit_square.right_wall = False
        #self.exit_square.visited = False


        self.explore_neighbors(self.enter_square)

    def explore_neighbors(self, square):
        """
            Explore unvisited neighbors in random order
            
            
        """
        square.visited = True
        self.current_square = square
        nbrs = []
        if square.y > 0:
            nbrs.append(self.board[square.y - 1][square.x])
        if square.x > 0:
            nbrs.append(self.board[square.y][square.x - 1])
        if square.y < self.height - 1:
            nbrs.append(self.board[square.y + 1][square.x])
        if square.x < self.width - 1:
            nbrs.append(self.board[square.y][square.x + 1])
        
        rand = random.Random()
        rand.shuffle(nbrs)
        
        self.outputboard()

        for nbr in nbrs:
            if not nbr.visited:
                #nbr.visited = True
                square.destroy_wall(nbr)
                self.explore_neighbors(nbr)












class Square:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.right_wall = True
        self.down_wall = True
        self.visible = False
        self.visited = False

    def destroy_wall(self, other):
        print "Destroying wall %s, %s" % (self, other)
        if other.x == self.x:
            if other.y == self.y - 1:
                other.down_wall = False
            elif other.y == self.y + 1:
                self.down_wall = False
        elif other.y == self.y:
            if other.x == self.x - 1:
                other.right_wall = False
            elif other.x == self.x + 1:
                self.right_wall = False
        print "Destroyed wall %s, %s" % (self, other)

    def __str__(self):
        if self.down_wall:
            d = "_"
        else:
            d = " "
        if self.right_wall:
            r = "|"
        else:
            r = " "

        if self.visited:
            v = "v"
        else:
            v = " "

        return "[%s](%d,%d)%s%s" % (v, self.x, self.y, d, r)


if __name__ == "__main__":
    m = Maze(5, 5)
