from datatoy.modifiers import apply_modifiers_to_grammar, get_all_modifiers
from datatoy.survey_data import get_survey_data
from templates.areyourobot_grammar import ARobotOrHuman
from templates.common_rules import Adjective
import math
from num2words import num2words
from templates.gramdef import SimpleGramChoice, good_first_ones, Grammar


def get_amb_choices_from_labels():
    survey_df = get_survey_data()
    amb = survey_df.query('pos_amb_neg == "a"')
    # TODO: Should maybe sub in ARobot with a modifier
    return list(amb.utterance)


class _AmbigiousBase(SimpleGramChoice):
    choices = [
        # We are going to just pull these directly from the labels. This is
        #   because those labels also include the justifications. It is a bit
        #   cleaner to just let that file be the single source of truth.
        *get_amb_choices_from_labels(),
        "are you?",  # Robot> "Are you a man?" Human> "Are you?"
    ]
    partitionable = True


def get_amb_grammar(use_mods: bool = True):
    gram = Grammar(_AmbigiousBase)
    if use_mods:
        gram = apply_modifiers_to_grammar(gram, get_all_modifiers())
    return gram


