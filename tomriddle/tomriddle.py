from math import floor, log
from collections import OrderedDict
from sympy import Symbol
import sympy.logic.boolalg as form
from itertools import product, combinations
from functools import reduce
from pprint import pprint
import operator
import json
import sys

from .fragments import get_default_fragments, get_fragments_from, clean
import pycosat

import IPython


def printerr(msg):
    print(msg, file=sys.stderr)


def main(args):

    try:
        with open(args.corpus, "r") as f:
            fragments = get_fragments_from(f)
    except AttributeError:
        fragments = get_default_fragments()

    for answer in riddler(args.answer, fragments, constraints=args.constraints):
        print(answer)


def riddler(answer, fragments, constraints=[]):
    """
    Return an interator over pronouncable riddle strings like
    "tommarvoloriddle" given answer strings like "iamlordvoldemort".

    If constraints are provided, require that they appear as substrings
    and in the given order (potentially with other material in between).

    If fragments is None and constraints are unset, iterate over permutations

    If fragments is None, iterate over permutations with constraints
    """

    # imagine an n*n grid, each row is an input answer letter
    # each column is an output riddle index
    # if the cell is marked, then that answer-letter is mapped to that riddle-index

    #         i                                  x
    #         a             x
    #         m          x
    #         l                                           x
    #         o                            x
    #         r                               x
    # --in--> d                                        X
    #         v                   x
    #         o                      x
    #         l                         x
    #         d                                     x
    #         e                                              x
    #         m       x
    #         o    x
    #         r                x
    #         t x
    #           00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15
    #                                                  |
    #                                                  |
    #                                                 out
    #                                                  |
    #                                                  v
    #           t  o  m  m  a  r  v  o  l  o  r  i  d  d  l  e

    letters = clean(answer)
    riddle_positions = list(range(len(letters)))
    letter_numbers = riddle_positions.copy()

    # display numbers with 0 padding
    repr_width = floor(log(max(letter_numbers)))

    def numstr(num):
        template = "{:" + str(repr_width) + "}"
        return template.format(num)

    # a symbol for each cell in the grid above
    # and various ways to reference/describe them
    display_key = {}
    columns = []
    symb_num2riddle_letter = {}
    all_symbols = []
    i = 1
    for idx in riddle_positions:
        column = []
        for char_idx, char in enumerate(letters):

            symb = Symbol(str(i))
            all_symbols.append(symb)
            display_key[i] = f"{numstr(char_idx)}>{char}>{numstr(idx)}"
            symb_num2riddle_letter[i] = char
            column.append(symb)
            i += 1
        columns.append(column)

    rows = map(
        list, zip(*columns)
    )  # transpose: https://stackoverflow.com/a/6473724/1054322

    print()
    pprint(display_key)

    ## at least one allocation per column
    # covers = []
    # for cover in product(*columns):
    #    expr = reduce(operator.and_, cover)
    #    covers.append(expr)
    # all_ins_covered = reduce(operator.or_, covers)
    #
    ## no more than one allocation per column
    # dupes = []
    # for column in columns:
    #    for incom, patible in combinations(column, 2):
    #        dupes.append((incom & patible))
    # no_dupes = ~reduce(operator.or_, dupes)

    # at least one allocation per row
    letters_represented = []
    for row in rows:
        letters_represented.append(reduce(operator.or_, row))
    all_ins_covered = reduce(operator.and_, letters_represented)

    # at least one allocation per column
    positions_represented = []
    for column in columns:
        positions_represented.append(reduce(operator.or_, row))
    all_outs_covered = reduce(operator.and_, positions_represented)

    # not n+1 (or more) allocations (preserves bijection)
    crowdings = []
    for one_too_many in combinations(all_symbols, len(letters) + 1):
        crowdings.append(reduce(operator.and_, one_too_many))
    not_too_many = ~reduce(operator.or_, crowdings)

    pre_cnf = all_ins_covered & all_outs_covered & not_too_many
    printerr("pre_cnf:")
    printerr(pre_cnf)

    cnf = form.to_cnf(pre_cnf, force=True, simplify=True)
    printerr("cnf:")
    printerr(cnf)

    cnfstr = str(cnf)
    for target, result in [("(", "["), (")", "]"), ("|", ","), ("&", ","), ("~", "-")]:
        cnfstr = cnfstr.replace(target, result)

    cnf = json.loads("[{}]".format(cnfstr))
    printerr(cnf)

    # if the user has chosen to generate permutations the hard way
    if fragments is None and not constraints:
        permute = pycosat.itersolve(cnf)
        while True:
            try:

                # get a solution, treat symbols as integers
                chosen = map(lambda x: int(str(x)), next(permute))

                # translate into a riddle string
                chosen = filter(lambda x: x > 0, chosen)
                lookup = symb_num2riddle_letter
                riddle = "".join([lookup[sn] for sn in chosen])
                IPython.embed()
                yield riddle

            except StopIteration:
                printerr("done")
                break
    else:
        raise NotImplementedError("Hey Matt, write this part")
