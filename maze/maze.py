#!/usr/bin/python

import curses
import random

class Maze:
    STRAIGHT_BIAS = 0.2

    board = {}

    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.steps = 0
        self.newboard(width, height)
        curses.wrapper(self.newgame)
        print self.retval
        solution_size = 0
        explored_squares = 0
        for row in self.board.values():
            for sq in row.values():
                if sq.in_solution:
                    solution_size += 1
                if sq.in_solution is not None:
                    explored_squares += 1
        print "solution {} squares. {} / {} squares visited, {} steps".format(
            solution_size, explored_squares, width * height, self.steps)

    def visit_neighbors(self, square):
        self.steps += 1
        square.visible = True
        if square.x > 0:
            left_neighbor = self.board[square.y][square.x]
            while left_neighbor and not left_neighbor.right_wall:
                left_neighbor.visible = True
                if left_neighbor.x > 0:
                    left_neighbor = self.board[left_neighbor.y][left_neighbor.x - 1]
                else:
                    left_neighbor = None

        if square.y > 0:
            top_neighbor = self.board[square.y - 1][square.x]
            while top_neighbor and not top_neighbor.down_wall:
                top_neighbor.visible = True
                if top_neighbor.y > 0:
                    top_neighbor = self.board[top_neighbor.y - 1][top_neighbor.x]
                else:
                    top_neighbor = None
        if not square.right_wall and square.x < len(self.board[0]) - 1:
            right_neighbor = square
            while right_neighbor and not right_neighbor.right_wall and right_neighbor.x < len(self.board[0]) - 1:
                right_neighbor = self.board[right_neighbor.y][right_neighbor.x + 1]
                right_neighbor.visible = True
        if not square.down_wall and square.y < len(self.board) - 1:
            down_neighbor = square
            while down_neighbor and not down_neighbor.down_wall and down_neighbor.y < len(self.board) - 1:
                down_neighbor = self.board[down_neighbor.y + 1][down_neighbor.x]
                down_neighbor.visible = True

    def newgame(self, stdscr):
        self.current_square = self.enter_square
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_RED)
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLUE)
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_GREEN)
        self.stdscr = stdscr
        self.stdscr.clear()
        self.printwholeboard()
        #self.printboard()
        self.stdscr.refresh()
        key = None
        while (key != 'q'):
            key = self.stdscr.getkey()
            prev_square = self.current_square
            if (key == 'KEY_LEFT' or key == 'h') and self.current_square.x > 0:
                neighbor = self.board[self.current_square.y][self.current_square.x - 1]
                if not neighbor.right_wall:
                    self.current_square = neighbor
                    self.visit_neighbors(self.current_square)
            elif (key == 'KEY_RIGHT' or key == 'l') and not self.current_square.right_wall and self.current_square.x < len(self.board[0]) - 1:
                neighbor = self.board[self.current_square.y][self.current_square.x + 1]
                self.current_square = neighbor
                self.visit_neighbors(self.current_square)
            elif (key == 'KEY_UP' or key == 'k') and self.current_square.y > 0:
                neighbor = self.board[self.current_square.y - 1][self.current_square.x]
                if not neighbor.down_wall:
                    self.current_square = neighbor
                    self.visit_neighbors(self.current_square)
            elif (key == 'KEY_DOWN' or key == 'j') and not self.current_square.down_wall and self.current_square.y < len(self.board) - 1:
                neighbor = self.board[self.current_square.y + 1][self.current_square.x]
                self.current_square = neighbor
                self.visit_neighbors(self.current_square)
            elif key == 's':
                self.solve()
            if self.haswon():
                self.retval = "You win!"
                return
            if self.current_square != prev_square:
                if self.current_square.in_solution:
                    prev_square.in_solution = False
                else:
                    prev_square.in_solution = True
            self.printboard()
            self.stdscr.refresh()
        self.retval = "Goodbye"

    def haswon(self):
        return self.current_square == self.exit_square


    def printboard(self):
        """There are a few cases here:
            * I am visible
            ** Show my walls
            * I am not visible
            ** Neither of my right or down neighbors are visible
            *** Show "##"
            ** Both my right and down neighbors are visible
            *** Show my walls


        """
        for y in self.board:
            for x in self.board[y]:
                square = self.board[y][x]
                color = 1
                if square == self.current_square:
                    color = 2
                elif square == self.exit_square or square.in_solution:
                    color = 3
                show_right = False
                show_down = False
                if square.visible:
                    show_right = True
                    show_down = True
                else:
                    if x < len(self.board[0]) - 1:
                        right_neighbor = self.board[y][x + 1]
                        if right_neighbor.visible:
                            show_right = True
                    if y < len(self.board) - 1:
                        down_neighbor = self.board[y + 1][x]
                        if down_neighbor.visible:
                            show_down = True
                strtext = "##"
                if not show_right and not show_down:
                    strtext = "##"
                elif show_right and not show_down:
                    if square.right_wall:
                        strtext = "#|"
                    else:
                        # should not happen
                        strtext = "# "
                elif show_down and not show_right:
                    if square.down_wall:
                        strtext = "_#"
                    else:
                        # should not happen
                        strtext = " #"
                elif square.down_wall and square.right_wall:
                    strtext = "_|"
                elif square.right_wall:
                    strtext = " |"
                elif square.down_wall:
                    strtext = "__"
                else:
                    strtext = "  "
                self.stdscr.addstr(y, x * 2, strtext[0], curses.color_pair(color))
                self.stdscr.addstr(y, x * 2 + 1, strtext[1], curses.color_pair(color))

    def printwholeboard(self):
        for y in self.board:
            for x in self.board[y]:
                square = self.board[y][x]
                color = 1
                if square == self.current_square:
                    color = 2
                elif square == self.exit_square or square.in_solution:
                    color = 3
                if square.down_wall and square.right_wall:
                    strtext = "_|"
                elif square.right_wall:
                    strtext = " |"
                elif square.down_wall:
                    strtext = "__"
                else:
                    strtext = "  "
                self.stdscr.addstr(y, x * 2, strtext[0], curses.color_pair(color))
                self.stdscr.addstr(y, x * 2 + 1, strtext[1], curses.color_pair(color))

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
                else:
                    line += "  "
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

        # direction is [y, x]. This is to introduce a slight bias to make the maze with straighter corridors
        if rand.randint(0, 1) == 0:
            direction = [0, 1]
        else:
            direction = [1, 0]
        self.explore_neighbors(self.enter_square, direction)

        self.current_square = self.enter_square
        self.current_square.visited = True

        if rand.randint(0, 1) == 0:
            direction = [0, 1]
        else:
            direction = [1, 0]
        self.explore_neighbors(self.enter_square, direction)

    def explore_neighbors(self, square, direction):
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

        straight_coords = [square.y + direction[0], square.x + direction[1]]
        if straight_coords[0] in self.board and straight_coords[1] in self.board[straight_coords[0]]:
            straight_neighbor = self.board[straight_coords[0]][straight_coords[1]]

            if rand.random() < self.STRAIGHT_BIAS and straight_neighbor in nbrs:
                nbrs.remove(straight_neighbor)
                nbrs.insert(0, straight_neighbor)

        for nbr in nbrs:
            if not nbr.visited:
                #nbr.visited = True
                square.destroy_wall(nbr)
                self.explore_neighbors(nbr, [nbr.y - square.y, nbr.x - square.x])

    def solve(self):
        self.solve_step(self.current_square)

    def solve_step(self, square):
        nbrs = []
        self.current_square = square
        square.in_solution = True
        self.visit_neighbors(self.current_square)
        self.printboard()
        self.stdscr.refresh()
        if self.haswon():
            return
        if square.x < self.width - 1 and not square.right_wall:
            nbrs.append(self.board[square.y][square.x + 1])
        if square.y < self.height - 1 and not square.down_wall:
            nbrs.append(self.board[square.y + 1][square.x])
        if square.x > 0 and not self.board[square.y][square.x - 1].right_wall:
            nbrs.append(self.board[square.y][square.x - 1])
        if square.y > 0 and not self.board[square.y - 1][square.x].down_wall:
            nbrs.append(self.board[square.y - 1][square.x])

        for nbr in nbrs:
            if nbr.in_solution is None:
                self.solve_step(nbr)
                self.printboard()
                self.stdscr.refresh()
                if self.haswon():
                    return

        square.in_solution = False
        self.current_square = square
        self.printboard()
        self.stdscr.refresh()

class Square:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.right_wall = True
        self.down_wall = True
        self.visible = False
        #self.visible = True
        self.visited = False
        self.in_solution = None

    def destroy_wall(self, other):
        #print "Destroying wall %s, %s" % (self, other)
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
        #print "Destroyed wall %s, %s" % (self, other)

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
    m = Maze(40, 40)
