from tomriddle import cnf
from sympy import symbols
from operator import invert
from itertools import combinations

from pycosat import itersolve

from tomriddle import satbridge


def test_max_n_true():

    symbs = symbols("a,b,c,d,e")
    ways_expr = cnf.max_n_true(symbs, 3)
    ways_satin = satbridge.expr_to_satfmt(ways_expr, symbs)

    ways = list(itersolve(ways_satin))

    # none with more than three true
    for way in ways:
        assert len(way) == len(symbs)
        true_symbs = list(filter(lambda x: x > 0, way))
        assert 3 >= len(true_symbs)

    # one for each subset of size 0, 1, 2, or 3
    expect_num = (
        len(list(combinations(symbs, 3)))
        + len(list(combinations(symbs, 2)))
        + len(list(combinations(symbs, 1)))
        + 1  # the empty solution
    )
    assert expect_num == len(ways)


def test_min_n_true():

    symbs = symbols("a,b,c,d,e")
    ways_expr = cnf.min_n_true(symbs, 3)
    ways_satin = satbridge.expr_to_satfmt(ways_expr, symbs)

    ways = list(itersolve(ways_satin))

    # none with more than three true
    for way in ways:
        assert len(way) == len(symbs)
        true_symbs = list(filter(lambda x: x > 0, way))
        assert 3 <= len(true_symbs)

    # one for each subset of size 0, 1, 2, or 3
    expect_num = (
        len(list(combinations(symbs, 3)))
        + len(list(combinations(symbs, 4)))
        + 1  # the full solution
    )
    assert expect_num == len(ways)
