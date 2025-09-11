"""Run the data module as a script."""

import argparse

from lyscripts import exit_cli
from lyscripts.cli import RichDefaultHelpFormatter
from lyscripts.data import enhance, generate, join, split

# Avoid conflict with built-in `filter` function
from lyscripts.data import filter as filter_


def main(args: argparse.Namespace):
    """Run the main script."""
    parser = argparse.ArgumentParser(
        prog="lyscripts data",
        description=__doc__,
        formatter_class=RichDefaultHelpFormatter,
    )
    parser.set_defaults(run_main=exit_cli)
    subparsers = parser.add_subparsers()

    # the individual scripts add `ArgumentParser` instances and their arguments to
    # this `subparsers` object
    enhance._add_parser(subparsers, help_formatter=parser.formatter_class)
    generate._add_parser(subparsers, help_formatter=parser.formatter_class)
    join._add_parser(subparsers, help_formatter=parser.formatter_class)
    split._add_parser(subparsers, help_formatter=parser.formatter_class)
    filter_._add_parser(subparsers, help_formatter=parser.formatter_class)

    args = parser.parse_args()
    args.run_main(args, parser)


if __name__ == "__main__":
    main()
