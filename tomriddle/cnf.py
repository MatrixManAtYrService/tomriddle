from itertools import product, combinations
from functools import reduce
import operator
import sympy.logic.boolalg as form


def AND(exprs):
    return reduce(operator.and_, exprs)


def OR(exprs, convert=False):

    if convert:
        # this will be slow for many clauses
        # https://cs.stackexchange.com/a/41071/97082
        return form.to_cnf(reduce(operator.or_, exprs), simplify=True, force=True)
    else:
        return reduce(operator.or_, exprs)


def max_n_true(symbols, n):
    """
    Takes an iterable of symbols, returns a CNF clause which allows
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
    Takes an iterable of symbols, returns a CNF clause which requires
    n of them to be true at once.
    """

    clauses = []
    for microstate in combinations(symbols, n):
        clause = OR(microstate)
        clauses.append(clause)
    expr = AND(clauses)
    return expr


def from_dnf(expr, strategy="product"):
    """
    Takes a DNF expression and returns the equivalent CNF expression
    """

    in_terms = []
    for clause in expr.args:
        in_terms.append([term for term in clause.args])

    out_terms = product(*in_terms)
    return AND([OR(c) for c in out_terms])
