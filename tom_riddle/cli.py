"""Console script for tom_riddle."""
import argparse
import sys
from tom_riddle import tom_riddle.main


def main():
    """Console script for tom_riddle."""
    parser = argparse.ArgumentParser()
    parser.add_argument('input')
    args = parser.parse_args()

    output = tom_riddle.main(args)
    print(output)

    return 0


if __name__ == "__main__":
    sys.exit(main())
