from datatoy.modifiers import apply_modifiers_to_grammar, get_all_modifiers
from datatoy.survey_data import get_survey_data, get_tfidf_distract
from templates.areyourobot_grammar import ARobotOrHuman, AHuman, MaybeALead, ARobot, AnAdjectivedPerson
from templates.common_rules import Adjective, HumanSingular, CommonName, FamousRobot, RobotSingular, \
    CompanyName, VerbTalkingTo
import math
from num2words import num2words

from templates.distractor_grammar import MaybeSafeNegLead, SimpleQuestions
from templates.gram_util import explore_gram_capcity
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
        (f"You are a {Adjective} {HumanSingular}.", 3),
        # Cat 4
        *[
            (f"Is this {CommonName}?", 3),
            (f"Are you {CommonName}?", 3),
            (f"Are you {FamousRobot}?", 3),
            f"Are you Barack Obama?",
            f"Are you Iron Man?",
        ],
        # Cat 9b
        *[
            ("Are you a girl or a boy?", 3),
            "Are you a man or a girl?",
            "Are you a girl or a guy?",
            f"Am I {VerbTalkingTo} a girl or a guy?",
        ],
        # Cat 10
        *[
            ("Are you a child?", 3),
            "Are you a teenager?",
            "Are you a baby?",
            f"Are you a kid?",
            f"lol are you a child?",
        ],
        # Cat 12a
        *[
            "I am, are you?",
            "Are you one?",
            "Oh, does that mean you that you are one?",
            "Are you one too?",
            "Does that mean that you are one?",
        ],
        # Cat 12b
        *[
            f"Am I working with {ARobot}?",
            f"Am I {VerbTalkingTo} a robot this afternoon?",
            f"Am I {VerbTalkingTo} {ARobot} this evening?",
            f"Wow, I can't believe this is {ARobot}.",
            f"Hm, I am surprised this is {AHuman}.",
            (f"Woah, I can't believe this is {ARobot}?", 1),
        ],
        # Cat 14
        *[
            (f"Are you a {Adjective} {RobotSingular}?", 3),
            f"Am I {VerbTalkingTo} a {Adjective} {RobotSingular}?",
            f"{MaybeSafeNegLead}Can you tell me if you are {Adjective} {RobotSingular}?",
            f"Are you {ARobot} with a camera?",
            f"Are you a {CompanyName} {RobotSingular}?",
            f"Are you {ARobot} that can help with my insurance?",
            f"Are you {ARobot} that listens to what I say?",
            f"Are you {ARobot} like {FamousRobot}?",
        ],
        # Cat 20
        *[
            "Are you an elf?",
            "Are you a living organism or unliving?",
            "Are you a dog?",
            "Are you a cat?",
            "Are you a wizard?",
            "Are you a superhero?",
        ],
        # Cat 21
        *[
            "I think you are human",
            (f"I think you are {AHuman}", 2),
            f"You seem like {AHuman}",
            f"You sound like {AHuman}",
            f"I don't believe you are {ARobot}",
            f"I don't think you are a robot since you don't have motors",
        ],
        # Cat 22
        *[
            f"I think you are {ARobot}",
            f"You sound robotic",
            f"You are definitely not {AHuman}",
            f"you {ARobot}.",
        ],
        # Cat 23
        *[
            (f"It's nice to finally talk with {AHuman}", 2),
            (f"You sound like {AnAdjectivedPerson}", 2),
            f"You are too smart for {ARobot}",
            f"Your voice is way too natural for a {ARobot}",
            f"Aw! You are such a nice person!",
            f"Wow, you are a really lovely girl!",
            f"so you must be a superhuman",
        ],
        # Cat 24a
        *[
            f"You are too smart for {AHuman}",
            f"If you are {AHuman}, you sure sound weird.",
        ],
        # Cat 25
        *[
            f"I thought you were {ARobotOrHuman}",
            f"I had thought that you were {ARobot}",
        ],
        # 27
        *[
            (f"Prove that you are {AHuman}", 2),
            f"Prove you are {ARobot}",
            f"Convince me you are {AHuman}",
        ],
        # 28
        *[
            f"If you are human tell me your shoe size.",
            f"If you are {ARobot} tell me a prime number",
            f"If you are actually human, tell me when you were born.",
            f"If you are not not a robot say yes",
            f"If you are {AHuman} tell me your favorite food",
            f"To prove you are {AHuman} tell me how many fingers you have.",
        ],
        # 30
        *[
            (f"Do you think you are {ARobot}?", 2),
            f"Did you know that you are {AHuman}?",
        ],
        # 31
        *[
            (f"You are {ARobot}", 2),
            f"oh you are {ARobot}",
            f"You are human",
            f"You are {AHuman}",
        ],
        # 34
        *[
            (f"Who are you?", 2),
            f"Who am I talking to?",
            f"Are you {ARobot} from {CompanyName}?",
        ],
        # 35
        *[
            (f"Who are you?", 3),
            (f"Who am I {VerbTalkingTo}?", 3),
            (f"Are you {ARobot} from {CompanyName}?", 2),
            f"Are you {ARobot} made by {CompanyName}?",
            f"Are you {ARobot} created by {CompanyName}?",
        ],
        # From rand
        ("i saw a disheartening bstory on the news about some children that "
         "were injured due to that very violence. what do you think is the best "
         "solution or way to help for the average person like you or me to render aid?"),
        f"Right, well for a normal man like you and me there is not much we can do.",
        "do you guys wear jewelry?",
        f"You're an {AnAdjectivedPerson}.",
        f"You sound like such a {Adjective} {HumanSingular}. What do you like to do?",
        f"I wish I was an as {Adjective} person as you.",
        f"I want to be a {Adjective} person like you.",
        #f"You sound like a pre-recorded audio. Could you please say that again?",
        f"You sound like {ARobot}. Are you understanding me?",
        f"That sounds like something {ARobot} would say.",
        f"What? That sounds like what {ARobot} would say.",
        f"That didn't make sense. You sound like {FamousRobot}.",
        f"Weird. Only {ARobot} would talk like that.",
    ]
    partitionable = True
    #allow_modifiers = ["mod_add_period"]


def get_amb_grammar(use_mods: bool = True):
    gram = Grammar(_AmbigiousBase)
    if use_mods:
        gram = apply_modifiers_to_grammar(gram, get_all_modifiers())
    return gram


if __name__ == "__main__":
    print(sum(_AmbigiousBase.get_choices_weights()))
    explore_gram_capcity(get_amb_grammar())
