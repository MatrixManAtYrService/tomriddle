from tomriddle import satbridge
from tomriddle import cnf
from sympy import symbols, Symbol


def test_tofrom_expr():

    symbs = symbols("A,B,C,D,E,F,G")
    expr = cnf.AND(
        [
            cnf.OR(symbols("A,B,C")),
            cnf.OR(symbols("D,E,F")),
            ~Symbol("D") | ~Symbol("G"),
        ]
    )

    ints = satbridge.expr_to_satfmt(expr, symbs)
    sameexpr = satbridge.satfmt_to_expr(ints, symbs)

    assert expr == sameexpr


def test_to_satfmt():

    symbs = symbols("A,B,C,D,E,F,G")
    expr = cnf.AND(
        [
            cnf.OR(symbols("A,B,C")),
            cnf.OR(symbols("D,E,F")),
            ~Symbol("D") | ~Symbol("G"),
        ]
    )

    ints = satbridge.expr_to_satfmt(expr, symbs)

    assert ints == [[1, 2, 3], [4, 5, 6], [-4, -7]]


def test_to_str():
    # fmt: off
    strs = ["1.H.0", "1.E.0", "1.L.0", "2.L.0", "1.O.0",
            "1.H.1", "1.E.1", "1.L.1", "2.L.1", "1.O.1",
            "1.H.2", "1.E.2", "1.L.2", "2.L.2", "1.O.2",
            "1.H.3", "1.E.3", "1.L.3", "2.L.3", "1.O.3",
            "1.H.4", "1.E.4", "1.L.4", "2.L.4", "1.O.4"]
    sat_out =  [ -1,  -2,  -3,  -4,   5,
                  6,  -7,  -8,  -9, -10,
                -11,  12, -13, -14, -15,
                -16, -17,  18, -19, -20,
                -21, -22, -23,  24, -25]
    # fmt: on

    symbs = symbols(strs)
    string = satbridge.satout_to_str(sat_out, symbs)

    assert string == "OHELL"


def test_to_symb():

    # fmt: off
    symb_strs = ["1.H.0", "1.E.0", "1.L.0", "2.L.0", "1.O.0",
                 "1.H.1", "1.E.1", "1.L.1", "2.L.1", "1.O.1",
                 "1.H.2", "1.E.2", "1.L.2", "2.L.2", "1.O.2",
                 "1.H.3", "1.E.3", "1.L.3", "2.L.3", "1.O.3",
                 "1.H.4", "1.E.4", "1.L.4", "2.L.4", "1.O.4"]
    # fmt: on

    expect = list(map(Symbol, symb_strs))

    symbs = satbridge.str_to_symb("HELLO")

    assert expect == symbs
