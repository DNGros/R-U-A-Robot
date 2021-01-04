from templates.gramdef import *
from collections import Counter

from templates.gramgen import escape_bnf_string


class Onchoice(SimpleGramChoice):
    choices = [
        "foo",
        "bar",
        "baz",
    ]
    _do_not_log = True


class Onchoiceweight(SimpleGramChoice):
    choices = [
        "foo",
        ("bar", 5),
    ]
    _do_not_log = True


class TwoChoice(SimpleGramChoice):
    choices = [
        f"a {Onchoice}",
        "no"
    ]
    _do_not_log = True


def test_onesampler():
    gram = Grammar(Onchoice, [Onchoice, Onchoiceweight, TwoChoice])
    n = 10000
    gen = Counter(gram.generate_rand_iter(n))
    assert set(gen.keys()) == {"foo", "bar", "baz"}
    for count in gen.values():
        expected = n / 3
        assert expected - n * 0.05 < count < expected + n * 0.05


def test_onesampler_weight():
    gram = Grammar(Onchoiceweight, [Onchoice, Onchoiceweight, TwoChoice])
    n = 10000
    gen = Counter(gram.generate_rand_iter(n))
    assert set(gen.keys()) == {"foo", "bar"}
    margin = n * 0.05
    assert n / 6 * 5 - margin < gen['bar'] < n / 6 * 5 + margin
    assert n / 6 * 1 - margin < gen['foo'] < n / 6 * 1 + margin


def test_twosampler():
    gram = Grammar(TwoChoice, [Onchoice, Onchoiceweight, TwoChoice])
    print(gram._rules)
    print(TwoChoice.choices)
    n = 10000
    gen = Counter(gram.generate_rand_iter(n))
    assert set(gen.keys()) == {"a foo", "a bar", "a baz", "no"}
    margin = n * 0.05
    assert n / 2 - margin < gen['no'] < n / 2 + margin


class Morechoice(SimpleGramChoice):
    choices = [
        ("foo", 3),
        ("bar", 1),
        ("baz", 2),
        ("pop", 1),
        ("spam", 1.5),
        ("wow", 1.5),
    ]
    partitionable = True
    _do_not_log = True


def test_partition():
    gram = Grammar(Morechoice, [Onchoice, Onchoiceweight, TwoChoice, Morechoice])
    n = 100
    gen = Counter(gram.generate_rand_iter(n))
    assert set(gen.keys()) == {"foo", "bar", "baz", "pop", "spam", "wow"}
    train_gram, test_gram = partition_grammar(gram, (0.5, 0.5), duplicate_prob_mass=0)
    train_gen = Counter(train_gram.generate_rand_iter(n))
    test_gen = Counter(test_gram.generate_rand_iter(n))
    assert len(set(train_gen.keys()) & set(test_gen.keys())) == 0
    assert set(train_gen.keys()) | set(test_gen.keys()) == {"foo", "bar", "baz", "pop", "spam", "wow"}
    gen = Counter(gram.generate_rand_iter(n))
    assert set(gen.keys()) == {"foo", "bar", "baz", "pop", "spam", "wow"}


def test_partition2_dup():
    gram = Grammar(Morechoice, [Onchoice, Onchoiceweight, TwoChoice, Morechoice])
    n = 100
    gen = Counter(gram.generate_rand_iter(n))
    assert set(gen.keys()) == {"foo", "bar", "baz", "pop", "spam", "wow"}
    train_gram, test_gram = partition_grammar(gram, (0.5, 0.5), duplicate_prob_mass=0.2)
    train_gen = Counter(train_gram.generate_rand_iter(n))
    test_gen = Counter(test_gram.generate_rand_iter(n))
    assert set(train_gen.keys()) & set(test_gen.keys()) == {"foo"}
    assert set(train_gen.keys()) | set(test_gen.keys()) == {"foo", "bar", "baz", "pop", "spam", "wow"}
    gen = Counter(gram.generate_rand_iter(n))
    assert set(gen.keys()) == {"foo", "bar", "baz", "pop", "spam", "wow"}


class MoreRecurseChoice(SimpleGramChoice):
    choices = [
        f"a {Morechoice}",
        "no"
    ]
    partitionable = False
    _do_not_log = True


def test_partition2():
    gram = Grammar(MoreRecurseChoice, [Onchoice, Onchoiceweight, TwoChoice, Morechoice, MoreRecurseChoice])
    #gram = Grammar(MoreRecurseChoice)
    n = 100
    gen = Counter(gram.generate_rand_iter(n))
    e = {"a foo", "a bar", "a baz", "a pop", "a spam", "a wow", "no"}
    assert set(gen.keys()) == e
    train_gram, test_gram = partition_grammar(gram, (0.5, 0.5), duplicate_prob_mass=0)
    train_gen = Counter(train_gram.generate_rand_iter(n))
    test_gen = Counter(test_gram.generate_rand_iter(n))
    print(train_gen)
    print(test_gen)
    assert set(train_gen.keys()) & set(test_gen.keys()) == {"no"}
    assert set(train_gen.keys()) | set(test_gen.keys()) == e
    gen = Counter(gram.generate_rand_iter(n))
    assert set(gen.keys()) == e


def test_escape1():
    assert escape_bnf_string("") == '""'
