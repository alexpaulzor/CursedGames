#!/usr/bin/env python

import curses

import sys
from collections import defaultdict

class Sudoku:
  def __init__(self):
    self.grid = [ [ Square(row, col) for col in range(9) ] for row in range(9) ]
    self.sets = set()
    self.draw_small = False
    self.log = list(reversed([
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
      "w: write current state"
    ]))
    self.cursor_x = 0
    self.cursor_y = 0
    self.go_forward = True
    self.build_rows()
    self.build_columns()
    self.build_sectors()


  def load_game(self, line):
    """
      line is an 81-character representation of the board where given values are 1-9 and spaces are .
    """
    if len(line) != 81:
      print "Invalid line!"
      sys.exit(1)
    self.clues = 0

    for y in range(9):
      for x in range(9):
        char = line[y * 9 + x]
        if char != "." and char != " ":
          val = int(char)
          self.grid[y][x].set_value(val, True)
          self.clues += 1
        else:
          self.grid[y][x].clear()
    self.original_state = line
    self.steps = 0

  def current_state(self):
    # return the state of the board as would be loaded
    line = ''
    for y in range(9):
      for x in range(9):
        sq = self.grid[y][x]
        if sq.get_value():
          line += str(sq.get_value())
        else:
          line += '.'
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
    while self.cursor_y < 9 and self.cursor_x < 9 and steps > 0:
      self.steps += 1
      steps -= 1
      square = self.grid[self.cursor_y][self.cursor_x]
      #self.log.append("{} solving {}".format(self.go_forward, square))
      if not square.is_given:
        if not square.get_value():
          square.set_value(1)
          self.go_forward = True
        if not self.go_forward:
          if square.get_value() < 9:
            square.set_value(square.get_value() + 1)
            self.go_forward = True
          else:
            square.clear()
        while self.go_forward and not self.check_solution():
          #self.log.append("{} solving {}".format(self.go_forward, square))
          if square.get_value() == 9:
            square.clear()
            self.go_forward = False
          else:
            square.set_value(square.get_value() + 1)

      if self.go_forward:
        # advance
        if self.cursor_x == 8:
          self.cursor_y += 1
          self.cursor_x = 0
          if self.cursor_y == 9:
            self.cursor_y = 0
        else:
          self.cursor_x += 1
      else:
        # go back
        if self.cursor_x > 0:
          self.cursor_x -= 1
        elif self.cursor_y > 0:
          self.cursor_y -= 1
          self.cursor_x = 8
        else:
          # back at 0,0
          #self.go_forward = True
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
    while 12 + i < height and len(self.log) > i:
      self.stdscr.addstr(12 + i, 9 * 9, str(self.log[-1 - i]) + " " * 10)
      i += 1

    self.stdscr.refresh()


  def newgame(self, stdscr):
    self._init_colors()
    self.stdscr = stdscr
    self.stdscr.clear()
    self.draw_board()
    self.draw_small = False

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
        self.stdscr.nodelay(True)
        key = -1
        while not self.is_solved() and key == -1:
          key = self.stdscr.getch()
          self.solve(200)
          self.draw_board()
        self.stdscr.nodelay(False)
      elif key == 'R':
        self.load_game(self.original_state)
      elif key == 'f':
        self.grid[self.cursor_y][self.cursor_x].infer_values()
      elif key == 'F':
        for row in self.grid:
          for square in row:
            square.infer_values()
      elif key == 'w':
        self.log.append(self.current_state())

      self.cursor_x = self.cursor_x % 9
      self.cursor_y = self.cursor_y % 9
      self.draw_board()
    self.draw_board()

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

class Solvable(object):
  """Solvable handles the notification of dependent exclusivity sets.
  """

  def is_solved(self):
    """Override to compute if the requirement is satisfied"""
    return True

  def try_solve(self):
    """Override me"""
    pass

  def __init__(self):
    self.notifies = set()
    self.solved = False
    self.visited = False
    self.changed = False

  def flush(self, steps=1):
    if steps <= 0:
      return 0
    self.try_solve()
    if self.solved != self.is_solved():
      self.changed = True
      self.solved = self.is_solved()

    if self.changed:
      self.changed = False
      for solvable in self.notifies:
        steps = solvable.flush(steps - 1)
    return steps

  def add_notify(self, solvable):
    if solvable not in self.notifies:
      self.notifies.add(solvable)
      solvable.add_notify(self)


class Square(Solvable):
  def __init__(self, row, col):
    super(Square, self).__init__()
    self.name = "({},{})".format(row, col)
    self.is_given = False
    self.possible_values = set(range(1, 10))

  def clear(self):
    if not self.is_given:
      self.possible_values = set(range(1, 10))
      self.changed = True

  def is_solved(self):
    return len(self.possible_values) == 1

  def try_solve(self):
    for n in self.notifies:
      n.try_solve()

  def is_unknown(self):
    return len(self.possible_values) == 9

  def get_value(self):
    if not self.is_solved():
      return None
    return tuple(self.possible_values)[0]

  def set_value(self, value, given=None):
    if given is not None:
      self.is_given = given
    self.possible_values = set([value])

  def toggle_mark(self, value):
    if self.is_given:
      return
    if self.is_unknown():
      self.set_value(value)
      return
    if value in self.possible_values:
      self.possible_values.remove(value)
      if not any(self.possible_values):
        self.clear()
    else:
      self.possible_values.add(value)

  def conflict_squares(self):
    sqs = set()
    if self.is_unknown():
      return sqs
    for notify in self.notifies:
      for square in notify.squares:
        if not square.is_unknown() and square != self:
          if square.get_value() and square.get_value() in self.possible_values:
            sqs.add(square)
          elif self.get_value() and self.get_value() in square.possible_values:
            sqs.add(square)
    return sqs

  def infer_values(self):
    if self.get_value():
      return
    self.clear()
    for notify in self.notifies:
      for square in notify.squares:
        if square != self and square.get_value() in self.possible_values:
          self.possible_values.remove(square.get_value())

  def __repr__(self):
    return "{}: {}->{}".format(self.name, self.possible_values, self.get_value())

class ExclusiveSet(Solvable):
  """A collection of exactly 9 squares"""
  def __init__(self, name):
    super(ExclusiveSet, self).__init__()
    self.name = name
    self.squares = set()

  def known_values(self):
    return set(map(lambda s: s.get_value(), self.squares))

  def is_solved(self):
    if self.solved:
      return True
    known_values = self.known_values()
    if len(known_values) == len(self.squares) and None not in known_values:
      return True

  def add_square(self, square):
    self.squares.add(square)
    self.add_notify(square)

  def __repr__(self):
    return "{}: {}".format(self.name, self.known_values())


if __name__ == "__main__":
  if len(sys.argv) == 2:
    s = Sudoku()
    s.load_game(sys.argv[1])
    try:
      curses.wrapper(s.newgame)
    finally:
      print "\n".join(s.log)
      print s.original_state
      print s.current_state()
      if s.is_solved():
        print "You won!"
      print "({} clues, {} steps)".format(s.clues, s.steps)


