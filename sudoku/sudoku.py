
#!/usr/bin/env python

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

  def flush(self):
    for s in self.sets:
      s.flush()
    for row in self.grid:
      for square in row:
        square.flush()

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


class Solvable(object):
  """Solvable handles the notification of dependent exclusivity sets.
  """

  def is_solved(self):
    """Override to compute if the requirement is satisfied"""
    return True

  def __init__(self):
    self.notifies = set()
    self.solved = False
    self.visited = False
    self.changed = False

  def flush(self):
    if self.solved != self.is_solved():
      self.changed = True
      self.solved = self.is_solved()

    if self.changed:
      self.changed = False
      for solvable in self.notifies:
        solvable.flush()

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

  def is_solved(self):
    return len(self.possible_values) == 1

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
    known_values.discard(None)
    self._eliminate_known_values(known_values)
    self._eliminate_subsets()
    self._infer_values()

    return False

  def _eliminate_known_values(self, known_values):
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
    s.print_board()
    while not s.is_solved():
      sys.stdin.readline()
      s.flush()
      s.print_board()

