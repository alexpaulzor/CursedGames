
import sys
from square import Square
from sudokuset import Set

class Sudoku:
  def __init__(self):
    self.build_grid()
    self.sets = set()

  def build_grid(self):
    self.squares = {}
    for y in range(9):
      self.squares[y] = {}
      for x in range(9):
        self.squares[y][x] = Square(x, y)

  def load_game(self, line):
    """
      line is an 81-character representation of the board where given values are 1-9 and spaces are .
    """
    if len(line) != 81:
      print "Invalid line!"
      sys.exit(1)
    for y in self.squares:
      for x in self.squares[y]:
        char = line[y * 9 + x]
        if char != "." and char != " ":
          val = int(char) - 1
          self.squares[y][x].set_value(val, True)

  def build_sets(self):
    self.build_rows()
    self.build_columns()
    self.build_sectors()

  def build_rows(self):
    for y in self.squares:
      row = Set()
      for x in self.squares[y]:
        row.add_square(self.squares[y][x])
      self.sets.add(row)

  def build_columns(self):
    for x in range(9):
      column = Set()
      for y in range(9):
        column.add_square(self.squares[y][x])
      self.sets.add(column)

  def build_sectors(self):
    for i in range(3):
      for j in range(3):
        sector = Set()
        for y in range(3 * i, 3 * i + 3):
          for x in range(3 * j, 3 * j + 3):
            sector.add_square(self.squares[y][x])
        self.sets.add(sector)

  def print_board(self):
    for y in self.squares:
      if y % 3 == 0:
        print '=' * (9 * 3 + 8)
      row = ""
      for x in self.squares[y]:
        if x % 3 == 0:
          row += "||"
        if self.squares[y][x].is_certain:
          row += " %d " % (self.squares[y][x].value + 1)
        else:
          row += "   "
      row += "||"
      print row
    print '=' * (9 * 3 + 4)




if __name__ == "__main__":
  if len(sys.argv) == 2:
    s = Sudoku()
    s.load_game(sys.argv[1])
    s.build_sets()
    s.print_board()
  
