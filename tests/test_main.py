import pytest
from tomriddle import riddler
from tomriddle import Fragments

from itertools import permutations


def test_permute():
    """SAT-solving is a rather messy way of generating permutations, but we
    need to make sure that it at least does permutations before we start
    throwing additional constraints at it."""

    answer = "iam"

    # use itertools as an authority
    expect_riddles = sorted(["".join(x) for x in permutations(answer)])

    riddles = []
    for riddle in riddler(answer, None):
        riddles.append(riddle)

    got_riddles = sorted(riddles)

    assert expect_riddles == got_riddles


def test_permute_long():

    answer = "iamlo"
    riddle_iter = riddler(answer, None)
    riddle = next(riddle_iter)
    print(riddle)


def test_permute_too_long():

    answer = "iamlor"
    riddle_iter = riddler(answer, None)
    riddle = next(riddle_iter)
    print(riddle)


@pytest.mark.skip(reason="functionality not yet implemented")
def test_voldemort():

    f = Fragments(["lor", "ord", "vol", "dem", "mort"], ["iam"], [])
    q = "Tom Marvolo Riddle"
    a = "iamlordvoldemort"

    assert a in list(riddler(q, f))


@pytest.mark.skip(reason="functionality not yet implemented")
def test_superfoo():

    f = Fragments(
        ["foo", "bar", "but", "not", "baz", "are", "is"],
        ["nota"],
        (["superf"], ["zes"]),
    )
    q = "aaaabbbeeefinoooprrrsssttuuzz"
    a = "superfooisnotabarbutbazzesare"

    assert a in list(riddler(f, q))


@pytest.mark.skip(reason="functionality not yet implemented")
def test_superfoo_constraint():

    f = Fragments(
        ["foo", "bar", "but", "not", "baz", "are", "is"], ["nota"], ["zes", "superf"]
    )
    q = "aaaabbbeeefinoooprrrsssttuuzz"
    a1 = "superfooisnotabarbutbazzesare"
    a2 = "bazzesaresuperfoobutabarisnot"

    # must contain "baz" and "foo" in that order
    answers = list(riddler(f, q), constraint=["baz", "foo"])
    assert a2 in answers
    assert a1 not in answers

    # "superf" is a
    assert "superbar" not in answers
