#!/usr/bin/env python

import curses

import sys
from random import shuffle, randrange
from collections import defaultdict
import itertools
import time
from solvable import Square, ExclusiveSet

class Sudoku:
  def __init__(self):
    self.grid = [ [ Square(row, col) for col in range(9) ] for row in range(9) ]
    self.sets = set()
    self.draw_small = False
    self.log = []
    self.cursor_x = 0
    self.cursor_y = 0
    self.go_forward = True
    self.build_rows()
    self.build_columns()
    self.build_sectors()

  def help(self):
    self.log += list(reversed([
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
      "w: write current state",
      "g: generate board (sloooow)"
    ]))
    self.draw_board()

  def load_game(self, line):
    """
      line is an 81-character representation of the board where given values are 1-9 and spaces are .
      optionally with another 81 characters representing a solution or partial solution.
    """
    if not line:
      line = '.' * 81
    if len(line) not in (81, 2 * 81):
      print "Invalid line!"
      sys.exit(1)
    self.clues = 0
    self.log.append('load: ' + line)
    for y in range(9):
      for x in range(9):
        char = line[y * 9 + x]
        if char != "." and char != " ":
          val = int(char)
          self.grid[y][x].set_value(val, given=True)
          self.clues += 1
        elif len(line) == 2 * 81:
          char = line[81 + y * 9 + x]
          if char != "." and char != " ":
            val = int(char)
            self.grid[y][x].set_value(val, given=False)
        else:
          self.grid[y][x].clear()
    self.original_state = line
    self.steps = 0

  def generate(self, clues=20):
    # generate a game

    # clear the board
    # self.load_game(None)

    # solve
    solution = self.compute_solution()
    if not solution:
      self.log.append("Cannot solve! " + self.current_state())
      return
    givens = list(solution)
    all_squares = reduce(lambda l, row: l + row, self.grid, [])
    #shuffle(all_squares)
    self.load_game(''.join(givens))
    self.draw_board()
    sq = all_squares.pop()
    key = -1
    while key == -1:
      # Pick a random square that is not uncertain
      while any(all_squares) and (sq.is_given or not sq.get_value()):
        sq = all_squares.pop()
      if sq.is_given or not sq.get_value():
        self.log.append('No more squares to try')
        break
      self.cursor_x = sq.x
      self.cursor_y = sq.y
      sq_val = sq.get_value()
      sq.prevent_value(sq_val)
      self.log.append('generate trying without: ' + str(sq))
      self.draw_board()
      givens[9 * sq.y + sq.x] = '.'
      givens[81 + 9 * sq.y + sq.x] = '.'
      self.stdscr.nodelay(True)
      key = self.stdscr.getch()
      new_solution = self.compute_solution(''.join(givens[81:]))

      sq.prevent_value(None)

      if new_solution and new_solution != solution:
        # can't remove this square, since it's unsolvable or solvable another
        # way without it
        sq.set_value(sq_val, True)
        givens[9 * sq.y + sq.x] = str(sq_val)
        givens[81 + 9 * sq.y + sq.x] = str(sq_val)
      else:
        # can remove this square
        self.log.append("removing {}".format(sq))
        # #self.log.append(givens)
        # givens[9 * sq.y + sq.x] = '.'
        # givens[81 + 9 * sq.y + sq.x] = '.'
        #self.log.append(givens)
      self.load_game(''.join(givens))
    self.load_game(''.join(givens))
    self.stdscr.nodelay(False)
    self.draw_board()

  def compute_solution(self, initial_state=None):
    backup_state = self.current_state()
    direction = self.go_forward
    if initial_state is not None:
      self.load_game(initial_state)
    self.go_forward = True
    self.solve(None)
    if self.is_solved():
      solution = self.current_state()
      self.draw_board()
    else:
      solution = None
    self.load_game(backup_state)
    self.go_forward = direction
    return solution

  def current_state(self, givens_only=False):
    # return the state of the board as would be loaded
    line = ''
    for y in range(9):
      for x in range(9):
        sq = self.grid[y][x]
        if sq.get_value() and sq.is_given:
          line += str(sq.get_value())
        else:
          line += '.'
    if givens_only:
      return line
    for y in range(9):
      for x in range(9):
        sq = self.grid[y][x]
        if sq.get_value():
          line += str(sq.get_value())
        else:
          line += '.'
    #self.log.append('snapshot: ' + line)
    return line

  def is_solved(self):
    for s in self.sets:
      if not s.is_solved():
        return False
    for row in self.grid:
      for square in row:
        if not square.is_solved():
          return False
    return True

  def solve(self, steps=1):
    end_square = self.grid[self.cursor_y][self.cursor_x]
    while end_square.is_given:
      self.select_prev_square()
      end_square = self.grid[self.cursor_y][self.cursor_x]
    end_square.clear()
    end_square.reset_values_to_attempt()
    square = end_square
    self.log.append("s {} {} from {}: {}".format(self.go_forward, square, end_square, self.current_state()))
    key = -1
    while key == -1 and (steps is None or steps > 0) and not self.is_solved() and any(end_square.value_attempts):
      self.stdscr.nodelay(True)
      key = self.stdscr.getch()
      self.steps += 1
      if steps:
        steps -= 1

      if not square.is_given:
        if not square.get_value() and any(square.value_attempts):
          square.clear()
          square.set_value(square.value_attempts.pop())
          self.go_forward = True
        if not self.go_forward:
          if any(square.value_attempts):
            square.set_value(square.value_attempts.pop())
            self.go_forward = True
        while self.go_forward and not self.check_solution():
          #self.log.append("{} solving {}".format(self.go_forward, square))
          if not any(square.value_attempts):
            self.go_forward = False
          else:
            square.set_value(square.value_attempts.pop())

      if self.go_forward:
        self.select_next_square()
      else:
        square.clear()
        if square != end_square:
          square.reset_values_to_attempt()
          self.select_prev_square()

      if self.steps % 10000 == 0:
        self.log.append("s {} {} from {}: {}".format(self.go_forward, square, end_square, self.current_state()))
        self.draw_board()

      square = self.grid[self.cursor_y][self.cursor_x]
    self.stdscr.nodelay(False)

  def select_next_square(self):
    # advance
    if self.cursor_x == 8:
      self.cursor_y += 1
      self.cursor_x = 0
      if self.cursor_y == 9:
        self.cursor_y = 0
    else:
      self.cursor_x += 1
    #self.draw_board()

  def select_prev_square(self):
    # go back
    if self.cursor_x > 0:
      self.cursor_x -= 1
    elif self.cursor_y > 0:
      self.cursor_y -= 1
      self.cursor_x = 8
    else:
      # back at 0,0
      self.cursor_x = 8
      self.cursor_y = 8


  def check_solution(self):
    for y in range(9):
      # check column y
      values = filter(None, [self.grid[y][i].get_value() for i in range(9)])
      if len(values) != len(set(values)):
        #self.log.append("row {} invalid: {}".format(y, str(sorted(values))))
        return False
      for x in range(9):
        # check row
        values = filter(None, [self.grid[i][x].get_value() for i in range(9)])
        if len(values) != len(set(values)):
          #self.log.append("col {} invalid: {}".format(x, str(sorted(values))))
          return False
    # check 3x3 grids
    for qy in range(3):
      for qx in range(3):
        #self.log.append("grid {},{}: {}".format(qy, qx, ["{},{}".format(3 * qy + i % 3, 3 * qx + i / 3) for i in range(9)]))
        values = filter(None, [self.grid[3 * qy + i % 3][3 * qx + i / 3].get_value() for i in range(9)])
        if len(values) != len(set(values)):
          #self.log.append("grid {},{} invalid: {}".format(qy, qx, str(sorted(values))))
          return False
    #self.log.append('valid')
    return True

  def build_rows(self):
    for y in range(9):
      row = ExclusiveSet("row_{}".format(y))
      for x in range(9):
        row.add_square(self.grid[y][x])
      self.sets.add(row)

  def build_columns(self):
    for x in range(9):
      column = ExclusiveSet("col_{}".format(x))
      for y in range(9):
        column.add_square(self.grid[y][x])
      self.sets.add(column)

  def build_sectors(self):
    for i in range(3):
      for j in range(3):
        sector = ExclusiveSet("sector_{},{}".format(j, i))
        for y in range(3 * i, 3 * i + 3):
          for x in range(3 * j, 3 * j + 3):
            sector.add_square(self.grid[y][x])
        self.sets.add(sector)

  def draw_board(self):
    if self.draw_small:
      horiz_sep =       "#---+---+---#---+---+---#---+---+---#"
      major_horiz_sep = "#===+===+===#===+===+===#===+===+===#"
      blank_line      = "#   |   |   #   |   |   #   |   |   #"
      value_width = 3
    else:
      horiz_sep =       "#-------+-------+-------#-------+-------+-------#-------+-------+-------#"
      major_horiz_sep = "#=======+=======+=======#=======+=======+=======#=======+=======+=======#"
      blank_line      = "#       |       |       #       |       |       #       |       |       #"
      value_width = 7
    liney = 0
    self.stdscr.addstr(liney, 0, major_horiz_sep, curses.A_DIM)
    liney += 1
    selected_square = self.grid[self.cursor_y][self.cursor_x]
    conflicts = selected_square.conflict_squares()
    for y in range(9):
      linex = 0
      for line in range(1 if self.draw_small else 3):
        self.stdscr.addstr(liney, 0, blank_line, curses.A_DIM)
        linex = 1
        for x in range(9):
          square = self.grid[y][x]

          if self.cursor_x == x and self.cursor_y == y:
            self.stdscr.addstr(liney, linex, " " * value_width, curses.color_pair(10))
          elif not selected_square.is_unknown() and square in conflicts:
            self.stdscr.addstr(liney, linex, " " * value_width, curses.color_pair(13))
          elif square.get_value() and selected_square.get_value() == square.get_value():
            self.stdscr.addstr(liney, linex, " " * value_width, curses.color_pair(12))
          if self.draw_small:
            rng = [square.get_value()]
          else:
            rng = range(line * 3 + 1, line * 3 + 4)
          for i in rng:
            attributes = curses.A_UNDERLINE if square.is_given else 0
            if i and (i == square.get_value() or (not self.draw_small and
                i in square.possible_values and not square.is_unknown())):

              self.stdscr.addstr(liney, linex + 1, "{}".format(i), curses.color_pair(i)|attributes)
            if not self.draw_small:
              linex += 2
          linex += 2
          if self.draw_small:
              linex += 2
        liney += 1

      if (y+1) % 3 == 0:
        self.stdscr.addstr(liney, 0, major_horiz_sep, curses.A_DIM)
      else:
        self.stdscr.addstr(liney, 0, horiz_sep, curses.A_DIM)
      liney += 1

    value_counts = {i: 0 for i in range(1, 10)}
    for row in self.grid:
      for sq in row:
        v = sq.get_value()
        if v is not None:
          value_counts[v] += 1

    for i in range(1, 10):
      self.stdscr.addstr(i, 9 * 9, str(i), curses.color_pair(i))
      self.stdscr.addstr(i,
                         9 * 9 + 1,
                         ": {}         ".format(value_counts[i]),
                         curses.color_pair(12 if value_counts[i] == 9 else 0))
    self.stdscr.addstr(10, 9 * 9, "Steps: {}".format(self.steps))

    i = 0
    height, width = self.stdscr.getmaxyx()
    while 12 + i < height - 1 and len(self.log) > i:
      line = str(self.log[-1 - i])
      if len(line) < width - 9 * 9:
        line += ' ' * (width - 9 * 9 - len(line))
      self.stdscr.addstr(12 + i, 9 * 9, line[:(width - 9 * 9)])
      i += 1

    self.stdscr.refresh()


  def newgame(self, stdscr):
    self._init_colors()
    self.stdscr = stdscr
    self.stdscr.clear()
    self.draw_board()
    self.draw_small = False
    self.help()

    key = None
    while key != 'q' and not self.is_solved():

      try:
        key = self.stdscr.getkey()
        self.steps += 1
      except:
        # screen was resized or something
        key = None

      if (key == 'KEY_LEFT' or key == 'h'):
        self.cursor_x -= 1
      elif (key == 'KEY_RIGHT' or key == 'l'):
        self.cursor_x += 1
      elif (key == 'KEY_UP' or key == 'k'):
        self.cursor_y -= 1
      elif (key == 'KEY_DOWN' or key == 'j'):
        self.cursor_y += 1
      elif key in map(str, range(1, 10)):
        if self.draw_small:
          self.grid[self.cursor_y][self.cursor_x].clear()
        self.grid[self.cursor_y][self.cursor_x].toggle_mark(int(key))
      elif key == 'c':
        self.grid[self.cursor_y][self.cursor_x].clear()
      elif key == 's':
        self.draw_small = not self.draw_small
        self.stdscr.clear()
      elif key == 'a':
        self.solve()
      elif key == 'A':
        self.solve(None)
      elif key == 'R':
        self.load_game(self.original_state)
        self.load_game(self.current_state(True))
      elif key == 'f':
        self.grid[self.cursor_y][self.cursor_x].infer_values()
      elif key == 'F':
        for row in self.grid:
          for square in row:
            square.infer_values()
      elif key == 'w':  # write
        self.log.append(self.current_state())
      elif key == 'g':  # generate
        self.generate()
      elif key == 'H':
        self.help()

      self.cursor_x = self.cursor_x % 9
      self.cursor_y = self.cursor_y % 9
      self.draw_board()
    self.draw_board()
    time.sleep(3)

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
    curses.init_pair(10, curses.COLOR_WHITE, curses.COLOR_GREEN)
    curses.init_pair(11, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(12, curses.COLOR_BLACK, curses.COLOR_CYAN)
    curses.init_pair(13, curses.COLOR_BLACK, curses.COLOR_RED)


if __name__ == "__main__":
  s = Sudoku()
  game = sys.argv[1] if len(sys.argv) == 2 else None
  s.load_game(game)
  try:
    curses.wrapper(s.newgame)
  finally:
    print "\n".join(s.log)
    print s.original_state
    print s.current_state()
    if s.is_solved():
      print "You won!"
    print "({} clues, {} steps)".format(s.clues, s.steps)


