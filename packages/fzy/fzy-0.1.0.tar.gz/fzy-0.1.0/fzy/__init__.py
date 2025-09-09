__version__ = "v0.1.0"

import sys
from argparse import ArgumentParser, FileType

import yaml

from fzy.filtering import fuzzy_filter, NoMatch
from fzy.util import use_yaml_multiline_strings
from fzy.tui import tui


def main() -> None:
    parser = ArgumentParser(
        description="""
            Display and interactively search/filter YAML documents.
        """
    )
    parser.add_argument(
        "yaml",
        type=FileType("r"),
        default=sys.stdin,
        nargs="?",
        help="""
            A YAML file to filter. Defaults to stdin. Use '-' to specify stdin
            explicitly.
        """,
    )
    parser.add_argument(
        "query",
        type=str,
        default="",
        nargs="?",
        help="""
            The initial search term to use.
        """,
    )
    parser.add_argument(
        "--case-sensitive",
        "-c",
        action="store_true",
        default=False,
        help="""
            Make searches case-sensitive.
        """,
    )
    parser.add_argument(
        "--no-split-multiline-strings",
        "-S",
        action="store_true",
        default=False,
        help="""
            If given, don't split multi-line strings when the search matches
            lines within the string. (Tip: add a trailing space to your filter
            string to temporarily force this behaviour).
        """,
    )
    parser.add_argument(
        "--non-interactive",
        "-I",
        action="store_true",
        default=False,
        help="""
            If set, returns the documents matched by the query provided with
            `--query` without running the interactive matcher.
        """,
    )
    parser.add_argument(
        "--print-matched",
        "-p",
        action="store_true",
        default=False,
        help="""
            If set, prints the matched subset of the input documents on exit.
            Also makes pressing 'enter' exit the programme.
        """,
    )
    args = parser.parse_args()

    use_yaml_multiline_strings()

    if not args.non_interactive:
        matching = tui(
            args.yaml.read(),
            args.query,
            args.case_sensitive,
            not args.no_split_multiline_strings,
            exit_on_enter=args.print_matched,
        )
    else:
        matching = [
            fuzzy_filter(
                document,
                args.query,
                args.case_sensitive,
                not args.no_split_multiline_strings,
            )
            for document in yaml.safe_load_all(args.yaml.read())
        ]

    if args.print_matched or args.non_interactive:
        for i, document in enumerate(matching):
            if i != 0:
                print("\n---")
            if document is not NoMatch:
                print(yaml.dump(document, sort_keys=False, allow_unicode=True), end="")
            else:
                print("# No matches in this document")
