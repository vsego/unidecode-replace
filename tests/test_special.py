"""
Tests for the cases where unidecode comes into play.

The tests here should produce the results different from :py:func:`str.replace`
and :py:func:`re.sub`.

I don't speak Chinese. The examples used were picked from the list
[here](https://www.digmandarin.com/120-daily-used-short-sentences.html), and
filtered to have recurring characters (to check for multiple matches).
"""

import re

from unidecode import unidecode

from unidecode_replace import unidecode_replace, unidecode_wrap

from .utils import TestsBase


class TestSpecial(TestsBase):

    short_string = "他现在已经在路上了。"
    short_result = "他现失踪已经失踪路上了。"
    long_string = short_string + unidecode(short_string)
    search_str_1 = "在"
    search_str_2 = unidecode(search_str_1)
    search_re_1 = r"(在)(已)"
    search_re_2 = unidecode(search_re_1)
    sub_str = "失踪"

    case_string = "Übergröße oder ÜBERGRÖẞE"
    expected_str_sensitive = "Übergr!ße !der ÜBERGRÖẞE"
    expected_str_insensitive = "Übergr!ße !der ÜBERGR!ẞE"
    expected_regex_sensitive = "Übergr!ße !der ÜBERGRÖẞE"
    expected_regex_insensitive = "!bergr!ße !der !BERGR!ẞE"

    def test_unidecode_str(self):
        self.assertEqual(
            unidecode_replace(
                self.short_string, self.search_str_1, self.sub_str,
            ),
            self.short_result,
        )
        self.assertEqual(
            unidecode_replace(
                self.short_string, self.search_str_2, self.sub_str,
            ),
            self.short_result,
        )

    def test_mixed_str(self):
        def unidecode_except_sub(s: str) -> str:
            """
            Unidecode `s` except for the `sub_str` part.
            """
            return unidecode(s).replace(unidecode(self.sub_str), self.sub_str)

        self.assertEqual(
            unidecode_replace(
                self.long_string, self.search_str_1, self.sub_str,
            ),
            self.short_result + unidecode_except_sub(self.short_result),
        )
        self.assertEqual(
            unidecode_replace(
                self.long_string, self.search_str_2, self.sub_str,
            ),
            self.short_result + unidecode_except_sub(self.short_result),
        )

    def test_mixed_str_not_unidecoded(self):
        self.assertEqual(
            unidecode_replace(
                self.long_string,
                self.search_str_1,
                "XYZ",
                unidecoded_search=False,
            ),
            self.long_string.replace(self.search_str_1, "XYZ"),
        )
        self.assertEqual(
            unidecode_replace(
                self.long_string,
                self.search_str_2,
                "XYZ",
                unidecoded_search=False,
            ),
            self.long_string.replace(self.search_str_2, "XYZ"),
        )

    def test_wrap(self):
        short_result = "他现<<<在>>>已经<<<在>>>路上了。"
        self.assertEqual(
            unidecode_wrap(
                self.long_string, self.search_str_1, "<<<", ">>>",
            ),
            short_result + unidecode(short_result),
        )

    def test_dont_replace_partial_characters(self):
        # See docstring in unidecode_replace.search_item.SearchItem.chunjk_ok.
        self.assertEqual(
            unidecode_replace("北亰", "ei", "sub"),
            "北亰",
        )
        self.assertEqual(
            unidecode_replace("北亰", re.compile("ei"), "sub"),
            "北亰",
        )

    def test_pos_endpos(self):
        self.assertEqual(
            unidecode_wrap(
                self.short_string, self.search_str_1, "<<<", ">>>", pos=3,
            ),
            "他现在已经<<<在>>>路上了。"
        )
        self.assertEqual(
            unidecode_wrap(
                self.short_string, self.search_str_1, "<<<", ">>>", endpos=5,
            ),
            "他现<<<在>>>已经在路上了。"
        )

    def test_case_sensitive(self):
        self.assertEqual(
            unidecode_replace(self.case_string, "ö", "!"),
            self.expected_str_sensitive,
            "Case sensitive string search",
        )
        self.assertEqual(
            unidecode_replace(
                self.case_string, "ö", "!", str_case_sensitive=False,
            ),
            self.expected_str_insensitive,
            "Case insensitive string search",
        )
        self.assertEqual(
            unidecode_replace(
                self.case_string, "[öü]", "!", re_search=True,
            ),
            self.expected_str_sensitive,
            "Case sensitive regex search",
        )

    def test_case_insensitive_re_flags_on_regex(self):
        # str_case_sensitive should have no effect on regex searches.
        for str_case_sensitive in (False, True):
            msg_fmt = (
                f"Case {{}} regex search with"
                f" str_case_sensitive={str_case_sensitive}"
            )
            self.assertEqual(
                unidecode_replace(
                    self.case_string,
                    "[öü]",
                    "!",
                    str_case_sensitive=str_case_sensitive,
                    re_search=True,
                ),
                self.expected_regex_sensitive,
                msg_fmt.format("sensitive"),
            )
            self.assertEqual(
                unidecode_replace(
                    self.case_string,
                    "[öü]",
                    "!",
                    str_case_sensitive=str_case_sensitive,
                    re_search=True,
                    re_flags=re.I,
                ),
                self.expected_regex_insensitive,
                msg_fmt.format("insensitive"),
            )
            self.assertEqual(
                unidecode_replace(
                    self.case_string,
                    re.compile("[öü]"),
                    "!",
                    str_case_sensitive=str_case_sensitive,
                    re_search=True,
                ),
                self.expected_regex_sensitive,
                msg_fmt.format("sensitive"),
            )
            self.assertEqual(
                unidecode_replace(
                    self.case_string,
                    re.compile("[öü]"),
                    "!",
                    str_case_sensitive=str_case_sensitive,
                    re_search=True,
                    re_flags=re.I,  # Should be ignored!
                ),
                self.expected_regex_sensitive,
                msg_fmt.format("sensitive"),
            )
            self.assertEqual(
                unidecode_replace(
                    self.case_string,
                    re.compile("[öü]", flags=re.I),
                    "!",
                    str_case_sensitive=str_case_sensitive,
                    re_search=True,
                ),
                self.expected_regex_insensitive,
                msg_fmt.format("insensitive"),
            )

    def test_case_insensitive_re_flags_on_string(self):
        # re_flags should have no effect on string searches.
        for re_flags in (re.RegexFlag(0), re.I):
            msg_fmt = (
                f"Case {{}} string search with re_flags={re_flags}"
            )
            self.assertEqual(
                unidecode_replace(
                    self.case_string,
                    "ö",
                    "!",
                    re_flags=re_flags,
                ),
                self.expected_str_sensitive,
                msg_fmt.format("sensitive"),
            )
            self.assertEqual(
                unidecode_replace(
                    self.case_string,
                    "ö",
                    "!",
                    re_flags=re_flags,
                    str_case_sensitive=True,
                ),
                self.expected_str_sensitive,
                msg_fmt.format("sensitive"),
            )
            self.assertEqual(
                unidecode_replace(
                    self.case_string,
                    "ö",
                    "!",
                    re_flags=re_flags,
                    str_case_sensitive=False,
                ),
                self.expected_str_insensitive,
                msg_fmt.format("insensitive"),
            )
