"""
Unidecode-compatible string replacing.
"""

from copy import deepcopy
import itertools
import re
from typing import cast, TypeAlias, Callable, Sequence, Any, Optional

from .match import UnidecodeReMatch
from .replicas import unidecode_repl
from .search_item import SearchItem, get_search_item


SimpleSearchT: TypeAlias = str | re.Pattern
SearchT: TypeAlias = SimpleSearchT | Sequence[SimpleSearchT]
SimpleSubT: TypeAlias = (
    str | Callable[[str | re.Match | UnidecodeReMatch], str]
)
NormalizedSubT: TypeAlias = list[SimpleSubT]
SubT: TypeAlias = SimpleSubT | Sequence[SimpleSubT]
u2iT: TypeAlias = dict[int, int]


class _NoUnidecodingDict(u2iT):
    """
    Dictionary that returns the value of the key for missing keys.

    This is used to mimic `u2i` for non-unidecoded strings (when
    `unidecoded_search` in `UnidecodeReplace` is set to `False`).
    """

    def __missing__(self, key: int) -> int:
        return key

    def __contains__(self, key: object) -> bool:
        return True  # The length of `string` is ignored.


class UnidecodeReplace:
    """
    Unidecode-compatible string replacing.
    """

    def __init__(
        self,
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
    ) -> None:
        self.string = string
        self.search = search
        self.sub = sub
        self.allow_overlaps = allow_overlaps
        self.re_search = re_search
        self.re_flags = re_flags
        self.count = count
        self.pos = 0 if pos is None else pos
        self.endpos = (
            len(string) if endpos is None else min(len(string), endpos)
        )
        self.unidecoded_search = unidecoded_search
        self.str_case_sensitive = str_case_sensitive

        self.search_items = self._get_search_items()
        self.u2i, self.uni_str, self.uni_str_lower = self._get_unis()
        self._init_search_items()

    def _get_search_items(self) -> list[SearchItem]:
        """
        Return a list of `SearchItem` instances from `self.search`.
        """
        def is_proper_sequence(obj: Any) -> bool:
            """
            Return `True` if `obj` is a sequence, but not a string.
            """
            return isinstance(obj, Sequence) and not isinstance(obj, str)

        # Make sure that they are lists (and also copies of originals, not just
        # references).
        search = (
            list(deepcopy(self.search))  # type: ignore
            if is_proper_sequence(self.search) else
            [deepcopy(self.search)]  # type: ignore
        )
        sub = cast(
            NormalizedSubT,
            (
                list(deepcopy(self.sub))  # type: ignore
                if is_proper_sequence(self.sub) else
                [deepcopy(self.sub)]
            ),
        )

        # Check that we have something to search for.
        if not search:
            raise ValueError(
                "at least one search string or re.Pattern must be provided",
            )

        # Check that substitutions make sense and prepare the result.
        if len(search) == len(sub):
            result = [
                get_search_item(
                    self,
                    one_search,
                    one_sub,
                )
                for one_search, one_sub in zip(search, sub)
            ]
        elif len(sub) == 1:
            one_sub = sub[0]
            result = [
                get_search_item(
                    self,
                    one_search,
                    one_sub,
                )
                for one_search in search
            ]
        else:
            raise ValueError(
                "the number of search and sub terms must be equal (or there"
                " must be exactly one sub)",
            )

        return result

    def _init_search_items(self) -> None:
        """
        Initialize search items.
        """
        for search_item in self.search_items:
            search_item.reset_search()

        self.search_items[:] = [
            search_item
            for search_item in self.search_items
            if search_item.next() >= 0
        ]

    def _case_sensitive_needed(self) -> bool:
        """
        Return `True` if any of the searches is case-sensitive.
        """
        return any(
            search_item.case_sensitive for search_item in self.search_items
        )

    def _case_insensitive_needed(self) -> bool:
        """
        Return `True` if any of the searches is case-insensitive.
        """
        return any(
            not search_item.case_sensitive for search_item in self.search_items
        )

    def _get_unis(self) -> tuple[u2iT, Optional[str], Optional[str]]:
        """
        Return `u2i` mapping, plus search versions of `self.string`.

        The `u2i` mapping is a mapping of indexes from unidecoded string to the
        original one (`self.string`). This is needed because searching is done
        on the unidecoded string, while the replacing is supposed to be done on
        the original one.

        The two strings are unidecoded (or not, depending on
        `self.unidecoded_search`) and lowercase version of that if any of the
        searches require case-insensitive search.
        """
        def cased_result(
            u2i: u2iT, uni_str: str,
        ) -> tuple[u2iT, Optional[str], Optional[str]]:
            if self._case_sensitive_needed() and self.unidecoded_search:
                result_uni_str = uni_str
            else:
                result_uni_str = None
            if self._case_insensitive_needed():
                result_uni_str_lower = uni_str.lower()
            else:
                result_uni_str_lower = None
            return u2i, result_uni_str, result_uni_str_lower

        if not self.unidecoded_search:
            return cased_result(_NoUnidecodingDict(), self.string)

        uni_str = self.string

        # Unidecoded string as a list of unidecoded chunks to be merged.
        unidecoded_list = list(unidecode_repl(uni_str, "preserve"))

        # Mapping for unidecoded indexes to original ones ("unidecoded 2
        # index").
        u2i = dict(
            zip(
                itertools.accumulate(
                    (len(uni_str) for uni_str in unidecoded_list),
                    initial=0,
                ),
                range(len(unidecoded_list) + 1),
            ),
        )

        # This is really just `unidecode(string)`, but we couldn't call it
        # directly as we needed the intermediate step as the list used for
        # `u2i` above.
        uni_str = "".join(unidecoded_list)

        return cased_result(u2i, uni_str)

    @staticmethod
    def _skip_overlaps(search_items: list[SearchItem], last_pos: int) -> None:
        """
        Reposition search items' `pos` after an overlap and remove spent ones.
        """
        to_remove = [
            idx
            for idx, search_item in enumerate(search_items)
            if search_item.get_next_pos(min_ipos=last_pos) == -1
        ]
        for idx in to_remove[::-1]:
            del search_items[idx]

    def run(self) -> str:
        """
        Return `string` with unidecode-compatible replacements.

        For details, see :py:func:`unidecode_replace`.
        """
        count = self.count
        if not (count is None or (isinstance(count, int) and count > 0)):
            raise ValueError("count must be None or a positive integer")

        result = ""
        last_pos = 0
        matches = 0
        while self.search_items:
            si_idx, search_item = min(
                enumerate(self.search_items), key=lambda item: item[1].pos,
            )
            pos, next_pos = search_item.get_start_end()
            if pos >= last_pos or self.allow_overlaps:
                if last_pos > pos:
                    pos = last_pos
                sub = search_item.get_replace()
                result = f"{result}{self.string[last_pos:pos]}{sub}"
                last_pos = next_pos
                if count is not None:
                    matches += 1
                    if matches >= count:
                        break
                if self.allow_overlaps:
                    search_item.get_next_pos(min_ipos=pos + 1)
                else:
                    self._skip_overlaps(self.search_items, last_pos)
            if search_item.next() < 0:
                del self.search_items[si_idx]
            pos = last_pos
        result = f"{result}{self.string[last_pos:]}"
        return result
