"""
Functions for easier calls to `UnidecodeReplace`.
"""

import re
from typing import Optional

from .match import UnidecodeReMatch
from .replace import SearchT, SubT, UnidecodeReplace


def unidecode_replace(
    string: str,
    search: SearchT,
    sub: SubT,
    *,
    allow_overlaps: bool = False,
    re_search: bool = False,
    re_flags: re.RegexFlag = re.RegexFlag(0),
    count: Optional[int] = None,
    pos: Optional[int] = None,
    endpos: Optional[int] = None,
    unidecoded_search: bool = True,
    str_case_sensitive: bool = True,
) -> str:
    """
    Return string with bits replaced if they match transliteration searches.

    ```
    >>> unidecode_sub("\u5317\u4EB0", ["\u4EB0"], ["Replacement"])
    "Bei Replacement"
    >>> unidecode_sub("Jing", ["\u4EB0"], ["Replacement"])
    "Bei Replacement"
    ```

    This function performs replacement similar to `string.replace` for each
    pair of same-indexed values in `search` and `sub`, but with
    some differences:

    1. The searching is done on transliterated `string` and with transliterated
       values of `search`.

    2. The values in `sub` can be strings or callables (which accept
       one argument, the substring in the original `string` to be replaced).

    If `allow_overlaps` is set to `True`, substitutions will happen on the
    previously unsubstituted parts of overlapping matches.

    ```
    >>> unidecode_sub("abcde", ["bc", "cd"], ["BC", "CD"], allow_overlaps=True)
    'aBCCDe'
    >>> unidecode_sub("abcde", ["bc", "cd"], repr, allow_overlaps=True)
    "a'bc''d'e"
    ```

    This has some uses if, for example, you want to add colour to your text to
    mark found substrings. With Colorama, it would look like this:

    ```
    >>> unidecode_sub(
    ...     text,
    ...     search,
    ...     lambda s: f"{Fore.RED}{s}{Fore.RESET}",
    ...     allow_overlaps=True,
    ... )
    ```

    Allowing overlaps with string substitutes instead of callbacks is likely to
    ruin your text, as seen in the first overlap example above.

    :param string: The input string on which the search and replace are
        performed.
    :param search: A search string or a regex, or a sequence of them.
    :param sub: A replacement string or a function, or a sequence of them.
    :param allow_overlaps: If `True`, overlapping instances of found text are
        replaced.
    :param re_search: If `True` and `search` is a string, it'll be compiled as
        a regular expression. If it's a sequence, any string in it will also be
        compiled.
    :param re_flags: Flags used when compiling regular expressions (if
        `re_search` is set to `True`).
    :param count: If set, only the first `count` occurrences are replaced.
    :param pos, endpos: If defined, search and replace will only be done from
        positions `pos` (default: 0) to `endpos - 1` (defaulting to the end of
        `string`).
    :param unidecoded_search: If set to `False`, the search will be literal
        (i.e., not based on the unidecoded version of `string`). This behaves
        equivalently to `str.replace` and `re.sub`, but with the added benefit
        of doing multiple searches in one pass and allowing one to use `pos`
        and `endpos`.
    :param str_case_sensitive: If set to `True`, string searches will be
        performed in case-sensitive manner. If set to `False`, string searches
        will be performed in case-insensitive manner. This setting does not
        affect regex searching.
    :return: A copy of `string` with matched substrings replaced.
    """
    return UnidecodeReplace(
        string,
        search,
        sub,
        allow_overlaps=allow_overlaps,
        re_search=re_search,
        re_flags=re_flags,
        count=count,
        pos=pos,
        endpos=endpos,
        unidecoded_search=unidecoded_search,
        str_case_sensitive=str_case_sensitive,
    ).run()


def unidecode_wrap(
    string: str,
    search: SearchT,
    prefix: str,
    suffix: str,
    *,
    allow_overlaps: bool = False,
    re_search: bool = False,
    re_flags: re.RegexFlag = re.RegexFlag(0),
    count: Optional[int] = None,
    pos: Optional[int] = None,
    endpos: Optional[int] = None,
    unidecoded_search: bool = True,
    str_case_sensitive: bool = True,
) -> str:
    """
    Return string with bits wrapped if they match transliteration searches.

    :param string: The input string on which the search and replace are
        performed.
    :param search: A search string or a regex, or a sequence of them.
    :param prefix: A string to prepend to each matched substring.
    :param prefix: A string to append to each matched substring.
    :param allow_overlaps: If `True`, overlapping instances of found text are
        replaced.
    :param re_search: If `True` and `search` is a string, it'll be compiled as
        a regular expression. If it's a sequence, any string in it will also be
        compiled.
    :param re_flags: Flags used when compiling regular expressions (if
        `re_search` is set to `True`).
    :param count: If set, only the first `count` occurrences are replaced.
    :param pos, endpos: If defined, search and replace will only be done from
        positions `pos` (default: 0) to `endpos - 1` (defaulting to the end of
        `string`).
    :param unidecoded_search: If set to `False`, the search will be literal
        (i.e., not based on the unidecoded version of `string`). This behaves
        equivalently to `str.replace` and `re.sub`, but with the added benefit
        of doing multiple searches in one pass and allowing one to use `pos`
        and `endpos`.
    :param str_case_sensitive: If set to `True`, string searches will be
        performed in case-sensitive manner. If set to `False`, string searches
        will be performed in case-insensitive manner. This setting does not
        affect regex searching.
    :return: A copy of `string` with matched substrings replaced.
    """
    def sub(s: str | re.Match | UnidecodeReMatch) -> str:
        text = s.group(0) if isinstance(s, (re.Match, UnidecodeReMatch)) else s
        return f"{prefix}{text}{suffix}"

    return unidecode_replace(
        string,
        search,
        sub,
        allow_overlaps=allow_overlaps,
        re_search=re_search,
        re_flags=re_flags,
        count=count,
        pos=pos,
        endpos=endpos,
        unidecoded_search=unidecoded_search,
        str_case_sensitive=str_case_sensitive,
    )
