from itertools import product, combinations
from functools import reduce
import operator
import sympy.logic.boolalg as form


def AND(symbols):
    return reduce(operator.and_, symbols)


def OR(symbols, convert=False):

    if convert:
        # this will be slow for many clauses
        # https://cs.stackexchange.com/a/41071/97082
        return form.to_cnf(reduce(operator.or_, symbols), simplify=True, force=True)
    else:
        return reduce(operator.or_, symbols)


def max_n_true(symbols, n):
    """
    Takes an iterable of symbles, returns a CNF clause which allows
    at most n of them to be true at once.
    """

    clauses = []
    for microstate in combinations(symbols, n + 1):
        clause = OR(map(operator.invert, microstate))
        clauses.append(clause)
    expr = AND(clauses)
    return expr


def min_n_true(symbols, n):
    """
    Takes an iterable of symbles, returns a CNF clause which requires
    n of them to be true at once.
    """

    clauses = []
    for microstate in combinations(symbols, n):
        clause = OR(microstate)
        clauses.append(clause)
    expr = AND(clauses)
    return expr
