from tom_riddle import tom_riddle


def test_main():
    assert "foo" in tom_riddle.main(tom_riddle.Args("foo"))
