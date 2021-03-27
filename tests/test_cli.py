from tomriddle.cli import tomriddle


def test_noconstraints():
    args = tomriddle(args=["foobarbaz", "-s", "baz", "qux"], dry=True)
    assert args.answer == "foobarbaz"
    assert args.substr == ["baz", "qux"]
