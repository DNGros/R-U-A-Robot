import re

from datatoy.modifiers import modify_grammar, mod_dont, Modifier
from templates.gramdef import SimpleGramChoice, Grammar
from templates.gramgen import GramRecognizer, gram_to_lark_ebnf


class _ExampleThing(SimpleGramChoice):
    choices = [
        "I don't like pie",
        "foo",
    ]


def test_mod_choice():
    mod = Modifier("mymod", re.compile(r"\b(bad)\b"), ["good", "bad"])
    new_choice, new_weight = mod.apply_to_choice("I am bad", 1.0)
    print(new_choice)
    assert isinstance(new_choice, str)
    assert new_choice.startswith("I am [[")
    assert new_choice.endswith("]]")
    assert "bad" not in new_choice
    assert new_weight == 1.0


def test_mod1():
    gram = Grammar(_ExampleThing, [_ExampleThing])
    parser = GramRecognizer(gram)
    assert parser.is_in_grammar("I don't like pie")
    mod_gram = modify_grammar(gram, mod_dont)
    print(gram_to_lark_ebnf(mod_gram))
    parser = GramRecognizer(mod_gram)
    assert parser.is_in_grammar("I don't like pie")
    assert parser.is_in_grammar("I do not like pie")

