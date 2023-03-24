"""
Tests to make sure that `UnidecodeReMatch` works properly.
"""

import itertools
import re
from string import ascii_lowercase

from unidecode_replace import unidecode_replace, can_be_unidecoded

from .utils import TestsBase


class TestMatch(TestsBase):

    string = "他现失踪已经失踪路上了。"
    string_swap_shi_zong = "他现踪失已经踪失路上了。"
    string_with_spans = "他现[2-4]已经[6-8]路上了。"
    string_with_pos = "他现[0]已经[0]路上了。"
    search_original = re.compile(r"(?P<shi>失)(?P<zong>踪)")
    # >>> unidecode.unidecode("他现失踪已经失踪路上了。")
    # 'Ta Xian Shi Zong Yi Jing Shi Zong Lu Shang Liao . '

    def test_expand(self):
        self.assertEqual(
            unidecode_replace(
                self.string,
                self.search_original,
                lambda m: m.expand(r"\2\1"),
            ),
            self.string_swap_shi_zong,
        )

    def test_group(self):
        self.assertEqual(
            unidecode_replace(
                self.string,
                self.search_original,
                lambda m: m.group(2) + m.group(1),
            ),
            self.string_swap_shi_zong,
        )
        self.assertEqual(
            unidecode_replace(
                self.string,
                self.search_original,
                lambda m: m[2] + m[1],
            ),
            self.string_swap_shi_zong,
        )
        self.assertEqual(
            unidecode_replace(
                self.string,
                self.search_original,
                lambda m: m.group("zong") + m.group("shi"),
            ),
            self.string_swap_shi_zong,
        )
        self.assertEqual(
            unidecode_replace(
                self.string,
                self.search_original,
                lambda m: m["zong"] + m["shi"],
            ),
            self.string_swap_shi_zong,
        )
        self.assertEqual(
            unidecode_replace(
                self.string,
                self.search_original,
                lambda m: "".join(m.group(2, 1)),
            ),
            self.string_swap_shi_zong,
        )

    def test_groups(self):
        self.assertEqual(
            unidecode_replace(
                self.string,
                self.search_original,
                lambda m: "".join(reversed(m.groups())),
            ),
            self.string_swap_shi_zong,
        )

    def test_groupdict(self):
        def f(m):
            d = m.groupdict()
            return d["zong"] + d["shi"]

        self.assertEqual(
            unidecode_replace(
                self.string,
                self.search_original,
                f,
            ),
            self.string_swap_shi_zong,
        )

    def test_span(self):
        self.assertEqual(
            unidecode_replace(
                self.string,
                self.search_original,
                lambda m: f"[{'-'.join(str(v) for v in m.span(0))}]",
            ),
            self.string_with_spans,
        )

    def test_pos(self):
        self.assertEqual(
            unidecode_replace(
                self.string,
                self.search_original,
                lambda m: f"[{m.pos}]",
            ),
            self.string_with_pos,
        )

    def test_over_100_groups_ascii(self):
        names = tuple(
            "".join(name)
            for name in itertools.product(ascii_lowercase, repeat=2)
        )[:111]
        string = "".join(
            f"{str(idx ** 2) if idx else ''}{name.upper()}"
            for idx, name in enumerate(names)
        )
        regex = re.compile(
            r"\d*".join(rf"(?P<{name}>[A-Z]+)" for name in names),
        )
        sub1 = "".join(rf"\g<{name}>" for name in reversed(names))
        sub2 = "".join(
            rf"\g<{idx if idx < 100 else name}>"
            for idx, name in reversed(list(enumerate(names, start=1)))
        )
        expected = "".join(name.upper() for name in reversed(names))
        # If you don't understand the above, uncomment this to see what they
        # look like.
        # import unidecode
        # print("String:", repr(string))
        # print("Unidecoded:", repr(unidecode.unidecode(string)))
        # print("Regex:", repr(regex.pattern))
        # print("Sub 1:", repr(sub1))
        # print("Sub 2:", repr(sub2))
        self.assertEqual(
            unidecode_replace(string, regex, sub1),
            expected,
            "ASCII chars, group names only",
        )
        self.assertEqual(
            unidecode_replace(string, regex, sub2),
            expected,
            "ASCII chars, 99 numbered groups followed by named groups",
        )

    def test_over_100_groups_ch(self):
        names = tuple(
            "".join(name)
            for name in itertools.product(ascii_lowercase, repeat=2)
        )[:111]
        values = list()
        idx = 0x5000
        while len(values) < len(names):
            c = chr(0x503f + idx)
            if can_be_unidecoded(c):
                if not values or len(values) % 3 + 1 == len(values[-1]):
                    values.append(c)
                else:
                    values[-1] += c
            idx += 1
        string = "".join(
            f"{str(idx ** 2) if idx else ''}{value}"
            for idx, value in enumerate(values)
        )
        regex = re.compile(
            r"\d*".join(rf"(?P<{name}>\D+)" for name in names),
        )
        sub1 = "".join(rf"\g<{name}>" for name in reversed(names))
        sub2 = "".join(
            rf"\g<{idx if idx < 100 else name}>"
            for idx, name in reversed(list(enumerate(names, start=1)))
        )
        expected = "".join(value for value in reversed(values))
        # If you don't understand the above, uncomment this to see what they
        # look like.
        # import unidecode
        # print("String:", repr(string))
        # print("Unidecoded:", repr(unidecode.unidecode(string)))
        # print("Regex:", repr(regex.pattern))
        # print("Sub 1:", repr(sub1))
        # print("Sub 2:", repr(sub2))
        self.assertEqual(
            unidecode_replace(string, regex, sub1),
            expected,
            "Chinese chars, group names only",
        )
        self.assertEqual(
            unidecode_replace(string, regex, sub2),
            expected,
            "Chinese chars, 99 numbered groups followed by named groups",
        )

    def test_none_group(self):
        self.assertEqual(
            unidecode_replace(
                "abcdef",
                re.compile("(?:([a-c]+)|(x*))([d-f]+)"),
                lambda m: "|".join(
                    str(bool(m.group(idx) is None)) for idx in range(1, 4)
                ),
            ),
            "False|True|False",
        )
        self.assertEqual(
            unidecode_replace(
                "abcdef",
                re.compile("(?:([a-c]+)|(x*)|(?P<y>y*))([d-f]+)"),
                r"\1|\2|\3|\4",
            ),
            "abc|||def",
        )

    def test_pos_endpos(self):
        self.assertEqual(
            unidecode_replace(
                "abcdefg",
                "d",
                lambda m: f"[{m.pos}->{m.endpos}]",
                re_search=True,
                pos=1,
                endpos=5,
            ),
            "abc[1->5]efg",
        )

    def test_lastindex(self):
        self.assertEqual(
            unidecode_replace(
                "abcdefg",
                "cd",
                lambda m: f"[{m.lastindex}]",
                re_search=True,
            ),
            "ab[None]efg",
        )
        self.assertEqual(
            unidecode_replace(
                "abcdefg",
                "(X)?cd",
                lambda m: f"[{m.lastindex}]",
                re_search=True,
            ),
            "ab[None]efg",
        )
        self.assertEqual(
            unidecode_replace(
                "abcdefg",
                "((c)(d))",
                lambda m: f"[{m.lastindex}]",
                re_search=True,
            ),
            "ab[1]efg",
        )
        self.assertEqual(
            unidecode_replace(
                "abcdefg",
                "(c)(d)",
                lambda m: f"[{m.lastindex}]",
                re_search=True,
            ),
            "ab[2]efg",
        )
        self.assertEqual(
            unidecode_replace(
                "abcdefg",
                "((c)(d))(e)",
                lambda m: f"[{m.lastindex}]",
                re_search=True,
            ),
            "ab[4]fg",
        )

    def test_lastgroup(self):
        self.assertEqual(
            unidecode_replace(
                "abcdefg",
                "cd",
                lambda m: f"[{m.lastgroup}]",
                re_search=True,
            ),
            "ab[None]efg",
        )
        self.assertEqual(
            unidecode_replace(
                "abcdefg",
                "(?P<x>X)?cd",
                lambda m: f"[{m.lastgroup}]",
                re_search=True,
            ),
            "ab[None]efg",
        )
        self.assertEqual(
            unidecode_replace(
                "abcdefg",
                "(?P<cd>(?P<c>c)(?P<d>d))",
                lambda m: f"[{m.lastgroup}]",
                re_search=True,
            ),
            "ab[cd]efg",
        )
        self.assertEqual(
            unidecode_replace(
                "abcdefg",
                "(?P<c>c)(?P<d>d)",
                lambda m: f"[{m.lastgroup}]",
                re_search=True,
            ),
            "ab[d]efg",
        )
        self.assertEqual(
            unidecode_replace(
                "abcdefg",
                "(?P<cd>(?P<c>c)(?P<d>d))(?P<e>e)",
                lambda m: f"[{m.lastgroup}]",
                re_search=True,
            ),
            "ab[e]fg",
        )
        self.assertEqual(
            unidecode_replace(
                "abcdefg",
                "(?P<cd>(?P<c>c)(?P<d>d))(e)",
                lambda m: f"[{m.lastgroup}]",
                re_search=True,
            ),
            "ab[None]fg",
        )

    def test_re(self):
        regex = re.compile("b")
        self.assertEqual(
            unidecode_replace(
                "abc",
                regex,
                lambda m: f"[{m.re is regex},{m.re.pattern == regex.pattern}]",
            ),
            "a[False,True]c",
        )
        regex = re.compile("b", flags=re.I)
        expected = re.U | re.I  # Unicode is redundant, but present.
        self.assertEqual(
            unidecode_replace(
                "abc",
                regex,
                lambda m: f"[{m.re.flags == expected}]",
                re_flags=re.M,
            ),
            "a[True]c",
        )
        regex = re.compile("b", flags=re.I)
        expected = re.U | re.I  # Unicode is redundant, but present.
        self.assertEqual(
            unidecode_replace(
                "abc",
                regex,
                lambda m: f"[{m.re.flags == expected}]",
                re_flags=re.I,
            ),
            "a[True]c",
        )
