
class Square:
  def __init__(self, x, y):
    self.x = x
    self.y = y
    self.is_given = False
    self.is_certain = False
    self.value = False
    self.possible_values = [True for i in range(9)]
    self.sets = set()

  def set_value(self, value, given = False):
    self.value = value
    self.is_given = given
    self.is_certain = True
    self.possible_values = [i == value for i in range(9)]
    for s in self.sets:
      s.notify_certain(self)


        
