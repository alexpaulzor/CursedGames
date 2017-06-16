
# The Plan

Alright, let's try this thing again. This time with at least a tiny bit of design prep.

* I will use much of the existing display bits for the curses models and rendering
  * Squares should be able to draw themselves (and two of their borders).
* A new core concept: SudokuBoardState.
    * Represents the whole board
        * `[(possible value bitmask, is_given) for square in grid]`
        * Can also maintain a linked-list-like pointer to its previous state,
          in order to traverse backwards and forwards through moves.
            * This should enable teasing out of testcases
* The solver can then operate as functions with a `SudokuBoardState` as a param, and return a new `SudokuBoardState`.
    * Different board styles (x, meta, and eventually squiggly) can extend the
* The generator can utilize solver functions in sequence to construct linked chains of moves
* Bonus: support squiggly puzzles
* Document O() runtime for solver techniques
