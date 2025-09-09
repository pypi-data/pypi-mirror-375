fzy: Fuzzy YAML Viewer/Searcher
===============================

A tool which interactively displays YAML files and provides fuzzy interactive
searching and filtering, loosely inspired by
[`fzf`](https://github.com/junegunn/fzf).

![fzy demo](docs/demo.gif)

Usage
-----

Run `fzy` with a YAML file as an argument to display it on screen.

Use up/down/page-up/page-down to scroll.

Start typing key or value names to filter down the YAML document to just those
parts with a match.


As a library
------------

You can launch the `fzy` TUI from Python (rather than invoking the command via
a `subprocess`) like so:

    >>> import fzy
    >>> filtered_document = fzy.tui(yaml_string)

You can also perform filtering non-interactively like so:

    >>> import fzy
    >>> filtered_document = fzy.fuzzy_filter(parsed_yaml_document, "search pattern here")


Development
-----------

You can run the test suite using:

    $ pip install -r requirements-test.txt
    $ pytest

