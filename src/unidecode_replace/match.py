"""
Unidecode-compatible wrapper for `re.Match`.
"""

import re
from typing import Optional, TypeVar, TYPE_CHECKING, cast


if TYPE_CHECKING:
    from .replace import UnidecodeReplace  # pragma: no cover


_T = TypeVar("_T")


def _nnstr(s: Optional[str]) -> str:
    """
    Return non-`None` string (empty string if `s` is `None` or `s` otherwise).
    """
    return "" if s is None else s


class UnidecodeReMatch:
    """
    Unidecode-compatible wrapper for `re.Match`.

    This class offers the same functionality as `re.Match`, but it re-mapps
    the results (for example, indices) as defined by its `unidecode_replace`
    parent.

    In other words, `self._original` matches a part of unidecoded string on
    which the search is being done, while `self` itself does the same for the
    original string that was given to `unidecode_replace` instance.
    """

    def __init__(
        self,
        unidecode_replace: "UnidecodeReplace",
        original: re.Match,
    ) -> None:
        self._unidecode_replace = unidecode_replace
        self._original = original

    @property
    def unidecode_replace(self) -> "UnidecodeReplace":
        """
        Return instance's `unidecode_replace` parent.

        This is a property so that the value would be read-only (i.e.,
        protected from accidental changes).
        """
        return self._unidecode_replace

    @property
    def original(self) -> re.Match:
        """
        Return the original `re.Match` instance (without re-mapping).
        """
        return self._original

    @staticmethod
    def _dot_re(s: Optional[str], name: Optional[str] = None) -> str:
        """
        Return a subexpression for a regex group to match string `s`.

        For details, see :py:meth:`_get_fake_match`.

        :param s: What the result should match when used as a regular
            expression. This is generally a string, but it can also be `None`,
            which results in a group `()??` or `(?P<name>)??` that never
            matches.
        :param name: If defined, this is the name for a named group. If
            omitted, the created regex group remains unnamed.
        :return: A regex pattern.
        """
        if is_none := (s is None):
            regex = ""
        else:
            str_len = len(s)
            regex = "." * str_len if str_len <= 4 else f".{{{str_len}}}"
        if name is not None:
            regex = f"?P<{name}>{regex}"
        result = f"({regex})"
        if is_none:
            result += "??"  # non-greedy, to make sure it matches `None`
        return result

    def _get_fake_match(self) -> re.Match[str]:
        """
        Return a `re.Match` instance to be used with :py:meth:`expand`.

        In :py:meth:`expand`, we need a working `re.Match` instance, but
        populated from `self.unidecode_replace.string`. The one that we have
        came from its unidecoded version, so its groups might have unidecoded
        values instead of the original ones.

        However, populating one manually does not seem possible. So, this
        method is used to create a fake regular expression and a string that,
        when matched, result in a `re.Match` instance populated in the way that
        :py:meth:`expand` requires.
        """
        groups = self.groups()
        regex = ""
        string = ""
        gr_idx = 0
        for name, value in self.groupdict().items():
            while True:
                gr_value = groups[gr_idx]
                gr_idx += 1
                string += _nnstr(gr_value)
                if value == gr_value:
                    regex += self._dot_re(gr_value, name)
                    break
                else:
                    regex += self._dot_re(gr_value)
        while gr_idx < len(groups):
            gr_value = groups[gr_idx]
            regex += self._dot_re(gr_value)
            string += _nnstr(gr_value)
            gr_idx += 1
        result = re.match(f"{regex}$", string)
        if result is None:
            raise RuntimeError(  # pragma: no cover
                f"BUG: invalid regex {repr(regex)} for string {repr(string)}",
            )
        else:
            return result

    def expand(self, /, template: str) -> str:
        """
        Unidecode-compatible version of :py:meth:`re.Match.expand`.
        """
        return self._get_fake_match().expand(template)

    def group(
        self, *groups: int | str,
    ) -> Optional[str] | tuple[Optional[str], ...]:
        """
        Unidecode-compatible version of :py:meth:`re.Match.group`.
        """
        result = tuple(
            self.string[start:end] if start >= 0 and end >= 0 else None
            for start, end in (
                (self.start(group), self.end(group)) for group in groups
            )
        )
        return result[0] if len(result) == 1 else result

    def __getitem__(self, g: int | str) -> Optional[str]:
        """
        Return `self.group(g)`.
        """
        return cast(Optional[str], self.group(g))

    def groups(self, default: _T = None) -> tuple[Optional[str | _T], ...]:
        """
        Unidecode-compatible version of :py:meth:`re.Match.groups`.
        """
        return tuple(
            # value cannot be a tuple because we don't call `group(...)` with
            # multiple names.
            default if value is None else cast(str, value)
            for value in (
                self.group(group_idx)
                for group_idx in range(1, len(self.original.groups()) + 1)
            )
        )

    def groupdict(self, default: _T = None) -> dict[str, Optional[str | _T]]:
        """
        Unidecode-compatible version of :py:meth:`re.Match.groupdict`.
        """
        return {
            # value cannot be a tuple because we don't call `group(...)` with
            # multiple names.
            name: default if value is None else cast(Optional[str], value)
            for name, value in (
                (name, self.group(name)) for name in self.original.groupdict()
            )
        }

    def start(self, group: int | str = 0) -> int:
        """
        Unidecode-compatible version of :py:meth:`re.Match.start`.
        """
        u_start = self.original.start(group)
        return -1 if u_start < 0 else self.unidecode_replace.u2i[u_start]

    def end(self, group: int | str = 0) -> int:
        """
        Unidecode-compatible version of :py:meth:`re.Match.end`.
        """
        u_end = self.original.end(group)
        return -1 if u_end < 0 else self.unidecode_replace.u2i[u_end]

    def span(self, group: int | str = 0) -> tuple[int, int]:
        """
        Unidecode-compatible version of :py:meth:`re.Match.end`.
        """
        return (self.start(group), self.end(group))

    @property
    def pos(self) -> int:
        """
        Unidecode-compatible version of :py:meth:`re.Match.pos`.
        """
        return self.unidecode_replace.pos

    @property
    def endpos(self) -> int:
        """
        Unidecode-compatible version of :py:meth:`re.Match.endpos`.
        """
        return self.unidecode_replace.endpos

    @property
    def lastindex(self) -> Optional[int]:
        """
        Unidecode-compatible version of :py:meth:`re.Match.lastindex`.

        Note that there is nothing unidecode-specific here.
        """
        return self.original.lastindex

    @property
    def lastgroup(self) -> Optional[str]:
        """
        Unidecode-compatible version of :py:meth:`re.Match.lastgroup`.

        Note that there is nothing unidecode-specific here.
        """
        return self.original.lastgroup

    @property
    def re(self) -> re.Pattern:
        """
        Return the regular expression's pattern.

        Note that there is nothing unidecode-specific here.
        """
        return self.original.re

    @property
    def string(self) -> str:
        """
        Return the original string that was searched on.

        Note that there is nothing unidecode-specific here (i.e., the string is
        not unidecoded).
        """
        return self.unidecode_replace.string
