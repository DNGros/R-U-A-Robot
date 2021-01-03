from templates.gramdef import SimpleGramChoice, Grammar, clear_global_name_cache
from templates.gramgen import *
from util.util import get_only_element


class OneChoice(SimpleGramChoice):
    choices = [
        "foo",
        "bar",
        "baz",
    ]
    #_do_not_log = True


class TwoChoice(SimpleGramChoice):
    choices = [
        f"a {OneChoice}",
        "no"
    ]
    #_do_not_log = True


def test_simple_gen():
    text = get_only_element(rule_to_lark_ebnf(OneChoice))
    assert text == 'onechoice: "foo" | "bar" | "baz"'


def test_simple_gen_recur():
    text = get_only_element(rule_to_lark_ebnf(TwoChoice))
    assert text == 'twochoice: "a " onechoice | "no"'


def test_recognizer():
    gram = Grammar(TwoChoice, [TwoChoice, OneChoice])
    parser = GramRecognizer(gram)
    assert parser.is_in_grammar("no")
    assert parser.is_in_grammar("a foo")
    assert not parser.is_in_grammar("foo")
    assert not parser.is_in_grammar("no bad")


def test_fullgram():
    from templates.areyourobot_grammar import get_areyourobot_grammar
    parser = GramRecognizer(get_areyourobot_grammar())
    assert parser.is_in_grammar("are you a robot?")
    assert not parser._is_in_grammar("I like pasta")
    assert parser.is_in_grammar("are you a real person?")
    assert parser.is_in_grammar("hi are you a robot?")
    assert not parser.is_in_grammar("you person?")
    assert not parser.is_in_grammar("I would like to know,  You are a human 🥺")


def test_fullgram_profane():
    """This might fail if not allowing profanity. Can't figure out how to force
    it on for this test."""
    import templates.common_rules
    #templates.common_rules.ALLOW_PROFAN = True
    #import importlib
    ##clear_global_name_cache()
    import templates.areyourobot_grammar
    #importlib.reload(templates.areyourobot_grammar)
    parser = GramRecognizer(templates.areyourobot_grammar.get_areyourobot_grammar())
    assert parser.is_in_grammar("are you fucking robot?")


def test_rec_last_sentence():
    from templates.areyourobot_grammar import get_areyourobot_grammar
    parser = GramRecognizer(get_areyourobot_grammar(), check_last_sentence_by_itself=True)
    assert parser.is_in_grammar("that's cool i like elephants. are you a robot?")


def test_rec_last_sentence2():
    from templates.areyourobot_grammar import get_areyourobot_grammar
    parser = GramRecognizer(get_areyourobot_grammar(), check_last_sentence_by_itself=True)
    assert parser.is_in_grammar("that's cool i like elephants.are you a robot?")


def test_rec_last_comma():
    from templates.areyourobot_grammar import get_areyourobot_grammar
    parser = GramRecognizer(get_areyourobot_grammar(), check_last_comma_by_itself=True)
    assert parser.is_in_grammar("that's cool i like elephants, are you a robot?")


class EmptyChoice(SimpleGramChoice):
    choices = [
        f"",
        "foo"
    ]


def test_empty_choice():
    r1, r2 = rule_to_lark_ebnf(EmptyChoice)
    assert r1 == 'inner_emptychoice: "foo"'
    assert r2 == 'emptychoice: inner_emptychoice?'
    gram = Grammar(EmptyChoice, [EmptyChoice])
    parser = GramRecognizer(gram)
    assert parser.is_in_grammar("foo")
    assert parser.is_in_grammar("")


def test_empty_choice2():
    class NEmptyChoice(SimpleGramChoice):
        choices = [
            f"",
            OneChoice
        ]
    gram = Grammar(NEmptyChoice, [NEmptyChoice, OneChoice])
    parser = GramRecognizer(gram)
    assert parser.is_in_grammar("foo")
    assert parser.is_in_grammar("")


def test_new_line():
    class NewLine(SimpleGramChoice):
        choices = [
            f"foo\nbar",
            "foo"
        ]
    gram = Grammar(NewLine, [NewLine])
    text = gram_to_lark_ebnf(gram)
    print(text)
    parser = GramRecognizer(gram)
    assert parser.is_in_grammar("foo\nbar")
    assert not parser.is_in_grammar("foobar")
    assert parser.is_in_grammar("foo")


#def test_new_line_in_lead():
#    from templates.areyourobot_grammar import Lead
#    text = get_only_element(rule_to_lark_ebnf(Lead))
#    print(text)
#    assert r"\n" in text
