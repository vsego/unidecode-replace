import re

from unidecode_replace import unidecode_replace, unidecode_wrap

text = "U šumarku skrivenom... aBei Bei aaa \u5317\u4EB0"
print(text)
print(unidecode_replace(text, r"suma.\w+", "XXX", re_search=True))
print(unidecode_replace(text, r"Bei ", lambda s: f"<{s}>"))
print(
    unidecode_replace(
        text, r"\bBe\w+ ",
        lambda m: f"<{m[0]}>",
        re_search=True,
        re_flags=re.I,
    ),
)
print(unidecode_wrap(text, r"suma.\w+", "<", ">", re_search=True))
print(
    unidecode_wrap(
        text, r"\bBe\w+ ",
        "<",
        ">",
        re_search=True,
        re_flags=re.I,
    ),
)
