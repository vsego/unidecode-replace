"""
Functions that replicate internal functionality needed from `unidecode`.
"""

from typing import TypeAlias, Literal, Iterator
import warnings

from unidecode import UnidecodeError, Cache


ErrorsType: TypeAlias = Literal["ignore", "strict", "replace", "preserve"]


# Copy/paste (with minor code style changes) from unidecode==1.2.0.
def _get_repl_str(char):
    codepoint = ord(char)

    if codepoint < 0x80:
        # Already ASCII
        return str(char)

    if codepoint > 0xeffff:
        # No data on characters in Private Use Area and above.
        return None

    if 0xd800 <= codepoint <= 0xdfff:
        warnings.warn(
            f"Surrogate character {repr(char)} will be ignored."
            f" You might be using a narrow Python build.",
            RuntimeWarning,
            2,
        )

    section = codepoint >> 8    # Chop off the last two hex digits
    position = codepoint % 256  # Last two hex digits

    try:
        table = Cache[section]
    except KeyError:
        try:
            mod = __import__(
                f"unidecode.x{section:03x}",
                globals(),
                locals(),
                ["data"],
            )
        except ImportError:
            # No data on this character
            Cache[section] = None
            return None

        Cache[section] = table = mod.data

    if table and len(table) > position:
        return table[position]
    else:
        return None


def _unidecode_repl_char(
    index: int, char: str, errors: "ErrorsType", replace_str: str,
) -> str:
    """
    Return replacement string for `char` and position `index`.

    For arguments other than `index`, check :py:func:`unidecode.unidecode`.
    """
    repl = _get_repl_str(char)

    if repl is None:
        if errors == 'ignore':
            repl = ''
        elif errors == 'strict':
            raise UnidecodeError(
                'no replacement found for character %r in position %d' % (
                    char, index,
                ),
                index,
            )
        elif errors == 'replace':
            repl = replace_str
        elif errors == 'preserve':
            repl = char
        else:
            raise UnidecodeError(
                'invalid value for errors parameter %r' % errors,
            )

    return repl


def unidecode_repl(
    string: str, errors: "ErrorsType" = "ignore",
    replace_str: str = "?",
) -> Iterator[str]:
    """
    Return a generator with chunks replacing the characters in `string`.
    """
    return (
        _unidecode_repl_char(index, char, errors, replace_str)
        for index, char in enumerate(string)
    )


def can_be_unidecoded(string: str) -> bool:
    """
    Return `True` if the `string` can be unidecoded without errors.
    """
    try:
        for _ in unidecode_repl(string, "strict", "?"):
            pass
    except UnidecodeError:
        return False
    else:
        return True


def get_invalid_chars(string: str) -> set[str]:
    """
    Return a set of chars in `string` that fail to unidecode.
    """
    return {char for char in string if not can_be_unidecoded(char)}
