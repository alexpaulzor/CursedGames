# class Solvable(object):
#   """Solvable handles the notification of dependent exclusivity sets.
#   """

#   def is_solved(self):
#     """Override to compute if the requirement is satisfied"""
#     return True

#   def try_solve(self):
#     """Override me"""
#     pass

#   def __init__(self):
#     self.notifies = set()
#     self.solved = False
#     self.visited = False
#     self.changed = False

#   def flush(self, steps=1):
#     if steps <= 0:
#       return 0
#     self.try_solve()
#     if self.solved != self.is_solved():
#       self.changed = True
#       self.solved = self.is_solved()

#     if self.changed:
#       self.changed = False
#       for solvable in self.notifies:
#         steps = solvable.flush(steps - 1)
#     return steps

#   def add_notify(self, solvable):
#     if solvable not in self.notifies:
#       self.notifies.add(solvable)
#       solvable.add_notify(self)
import sys
from random import shuffle, randrange
from collections import defaultdict
import itertools
import time

class Square(object):
  def __init__(self, row, col):
    super(Square, self).__init__()
    self.name = "({},{})".format(row, col)
    self.x = col
    self.y = row
    self.is_given = False
    self.sets = set()
    self.solved = False
    self.visited = False
    self.changed = False
    self.prevent_value(None)
    self.clear()

  def add_set(self, set):
    self.sets.add(set)

  def clear(self):
    if not self.is_given:
      self.possible_values = set(range(1, 10))

  def is_solved(self):
    return len(self.possible_values) == 1

  def try_solve(self):
    if self.visited:
      return
    self.visited = True
    self.infer_values()
    for s in self.sets:
      s.try_solve()
    self.infer_values()
    self.visited = False

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
    if self.is_given:
      self.reset_values_to_attempt()

  def prevent_value(self, value):
    self.prevented_value = value
    self.clear()
    self.reset_values_to_attempt()

  def reset_values_to_attempt(self):
    if self.is_given:
      self.value_attempts = []
      return
    self.value_attempts = range(1, 10)
    if self.prevented_value in self.value_attempts:
      self.value_attempts.remove(self.prevented_value)
    shuffle(self.value_attempts)

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
    for s in self.sets:
      for square in s.squares:
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
    for s in self.sets:
      for square in s.squares:
        if square != self and square.get_value() in self.possible_values:
          self.possible_values.remove(square.get_value())

  def __repr__(self):
    return "{}: {}{} !{} ?{}".format(self.name, '=' if self.is_given else '?',
      self.get_value(), self.prevented_value, self.value_attempts)

class ExclusiveSet(object):
  """A collection of exactly 9 squares"""
  def __init__(self, name, enabled=True):
    super(ExclusiveSet, self).__init__()
    self.name = name
    self.squares = set()
    self.solved = False
    self.visited = False
    self.changed = False
    self.enabled = enabled

  def set_enabled(self, enabled):
    self.enabled = enabled

  def known_values(self):
    if not self.enabled:
      return set()
    return set(map(lambda s: s.get_value(), self.squares))

  def is_solved(self):
    if self.solved or not self.enabled:
      return True
    known_values = self.known_values()
    if len(known_values) == len(self.squares) and None not in known_values:
      return True

  def try_solve(self):
    pass
    # if self.visited:
    #   return
    # self.visited = True

  def add_square(self, square):
    self.squares.add(square)
    square.add_set(self)

  def __repr__(self):
    return "{}: {}".format(self.name, self.known_values())
