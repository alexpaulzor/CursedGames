
N = 3
N_2 = N * N
N_3 = N_2 * N
N_4 = N_3 * N


class Square(object):
    def __init__(self, x, y):
        super(Square, self).__init__()
        self.name = "({},{})".format(x, y)
        self.x = x
        self.y = y
        self.id = y * N_2 + x
        self.is_given = False
        self._value = None
        self.sets = set()
        self.solved = False
        self.visited = False
        self.changed = False
        self.prevent_value(None)
        self.clear()

    def add_set(self, s):
        self.sets.add(s)

    def clear(self):
        if not self.is_given:
            self.possible_values = set(range(1, 10))
            self._value = None

    def is_solved(self):
        return len(self.possible_values) == 1

    def try_solve(self):
        if self.visited:
            return
        self.visited = True
        self.infer_values()
        for s in self.sets:
            if not s.enabled:
                continue
            s.try_solve()
        self.infer_values()
        self.visited = False

    def is_unknown(self):
        return not self._value and len(self.possible_values) == 9

    def get_value(self):
        return self._value

    def set_value(self, value, given=None):
        if given is not None:
            self.is_given = given
        self._value = value
        self.possible_values = set([value])

    def prevent_value(self, value):
        self.prevented_value = value
        self.clear()
        self.reset_values_to_attempt()

    def reset_values_to_attempt(self):
        if self.is_given:
            self.value_attempts = []
            return
        all_values = set(range(1, 10))
        self.value_attempts = list(all_values)
        # probable_values = self._inferred_possible_values()
        # improbable_values = list(all_values - probable_values)
        # ideal_values = probable_values & self.possible_values
        # probable_values -= ideal_values
        # self.value_attempts = (list(ideal_values) + list(probable_values) +
        #                        list(improbable_values))
        if self.prevented_value in self.value_attempts:
            self.value_attempts.remove(self.prevented_value)

    def prepare_for_generate(self):
        if self.get_value():
            self.set_value(self.get_value(), False)
        else:
            self.clear()
        self.reset_values_to_attempt()

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
        self.set_possible_values(self.possible_values)

    def set_possible_values(self, possible_values):
        self.possible_values = possible_values
        if self.prevented_value in self.possible_values:
            self.possible_values.remove(self.prevented_value)
        if len(self.possible_values) == 1:
            self._value = tuple(self.possible_values)[0]
        else:
            self._value = None

    def conflict_squares(self):
        sqs = set()
        if self.is_unknown():
            return sqs
        for s in self.sets:
            if not s.enabled:
                continue
            for square in s.squares:
                if not square.is_unknown() and square != self:
                    sv = square.get_value()
                    if sv and sv in self.possible_values:
                        sqs.add(square)
        return sqs

    def infer_values(self):
        if self.get_value():
            return
        self.set_possible_values(self.possible_values &
                                 self._inferred_possible_values())

    def _inferred_possible_values(self):
        possible_values = set(range(1, 10))
        for s in self.sets:
            if not s.enabled:
                continue
            for square in s.squares:
                if square != self and square.get_value() in possible_values:
                    possible_values.remove(square.get_value())
        return possible_values

    def __repr__(self):
        return "{}: {}{} !{} ?{}".format(
            self.name,
            '=' if self.is_given else '?',
            self.get_value(),
            self.prevented_value,
            self.value_attempts)


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
        return False

    def try_solve(self):
        for msg in self.try_solve_iter():
            pass

    def try_solve_iter(self, verbose=False):
        if not self.enabled or self.is_solved():
            return
        known_values = self.known_values()
        # value -> set(squares possibly that value)
        possibles = {i: set() for i in range(1, 10)}
        solved_pairs = set()
        for sq in self.squares:
            for v in sq.possible_values:
                possibles[v].add(sq)
            # naked pairs
            if len(sq.possible_values) == 2 and sq not in solved_pairs:
                for msg in self._solve_naked_pairs(sq, solved_pairs,
                                                   verbose=verbose):
                    if verbose:
                        yield msg

        for v, sqs in possibles.iteritems():
            # If there's only one square with a given possible_value, solved!
            if v not in known_values and len(sqs) == 1:
                sq = next(iter(sqs))
                sq.set_value(v)
                if verbose:
                    yield "solved unique value: {}".format(sq)

    def _solve_naked_pairs(self, sq, solved_pairs, verbose=False):
        for sq2 in self.squares - solved_pairs:
            if sq == sq2 or sq.possible_values != sq2.possible_values:
                continue
            for sq_set in (sq.sets & sq2.sets):
                for sq3 in sq_set.squares:
                    if sq3 != sq and sq3 != sq2:
                        sq3.set_possible_values(
                            sq3.possible_values - sq.possible_values)
            solved_pairs.add(sq)
            solved_pairs.add(sq2)
            if verbose:
                yield "solve naked pair {} + {}".format(sq.name, sq2.name)

        # TODO: projection: if all of the squares including possible_value i are

    def add_square(self, square):
        self.squares.add(square)
        square.add_set(self)

    def __repr__(self):
        return "{}: {}".format(self.name, self.known_values())
