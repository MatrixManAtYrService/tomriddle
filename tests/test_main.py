from tomriddle import riddler
from tomriddle import Fragments


def test_permute():

    answer = "iam"
    riddle_iter = riddler(answer, None)

    for _ in range(10):
        riddle = next(riddle_iter)
        print(riddle)
        assert len(riddle) == len(answer)
        for char in answer:
            assert riddle.count(char) == answer.count(char)


def test_voldemort():

    f = Fragments(["lor", "ord", "vol", "dem", "mort"], ["iam"], [])
    q = "Tom Marvolo Riddle"
    a = "iamlordvoldemort"

    assert a in list(riddler(q, f))


def test_superfoo():

    f = Fragments(
        ["foo", "bar", "but", "not", "baz", "are", "is"],
        ["nota"],
        (["superf"], ["zes"]),
    )
    q = "aaaabbbeeefinoooprrrsssttuuzz"
    a = "superfooisnotabarbutbazzesare"

    assert a in list(riddler(f, q))


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
