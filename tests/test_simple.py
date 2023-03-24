"""
Tests for simple, non-unidecode specific cases.

The tests here should all be equivalent to the usual :py:func:`str.replace` and
:py:func:`re.sub`.

To make it easier to find one's way around them, the first few test methods are
named `test_{type_of_test}_{type_of_search}_{type_of_replace}`.
"""

import re
import textwrap

from unidecode_replace import (
    unidecode_replace, unidecode_wrap, UnidecodeReplace,
)

from .utils import TestsBase


def _fs(s: str) -> str:
    """
    Demo function to use as a callback `sub` with string search.
    """
    return s + s


def _fr(m: re.Match) -> str:
    """
    Demo function to use as a callback `sub` with regex search.
    """
    return m.group(2) + m.group(1)


def _fw(m: re.Match) -> str:
    """
    Function to use with `re.sub` to get the expected results for wraps.
    """
    return f"<<<{m.group(0)}>>>"


class TestSimple(TestsBase):

    short_string = "The quick brown fox jumps over the lazy dog."
    short_search_str = "quick"
    short_search_re = r"([rd])(o)"
    short_sub_str = "ʞɔınb"
    long_string = textwrap.dedent(
        """\
        Peter Piper picked a peck of pickled peppers
        A peck of pickled peppers Peter Piper picked
        If Peter Piper picked a peck of pickled peppers
        Where’s the peck of pickled peppers Peter Piper picked? \
        """,
    )
    long_search_str = "peck"
    long_search_re = r"(pick)(led)?\b"
    long_sub_str = "ʞɔǝd"

    def test_basic_str_str(self):
        self.assertEqual(
            unidecode_replace(
                self.short_string, self.short_search_str, self.short_sub_str,
            ),
            self.short_string.replace(
                self.short_search_str, self.short_sub_str,
            ),
        )
        self.assertEqual(
            unidecode_replace(
                self.long_string, self.long_search_str, self.long_sub_str,
            ),
            self.long_string.replace(self.long_search_str, self.long_sub_str),
        )
        self.assertEqual(
            unidecode_replace(
                self.long_string, self.long_search_str, self.long_sub_str,
                count=2,
            ),
            self.long_string.replace(
                self.long_search_str, self.long_sub_str, 2,
            ),
        )

    def test_basic_re_str(self):
        self.assertEqual(
            unidecode_replace(
                self.short_string,
                re.compile(self.short_search_re),
                self.short_sub_str,
            ),
            re.sub(
                self.short_search_re,
                self.short_sub_str,
                self.short_string,
            ),
        )
        self.assertEqual(
            unidecode_replace(
                self.long_string,
                re.compile(self.long_search_re),
                self.long_sub_str,
            ),
            re.sub(
                self.long_search_re,
                self.long_sub_str,
                self.long_string,
            ),
        )
        self.assertEqual(
            unidecode_replace(
                self.long_string,
                re.compile(self.long_search_re),
                self.long_sub_str,
                count=2,
            ),
            re.sub(
                self.long_search_re,
                self.long_sub_str,
                self.long_string,
                2,
            ),
        )

    def test_re_str_str(self):
        self.assertEqual(
            unidecode_replace(
                self.short_string,
                self.short_search_re,
                self.short_sub_str,
                re_search=True,
            ),
            re.sub(
                self.short_search_re,
                self.short_sub_str,
                self.short_string,
            ),
        )
        self.assertEqual(
            unidecode_replace(
                self.long_string,
                self.long_search_re,
                self.long_sub_str,
                re_search=True,
            ),
            re.sub(
                self.long_search_re,
                self.long_sub_str,
                self.long_string,
            ),
        )
        self.assertEqual(
            unidecode_replace(
                self.long_string,
                self.long_search_re,
                self.long_sub_str,
                re_search=True,
                count=2,
            ),
            re.sub(
                self.long_search_re,
                self.long_sub_str,
                self.long_string,
                2,
            ),
        )

    def test_basic_str_callback(self):
        self.assertEqual(
            unidecode_replace(
                self.short_string, self.short_search_str, _fs,
            ),
            self.short_string.replace(
                self.short_search_str, 2 * self.short_search_str,
            ),
        )
        self.assertEqual(
            unidecode_replace(
                self.long_string, self.long_search_str, _fs,
            ),
            self.long_string.replace(
                self.long_search_str, 2 * self.long_search_str,
            ),
        )
        self.assertEqual(
            unidecode_replace(
                self.long_string, self.long_search_str, _fs,
                count=2,
            ),
            self.long_string.replace(
                self.long_search_str, 2 * self.long_search_str, 2,
            ),
        )

    def test_basic_re_callback(self):
        self.assertEqual(
            unidecode_replace(
                self.short_string,
                re.compile(self.short_search_re),
                _fr,
            ),
            re.sub(
                self.short_search_re,
                _fr,
                self.short_string,
            ),
        )
        self.assertEqual(
            unidecode_replace(
                self.long_string,
                re.compile(self.long_search_re),
                _fr,
            ),
            re.sub(
                self.long_search_re,
                _fr,
                self.long_string,
            ),
        )
        self.assertEqual(
            unidecode_replace(
                self.long_string,
                re.compile(self.long_search_re),
                _fr,
                count=2,
            ),
            re.sub(
                self.long_search_re,
                _fr,
                self.long_string,
                2,
            ),
        )

    def test_re_str_callback(self):
        self.assertEqual(
            unidecode_replace(
                self.short_string,
                self.short_search_re,
                _fr,
                re_search=True,
            ),
            re.sub(
                self.short_search_re,
                _fr,
                self.short_string,
            ),
        )
        self.assertEqual(
            unidecode_replace(
                self.long_string,
                self.long_search_re,
                _fr,
                re_search=True,
            ),
            re.sub(
                self.long_search_re,
                _fr,
                self.long_string,
            ),
        )
        self.assertEqual(
            unidecode_replace(
                self.long_string,
                self.long_search_re,
                _fr,
                re_search=True,
                count=2,
            ),
            re.sub(
                self.long_search_re,
                _fr,
                self.long_string,
                2,
            ),
        )

    def test_lists(self):
        self.assertEqual(
            unidecode_replace(
                self.short_string,
                [self.short_search_str, re.compile(self.short_search_re)],
                [self.short_sub_str, "XXX"],
            ),
            re.sub(
                self.short_search_re,
                "XXX",
                self.short_string.replace(
                    self.short_search_str, self.short_sub_str,
                ),
            ),
        )
        self.assertEqual(
            unidecode_replace(
                self.long_string,
                [self.long_search_str, re.compile(self.long_search_re)],
                [self.long_sub_str, "XXX"],
            ),
            re.sub(
                self.long_search_re,
                "XXX",
                self.long_string.replace(
                    self.long_search_str, self.long_sub_str,
                ),
            ),
        )
        self.assertEqual(
            unidecode_replace(
                self.long_string,
                [self.long_search_str, re.compile(self.long_search_re)],
                [self.long_sub_str, "XXX"],
                count=3,
            ),
            re.sub(
                self.long_search_re,
                "XXX",
                self.long_string.replace(
                    self.long_search_str, self.long_sub_str, 2,
                ),
                1,
            ),
        )

    def test_basic_list_str(self):
        self.assertEqual(
            unidecode_replace(
                self.short_string,
                [self.short_search_str, re.compile(self.short_search_re)],
                self.short_sub_str,
            ),
            re.sub(
                self.short_search_re,
                self.short_sub_str,
                self.short_string.replace(
                    self.short_search_str, self.short_sub_str,
                ),
            ),
        )
        self.assertEqual(
            unidecode_replace(
                self.long_string,
                [self.long_search_str, re.compile(self.long_search_re)],
                self.long_sub_str,
            ),
            re.sub(
                self.long_search_re,
                self.long_sub_str,
                self.long_string.replace(
                    self.long_search_str, self.long_sub_str,
                ),
            ),
        )
        self.assertEqual(
            unidecode_replace(
                self.long_string,
                [self.long_search_str, re.compile(self.long_search_re)],
                self.long_sub_str,
                count=3,
            ),
            re.sub(
                self.long_search_re,
                self.long_sub_str,
                self.long_string.replace(
                    self.long_search_str, self.long_sub_str, 2,
                ),
                1,
            ),
        )

    def test_wrap(self):
        self.assertEqual(
            unidecode_wrap(
                self.short_string,
                [self.short_search_str, re.compile(self.short_search_re)],
                "<<<",
                ">>>",
            ),
            re.sub(
                f"{re.escape(self.short_search_str)}|{self.short_search_re}",
                _fw,
                self.short_string,
            ),
        )
        self.assertEqual(
            unidecode_wrap(
                self.long_string,
                [self.long_search_str, re.compile(self.long_search_re)],
                "<<<",
                ">>>",
            ),
            re.sub(
                f"{re.escape(self.long_search_str)}|{self.long_search_re}",
                _fw,
                self.long_string,
            ),
        )
        self.assertEqual(
            unidecode_wrap(
                self.long_string,
                [self.long_search_str, re.compile(self.long_search_re)],
                "<<<",
                ">>>",
                count=3,
            ),
            re.sub(
                f"{re.escape(self.long_search_str)}|{self.long_search_re}",
                _fw,
                self.long_string,
                3,
            ),
        )

    def test_search_item_repr(self):
        import unidecode_replace.search_item as module
        for class_name, search_repr in (
            ("SearchItemStr", "'ex'"),
            ("SearchItemRegex", "re.compile('ex')"),
        ):
            class_ = getattr(module, class_name)
            instance = class_(
                UnidecodeReplace("Text", "ex", "Sub"),
                "ex",
                "Sub",
            )
            self.assertEqual(
                repr(instance),
                f"{class_name}({search_repr}, 'Sub', pos=-1)",
            )
            instance.next()
            self.assertEqual(
                repr(instance),
                f"{class_name}({search_repr}, 'Sub', pos=1)",
            )

    def test_overlaps(self):
        self.assertEqual(
            unidecode_replace("ababa", "aba", "x"),
            "xba",
        )
        self.assertEqual(
            unidecode_replace("ababa", "aba", "x", allow_overlaps=True),
            "xx",
        )
        self.assertEqual(
            unidecode_replace("abcababc", "aba", "x", allow_overlaps=True),
            "abcxbc",
        )
        self.assertEqual(
            unidecode_replace("abcababac", "aba", "x", allow_overlaps=True),
            "abcxxc",
        )

    def test_empty_search(self):
        with self.assertRaises(ValueError):
            unidecode_replace("Text", list(), "something")
        with self.assertRaises(ValueError):
            unidecode_replace("Text", "", "something")
        with self.assertRaises(ValueError):
            unidecode_replace("Text", "", "something", re_search=True)

    def test_wrong_search_type(self):
        with self.assertRaises(TypeError):
            unidecode_replace("Text", 13.17, "something")

    def test_wrong_amount_of_subs(self):
        # No subs for one search.
        with self.assertRaises(ValueError):
            unidecode_replace("Text", "something", list())

        # Too many subs for one search.
        with self.assertRaises(ValueError):
            unidecode_replace("Text", "something", ["foo", "bar"])

        # No subs for multiple searches.
        with self.assertRaises(ValueError):
            unidecode_replace("Text", ["some", "thing"], list())

        # Too few subs for multiple searches.
        with self.assertRaises(ValueError):
            unidecode_replace("Text", ["some", "th", "ing"], ["foo", "bar"])

        # Too many subs for multiple searches.
        with self.assertRaises(ValueError):
            unidecode_replace("Text", ["some", "thing"], ["foo", "bar", "fb"])

    def test_wrong_sub(self):
        with self.assertRaises(TypeError):
            unidecode_replace("Text", "foo", 13.17)

    def test_bad_count(self):
        with self.assertRaises(ValueError):
            unidecode_replace("Text", "foo", "bar", count=-17)
        with self.assertRaises(ValueError):
            unidecode_replace("Text", "foo", "bar", count=17.19)

    def test_search_item_init(self):
        import unidecode_replace.search_item as module
        for class_name in ("SearchItemStr", "SearchItemRegex"):
            class_ = getattr(module, class_name)
            self.assertEqual(
                class_(
                    UnidecodeReplace("Text", "ex", "Sub"),
                    "ex",
                    "Sub",
                ).get_start_end(),
                (-1, -1),
            )

    def test_edge_cases(self):
        self.assertEqual(unidecode_replace("aba", "aba", "xyz"), "xyz")
        self.assertEqual(unidecode_replace("abab", "aba", "xyz"), "xyzb")
        self.assertEqual(unidecode_replace("abab", "bab", "xyz"), "axyz")
        self.assertEqual(unidecode_replace("ab~ab", "ab", "xyz"), "xyz~xyz")
        self.assertEqual(unidecode_replace(7 * "ab", "ab", "xyz"), 7 * "xyz")

    def test_pos_endpos(self):
        # In effect, same searches and replacements, but one is a search by a
        # string and the other is a search by a regular expression.
        for search_by, search in (
            ("string", "a"), ("regex", re.compile(r"[ay]")),
        ):
            self.assertEqual(
                unidecode_replace("abacada", search, "X"),
                "XbXcXdX",
                msg=f"search by {search_by}",
            )

            self.assertEqual(
                unidecode_replace("abacada", search, "X", pos=0),
                "XbXcXdX",
                msg=f"search by {search_by}",
            )
            self.assertEqual(
                unidecode_replace("abacada", search, "X", pos=1),
                "abXcXdX",
                msg=f"search by {search_by}",
            )
            self.assertEqual(
                unidecode_replace("abacada", search, "X", pos=2),
                "abXcXdX",
                msg=f"search by {search_by}",
            )
            self.assertEqual(
                unidecode_replace("abacada", search, "X", pos=3),
                "abacXdX",
                msg=f"search by {search_by}",
            )

            self.assertEqual(
                unidecode_replace("abacada", search, "X", endpos=7),
                "XbXcXdX",
                msg=f"search by {search_by}",
            )
            self.assertEqual(
                unidecode_replace("abacada", search, "X", endpos=6),
                "XbXcXda",
                msg=f"search by {search_by}",
            )
            self.assertEqual(
                unidecode_replace("abacada", search, "X", endpos=5),
                "XbXcXda",
                msg=f"search by {search_by}",
            )
            self.assertEqual(
                unidecode_replace("abacada", search, "X", endpos=4),
                "XbXcada",
                msg=f"search by {search_by}",
            )

            self.assertEqual(
                unidecode_replace("abacada", search, "X", pos=0, endpos=7),
                "XbXcXdX",
                msg=f"search by {search_by}",
            )
            self.assertEqual(
                unidecode_replace("abacada", search, "X", pos=1, endpos=6),
                "abXcXda",
                msg=f"search by {search_by}",
            )
            self.assertEqual(
                unidecode_replace("abacada", search, "X", pos=2, endpos=5),
                "abXcXda",
                msg=f"search by {search_by}",
            )
            self.assertEqual(
                unidecode_replace("abacada", search, "X", pos=3, endpos=4),
                "abacada",
                msg=f"search by {search_by}",
            )

    def test_get_next_pos_done(self):
        for unidecoded_search in (True, False):
            unidecode_replace = UnidecodeReplace(
                "abcd", "b", "X", unidecoded_search=unidecoded_search,
            )
            for i in range(2, 4):
                self.assertEqual(
                    unidecode_replace.search_items[0].get_next_pos(),
                    i,
                    f"unidecoded_search={unidecoded_search}, i={i}",
                )
            self.assertEqual(
                unidecode_replace.search_items[0].get_next_pos(),
                -1,
                f"unidecoded_search={unidecoded_search}, last one",
            )

    def test_check_consecutives(self):
        self.assertEqual(unidecode_replace("abba", "b", "X"), "aXXa")
        self.assertEqual(
            unidecode_replace("abca", "[bc]", "X", re_search=True),
            "aXXa",
        )

    def test_case_insensitive(self):
        self.assertEqual(
            unidecode_replace("abcdABCD", "b", "X"),
            "aXcdABCD",
        )
        self.assertEqual(
            unidecode_replace("abcdABCD", "b", "X", str_case_sensitive=False),
            "aXcdAXCD",
        )
        self.assertEqual(
            unidecode_replace("abcdABCD", "[bd]", "X", re_search=True),
            "aXcXABCD",
        )
        self.assertEqual(
            unidecode_replace(
                "abcdABCD",
                "[bd]",
                "X",
                re_search=True,
                str_case_sensitive=False,
            ),
            "aXcXABCD",
        )
        self.assertEqual(
            unidecode_replace(
                "abcdABCD", "[bd]", "X", re_search=True, re_flags=re.I,
            ),
            "aXcXAXCX",
        )
