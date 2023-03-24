"""
`SearchItem` and its subclasses.

These are used to keep search items while performing replace operation. Their
purpose is internal and they should not be used outside of the package.
"""

import abc
import re
from typing import TYPE_CHECKING, Optional, cast, Iterator

from unidecode import unidecode

from .match import UnidecodeReMatch


if TYPE_CHECKING:
    from .replace import (  # pragma: no cover
        UnidecodeReplace, SearchT, SimpleSubT,
    )


class SearchItem(abc.ABC):
    """
    One search item.
    """

    def __init__(
        self,
        unidecode_replace: "UnidecodeReplace",
        one_search: "SearchT",
        one_sub: "SimpleSubT",
    ) -> None:
        self.unidecode_replace = unidecode_replace
        self.search = one_search

        if not (isinstance(one_sub, str) or callable(one_sub)):
            raise TypeError("sub must be strings or callables")
        self.sub = one_sub

        self._pos = -1
        self._pos_iter: Optional[Iterator[int]] = None

    @property
    @abc.abstractmethod
    def case_sensitive(self) -> bool:
        """
        Return `True` if any the search is case-sensitive search.
        """
        raise NotImplementedError()  # pragma: no cover

    @property
    def uni_str(self) -> str:
        result = (
            (
                self.unidecode_replace.uni_str
                if self.unidecode_replace.unidecoded_search else
                self.unidecode_replace.string
            )
            if self.case_sensitive else
            self.unidecode_replace.uni_str_lower
        )
        if result is None:
            raise RuntimeError(  # pragma: no cover
                "BUG: uni_str was not created for {repr(self)}",
            )
        else:
            return result

    def reset_search(self) -> int:
        """
        Reset attributes related to the current search position.
        """
        self._pos = -1
        self._pos_iter = (
            iter(self.unidecode_replace.u2i.keys())
            if self.unidecode_replace.unidecoded_search else
            None
        )
        return -1

    def __repr__(self):
        return (
            f"{type(self).__name__}({repr(self.search)}, {repr(self.sub)},"
            f" pos={self.pos})"
        )

    @property
    def pos(self):
        """
        Return position in unidecoded string corresponding to `original_pos`.
        """
        return self._pos

    def get_next_pos(
        self,
        *,
        min_pos: Optional[int] = None,
        min_ipos: Optional[int] = None,
    ) -> int:
        """
        Find and return the next viable value for `self.pos`.
        """
        def pos_is_good():
            return (
                (min_pos is None or self._pos >= max(0, min_pos))
                and (min_ipos is None or u2i[self._pos] >= max(0, min_ipos))
                and (u2i[self._pos] >= self.unidecode_replace.pos)
            )

        u2i = self.unidecode_replace.u2i
        endpos = self.unidecode_replace.endpos

        if (min_pos is not None or min_ipos is not None) and pos_is_good():
            return (
                self._pos if u2i[self._pos] < endpos else self.reset_search()
            )

        if self._pos_iter is None:
            self._pos += 1
            if self._pos >= len(self.unidecode_replace.string):
                return self.reset_search()
            return self._pos

        while True:
            try:
                self._pos = next(self._pos_iter)
            except StopIteration:  # pragma: no cover
                # A failsafe that should not happen. The `if` below should stop
                # it before we run out of `_pos_iter`.
                return self.reset_search()
            if u2i[self._pos] >= endpos:
                return self.reset_search()
            if pos_is_good():
                return self._pos

    @abc.abstractmethod
    def get_start_end(self) -> tuple[int, int]:
        """
        Return start and end indices of the last search in the original string.

        :return: A tuple `(start, end)` such that
            `self.unidecode_replace.string[start:end]` is the substring
            corresponding to the last successfully found unidecoded substring.
            If nothing was found, the return value is `(-1, -1)`.
        """
        raise NotImplementedError()  # pragma: no cover

    def chunk_ok(self, start: int, end: int) -> bool:
        """
        Return `True` if the `start` and `end` are legitimate positions.

        Consider the following example: string `"\u5317\u4EB0"` (i.e.,
        `"北亰"`) is unidecoded as `"Bei Jing "`. This means that `"Bei "`
        (defined by `start = 0, end = 4`) is an ok chunk, but `"ei"` (defined
        by `start = 1, end = 3`) is not because it matches only a part of the
        original characters. We cannot replace `"ei"` but leave `"B"` before it
        and `" "` after it, because they are all together a single character
        `"北"` in the original string and we can only replace or leave the
        whole character. Therefore, the match we found is not valid and this
        method will return `False`.
        """
        u2i = self.unidecode_replace.u2i
        return start in u2i and end in u2i

    @abc.abstractmethod
    def next(self) -> int:
        """
        Perform search and return the next value for `self.pos`.
        """
        raise NotImplementedError()  # pragma: no cover

    @abc.abstractmethod
    def get_replace(self) -> str:
        """
        Return the string that should replace currently found substring.
        """
        raise NotImplementedError()  # pragma: no cover


class SearchItemStr(SearchItem):
    """
    One search string.
    """

    def __init__(
        self,
        unidecode_replace: "UnidecodeReplace",
        one_search: str,
        one_sub: "SimpleSubT",
    ) -> None:
        if not unidecode_replace.str_case_sensitive:
            one_search = one_search.lower()
        if unidecode_replace.unidecoded_search:
            one_search = unidecode(one_search)
        if not one_search:
            raise ValueError("search strings must not be empty")
        super().__init__(unidecode_replace, one_search, one_sub)

    @property
    def case_sensitive(self) -> bool:
        """
        Return `True` if any the search is case-sensitive search.
        """
        return self.unidecode_replace.str_case_sensitive

    def get_start_end(self) -> tuple[int, int]:
        """
        Return start and end indices of the last search in the original string.

        :return: A tuple `(start, end)` such that
            `self.unidecode_replace.string[start:end]` is the substring
            corresponding to the last successfully found unidecoded substring.
            If nothing was found, the return value is `(-1, -1)`.
        """
        pos = self.pos
        u2i = self.unidecode_replace.u2i
        search_str = cast(str, self.search)
        try:
            return u2i[pos], u2i[pos + len(search_str)]
        except KeyError:
            return -1, -1

    def next(self) -> int:
        """
        Perform search and return the next value for `self.pos`.
        """
        pos = self.pos if self.pos >= 0 else self.get_next_pos()
        uni_str = self.uni_str
        search_str = cast(str, self.search)
        while True:
            try:
                pos = uni_str.index(search_str, pos)
            except ValueError:
                return self.reset_search()
            else:
                if (
                    pos == self.get_next_pos(min_pos=pos)
                    and self.chunk_ok(pos, pos + len(search_str))
                ):
                    return pos
            pos = self.get_next_pos(min_pos=pos + 1)
            if pos < 0:
                return -1

    def get_replace(self) -> str:
        """
        Return the string that should replace currently found substring.
        """
        if isinstance(self.sub, str):
            return self.sub
        elif callable(self.sub):
            start, end = self.get_start_end()
            return self.sub(self.unidecode_replace.string[start:end])
        else:
            raise TypeError(  # pragma: no cover
                f"invalid type of a sub: {type(self.sub).__name__}",
            )


class SearchItemRegex(SearchItem):
    """
    One search regex.
    """

    def __init__(
        self,
        unidecode_replace: "UnidecodeReplace",
        one_search: "SearchT",
        one_sub: "SimpleSubT",
    ) -> None:
        if isinstance(one_search, re.Pattern):
            re_flags = re.RegexFlag(one_search.flags)
            one_search = str(one_search.pattern)
            if unidecode_replace.unidecoded_search:
                one_search = unidecode(one_search)
        else:
            re_flags = unidecode_replace.re_flags

        if re.match(f"(?:{one_search})$", ""):
            raise ValueError("search patterns must not match empty strings")

        self._case_sensitive = not (re_flags & re.I)

        one_search = re.compile(one_search, flags=re_flags)

        super().__init__(unidecode_replace, one_search, one_sub)
        self.m: Optional[UnidecodeReMatch] = None

    @property
    def case_sensitive(self) -> bool:
        """
        Return `True` if any the search is case-sensitive search.
        """
        return self._case_sensitive

    def next(self) -> int:
        """
        Perform search and return the next value for `self.pos`.
        """
        pos = self.pos if self.pos >= 0 else self.get_next_pos()
        uni_str = self.uni_str
        search_re = cast(re.Pattern, self.search)
        while True:
            uni_m = search_re.search(uni_str, pos)
            if uni_m is None:
                self.m = None
                return -1
            pos = uni_m.start()
            end = uni_m.end()
            if (
                pos == self.get_next_pos(min_pos=pos)
                and self.chunk_ok(pos, end)
            ):
                self.m = UnidecodeReMatch(self.unidecode_replace, uni_m)
                return pos
            pos = self.get_next_pos(min_pos=pos + 1)
            if pos < 0:
                return -1

    def get_replace(self) -> str:
        """
        Return the string that should replace currently found substring.
        """
        if self.m is None:  # pragma: no cover
            raise ValueError("this should not have happened")
        elif isinstance(self.sub, str):
            return self.m.expand(self.sub)
        elif callable(self.sub):
            return self.sub(self.m)
        else:
            raise TypeError(  # pragma: no cover
                f"invalid type of a sub: {type(self.sub).__name__}",
            )

    def get_start_end(self) -> tuple[int, int]:
        """
        Return start and end indices of the last search in the original string.

        :return: A tuple `(start, end)` such that
            `self.unidecode_replace.string[start:end]` is the substring
            corresponding to the last successfully found unidecoded substring.
            If nothing was found, the return value is `(-1, -1)`.
        """
        if self.m is None:
            return -1, -1
        else:
            return self.m.start(), self.m.end()


def get_search_item(
    unidecode_replace: "UnidecodeReplace",
    one_search: "SearchT",
    one_sub: "SimpleSubT",
) -> SearchItem:
    """
    Return an instance of the correct subclass of `SearchItem` for `search`.

    :param one_search: One search term (a string or a regex pattern) to be
        searched for in the main text.
    :param one_sub: One substitution term (a string or a callable accepting
        a string and a `re.Match` instance).
    :raise TypeError: Raised if `one_search` is neither a string nor a
        `re.Pattern`.
    :return: An instance of the correct subclass of `SearchItem`.
    """
    if unidecode_replace.re_search and isinstance(one_search, str):
        one_search = re.compile(one_search, flags=unidecode_replace.re_flags)
    if isinstance(one_search, str):
        return SearchItemStr(unidecode_replace, one_search, one_sub)
    elif isinstance(one_search, re.Pattern):
        return SearchItemRegex(
            unidecode_replace, one_search, one_sub,
        )
    else:
        raise TypeError("search items must be strings or re.Pattern instances")
