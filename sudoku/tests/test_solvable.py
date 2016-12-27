# flake8: noqa: E231, E265, E501
from sudoku.solvable import ExclusiveSet, Square
from pprint import pprint

# HARD_TEST_BOARD =     '.1795......5..1.3.3.....8...6..1..94.........92..7..5...6.....3.3.5..9......3647.'
# FIENDISH_TEST_BOARD = '...6..142.26......7....4..9.....62...6.9.1.5...53.....9..4....7......81.842..7...'


def test_set_sol():
    pass


def test_group_values():
    # From:
    ##=======+=======+=======#
    ## 1 2 3 |     3 |     3 #
    ## 4     | 4     | 4     # A
    ## 7     | 7     | 7     #
    ##-------+-------+-------#
    ##       |     3 |     3 #
    ##       | 4   6 | 4   6 # B
    ##   8   |       |       #
    ##-------+-------+-------#
    ## 1 2   |       |       #
    ## 4   6 |       |   5   # C
    ## 7     |     9 |       #
    ##=======+=======+=======#
    #    0       1       2

    # To:
    ##=======+=======+=======#
    ## 1 2   |     3 |     3 #
    ##       | 4     | 4     # A
    ##       | 7     | 7     #
    ##-------+-------+-------#
    ##       |     3 |     3 #
    ##       | 4   6 | 4   6 # B
    ##   8   |       |       #
    ##-------+-------+-------#
    ## 1 2   |       |       #
    ##       |       |   5   # C
    ##       |     9 |       #
    ##=======+=======+=======#
    #    0       1       2

    START_PVS = [(1,2,3,4,7), (3,4,7), (3,4,7),
                 (8,),        (3,4,6), (3,4,6),
                 (1,2,4,6,7), (9,),    (5,)]

    EXPECTED_PVS = [(1,2), (3,4,7), (3,4,7),
                    (8,),  (3,4,6), (3,4,6),
                    (1,2), (9,),    (5,)]

    sector_set = ExclusiveSet("sector_2x2")
    pvs = iter(START_PVS)
    squares = []
    for y in range(3):
        row = []
        for x in range(3):
            sq = Square(x, y)
            sq.set_possible_values(set(next(pvs)))
            row.append(sq)
            sector_set.add_square(sq)
        squares.append(row)

    pprint(squares)

    for msg in sector_set.try_solve_iter(verbose=True):
        pprint(msg)

    pprint(squares)

    expected_pvs = iter(EXPECTED_PVS)
    for y in range(3):
        for x in range(3):
            pprint(squares[y][x])
            assert squares[y][x].possible_values == set(next(expected_pvs))
