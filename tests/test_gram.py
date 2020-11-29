from templates.gramdef import *
from collections import Counter


class Onchoice(SimpleGramChoice):
    choices = [
        "foo",
        "bar",
        "baz",
    ]


def test_onesampler():
    gram = Grammar(Onchoice)
    n = 10000
    gen = Counter(gram.generate_rand_iter(n))
    assert set(gen.keys()) == {"foo", "bar", "baz"}
    for count in gen.values():
        expected = n / 3
        assert expected - n * 0.05 < count < expected + n * 0.05


