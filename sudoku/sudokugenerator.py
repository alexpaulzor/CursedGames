from sudokuboard import (
    SudokuBoardSolver, N, N_4, shuffle, MIN_CLUES, UnsolvableError,
    MAX_CLUES)


class SudokuBoardGenerator(SudokuBoardSolver):
    def generate_iter(self, verbose=False):
        # generate a game
        for row in self.grid:
            for sq in row:
                sq.prepare_for_generate()
        yield self.log("gen: Computing solution...")
        # for msg in self.solve_iter(verbose=verbose):
        #     yield msg
        if not self.is_solved():
            yield "Bruteforcing from " + self.current_state()
            for msg in self.bruteforce_iter():
                yield msg
        solution = self.current_state(include_possibles=False)
        if not self.is_solved():
            yield self.log("gen: Cannot solve! " + solution)
            return

        def given_str(g):
            return (('x' if self.x_regions else '') +
                    ('m' if self.meta_regions else '') +
                    ''.join(g))

        givens = list(solution.translate(None, 'xm|'))
        givens = ['.'] * N_4 + givens[81:]
        all_squares = reduce(lambda l, row: l + row, self.grid, [])
        shuffle(all_squares)

        self.load_game(given_str(givens))
        yield self.log("gen: solution: " + solution)

        sq = None
        given_squares = set()
        while True:
            sq = all_squares.pop()
            # Pick a random square that is not uncertain
            while any(all_squares) and (sq.is_given or not sq.get_value()):
                yield self.log("gen: skipping {}".format(sq))
                new_sq = all_squares.pop()
                # if not sq.is_given:
                #     all_squares.insert(sq, 0)
                sq = new_sq
            sq_val = sq.get_value()
            if not any(all_squares) or len(given_squares) <= MIN_CLUES:
                for sq in all_squares:
                    if sq_val:
                        sq.set_value(sq_val, True)
                    givens[sq.id] = str(sq_val)
                    givens[N_4 + sq.id] = str(sq_val)
                    given_squares.add(sq)
                self.log("gen: as: {!r} gs: {!r}".format(all_squares, given_squares))
                break
            self.cursor_x = sq.x
            self.cursor_y = sq.y
            sq.prevent_value(sq_val)
            msg = 'gen: [{} togo / {} clues] trying with {} != {}'.format(
                len(all_squares), len(given_squares), str(sq), sq_val)
            yield self.log(msg)
            givens[sq.id] = '.'
            givens[N_4 + sq.id] = '.'
            yield self.log("gen: loading " + given_str(givens[:81]))
            self.load_game(given_str(givens[:81]))
            try:
                for msg in self.solve_iter():
                    yield msg
            except UnsolvableError as ue:
                yield str(ue)
            sq.prevent_value(None)
            if self.is_solved() and self.current_state(include_possibles=False) != solution:
                # can't remove this square, since it's unsolvable
                # or solvable another way without it
                given_squares.add(sq)
                msg = "gen: keeping {} ({} clues)".format(
                    sq, len(given_squares))
                yield self.log(msg)
                sq.set_value(sq_val, True)
                givens[sq.id] = str(sq_val)
                givens[N_4 + sq.id] = str(sq_val)

            else:
                # can remove this square
                sq.is_given = False
                sq.clear()
                sq.reset_values_to_attempt()
                msg = "gen: unsolvable unless {}={}, removing".format(sq, sq_val)
                yield self.log(msg)
            yield self.log("gen: loading " + given_str(givens))
            self.load_game(given_str(givens))

        self.log('gen: Done! ' + given_str(givens[:81]))
        while any(all_squares) and len(given_squares) < MAX_CLUES:
            sq = all_squares.pop()
            sq_val = sq.get_value()
            if not sq_val:
                continue
            sq.set_value(sq_val, True)
            givens[sq.id] = str(sq_val)
            givens[N_4 + sq.id] = str(sq_val)
            given_squares.add(sq)
        self.log("gen: loading " + given_str(givens[:81]))
        self.load_game(given_str(givens[:81]))
        if MIN_CLUES <= self.clues <= MAX_CLUES:
            self.write_to_generated_log()
        else:
            self.log('gen: Interrupted with {} clues'.format(
                len(given_squares)))

    def write_to_generated_log(self):
        givens = self.current_state(givens_only=True)
        self.log('saving with {} clues: {}'.format(self.clues, givens))
        with open('puzzles/generated.sudoku.txt', 'a') as f:
            f.write(givens + '\n')
