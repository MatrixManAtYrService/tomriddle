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

    # make a cnf expr forbidding any of the ways to have too many
    clauses = []
    for microstate in combinations(payload, n + 1):
        clause = list(map(lambda x: -x, microstate))
        clauses.append(clause)
    return clauses


def min_n_true(variables, n, mapper=None):
    """
    Takes an iterable of ints, or an iterable of Symbols and a mapper.
    Returns a CNF expression that requires n of them to be true at once.
    """

    # make sat-friendly (if not already)
    payload = _to_list(variables, mapper)

    # make a dnf expr: OR(AND(),AND(),...,AND())
    # which lists the way for there to be enough true variables
    clauses = []
    for microstate in combinations(payload, n):
        clauses.append(list(microstate))

    # convert it to cnf: AND(OR(),OR(),...,OR())
    return from_dnf(clauses)


def _next_set(args):
    """
    Deterministically take one element from a set of sets
    """

    # no dupes, deterministic order, larger sets first
    items = sorted(list(map(frozenset, args)), key=lambda x: -len(x))
    return items[0], set(items[1:])


def _setproduct(argsets):
    """
    Like itertools.product, but iterates from a set of frozensets instead
    of a list of tuples. In the from_dnf case below, that means fewer
    duplicates to remove after the cross product is calculated. Recurses.

    Omit 'current' to start recurion.  Otherwise use it to pass partial
    clauses to the next stack frame.
    """

    # terminate recursion when no work remains
    if sum(map(len, argsets)) == 0:
        return frozenset({})

    # otherwise gobble another set
    current_set, next_sets = _next_set(argsets)

    # recurse
    subproduct = list(_setproduct(next_sets))

    for element in current_set:
        if not subproduct:
            yield frozenset({element})
        else:
            for factor in subproduct:
                yield frozenset({element}).union(factor)


def from_dnf(dnf_clauses, mapper=None):
    """
    Takes a DNF expression and returns a CNF expression

    The first param can also be a sympy expression, but you'll still
    get a list back.  If so, mapper is required.

    For large expression the pre-deduplicated step becomes intractiable
    around four or five symbols, maybe this can be optimized.
    """

    if type(dnf_clauses) != list:
        clauses = _to_list(dnf_clauses, mapper)
    else:
        clauses = dnf_clauses

    return [list(x) for x in _setproduct(clauses)]
