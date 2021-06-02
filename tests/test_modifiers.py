import re

from templates.modifiers import modify_grammar, Modifier, apply_modifiers_to_grammar, \
    make_modifier_word_synonym
from templates.ruar_mods import get_all_modifiers
from templates.gramdef import SimpleGramChoice, Grammar, clear_global_name_cache
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


mod_dont = Modifier(
    "mod_dont_t",
    re.compile(r"\b(don't|do not|dont)\b"),
    [("don't", 1), ("do not", 1), ("dont", 0.05)]
)


def test_mod1():
    new_choice, new_weight = mod_dont.apply_to_choice("I don't like pie", 1.0)
    assert new_choice.startswith("I [[")
    assert new_choice.endswith("]] like pie")
    gram = Grammar(_ExampleThing, [_ExampleThing])
    parser = GramRecognizer(gram)
    assert parser.is_in_grammar("I don't like pie")
    mod_gram = modify_grammar(gram, mod_dont)
    print(gram_to_lark_ebnf(mod_gram))
    parser = GramRecognizer(mod_gram)
    assert parser.is_in_grammar("I don't like pie")
    assert parser.is_in_grammar("I do not like pie")


def test_mod_tworule():
    class _BRule(SimpleGramChoice):
        choices = [
            "I do not",
            "I",
        ]

    class _ARule(SimpleGramChoice):
        choices = [
            f"{_BRule} like green eggs and ham",
            f"{_BRule} sam I am",
        ]

    gram = Grammar(_ARule, [_ARule, _BRule])
    mod_gram = modify_grammar(gram, mod_dont)
    print(gram_to_lark_ebnf(mod_gram))
    parser = GramRecognizer(mod_gram)
    assert parser.is_in_grammar("I don't like green eggs and ham")


def test_all_mods():
    #from templates.areyourobot_grammar import ARobot
    class _SimpleARobot(SimpleGramChoice):
        choices = [
            "a robot",
            "a computer",
            "a computer",
        ]

    class _OtherExample(SimpleGramChoice):
        choices = [
            "I don't like pie.",
            "I ain't good at grammar",
            f"are you {_SimpleARobot}?",
        ]
    grammar = Grammar(_OtherExample, [_OtherExample, _SimpleARobot])
    print(gram_to_lark_ebnf(grammar))
    parser = GramRecognizer(grammar)
    assert parser.is_in_grammar("I don't like pie.")
    print("------- PASS FIRST -------------")
    grammar = apply_modifiers_to_grammar(grammar, get_all_modifiers())
    print(gram_to_lark_ebnf(grammar))
    parser = GramRecognizer(grammar)
    assert parser.is_in_grammar("I do not like pie")
    assert parser.is_in_grammar("r u an robot?")


def test_all_mods2():
    #clear_global_name_cache()
    from templates.areyourobot_grammar import ARobot
    class _OtherExample(SimpleGramChoice):
        choices = [
            "I don't like pie",
            "I ain't good at grammar",
            f"are you {ARobot}?",
            f"you know I am a person",
            f"are you completely good?"
        ]
    #grammar = Grammar(_OtherExample, [ARobot, _OtherExample])
    grammar = Grammar(_OtherExample)
    print(gram_to_lark_ebnf(grammar))
    parser = GramRecognizer(grammar)
    assert parser.is_in_grammar("I don't like pie")
    print("------- PASS FIRST -------------")
    grammar = apply_modifiers_to_grammar(grammar, get_all_modifiers())
    print(gram_to_lark_ebnf(grammar))
    parser = GramRecognizer(grammar)
    assert parser.is_in_grammar("I do not like pie")
    assert parser.is_in_grammar("r u an robot?")
    assert parser.is_in_grammar("r u an robot")
    assert parser.is_in_grammar("you know I am a person")
    assert parser.is_in_grammar("you know I'm a person")


def test_mod_typo():
    class _OtherExample(SimpleGramChoice):
        choices = [
            f"are you completely good?"
        ]
    #grammar = Grammar(_OtherExample, [ARobot, _OtherExample])
    grammar = Grammar(_OtherExample)
    #print(gram_to_lark_ebnf(grammar))
    #assert parser.is_in_grammar("I don't like pie")
    #print("------- PASS FIRST -------------")
    grammar = apply_modifiers_to_grammar(grammar, get_all_modifiers())
    print(gram_to_lark_ebnf(grammar))
    parser = GramRecognizer(grammar)
    assert parser.is_in_grammar("are you completelyl good?")


def test_dropped_word():
    #clear_global_name_cache()
    from templates.areyourobot_grammar import ARobot
    class _AnAExample(SimpleGramChoice):
        choices = [
            "You are a good boy",
            "You are an apple",
            "a good boy",
            "bad boy a",
            "a happy boy a",
        ]
    grammar = Grammar(_AnAExample, [_AnAExample])
    parser = GramRecognizer(grammar)
    assert parser.is_in_grammar("You are a good boy")
    assert not parser.is_in_grammar("You are an good boy")
    grammar = apply_modifiers_to_grammar(grammar, make_modifier_word_synonym(
        "toy_a_modifier", ["a", "an"], delete_word_weight=1.0
    ))
    print(gram_to_lark_ebnf(grammar))
    parser = GramRecognizer(grammar)
    assert parser.is_in_grammar("You are an good boy")
    assert parser.is_in_grammar("You are a good boy")
    assert parser.is_in_grammar("You are good boy")
    assert parser.is_in_grammar("You are apple")
    assert not parser.is_in_grammar("You are an pple")
    assert parser.is_in_grammar("a good boy")
    assert parser.is_in_grammar("good boy")
    assert parser.is_in_grammar("bad boy a")
    assert parser.is_in_grammar("bad boy")
    assert parser.is_in_grammar("happy boy")


def test_comma_thing():
    class _OtherExample(SimpleGramChoice):
        choices = [
            "I,love this",
            "hello,bob",
            "yo,i,like,pie",
        ]
    grammar = Grammar(_OtherExample, [_OtherExample])
    print(gram_to_lark_ebnf(grammar))
    parser = GramRecognizer(grammar)
    assert parser.is_in_grammar("I,love this")
    print("------- PASS FIRST -------------")
    grammar = apply_modifiers_to_grammar(grammar, get_all_modifiers())
    print(gram_to_lark_ebnf(grammar))
    parser = GramRecognizer(grammar)
    assert parser.is_in_grammar("I,love this")
    assert parser.is_in_grammar("I, love this")
    assert parser.is_in_grammar("I. love this")


def test_insert_period():
    class _OtherExample(SimpleGramChoice):
        choices = [
            "Hello",
        ]
        allow_modifiers = ["mod_add_period"]
    grammar = Grammar(_OtherExample, [_OtherExample])
    parser = GramRecognizer(grammar)
    assert parser.is_in_grammar("Hello")
    assert not parser.is_in_grammar("Hello.")
    print("------- PASS FIRST -------------")
    grammar = apply_modifiers_to_grammar(grammar, get_all_modifiers())
    print(gram_to_lark_ebnf(grammar))
    parser = GramRecognizer(grammar)
    assert parser.is_in_grammar("Hello")
    assert parser.is_in_grammar("Hello.")


def test_ignore_mod():
    #clear_global_name_cache()
    from templates.areyourobot_grammar import ARobot
    class _AnAExample(SimpleGramChoice):
        choices = [
            "You are a robot?",
        ]
        ignore_modifiers = ["mod_question"]
    grammar = Grammar(_AnAExample, [_AnAExample])
    parser = GramRecognizer(grammar)
    assert parser.is_in_grammar("You are a robot?")
    assert not parser.is_in_grammar("You are a robot")
    grammar = apply_modifiers_to_grammar(grammar, [
        Modifier(
            "mod_question",
            re.compile(r"(\?+)"),
            [("?", 3), ("", 1), ("??", 0.05), ("???", 0.05), ("????", 0.01), ("!?", 0.05)],
        ),
        Modifier(
            "robot_to_cloud",
            re.compile(r"robot"),
            [("robot", 3), ("cloud", 1)],
        ),
    ])
    print(gram_to_lark_ebnf(grammar))
    parser = GramRecognizer(grammar)
    assert parser.is_in_grammar("You are a robot?")
    assert not parser.is_in_grammar("You are a robot")
    assert not parser.is_in_grammar("You are a robot.")
    assert parser.is_in_grammar("You are a cloud?")
    assert not parser.is_in_grammar("You are a cloud")

