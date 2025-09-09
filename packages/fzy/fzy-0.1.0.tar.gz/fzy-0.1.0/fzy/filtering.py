"""
Routines for fuzzily filtering thorugh deserialsed YAML/JSON style structures
made up of nested dictionaries and lists.


Paths
-----

YAML/JSON datastructures can be considered as addressible via 'paths'
consisting of a list of dictionary keys (strings) or list indices (ints). For
example in the following::

    ---
    foo:
      bar:
        - 111
        - 222
        - 333

The value '222' has a path of ``['foo', 'bar', 1]``. The list of numbers itself
has the path ``['foo', 'bar']`` and the top-level document has the path ``[]``.

As a special case, multi-line strings are treated as both a single string and
as an array of single-line strings. This means that it is possible to match
both the whole string and just a part of it.


Fuzzy filtering
---------------

A document is filtered by performing fuzzy search on its paths and values. Any
values or paths (and their decedents) are included in the output. To achieve
this, we essentially convert the document into a series of text-based path and
value descriptions and use a regular expression to test whether they match the
user-provided pattern.

The :py:func:`fuzzy_filter` function implements the top-level functionality.

"""

from typing import Any, Iterator, cast

import re
from functools import partial


def path_to_string(path: list[str | int] = []) -> str:
    """
    Convert a path within a datastructure into a string for fuzzy matching.

    These strings are guaranteed to be unique for a unique path.

    For example: ["foo", "bar", 10] becomes "'foo'.'bar'[10]".
    """
    out = ""
    for part in path:
        if isinstance(part, str):
            out += f".{part!r}"
        else:
            out += f"[{part!r}]"
    return out.lstrip(".")


class MultiLineStringFragment(str):
    """
    A str, but wrapped to annotate it as being from a part of a multi-line
    string in the output if :py:func:`iter_flat`.
    """


def iter_flat(
    obj: Any,
    split_multiline_strings: bool = True,
    dict_placeholder: Any = "{}",
    list_placeholder: Any = "[]",
    _path: list[str | int] = [],
) -> Iterator[tuple[str, Any]]:
    """
    Iterate over a document as a sequence of (path, value) tuples.

    The list_placeholder and dict_placeholder values will be generated for each
    dict or list encountered.

    The split_multiline_strings argument controls whether strings are
    represented as both a single string and as an array of single line strings,
    or just as a string.
    """
    recurse = partial(
        iter_flat,
        split_multiline_strings=split_multiline_strings,
        dict_placeholder=dict_placeholder,
        list_placeholder=list_placeholder,
    )
    if isinstance(obj, dict):
        yield (path_to_string(_path), dict_placeholder)
        for key, value in obj.items():
            yield from recurse(value, _path=_path + [key])
    elif isinstance(obj, list):
        yield (path_to_string(_path), list_placeholder)
        for i, value in enumerate(obj):
            yield from recurse(value, _path=_path + [i])
    elif isinstance(obj, str):
        yield (path_to_string(_path), obj)
        if split_multiline_strings:
            lines = obj.splitlines(keepends=True)
            for i, line in enumerate(lines):
                yield (path_to_string(_path + [i]), MultiLineStringFragment(line))
    else:
        yield (path_to_string(_path), obj)


NoMatch = object()
"""
A sentinel value indicating no part of a document was matched by
:py:func:`filter_matching_paths`.
"""


def filter_matching_paths(
    obj: Any,
    paths: set[str],
    elision_marker: str = "⋯",
    _path: list[str | int] = [],
) -> Any:
    """
    Given a document, produce a copy containing only paths (and their children)
    specified in the 'paths' set. Partial matches of lines in multiline strings
    are indicated via addition of the elision_marker which defaults to a
    unicode ellipse (…).

    Where a parent and child path are both included in 'paths', the child path
    is effecitvely ignored as the whole parent structure will be included
    as-is.

    Returns the sentinel 'NoMatch' value if no part of the provided object was
    matched.
    """
    if path_to_string(_path) in paths:
        return obj
    elif isinstance(obj, str):
        # Filter only matched lines in multi-line strings
        lines = cast(list[str | None], obj.splitlines(keepends=True))
        for i, line in enumerate(lines):
            if path_to_string(_path + [i]) not in paths:
                lines[i] = None

        if all(line is None for line in lines):
            return NoMatch

        # Remove repeated 'None's
        for i, (line, next_line) in list(enumerate(zip(lines[:], lines[1:])))[::-1]:
            if line is None and next_line is None:
                del lines[i + 1]

        return "".join(
            line if line is not None else f"{elision_marker}\n" for line in lines
        )
    elif isinstance(obj, dict):
        new_dict = {}
        for key, value in obj.items():
            matching_value = filter_matching_paths(
                value, paths, elision_marker, _path + [key]
            )
            if matching_value is not NoMatch:
                new_dict[key] = matching_value
        # NB: If we've got to this point, unless we match a sub item, this
        # dictionary won't be included. As such if new_dict doesn't contain any
        # matching subitems there's nothing to return.
        if not new_dict:
            return NoMatch
        else:
            return new_dict
    elif isinstance(obj, list):
        new_list = []
        for i, value in enumerate(obj):
            matching_value = filter_matching_paths(
                value, paths, elision_marker, _path + [i]
            )
            if matching_value is not NoMatch:
                new_list.append(matching_value)
        # NB: See comment about new_dict above.
        if not new_list:
            return NoMatch
        else:
            return new_list
    else:
        return NoMatch


def split_search(search: str) -> list[str]:
    """
    Split search string into words, each of which will be searched for.

    Specifically, splits on whitespace, ":", "=" and "." and also around [nnn]. This
    means you can write ``[0]`` to match the zeroth entry in a list.
    """
    return re.split(r"\s+|(?=\[)|(?<=\])|(?=[:=.])|(?<=[:=.])", search)


def fuzzy_filter(
    obj: Any,
    search: str,
    case_sensitive: bool = False,
    split_multiline_strings: bool = True,
    elision_marker: str = "⋯",
) -> Any:
    """
    Fuzzily filter a document according to the specified search string.

    The search string will match against both path components and values.
    Matching occurs at the word-level. This means that, for example, 'foo bar'
    will match 'foobar', 'xxfooxx and xxbarxx' but not 'f o o b a r'.

    If split_multiline_strings is enabled, individual lines in multi-line
    strings may be matched (in preference to the whole string). In this
    instance, omitted lines are indicated by the insertion of the
    elision_marker.
    """
    # Make a regex which matches the searched words in order, but with any
    # values inbetween (including none!)
    matcher = re.compile(
        # NB: Non-greedy matching used to prefer matching earlier in the input
        # (i.e. in the path, not value) so that we only trigger multi-line
        # string matches if we absolutely can't match the path.
        ".*?".join(re.escape(part) for part in split_search(search)),
        flags=(0 if case_sensitive else re.IGNORECASE),
    )

    # Find the path/value pairs which match the search term
    selected_paths = set()
    for path, value in iter_flat(obj, split_multiline_strings):
        if match := matcher.search(f"{path}:={value}"):
            matched_part_of_value = match.end() > len(path) + 2
            if (
                isinstance(value, str)
                and split_multiline_strings
                and matched_part_of_value
            ):
                # If we matched the contents of individual line within a
                # multi-line string, only match the line (not the whole string)
                # in split_multiline_strings mode. Otherwise, only match the
                # whole string (and not the individual lines)
                if isinstance(value, MultiLineStringFragment):
                    selected_paths.add(path)
            else:
                selected_paths.add(path)

    # Return the subset of the document containing those paths.
    return filter_matching_paths(obj, selected_paths, elision_marker)
