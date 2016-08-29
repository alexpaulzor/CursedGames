
#!/usr/bin/env python

import curses

import sys
from collections import defaultdict

class Sudoku:
  def __init__(self):
    self.grid = [ [ Square(row, col) for col in range(9) ] for row in range(9) ]
    self.sets = set()
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
    for y in range(9):
      for x in range(9):
        char = line[y * 9 + x]
        if char != "." and char != " ":
          val = int(char)
          self.grid[y][x].set_value(val, True)

  def is_solved(self):
    for s in self.sets:
      if not s.is_solved():
        return False
    for row in self.grid:
      for square in row:
        if not square.is_solved():
          return False
    return True

  def flush(self, steps=1):
    for s in self.sets:
      steps = s.flush(steps)
    for row in self.grid:
      for square in row:
        steps = square.flush(steps)

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

  def print_board(self):
    for s in self.sets:
      print s
      for sq in s.squares:
        print "  {}".format(sq)
    horiz_sep =       "#-------+-------+-------#-------+-------+-------#-------+-------+-------#"
    major_horiz_sep = "#=======+=======+=======#=======+=======+=======#=======+=======+=======#"
    board = [major_horiz_sep]
    for y in range(9):
      lines = ["# " for l in range(3)]
      for x in range(9):
        square = self.grid[y][x]
        for i in range(1, 10):
          if i in square.possible_values:
          #if i == square.get_value():
            lines[(i-1) / 3] += "{} ".format(i)
          else:
            lines[(i-1) / 3] += "  "
        for l in range(3):
          if (x+1) % 3 == 0:
            lines[l] += '# '
          else:
            lines[l] += '| '
      board += lines
      if (y+1) % 3 == 0:
        board += [major_horiz_sep]
      else:
        board += [horiz_sep]
    print "\n".join(board)

  def print_small_board(self):
    horiz_sep = "+-+-+-+-+-+-+-+-+-+"
    board = [horiz_sep]
    for y in range(9):
      line = "|"
      for x in range(9):
        square = self.grid[y][x]
        if square.get_value():
          line += "{}".format(square.get_value())
        else:
          line += " "
        line += '|'
      board += [line]
      board += [horiz_sep]
    print "\n".join(board)


  def draw_board(self):
    horiz_sep =       "#-------+-------+-------#-------+-------+-------#-------+-------+-------#"
    major_horiz_sep = "#=======+=======+=======#=======+=======+=======#=======+=======+=======#"
    blank_line      = "#       |       |       #       |       |       #       |       |       #"
    liney = 0
    self.stdscr.addstr(liney, 0, major_horiz_sep)
    liney += 1
    selected_square = self.grid[self.cursor_y][self.cursor_x]
    for y in range(9):
      linex = 0
      for line in range(3):
        self.stdscr.addstr(liney, 0, blank_line)
        linex = 1
        for x in range(9):
          square = self.grid[y][x]

          if self.cursor_x == x and self.cursor_y == y:
            self.stdscr.addstr(liney, linex, "       ", curses.color_pair(10))
          elif square.get_value() and selected_square.get_value() == square.get_value():
            self.stdscr.addstr(liney, linex, "       ", curses.color_pair(12))
          for i in range(line * 3 + 1, line * 3 + 4):
            if i in square.possible_values and not square.is_unknown():
              if square.is_given:
                self.stdscr.addstr(liney, linex, " ", curses.color_pair(11))
              self.stdscr.addstr(liney, linex + 1, "{}".format(i), curses.color_pair(i))
            linex += 2
          linex += 2
        liney += 1

      if (y+1) % 3 == 0:
        self.stdscr.addstr(liney, 0, major_horiz_sep)
      else:
        self.stdscr.addstr(liney, 0, horiz_sep)
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

    self.stdscr.refresh()


  def draw_small_board(self):
    horiz_sep = "+-+-+-+-+-+-+-+-+-+"
    #board = [horiz_sep]
    self.stdscr.addstr(0, 0, horiz_sep)
    for y in range(9):
      linex = 0
      #line = "|"
      self.stdscr.addstr(2 * y + 1, 0, "|")
      linex += 1
      for x in range(9):
        square = self.grid[y][x]
        if square.get_value():
          #line += "{}".format(square.get_value())
          self.stdscr.addstr(2 * y + 1,
                             linex,
                             "{}".format(square.get_value()),
                             curses.color_pair(square.get_value()))
          linex += 1
        else:
          #line += " "
          self.stdscr.addstr(2 * y + 1, linex, " ")
          linex += 1
        #line += '|'
        self.stdscr.addstr(2 * y + 1, linex, "|")
        linex += 1
      #board += [line]
      #board += [horiz_sep]
      self.stdscr.addstr(2 * y + 2, 0, horiz_sep)
    self.stdscr.refresh()
    #print "\n".join(board)

  def newgame(self, stdscr):
    self._init_colors()
    self.stdscr = stdscr
    self.stdscr.clear()
    self.cursor_x = 0
    self.cursor_y = 0
    self.draw_board()

    key = None
    while key != 'q' and not self.is_solved():

      key = self.stdscr.getkey()
      if key == 's':
        self.flush(1)
      elif (key == 'KEY_LEFT' or key == 'h'):
        self.cursor_x -= 1
      elif (key == 'KEY_RIGHT' or key == 'l'):
        self.cursor_x += 1
      elif (key == 'KEY_UP' or key == 'k'):
        self.cursor_y -= 1
      elif (key == 'KEY_DOWN' or key == 'j'):
        self.cursor_y += 1
      elif key in map(str, range(1, 10)):
        self.grid[self.cursor_y][self.cursor_x].toggle_mark(int(key))
      elif key == 'c':
        self.grid[self.cursor_y][self.cursor_x].clear()
      elif key == 't':
        self.grid[self.cursor_y][self.cursor_x].flush(1)
      # elif key == 't':
      #   sq = self.grid[self.cursor_y][self.cursor_x]
      #   sq.flush(2)

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

  def set_value(self, value, given=False):
    self.is_given = given
    self.possible_values = set([value])
    self.changed = True

  def rule_out_values(self, values):
    if self.is_solved():
      return False
    if any(values & self.possible_values):
      self.possible_values -= values
      self.changed = True
      return True
    return False

  def toggle_mark(self, value):
    if self.is_given:
      return
    if self.is_unknown():
      self.set_value(value)
      return
    if value in self.possible_values:
      self.rule_out_values(set([value]))
    else:
      self.possible_values.add(value)
      self.changed = True

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

  def try_solve(self):
    known_values = self.known_values()
    known_values.discard(None)
    self.eliminate_known_values(known_values)
    self._eliminate_subsets()
    self._infer_values()

    return False

  def eliminate_known_values(self, known_values):
    for s in self.squares:
      if not s.is_solved():
        s.rule_out_values(known_values)

  def _eliminate_subsets(self):
    """Find groups within a set of size n (usually 2 or 3) that all
    share the same <= n possible values.
    Subtract those values from all other squares in the set
    """
    # keys: string of ordered digits in possible_values
    # values: set of squares
    subsets = defaultdict(set)
    for sq in self.squares:
      if not sq.is_solved():
        key = ''.join(map(str, sorted(sq.possible_values)))
        subsets[key].add(sq)

    for key in subsets:
      for sq in self.squares:
        if sq.possible_values <= set(map(int, key)):
          subsets[key].add(sq)

    for key in subsets:
      # If there are as many equivalently unknown hosts as unknowns,
      # exclude that set from the rest
      if len(key) == len(subsets[key]):
        for sq in self.squares - subsets[key]:
          sq.rule_out_values(set(map(int, key)))

  def _infer_values(self):
    squares_for_value = {i: filter(lambda sq: i in sq.possible_values, self.squares) for i in range(1, 10)}
    for i in squares_for_value:
      if len(squares_for_value[i]) == 1:
        squares_for_value[i][0].set_value(i)


  def something_else(self):
    pass

    #     for v in s.possible_values:
    #       possible_values[v].add(s)

    # possible_values = {i: set() for i in (set(range(1, 10)) - known_values)}

    # for v in possible_values:
    #   if len(possible_values[v]) == 1:
    #     tuple(possible_values[v])[0].set_value(v)

    # for pset in possible_sets:
    #   for s in self.squares:
    #     if s.possible_values <= set(map(int, pset)):
    #       possible_sets[pset].add(s)

    # for pset in possible_sets:
    #   # If there are as many equivalently unknown hosts as unknowns,
    #   # exclude that set from the rest
    #   if len(pset) == len(possible_sets[pset]):
    #     for s in self.squares - possible_sets[pset]:
    #       s.rule_out_values(set(map(int, pset)))




    # return False

  def add_square(self, square):
    self.squares.add(square)
    self.add_notify(square)

  def __repr__(self):
    return "{}: {}".format(self.name, self.known_values())




if __name__ == "__main__":
  if len(sys.argv) == 2:
    s = Sudoku()
    s.load_game(sys.argv[1])
    curses.wrapper(s.newgame)
    if s.is_solved():
      print "You won!"

