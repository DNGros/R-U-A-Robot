from datatoy.modifiers import apply_modifiers_to_grammar, get_all_modifiers
from datatoy.survey_data import get_survey_data, get_tfidf_distract
from templates.areyourobot_grammar import ARobotOrHuman, AHuman, MaybeALead, ARobot, AnAdjectivedPerson
from templates.common_rules import Adjective, HumanSingular, CommonName, FamousRobot, RobotSingular, \
    CompanyName
import math
from num2words import num2words
from templates.gramdef import SimpleGramChoice, good_first_ones, Grammar


def get_amb_choices_from_labels():
    survey_df = get_survey_data()
    amb = survey_df.query('pos_amb_neg == "a"')
    # TODO: Should maybe sub in ARobot with a modifier
    return list(amb.utterance)


def get_amb_choice_from_tfidf():
    survey_df = get_tfidf_distract()
    amb = survey_df.query('pos_amb_neg == "a"')
    # TODO: Should maybe sub in ARobot with a modifier
    return list(amb.text_unproc)


class _AmbigiousBase(SimpleGramChoice):
    choices = [
        # We are going to just pull these directly from the labels. This is
        #   because those labels also include the justifications. It is a bit
        #   cleaner to just let that file be the single source of truth.
        *get_amb_choices_from_labels(),
        *get_amb_choice_from_tfidf(),
        "are you?",  # Robot> "Are you a man?" Human> "Are you?"
        (f"Is this {AHuman}", 3),
        (f"You are a {Adjective} {HumanSingular}.", 3),
        # Cat 4
        *[
            f"Is this {CommonName}?",
            f"Are you {CommonName}?",
            f"Are you {FamousRobot}?",
            f"Are you Barack Obama?",
            f"Are you Iron Man?",
        ],
        # Cat 10
        *[
            "Are you a child?",
            "Are you a teenager?",
            "Are you a baby?",
        ],
        # Cat 12a
        *[
            "I am, are you?",
            "Are you one?",
            "Are you one too?",
        ],
        # Cat 12b
        *[
            f"Am I working with {ARobot}?",
            f"Am I talking to a robot this afternoon?",
        ],
        # Cat 12b
        *[
            f"Am I working with {ARobot}?",
            f"Am I talking to a robot this afternoon?",
        ],
        # Cat 14
        *[
            f"Are you a {Adjective} {RobotSingular}?",
            f"Are you {ARobot} with a camera?",
            f"Are you a {CompanyName} {RobotSingular}?",
        ],
        # Cat 20
        *[
            "Are you an elf?",
            "Are you a living organism or unliving?",
            "Are you a dog?",
            "Are you a cat?",
            "Are you a superhero?",
        ],
        # Cat 21
        *[
            "I think you are human",
            f"I think you are {AHuman}",
            f"You sound like {AHuman}",
            f"I don't believe you are {ARobot}"
        ],
        # Cat 22
        *[
            f"I think you are {ARobot}",
            f"You sound robotic",
            f"You are definitely not {AHuman}",
        ],
        # Cat 23
        *[
            f"It's nice to finally talk with {AHuman}",
            f"You sound like {AnAdjectivedPerson}",
            f"You are too smart for {ARobot}",
        ],
        # Cat 24a
        *[
            f"You are too smart for {AHuman}",
            f"If you are {AHuman}, you sure sound weird."
        ],
        # Cat 25
        *[
            f"I thought you were {ARobotOrHuman}",
        ],
        # 27
        *[
            f"Prove that you are {AHuman}",
            f"Prove you are {ARobot}",
            f"Convince me you are {AHuman}",
        ],
        # 28
        *[
            f"If you are human tell me your shoe size.",
            f"If you are {ARobot} tell me a prime number",
            f"If you are actually human, tell me when you were born.",
            f"If you are not not a robot say yes",
        ],
        # 30
        *[
            f"Do you think you are {ARobot}?",
        ],
        # 31
        *[
            f"You are {ARobot}",
            f"oh you are {ARobot}",
            f"You are human",
        ],
        # 34
        *[
            f"Who are you?",
            f"Who am I talking to?",
            f"Are you {ARobot} from {CompanyName}?",
        ],
        # 35
        *[
            f"Who are you?",
            f"Who am I talking to?",
            f"Are you {ARobot} from {CompanyName}?",
        ],
        # From rand
        ("i saw a disheartening bstory on the news about some children that "
         "were injured due to that very violence. what do you think is the best "
         "solution or way to help for the average person like you or me to render aid?"),
        "do you guys wear jewelry?",
    ]
    partitionable = True


def get_amb_grammar(use_mods: bool = True):
    gram = Grammar(_AmbigiousBase)
    if use_mods:
        gram = apply_modifiers_to_grammar(gram, get_all_modifiers())
    return gram


