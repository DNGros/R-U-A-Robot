from templates.gramdef import SimpleGramChoice, Grammar
from templates.gramgen import *


class OneChoice(SimpleGramChoice):
    choices = [
        "foo",
        "bar",
        "baz",
    ]


class TwoChoice(SimpleGramChoice):
    choices = [
        f"a {OneChoice}",
        "no"
    ]


def test_simple_gen():
    text = rule_to_lark_ebnf(OneChoice)
    assert text == 'onechoice: "foo" | "bar" | "baz"'


def test_simple_gen_recur():
    text = rule_to_lark_ebnf(TwoChoice)
    assert text == 'twochoice: "a " onechoice | "no"'


def test_recognizer():
    gram = Grammar(TwoChoice, [TwoChoice, OneChoice])
    parser = GramRecognizer(gram)
    assert parser.is_in_grammar("no")
    assert parser.is_in_grammar("a foo")
    assert not parser.is_in_grammar("foo")
    assert not parser.is_in_grammar("no bad")


def test_fullgram():
    from templates.areyourobot_grammar import areyourobot_grammar_obj
    parser = GramRecognizer(areyourobot_grammar_obj)
    assert parser._is_in_grammar("are you a robot?")
    assert not parser._is_in_grammar("I like pasta")
    assert parser._is_in_grammar("are you a real person?")

