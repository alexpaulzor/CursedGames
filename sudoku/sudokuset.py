

class Set:
  def __init__(self):
    self.squares = set()
    self.is_solved = False
    # TODO: do we want values?
    self.values = dict(zip(range(0, 9), [False for i in range(0, 9)]))
    self.num_unknown_values = 9

  def notify_certain(self, square):
    if not self.values[square.value]:
      self.values[square.value] = square
      self.num_unknown_values -= 1
      self.try_infer_remaining()

  def try_infer_remaining(self):
    if self.num_unknown_values == 1:
      unknown_squares = self.squares.copy()
      missing_value = False
      for i in self.values:
        if self.values[i]:
          unknown_squares.remove(self.values[i])
        else:
          missing_value = i
      if len(unknown_squares) == 1:
        square = unknown_squares.pop()
        square.set_value(missing_value)
        self.solved = True

  def add_square(self, square):
    self.squares.add(square)
    square.sets.add(self)
    if square.is_certain:
      self.notify_certain(square)


    
