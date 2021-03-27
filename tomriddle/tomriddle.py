from math import floor, log
from collections import OrderedDict
from sympy import Symbol
import sympy.logic.boolalg as form
from itertools import product
from functools import reduce
from pprint import pprint
import json

from .fragments import get_default_fragments, get_fragments_from, clean
import pycosat


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

    #  i                                  x
    #  a             x
    #  m          x
    #  l                                           x
    #  o                            x
    #  r                               x
    #  d                                        x
    #  v                   x
    #  o                      x
    #  l                         x
    #  d                                     x
    #  e                                              x
    #  m       x
    #  o    x
    #  r                x
    #  t x
    #    00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15
    #
    #    t  o  m  m  a  r  v  o  l  o  r  i  d  d  l  e

    letters = clean(answer)
    riddle_positions = list(range(len(letters)))
    letter_numbers = riddle_positions.copy()

    # display numbers with 0 padding
    repr_width = floor(log(max(letter_numbers)))
    symb_ct = max(letter_numbers) ** 2

    def numstr(num):
        template = "{:" + str(repr_width) + "}"
        return template.format(num)

    # a symbol for each cell in the grid above
    pos2let2sym = OrderedDict()
    let2pos2sym = OrderedDict()
    symstr2symnum = {}
    columns = []
    i = 1
    for idx in riddle_positions:
        column = []
        for char_idx, char in enumerate(letters):

            symb = Symbol(str(i))
            symstr2symnum[i] = f"{numstr(char_idx)}>{char}>{numstr(idx)}"
            pos2let2sym.setdefault(idx, OrderedDict())[char_idx] = symb
            let2pos2sym.setdefault(char_idx, OrderedDict())[idx] = symb
            column.append(symb)
            i += 1
        columns.append(column)

    pprint(symstr2symnum)

    # no more than one allocation per column
    column_uniqueness = []
    for this_loc, this_letter in product(riddle_positions, letter_numbers):

        # if this allocation occurred
        expr = pos2let2sym[this_loc][this_letter]

        # no other allocation occurred here
        for other_letter in letter_numbers:
            if other_letter != this_letter:
                expr &= ~let2pos2sym[other_letter][this_loc]

        # and this letter can't be anywhere else
        for other_loc in riddle_positions:
            if this_loc != other_loc:
                expr &= ~pos2let2sym[other_loc][this_letter]

        column_uniqueness.append(expr)

    pre_cnf = reduce(lambda a, b: a | b, column_uniqueness)

    # no less than one allocation per column
    every_letter = []
    for choice in product(*columns):
        expr = reduce(lambda a, b: a & b, choice)
        every_letter.append(expr)
    pop = reduce(lambda a, b: a | b, every_letter)
    pre_cnf &= pop
    print("pre_cnf:")
    print(pre_cnf)

    cnf = form.to_cnf(pre_cnf, force=True, simplify=True)
    print("cnf:")
    print(cnf)

    cnfstr = str(cnf)
    for target, result in [("(", "["), (")", "]"), ("|", ","), ("&", ","), ("~", "-")]:
        cnfstr = cnfstr.replace(target, result)

    cnf = json.loads("[{}]".format(cnfstr))
    print(cnf)

    return pycosat.itersolve(cnf)
