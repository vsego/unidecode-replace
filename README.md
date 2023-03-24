# Unidecode Replace

This is a Python package providing search-and-replace in a unidecode compatible manner. This means that, when searching, [unidecode](https://pypi.org/project/Unidecode/) equivalences are taken into account, but the replacing is still done on the original string.

For example, German character "ö" unidecodes as "o". So, when searching a text in German language, one could search for "o" and expect to find every "o", but also every "ö" (the opposite is also true: searching for "ö" would find both of these characters). Unidecode Replace will do this:

```python
>>> from unidecode_replace import unidecode_replace
>>> unidecode_replace("Übergröße", "ö", "!!!")
'Übergr!!!ße'
>>> unidecode_replace("Übergröße", "o", "!!!")
'Übergr!!!ße'
>>> unidecode_replace("Just an ordinary 'o'", "ö", "!!!")
"Just an !!!rdinary '!!!'"
```

**Note:** If you like the features described in this document, but you want a regular (not unidecode-compatible) search, there is a flag for that.

## Content

1. [Main functions](#main-functions)
    1. [`unidecode_replace`](#unidecode_replace)
    2. [`unidecode_wrap`](#unidecode_wrap)
2. [Main arguments](#main-arguments)
    1. [Search(es)](#searches)
    2. [Substitution(s)](#substitutions)
3. [Auxiliary functions from `unidecode`](#auxiliary-functions-from-unidecode)
4. [Exposed internals](#exposed-internals)

## Main functions

### `unidecode_replace`

The core of the package is `unidecode_replace` function, which is a wrapper for the class `UnidecodeReplace` that does all the work. It's signature is this:

```python
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
) -> str: ...
```

The arguments are as follows:

- `string`: The input string on which the search and replace are performed.
- `search`: A search string or a regex, or a sequence of them. For more details, see [Search(es)](#searches).
- `sub`: A replacement string or a function, or a sequence of them. For more details, see [Substitution(s)](#substitutions).
- `allow_overlaps`: If `True`, overlapping instances of found text are replaced.
- `re_search`: If `True` and `search` is a string, it'll be compiled as a regular expression. If it's a sequence, any string in it will also be compiled.
- `re_flags`: Flags used when compiling regular expressions (if `re_search` is set to `True`).
- `count`: If set, only the first `count` occurrences are replaced.
- `pos`, `endpos`: If defined, search and replace will only be done from position `pos` (default: 0) to `endpos - 1` (defaulting to the end of `string`).
- `unidecoded_search`: If set to `False`, the search will be literal (i.e., not based on the unidecoded version of `string`). This behaves equivalently to `str.replace` and `re.sub`, but with the added benefit of doing multiple searches in one pass and allowing one to use `pos` and `endpos`.
- `str_case_sensitive`: If set to `True`, string searches will be performed in case-sensitive manner. If set to `False`, string searches will be performed in case-insensitive manner. This setting does not affect regex searching.

The function returns a copy of `string` with matched substrings replaced.

### `unidecode_wrap`

This function does pretty much the same thing as `unidecode_replace`, except that its `sub` is replaced by two arguments: `prefix` and `suffix`:

```python
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
) -> str: ...
```

What it does is wrapping each found substring with two values. The main purpose is easy marking of what was found. For example,

```python
>>> unidecode_wrap("This is some string.", "some", "<b>", "</b>")
'This is <b>some</b> string.'
```

## Main arguments

Let us consider two main arguments - search(es) and substitution(s) - in more detail.

### Search(es)

As mentioned above, the search argument `string` can be a string, a regular expression (`re.Pattern`), or a sequence of one or more of these.

If it is a string, then:

1. If `re_search` is set to `False`, it will be matched to `string` as it is.

2. If `re_search` is set to `True`, it will be compiled as a regular expression before being matched to `string`.

If it is a regular expression or `re_search` is set to `True`, the matching will be the usual regex one.

If it is a regex pattern (i.e., a compiled regex), the matching is done as one would expect of regex searches.

If it is a sequence, each item (a string or a regex pattern) is treated as just described.

If `str_case_sensitive` flag is set to `False`, all string matches are done in case-insensitive manner, and if it's `True` then they are case-sensitive. This setting does not affect regular expressions.

When a string is compiled as a regex (because `re_search` is set to `True`), the value of `re_flags` is used as `flags` in `re.compile`. For example, include `re.I` here to get case-insensitive search. However, for regex pattern searches (i.e., those that are already compiled), `re_search` and `re_flags` have no effect.

To avoid unidecode-compatible searching (for example, treating "ö" and "o" as the same character), set `unidecoded_search` to `False`.

### Substitution(s)

As mentioned above, the substitution argument `sub` can be a string or a callable or a sequence of these things. Let us see how these act one-on-one (i.e., when there is only one `search` and one `sub` item).

1. If `search` is a string and `sub` is a string, than any matched substring of `string` will be replaced by `sub`.

2. If `search` is a string and `sub` is a callable, it should accept one string (which will have the found substring provided) and any matched substring of `string` will be replaced by whatever that callable returns.

3. If `search` is a regex pattern and `sub` is a string, than any matched substring of `string` will be replaced by the expanded `sub` (i.e., any regex groups in it will be replaced by the values of those groups).

4. If `search` is a regex pattern and `sub` is a callable, it should accept one argument `m` and any matched substring of `string` will be replaced by whatever that callable returns.

The argument `m` mentioned in item #4 is a `UnidecodeReMatch` instance. This can be used as a normal `re.Match` as it wraps the original one (accessible as `m.original`), but it will be properly mapped to `string` (`m.original` has its values matching the unidecoded version of `string`).

If given as sequences, `search` and `sub` should be of the same length and they will match 1-to-1, meaning that the first search item will be replaced with the first substitution item, the second search item will be replaced with the second substitution item, etc.

There is one exception to this rule: if `search` is a sequence, then `sub` can still be a single item or a sequence containing only one item. In this special case, all matched search items will be substituted by that same one substitution item. This is effectively used by `unidecode_wrap`, which internally provides a single callable `sub`.

## Auxiliary functions from `unidecode`

There are two auxiliary functions whose functionality is more related to `unidecode`, but they are exposed in this package:

1. `can_be_unidecoded(string: str) -> bool`: Return `True` if the `string` can be unidecoded without errors.

2. `get_invalid_chars(string: str) -> set[str]`: Return a set of chars in `string` that fail to unidecode.

## Exposed internals

Apart from `unidecode_replace` and `unidecode_wrap`, the package also exposes the following classes (but most of them won't be imported with `from unidecode_replace import *`):

1. `UnidecodeReplace`: The class that does all the actual work. Since `unidecode_replace` exposes all of its functionality, you'd only want to use this if you were to inherit it.

2. `SearchItem`, `SearchItemStr`, `SearchItemRegex`: Internal classes that hold `(search, sub)` pairs and perform the actual searching and generating the replacement strings. You probably don't need these for more than just type annotations in the event of inheriting `UnidecodeReplace` and extending its search capabilities.

3. `UnidecodeReMatch`: The wrapper class for `re.Match`, used to map the results of regular expressions performed on unidecoded strings back to the original ones. Also unlikely to be used for more than type annotations, but this one is exposed in `__all__`. The reason for this is that one might need it for type annotations in the callables used as substituted when searching with regular expressions.

4. `SearchT`, `SubT`, `u2iT`: Types for `search` and `sub` arguments, and for `u2i` attribute (an internal mapping used by `UnidecodeReplace` to map indexes from unidecoded string to the original (input) one).
