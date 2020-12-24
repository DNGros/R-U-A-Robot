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


distractor_grammar = Grammar(_DistractorBase)
