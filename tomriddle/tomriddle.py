from math import floor, log
from collections import OrderedDict
from sympy import symbols, simplify
import sympy.logic.boolalg as form
from itertools import product
from functools import reduce

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

    def numstr(num):
        template = "{:" + str(repr_width) + "}"
        return template.format(num)

    symb_list = symbols(",".join(map(str, range(len(letters) ** 2))))

    def symbstr(num):
        return symb_list[num]

    # a symbol for each cell in the grid above
    pos2let2sym = OrderedDict()
    let2pos2sym = OrderedDict()
    i = 0
    for char_idx, char in enumerate(letters):
        for idx in riddle_positions:
            symb = symbols(f"{numstr(char_idx)}>{char}>{numstr(idx)}")
            pos2let2sym.setdefault(idx, OrderedDict())[char_idx] = symb
            let2pos2sym.setdefault(char_idx, OrderedDict())[idx] = symb

            # symb = symbstr(idx)
            # pos2let2sym.setdefault(idx, OrderedDict())[char_idx] = i
            # let2pos2sym.setdefault(char_idx, OrderedDict())[idx] = i
            # i += 1

    # expressions asserting that a letter is "here" and not "anywhere else"
    column_uniqueness = set()
    for riddle_idx, letter_num in product(riddle_positions, letter_numbers):

        # if this allocation occurred
        expr = pos2let2sym[riddle_idx][letter_num]

        # no other allocation occurred here
        for other_letter in letter_numbers:
            if other_letter != letter_num:
                expr |= ~let2pos2sym[other_letter][riddle_idx]

        column_uniqueness.add(expr)

    permutation_condition = print(reduce(lambda a, b: a & b, column_uniqueness))
