from templates.gramdef import *
from collections import Counter


class Onchoice(SimpleGramChoice):
    choices = [
        "foo",
        "bar",
        "baz",
    ]


class Onchoiceweight(SimpleGramChoice):
    choices = [
        "foo",
        ("bar", 5),
    ]


class TwoChoice(SimpleGramChoice):
    choices = [
        f"a {Onchoice}",
        "no"
    ]


def test_onesampler():
    gram = Grammar(Onchoice)
    n = 10000
    gen = Counter(gram.generate_rand_iter(n))
    assert set(gen.keys()) == {"foo", "bar", "baz"}
    for count in gen.values():
        expected = n / 3
        assert expected - n * 0.05 < count < expected + n * 0.05


def test_onesampler_weight():
    gram = Grammar(Onchoiceweight)
    n = 10000
    gen = Counter(gram.generate_rand_iter(n))
    assert set(gen.keys()) == {"foo", "bar"}
    margin = n * 0.05
    assert n / 6 * 5 - margin < gen['bar'] < n / 6 * 5 + margin
    assert n / 6 * 1 - margin < gen['foo'] < n / 6 * 1 + margin


def test_twosampler():
    gram = Grammar(TwoChoice)
    print(gram._rules)
    print(TwoChoice.choices)
    n = 10000
    gen = Counter(gram.generate_rand_iter(n))
    assert set(gen.keys()) == {"a foo", "a bar", "a baz", "no"}
    margin = n * 0.05
    assert n / 2 - margin < gen['no'] < n / 2 + margin


class Morechoice(SimpleGramChoice):
    choices = [
        "foo",
        "bar",
        "baz",
        "pop",
        "spam",
        "wow",
    ]
    partitionable = True


def test_partition():
    gram = Grammar(Morechoice)
    n = 100
    gen = Counter(gram.generate_rand_iter(n))
    assert set(gen.keys()) == {"foo", "bar", "baz", "pop", "spam", "wow"}
    train_gram, test_gram = partition_grammar(gram, (0.5, 0.5))
    train_gen = Counter(train_gram.generate_rand_iter(n))
    test_gen = Counter(test_gram.generate_rand_iter(n))
    assert len(set(train_gen.keys()) & set(test_gen.keys())) == 0
    assert set(train_gen.keys()) | set(test_gen.keys()) == {"foo", "bar", "baz", "pop", "spam", "wow"}
    gen = Counter(gram.generate_rand_iter(n))
    assert set(gen.keys()) == {"foo", "bar", "baz", "pop", "spam", "wow"}
