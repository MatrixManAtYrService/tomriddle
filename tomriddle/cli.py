import argparse
import sys
from .tomriddle import main


def tomriddle(args=None, dry=False):
    parser = argparse.ArgumentParser()
    parser.add_argument("answer")
    parser.add_argument("-s", "--substr", nargs="+", default=[])

    if args:
        args = parser.parse_args(args)
    else:
        args = parser.parse_args()

    if not dry:
        main(args)
    else:
        return args


if __name__ == "__main__":
    sys.exit(main())
