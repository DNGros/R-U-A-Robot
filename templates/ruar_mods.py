import re

from templates.modifiers import make_modifier_word_synonym, Modifier
from typos.good_typos import WIKI_TYPOS, OTHER_TYPOS
from util.util import flatten_list


def get_all_modifiers():
    base_modifiers = [
        *make_modifier_word_synonym(
            "mod_dont",
            [("don't", 1), ("do not", 1), ("dont", 0.05)]
        ),
        *make_modifier_word_synonym(
            "mod_aint",
            [("are not", 1), ("ain't", 1), ("aint", 0.05)]
        ),
        Modifier(
            "mod_period",
            re.compile(r"(\.)$"),
            [(".", 4), ("", 1), ("!", 0.05), ("..", 4/1500)]
        ),
        Modifier(
            "mod_question",
            re.compile(r"(\?+)"),
            [("?", 5), ("", 1), ("??", 0.02), ("???", 0.05), ("????", 0.01), ("!?", 0.05)],
        ),
        *make_modifier_word_synonym(
            "mod_a",
            [("a", 1), ("an", 1), ("a a", 100/1000)],
            original_multiplier=100,
            delete_word_weight=1
        ),
        # Sometimes we ignore the dropped version, but we still want to keep
        #   the version that swaps a/an
        *make_modifier_word_synonym(
            "mod_a_no_drop",
            [("a", 1), ("an", 1), ("a a", 100/1000)],
            original_multiplier=100,
            delete_word_weight=None,
        ),
        *make_modifier_word_synonym(
            "mod_please",
            [("please", 1), ("plz", 1), ("pls", 0.5)],
            original_multiplier=30
        ),
        *make_modifier_word_synonym(
            "mod_youre",
            [("you are", 1), ("you're", 1), ("your", 1), ("youre", 0.1), ("ur", 0.01)],
            original_multiplier=50
        ),
        *make_modifier_word_synonym(
            "mod_you",
            [("you", 1), ("u", 1)],
            original_multiplier=100
        ),
        *make_modifier_word_synonym(
            "mod_are",
            [("are", 1), ("r", 1)],
            original_multiplier=100
        ),
        *make_modifier_word_synonym(
            "mod_talking",
            [("talking", 1), ("talkin", 1)],
            original_multiplier=40
        ),
        *make_modifier_word_synonym(
            "mod_there",
            [("there", 1), ("they're", 1), ("there", 1), ("theyre", 0.05)],
            original_multiplier=40
        ),
        *make_modifier_word_synonym(
            "mod_really",
            [("really", 1), ("rly", 1), ("reeeally", 0.25)],
            original_multiplier=50
        ),
        *make_modifier_word_synonym(
            "mod_to",
            [("to", 1), ("too", 1)],
            original_multiplier=50
        ),
        *make_modifier_word_synonym(
            "mod_im",
            [("I'm", 1), ("I am", 1)],
            original_multiplier=30
        ),
        Modifier(
            "mod_comma_space",
            re.compile(r", "),
            [(", ", 10), (",", 1), (". ", 0.1), (" ", 0.03)],
            #rule_sub_left_prefix=r"\1",
            #rule_sub_right_suffix=r"\2",
        ),
        Modifier(
            "mod_comma_nospace",
            re.compile(r","),
            [(", ", 1), (",", 10), (". ", 0.1), (" ", 0.03)],
            #rule_sub_left_prefix=r"\1",
            #rule_sub_right_suffix=r"\2",
        ),
        Modifier(
            "mod_add_period",
            re.compile(r"([a-z])$", re.MULTILINE),
            [("", 15), (".", 1)],
            rule_sub_left_prefix=r"\1",
            require_explicit_allow=True,
            #rule_sub_right_suffix=r"\2",
        ),
        #Modifier(
        #    "mod_unquote",
        #    re.compile(r"(\w),(\w)"),
        #    [("", 1), (r'""', 1), (r"''", 0.1)],
        #    rule_sub_left_prefix=r"\1",
        #    rule_sub_right_suffix=r"\2",
        #),
    ]
    typo_modifiers = flatten_list(
        make_modifier_word_synonym(
            f"mod_typo_{correct}",
            [correct] + typos,
            original_multiplier=150
        )
        for correct, typos in dict(WIKI_TYPOS, **OTHER_TYPOS).items()
    )
    base_modifiers.extend(typo_modifiers)
    return base_modifiers