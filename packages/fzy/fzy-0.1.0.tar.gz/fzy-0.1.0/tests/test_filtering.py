import pytest

from typing import Any

from fzy.filtering import (
    path_to_string,
    iter_flat,
    NoMatch,
    filter_matching_paths,
    split_search,
    fuzzy_filter,
)


@pytest.mark.parametrize(
    "path, exp",
    [
        ([], ""),
        (["foo"], "'foo'"),
        (["foo", "bar"], "'foo'.'bar'"),
        ([123], "[123]"),
        ([123, 321], "[123][321]"),
        (["foo", 123], "'foo'[123]"),
        ([123, "foo"], "[123].'foo'"),
    ],
)
def test_path_to_string(path: list[str | int], exp: str) -> None:
    assert path_to_string(path) == exp


@pytest.mark.parametrize(
    "obj, exp",
    [
        # Atomic values
        (None, [("", None)]),
        (123, [("", 123)]),
        # Strings
        ("foo", [("", "foo"), ("[0]", "foo")]),
        (
            "foo\nbar\nbaz",
            [
                ("", "foo\nbar\nbaz"),
                ("[0]", "foo\n"),
                ("[1]", "bar\n"),
                ("[2]", "baz"),
            ],
        ),
        # Lists
        ([], [("", "[]")]),
        (
            [1, 2],
            [
                ("", "[]"),
                ("[0]", 1),
                ("[1]", 2),
            ],
        ),
        # Dictionaries
        ({}, [("", "{}")]),
        (
            {"a": 123, "b": 321},
            [
                ("", "{}"),
                ("'a'", 123),
                ("'b'", 321),
            ],
        ),
        # Nesting
        (
            {"a": {"aa": 11, "ab": 12}, "b": {"ba": 21, "bb": 22}},
            [
                ("", "{}"),
                ("'a'", "{}"),
                ("'a'.'aa'", 11),
                ("'a'.'ab'", 12),
                ("'b'", "{}"),
                ("'b'.'ba'", 21),
                ("'b'.'bb'", 22),
            ],
        ),
    ],
)
def test_iter_flat(obj: Any, exp: list[tuple[str, Any]]) -> None:
    assert list(iter_flat(obj)) == exp


@pytest.mark.parametrize(
    "paths, exp",
    [
        # Nothing should match when no paths given
        (set(), NoMatch),
        # Simple sub path
        ({"'foo'"}, {"foo": 123}),
        # Nested sub path
        (
            {"'bar'"},
            {
                "bar": {
                    "baz": 456,
                    "qux": 789,
                }
            },
        ),
        # Deep path
        ({"'bar'.'baz'"}, {"bar": {"baz": 456}}),
        # Everything should match when root path given
        (
            {""},
            {
                "foo": 123,
                "bar": {
                    "baz": 456,
                    "qux": 789,
                },
                "quo": "one\ntwo\nthree\nfour",
            },
        ),
        # String
        ({"'quo'"}, {"quo": "one\ntwo\nthree\nfour"}),
        # Line in string
        ({"'quo'[0]"}, {"quo": "one\n⋯\n"}),
        ({"'quo'[1]"}, {"quo": "⋯\ntwo\n⋯\n"}),
        ({"'quo'[3]"}, {"quo": "⋯\nfour"}),
        # Multiple lines in string
        ({"'quo'[0]", "'quo'[3]"}, {"quo": "one\n⋯\nfour"}),
        ({"'quo'[0]", "'quo'[1]", "'quo'[3]"}, {"quo": "one\ntwo\n⋯\nfour"}),
    ],
)
def test_filter_matching_paths(paths: set[str], exp: Any) -> None:
    assert (
        filter_matching_paths(
            {
                "foo": 123,
                "bar": {
                    "baz": 456,
                    "qux": 789,
                },
                "quo": "one\ntwo\nthree\nfour",
            },
            paths,
        )
        == exp
    )


@pytest.mark.parametrize(
    "search, exp",
    [
        # Empty
        ("", [""]),
        # Single words
        ("foo", ["foo"]),
        # Space separated words
        ("foo bar", ["foo", "bar"]),
        ("foo  bar", ["foo", "bar"]),
        # Square brackets
        ("foo[123][456]bar", ["foo", "[123]", "[456]", "bar"]),
        # Colon, equals and dot
        ("foo=bar", ["foo", "=", "bar"]),
        ("foo:bar", ["foo", ":", "bar"]),
        ("foo.bar", ["foo", ".", "bar"]),
    ],
)
def test_split_search(search: str, exp: list[str]) -> None:
    assert split_search(search) == exp


class TestFuzzyFilter:
    @pytest.mark.parametrize(
        "search, exp",
        [
            # Fully matching
            (
                "",
                {
                    "foo": 123,
                    "bar": {
                        "baz": 456,
                        "qux": [100, 200, 300],
                    },
                    "quo": "one\ntwo\nthree\nfour",
                },
            ),
            # Non-matching
            ("I don't match anything", NoMatch),
            # Matching on keys
            ("foo", {"foo": 123}),
            ("oo", {"foo": 123}),
            ("bar baz", {"bar": {"baz": 456}}),
            ("b b", {"bar": {"baz": 456}}),
            # Matching on indices
            ("bar[0]", {"bar": {"qux": [100]}}),
            ("bar[1]", {"bar": {"qux": [200]}}),
            # Matching on values
            ("123", {"foo": 123}),
            # Matching on keys, values and indices
            ("foo = 123", {"foo": 123}),
            ("bar [0] = 100", {"bar": {"qux": [100]}}),
            # Match on path
            ("bar.baz", {"bar": {"baz": 456}}),
            ("bar.qux[1]", {"bar": {"qux": [200]}}),
            # Match string's key to get whole string
            ("quo", {"quo": "one\ntwo\nthree\nfour"}),
            ("quo:=", {"quo": "one\ntwo\nthree\nfour"}),
            # Match string line numbers
            ("quo[1]", {"quo": "⋯\ntwo\n⋯\n"}),
            # Match string contents
            ("four", {"quo": "⋯\nfour"}),
            ("ee", {"quo": "⋯\nthree\n⋯\n"}),
            ("quo t", {"quo": "⋯\ntwo\nthree\n⋯\n"}),
        ],
    )
    def test_filtering(self, search: str, exp: Any) -> None:
        assert (
            fuzzy_filter(
                {
                    "foo": 123,
                    "bar": {
                        "baz": 456,
                        "qux": [100, 200, 300],
                    },
                    "quo": "one\ntwo\nthree\nfour",
                },
                search,
            )
            == exp
        )

    def test_case_sensitivity(self) -> None:
        assert fuzzy_filter({"FoO": 123}, "FoO", case_sensitive=False) == {"FoO": 123}
        assert fuzzy_filter({"FoO": 123}, "foo", case_sensitive=False) == {"FoO": 123}
        assert fuzzy_filter({"FoO": 123}, "foo", case_sensitive=True) == NoMatch
        assert fuzzy_filter({"FoO": 123}, "FoO", case_sensitive=True) == {"FoO": 123}

    def test_disable_multiline(self) -> None:
        assert fuzzy_filter(
            {
                "qux": "not me!",
                "quo": "one\ntwo\nthree\nfour",
            },
            "two",
            split_multiline_strings=False,
        ) == {"quo": "one\ntwo\nthree\nfour"}
