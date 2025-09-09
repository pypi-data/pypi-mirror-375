"""
This module implements a simple TUI for displaying and interactively filtering
YAML documents based on the `urwid` library.
"""

from typing import Hashable, Any, Callable

from fzy.filtering import NoMatch, fuzzy_filter

import yaml
import urwid  # type: ignore
import pygments.lexers
from pygments.token import Token


FILTER_WIDGET_PALETTE = [
    ("prompt", "dark blue, bold", "default"),
    ("filter", "default, bold", "default"),
    ("dim", "dark gray", "default"),
]
"""Suggested palette for FilterWidget UI components."""


class FilterWidget(urwid.Frame):
    """
    A widget which shows a text-entry box at the bottom of the screen and a
    scrollable text view on the rest of the screen.
    """

    text: urwid.Text
    """The text display widget showing the filter output"""

    edit: urwid.Edit
    """The edit box for entering the filter text"""

    def __init__(
        self,
        get_filter_output: Callable[[urwid.Text, str], None],
        initial_filter: str = "",
        prompt: str = "> ",
    ) -> None:
        """
        Parameters
        ----------
        get_filter_output : fn(text_widget: urwid.Text, new_filter: str) -> None
            A callback function which is called every time the filter
            expression is changed by the user. This callback should perform
            whatever filtering is needed and then populate the provided
            text_widget with the filtered value. This process may be
            asynchronous.
        initial_filter : str
            The initial contents of the filter
        prompt : str
            The prompt to show on the filter line.
        """
        self.text = urwid.Text(("dim", "Loading..."))
        self.edit = urwid.Edit(("prompt", prompt), initial_filter)
        super().__init__(
            urwid.Scrollable(self.text),
            footer=urwid.AttrMap(self.edit, "filter"),
            focus_part="footer",
        )

        urwid.connect_signal(
            self.edit,
            "change",
            lambda _edit, new_filter: get_filter_output(self.text, new_filter),
        )

        # Get initial filter output.
        get_filter_output(self.text, self.edit.get_edit_text())

    def keypress(self, size: tuple[int, int], key: str) -> str | None:
        # Redirect vertical motion keys to the scrollable text view
        if key in ("up", "down", "page up", "page down"):
            maxcol, maxrow = size

            if self.header is not None:
                maxrow -= self.header.rows((maxcol,))
            if self.footer is not None:
                maxrow -= self.footer.rows((maxcol,))

            return self.body.keypress((maxcol, maxrow), key)
        else:
            return super().keypress(size, key)


YAML_PALETTE = [
    # Document start/end marker
    (Token.Name.Namespace, "light gray", "default"),
    # Comments
    (Token.Comment.Single, "dark green", "default"),
    # Dictionary keys
    (Token.Name.Tag, "light blue", "default"),
    (Token.Punctuation, "light blue", "default"),  # Colon
    # Arrays
    (Token.Punctuation.Indicator, "brown", "default"),  # Dash, brackets & commas
    # Strings
    (Token.Literal.String, "yellow", "default"),  # Quoted string
    (Token.Name.Constant, "yellow", "default"),  # Multi-line string
    # Literals of all kinds (including unquoted strings
    (Token.Literal.Scalar.Plain, "light cyan", "default"),  # Bool
    (Token.Name.Variable, "light cyan", "default"),  # Bool
]
"""Urwid palette for YAML tokenisation by pygments."""


def yaml_syntax_highlighting(yaml: str) -> list[tuple[Hashable, str]]:
    """
    Produce a urwid markup stream producing a syntax highlighting of the
    provided YAML literal.

    The `YAML_PALETTE` palette can be used to colourise the resulting text.
    """
    yaml_lexer = pygments.lexers.get_lexer_by_name("yaml")
    return list(yaml_lexer.get_tokens(yaml))


def tui(
    raw_input: str,
    initial_search: str = "",
    case_sensitive: bool = False,
    split_multiline_strings: bool = True,
    exit_on_enter: bool = False,
) -> list[Any]:
    """
    Run an interactive fuzzy YAML filter.

    Use Ctrl+C or escape to exit.

    Returns the YAML subset documents selected when the UI was exited. Returns
    the NoMatch sentinel for documents containing no matching content.

    As a special case, if the search ends with a non-zero number of spaces,
    split_multiline_strings mode forced to off.
    """
    parsed_input = list(yaml.safe_load_all(raw_input))

    # The current set of matches
    matches = parsed_input

    def get_filter_output(text: urwid.Text, new_filter) -> None:
        nonlocal matches
        new_text = None

        if new_filter == "":
            # Special case: When no filter specified, display the original YAML
            # (with all its original formatting)
            matches = parsed_input
            new_text = yaml_syntax_highlighting(raw_input)
        else:
            matches = [
                fuzzy_filter(
                    document,
                    new_filter,
                    case_sensitive=case_sensitive,
                    split_multiline_strings=(
                        # Special case: when filter ends with a space, force
                        # multi-line string matching off.
                        split_multiline_strings
                        and not new_filter.endswith(" ")
                    ),
                )
                for document in parsed_input
            ]

            new_text = []
            for document in matches:
                if new_text != []:
                    new_text.append((Token.Name.Namespace, "\n---\n"))
                if document is not NoMatch:
                    new_text.extend(
                        yaml_syntax_highlighting(
                            yaml.dump(document, sort_keys=False, allow_unicode=True)
                        )
                    )
                else:
                    new_text.append(("dim", "# No matches in this document"))

        text.set_text(new_text)

    def quit_on_esc(key: str) -> None:
        if key == "esc":
            raise urwid.ExitMainLoop()
        elif key == "enter" and exit_on_enter:
            raise urwid.ExitMainLoop()

    try:
        urwid.MainLoop(
            FilterWidget(get_filter_output, initial_search),
            FILTER_WIDGET_PALETTE + YAML_PALETTE,
            unhandled_input=quit_on_esc,
            handle_mouse=False,
        ).run()
    except KeyboardInterrupt:
        pass

    return matches
