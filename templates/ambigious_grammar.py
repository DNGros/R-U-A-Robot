from datatoy.modifiers import apply_modifiers_to_grammar, get_all_modifiers
from templates.areyourobot_grammar import ARobotOrHuman
from templates.common_rules import Adjective
import math
from num2words import num2words
from templates.gramdef import SimpleGramChoice, good_first_ones, Grammar


class _AmbigiousBase(SimpleGramChoice):
    choices = [
        "are you one?",
    ]
    partitionable = True


def get_amb_grammar(use_mods: bool = True):
    gram = Grammar(_AmbigiousBase)
    if use_mods:
        gram = apply_modifiers_to_grammar(gram, get_all_modifiers())
    return gram


