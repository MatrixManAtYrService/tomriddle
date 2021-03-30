from itertools import product, combinations
from functools import reduce
import operator
import sympy.logic.boolalg as form
from sympy import Symbol, Not, And, Or

from tomriddle import satbridge


def AND(exprs):
    return reduce(operator.and_, exprs)


def OR(exprs, convert=False):

    if convert:
        # this will be slow for many clauses
        # https://cs.stackexchange.com/a/41071/97082
        return form.to_cnf(reduce(operator.or_, exprs), simplify=True, force=True)
    else:
        return reduce(operator.or_, exprs)


def _to_list(it, mapper):
    """
    Whatever it is, make it into list of ints for use like this:
    https://pypi.org/project/pycosat/
    """

    def require(m):
        if m is None:
            raise TypeError("A mapper kwarg is required")

    if type(it) in [list, tuple]:

        list_of = type(it[0])
        if list_of == "int":
            return it

        elif list_of in [Symbol, Not]:
            require(mapper)
            return [mapper.to_int(x) for x in it]

        else:
            raise TypeError(f"Not sure what to do with a list of {list_of}")

    if type(it) == And:

        require(mapper)
        return satbridge.expr_to_satfmt(it, mapper)

    if type(it) == Or:

        require(mapper)
        return satbridge.expr_to_satfmt(it, mapper, convert_cnf=False)

    raise TypeError(f"Whats a {type(it)}?")


def max_n_true(variables, n, mapper=None):
    """
    Takes an iterable of symbols, returns a CNF clause which allows
    at most n of them to be true at once.
    """

    # make sat-friendly (if not already)
    payload = _to_list(variables, mapper)

    # make a cnf expr
    clauses = []
    for microstate in combinations(payload, n + 1):
        clause = list(map(lambda x: -x, microstate))
        clauses.append(clause)
    return clauses


def min_n_true(variables, n, mapper=None):
    """
    Takes an iterable of  ints, or an iterable of Symbols and a mapper.
    Returns a CNF expression n of them to be true at once.
    """

    # make sat-friendly (if not already)
    payload = _to_list(variables, mapper)

    # make a cnf expr
    clauses = []
    for microstate in combinations(payload, n):
        clauses.append(microstate)
    return clauses


def from_dnf(dnf_clauses, mapper=None):
    """
    Takes a DNF expression as a list of lists of ints and returns the
    equivalent CNF expression as a list of list of ints.

    Sympy is rather slow at this.

    The first param can also be a sympy expression, but you'll still
    get a list back.  A mapper is required for this.
    """

    if type(dnf_clauses) != list:
        clauses = _to_list(dnf_clauses, mapper)
    else:
        clauses = dnf_clauses

    return list(product(*clauses))
