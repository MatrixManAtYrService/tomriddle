import json
import re

from sympy.logic.boolalg import is_cnf, to_cnf
from sympy.parsing.sympy_parser import parse_expr
from sympy import Symbol

from tomriddle import cnf


# used to transform strings like
#     x & (y | z)
# into ones like
#     [x], [y, z]
# (towards json)
syntax_map = {"(": "[", ")": "]", "|": ",", "&": ",", "~": "-"}


def get_symbstr_map(symbols):
    """
    Given sympy sybols[A, B, C] return a map { "A":1, "B":2, "C":2 }
    Used to complete the transformation from expression string to json
    """

    symbstr2int = {}
    for i, symbol in enumerate(symbols, start=1):
        symbstr2int[str(symbol)] = i

    return symbstr2int


def get_intsymb_map(symbols):
    """
    Given sympy sybols[A, B, C] return a map { "A":1, "B":2, "C":2 }
    Used to complete the transformation from expression string to json
    """

    int2symb = {}
    for i, symbol in enumerate(symbols, start=1):
        int2symb[i] = symbol

    return int2symb


def expr_to_satfmt(expr, symbols):
    """
    Takes a sympy formula in CNF, return a list of lists of integers for
    use with pycosat
    """

    # ensure CNF
    cnf_expr = None
    if not is_cnf(expr):
        print(
            "Got a non-CNF expression, converting... (depending on the size and "
            "structure of the expression, this could take a prohibitively long time)"
        )
        # see https://cs.stackexchange.com/a/41071/97082 for an explanation
        # if this becomes a problem, Tseitin transforms might be worth exploring
        # for now I'm just gonna try to stick to CNF everywhere

        cnf_expr = to_cnf(expr, simplify=True, force=True)
    else:
        cnf_expr = expr

    # I'm not sure if mutating the expression string to JSON and back is a good idea.
    # If you're a sympy wizard, please show me the smarter way.
    # test cmd: pytest -s tests/test_satbridge.py::test_tofrom_expr

    # make list of integers
    cnf_str = str(cnf_expr)
    translate = get_symbstr_map(symbols)
    translate.update(syntax_map)

    for target, result in translate.items():
        cnf_str = cnf_str.replace(target, str(result))

    return json.loads("[{}]".format(cnf_str))


def satfmt_to_expr(int_list, symbols, strings=None):
    """
    Takes a list of integers like pycosat needs, return a sympy expression
    """

    # rehydrate symbols
    int2symb = get_intsymb_map(symbols)

    def getsymb(n):
        if n > 0:
            return int2symb[n]
        else:
            return ~int2symb[abs(n)]

    # build expr
    clauses = []
    for clause in int_list:
        clauses.append(cnf.OR(map(getsymb, clause)))
    expr = cnf.AND(clauses)

    return expr


def satout_to_str(int_list, symbols):
    """Given symbols like:

    1.O.0 1.O.1 1.O.2 1.O.3 1.O.4
    2.L.0 2.L.1 2.L.2 2.L.3 2.L.4
    1.L.0 1.L.1 1.L.2 1.L.3 1.L.4
    1.E.0 1.E.1 1.E.2 1.E.3 1.E.4
    1.H.0 1.H.1 1.H.2 1.H.3 1.H.4

    If 2.L.3 is true, it means: the 2nd L goes at index 3

    Indexed so that the first n elements are all the ways to put a
    letter in the first position, and then next n are the ways
    put a letter in the second position... and the last element
    means: "put the last element in the last position"

    4  9  14  19  24
    3  8  13  18  23
    2  7  12  17  22
    1  6  11  16  21
    0  5  10  15  20

    Also given a solver output like:
     [-1,   -2,  -3,  -4,   5,
       6,   -7,  -8,  -9, -10,
      -11,  12, -13, -14, -15,
      -16, -17,  18, -19, -20,
      -21, -22, -23,  24, -25, ]

    Produce strings like "OHELL"
    """

    regexpr = re.compile(r"^([0-9])+\.([^.]+)\.([0-9]+)$")

    idx2str = []
    length = 0

    # gather symbols and indices
    for true_symb_num in filter(lambda x: x > 0, int_list):

        # parse symbol string
        symb_idx = true_symb_num - 1
        symb_str = str(symbols[symb_idx])
        match = regexpr.match(symb_str)

        # register mapping
        string = match.group(2)
        idx = match.group(3)
        idx2str.append((idx, string))

    # make a string
    out = []
    for _, string in sorted(idx2str):
        out.append(string)

    return "".join(out)


def str_to_symb(string):
    """
    Given a string like "HELLO", return a list of symbols like:

    ["1.H.0", "1.E.0", "1.L.0", "2.L.0", "1.O.0",
     "1.H.1", "1.E.1", "1.L.1", "2.L.1", "1.O.1",
     "1.H.2", "1.E.2", "1.L.2", "2.L.2", "1.O.2",
     "1.H.3", "1.E.3", "1.L.3", "2.L.3", "1.O.3",
     "1.H.4", "1.E.4", "1.L.4", "2.L.4", "1.O.4"]

    See satout_to_str for naming rationale.
    """

    # get frequency by character and by index
    c_freq = {}
    i_freq = {}
    for i, c in enumerate(string):
        c_freq.setdefault(c, 0)
        c_freq[c] += 1
        i_freq[i] = c_freq[c]

    # get num.char.* part of symbol
    i_symb = {}
    for i, c in enumerate(string):
        numchar = str(i_freq[i])
        i_symb[i] = ".".join([numchar, c])

    # append *.index part of symbol
    symbs = []
    for j, _ in enumerate(string):
        for i, _ in enumerate(string):
            prefix = i_symb[i]
            s = Symbol(".".join([prefix, str(j)]))
            symbs.append(s)

    return symbs
