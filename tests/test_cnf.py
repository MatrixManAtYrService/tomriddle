from tomriddle import cnf
from time import time
from sympy import symbols
import sympy.logic.boolalg as form
from operator import invert
from itertools import combinations

from pycosat import itersolve

from tomriddle import satbridge


def test_max_n_true():

    symbs = symbols("a,b,c,d,e")
    mapper = satbridge.SymbolMapper(symbs)

    sat_in = cnf.max_n_true(symbs, 3, mapper=mapper)
    print(sat_in)
    ways = list(itersolve(sat_in))

    # none with more than three true
    for way in ways:
        assert len(way) == len(symbs)
        true_symbs = list(filter(lambda x: x > 0, way))
        assert 3 >= len(true_symbs)
        print(true_symbs)

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

    sat_in = cnf.min_n_true(symbs, 3, mapper=mapper)
    print(sat_in)
    ways = list(itersolve(sat_in))

    # none with more than three true
    for way in ways:
        assert len(way) == len(symbs)
        true_symbs = list(filter(lambda x: x > 0, way))
        assert 3 <= len(true_symbs)
        print(true_symbs)

    # one for each subset of size 0, 1, 2, or 3
    expect_num = (
        len(list(combinations(symbs, 3)))
        + len(list(combinations(symbs, 4)))
        + 1  # the full solution
    )
    assert expect_num == len(ways)


def test_exactly_n_true():

    symbs = symbols("a,b,c,d,e")
    mapper = satbridge.SymbolMapper(symbs)

    min_constraint = cnf.min_n_true(symbs, 2, mapper=mapper)
    max_constraint = cnf.max_n_true(symbs, 2, mapper=mapper)

    solutions = list(itersolve(min_constraint + max_constraint))

    assert len(list(combinations(symbs, 2))) == len(solutions)

    for sol in solutions:
        true_only = list(filter(lambda x: x > 0, sol))
        assert 2 == len(true_only)


def dnf_equivalence(expr, symbs):

    mapper = satbridge.SymbolMapper(symbs)

    # convert with sympy
    def control(expr):
        cnf_expr = form.to_cnf(expr, simplify=True, force=True)
        sat_in = satbridge.expr_to_satfmt(cnf_expr, mapper)
        return sat_in

    # convert with something I made up
    def experiment(expr):
        return cnf.from_dnf(expr, mapper)

    def get_solns(func):

        # make expression
        before = time()
        cnf_clauses = func(expr)

        # find solutions
        solutions = []
        for sat_out in itersolve(cnf_clauses):
            true_only = list(filter(lambda x: x > 0, sat_out))
            if true_only:
                expr_out = cnf.AND(list(map(mapper.to_symb, true_only)))
                solutions.append(expr_out)

        after = time()
        return solutions, after - before

    # do they yield the same solutions?
    experiment_solns, experiment_duration = get_solns(experiment)
    control_solns, control_duration = get_solns(control)

    print("control", control_duration, "seconds")
    print("experiment", experiment_duration, "seconds")

    # this an obnoxious way to assert equality,
    # but expressions aren't hashable and order doesn't matter

    for c in control_solns:
        assert c in experiment_solns

    for e in experiment_solns:
        assert e in control_solns


def test_dnf_a():

    # which ways for every other one to be true
    symbs = symbols("a,b,c,d,e,f")
    a, b, c, d, e, f = symbs
    expr = (a & c & e) | (b & d & f)
    dnf_equivalence(expr, symbs)


def test_dnf_b():

    # how many ways for 3 of these to be true?
    symbs = symbols("a,b,c,d,e,f")
    microstates = []
    for microstate in combinations(symbs, 2):
        microstates.append(cnf.AND(microstate))
    expr = cnf.OR(microstates)

    dnf_equivalence(expr, symbs)


def test_dnf_c():

    # how many ways for 3 of these to be true?
    symbs = symbols("a,b,c,d,e,f,g")
    a, b, c, d, e, f, g = symbs
    expr = a | (b & ~c) | (a & c) | (d & ~e & ~f & g) | ~g

    dnf_equivalence(expr, symbs)


def test_bcd():

    # how many ways for 3 consecurive of these to be true?
    symbs = symbols("a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t")
    mapper = satbridge.SymbolMapper(symbs)
    a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t = symbs

    straight_expr = (a & b & c) | (b & c & d) | (c & d & e) | (d & e & f) | (g & h & i)
    straight = cnf.from_dnf(straight_expr, mapper=mapper)

    max3 = cnf.max_n_true(symbs, 3, mapper=mapper)

    sat_in = straight + max3
    solutions = list(itersolve(sat_in))

    nofalse = sorted([list(filter(lambda x: x > 0, y)) for y in solutions])
    assert 5 == len(nofalse)
    print(nofalse)
