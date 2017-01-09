# flake8: noqa: E231, E265, E501
from sudoku.solvable import ExclusiveSet, Square
from pprint import pprint

# HARD_TEST_BOARD =     '.1795......5..1.3.3.....8...6..1..94.........92..7..5...6.....3.3.5..9......3647.'
# FIENDISH_TEST_BOARD = '...6..142.26......7....4..9.....62...6.9.1.5...53.....9..4....7......81.842..7...'


def test_set_sol():
    pass


def test_hidden_pair():
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

    _test_solve_iter(START_PVS, EXPECTED_PVS)

def _test_solve_iter(start_pvs, expected_pvs):
    sector_set = ExclusiveSet("sector_2x2")
    pvs = iter(start_pvs)
    squares = []
    for y in range(9):
        sq = Square(0, y)
        sq.set_possible_values(set(next(pvs)))
        squares.append(sq)
        sector_set.add_square(sq)

    pprint(squares)

    for msg in sector_set.try_solve_iter(verbose=True):
        pprint(msg)

    pprint(squares)

    expected_pvs_it = iter(expected_pvs)
    for y in range(9):
        pprint(squares[y])
        assert squares[y].possible_values == set(next(expected_pvs_it))


def test_hidden_pair_2():
    # From:
    #   2   |       |     3 #       | 1     |     3 #       |     3 |       #
    #       | 4 5 6 |   5   #       |       | 4     #       |   5 6 |       # I
    #       |       |       # 7     |       |       #   8   |       |     9 #
    # To:
    #   2   |       |     3 #       | 1     |     3 #       |     3 |       #
    #       | 4 5 6 |   5   #       |       | 4     #       |   5   |       # I
    #       |       |       # 7     |       |       #   8   |       |     9 #
    START_PVS = [(2,), (4,5,6), (3,5), (7,), (1,), (3,4), (8,), (3,5,6), (9,)]
    EXP_PVS =   [(2,), (4,5,6), (3,5), (7,), (1,), (3,4), (8,), (3,5),   (9,)]
    _test_solve_iter(START_PVS, EXP_PVS)

def test_triple():
    # From:
    #   2 3 |       |     3 #   2   |       |   2   #   2   | 1 2   | 1 2   #
    #       |     6 |   5   # 4     |       | 4     #       | 4 5   | 4 5   #
    #     9 |       |     9 # 7     |   8   | 7     # 7     | 7   9 |     9 #
    # To:
    #     3 |       |     3 #   2   |       |   2   #   2   | 1     | 1     #
    #       |     6 |   5   # 4     |       | 4     #       |   5   |   5   #
    #     9 |       |     9 # 7     |   8   | 7     # 7     |     9 |     9 #
    pass
