from tomriddle import cnf
from sympy import symbols
import sympy.logic.boolalg as form
from operator import invert
from itertools import combinations

from pycosat import itersolve

from tomriddle import satbridge


def test_max_n_true():

    symbs = symbols("a,b,c,d,e")
    mapper = satbridge.SymbolMapper(symbs)

    ways_expr = cnf.max_n_true(symbs, 3)
    ways_satin = satbridge.expr_to_satfmt(ways_expr, mapper)

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
    mapper = satbridge.SymbolMapper(symbs)

    ways_expr = cnf.min_n_true(symbs, 3)
    ways_satin = satbridge.expr_to_satfmt(ways_expr, mapper)

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


def dnf_equivalence(expr, symbs):

    mapper = satbridge.SymbolMapper(symbs)

    # convert with sympy
    def control(expr):
        return form.to_cnf(expr, simplify=True, force=True)

    # convert with something I made up
    experiment = cnf.from_dnf

    def get_solns(func):

        # make expression
        cnf_expr = func(expr)

        # find solutions
        solutions = []
        sat_in = satbridge.expr_to_satfmt(cnf_expr, mapper)
        for sat_out in itersolve(sat_in):
            true_only = filter(lambda x: x > 0, sat_out)
            expr_out = cnf.AND(map(mapper.to_symb, true_only))
            solutions.append(expr_out)

        return solutions

    # do they yield the same solutions?
    experiment_solns = get_solns(experiment)
    control_solns = get_solns(control)

    # this a dumb way to assert equality, but expressions aren't sortable and order doesn't matter
    for c in control_solns:
        assert c in experiment_solns

    for e in experiment_solns:
        assert e in control_solns


def test_dnf_a():

    symbs = symbols("a,b,c,d,e,f")
    a, b, c, d, e, f = symbs
    expr = (a & c & e) | (b & d & f)
    dnf_equivalence(expr, symbs)


def test_dnf_b():

    symbs = symbols("a,b,c,d,e,f,g,h,i")
    microstates = []
    for microstate in combinations(symbols("a,b,c,d,e,f,g,h,i"), 3):
        microstates.append(cnf.AND(microstate))
    expr = cnf.OR(microstates)

    dnf_equivalence(expr, symbs)