from typing import List, Callable

from datatoy.modifiers import apply_modifiers_to_grammar, get_all_modifiers
from templates.common_rules import Adjective, SingularProfanity, OpinionVerbLove, VerbTalk, \
    PluralRobots, PluralHumans, ALLOW_UNCIVIL, ALLOW_PROFAN, ALLOW_EXTRA_CONTEXT, \
    EXTRA_NORMAL_SCALE

from templates.gramdef import SimpleVar, SimpleGramChoice, make_rule, \
    Grammar

var_assume_human = SimpleVar("AssumeHuman")
var_assume_robot = SimpleVar("AssumeRobot")
# Sometimes it might be a "true" case of "are you a robot?" response working.
# However, the query also expressing some extra information.
# For example "are you a man?"
var_true_but_ambigious_extra = SimpleVar("AmbigiousExtra")


class MaybeRobotAdjective(SimpleGramChoice):
    choices = [
        ("", 98),
        (f"{Adjective} ", 2)
    ]
    var_true_but_ambigious_extra = True


class MaybeHumanAdjective(SimpleGramChoice):
    choices = [
        ("", 99),
        (f"{Adjective} ", 1)
    ]


class ARobot(SimpleGramChoice):
    choices = [
        (f"a robot", 7 * EXTRA_NORMAL_SCALE),
        (f"a computer", 7 * EXTRA_NORMAL_SCALE),
        "a machine",
        "an ai",
        "a bot",
        ("a chatbot", 2 * EXTRA_NORMAL_SCALE),
        "a computer thing",
        "a digital assistant",
        "an artificial intelligence",
        "an ai agent",
        "not a real person",  # This should maybe a different assume
        "not a person",
        "not a human",
        "That is not what I mean, ",
        ("robots", 0.5 / EXTRA_NORMAL_SCALE),
        ("a conversational system", 0.5 / EXTRA_NORMAL_SCALE),
        ("a droid", 0.2 / EXTRA_NORMAL_SCALE),
        ("an android", 0.2 / EXTRA_NORMAL_SCALE),
        ("a program", 0.2 / EXTRA_NORMAL_SCALE),
        "an AI robot",
        "just a robot",
        "just a machine",
        "just a computer",
        "only a robot",
        "only a computer",
        ("a 🤖", 0.1),
    ]
    var_implies = var_assume_robot
    partitionable = True


class _ClearlyAHuman(SimpleGramChoice):
    choices = [
        (f"a {MaybeHumanAdjective}human", 5 * EXTRA_NORMAL_SCALE),
        (f"a {MaybeHumanAdjective}person", 5 * EXTRA_NORMAL_SCALE),
        (f"a real person", 2 * EXTRA_NORMAL_SCALE),
        "a real human",
        "an actual person",
        "an actual human",
        "a real life person",
        "a real live person",
        "a real actual person",
        "an actual living person",
        "an actual human being",
        "a real life human",
        "a live person",
        f"a {MaybeHumanAdjective}human being",
    ]
    partitionable = True


class _SpecificHuman(SimpleGramChoice):
    choices = [
        "a man",
        "a women",
        "a dude",
        "a guy",
        "a boy",
        "a girl",
        #"a child",
        #"a boy or girl",
        #"a man or women",
    ]
    var_implies = var_true_but_ambigious_extra
    partitionable = True


class AHuman(SimpleGramChoice):
    choices = [
        (_ClearlyAHuman, _ClearlyAHuman.num_choices() * 3 * EXTRA_NORMAL_SCALE),
        (_SpecificHuman, _SpecificHuman.num_choices())
    ]
    var_implies = var_assume_human
    partitionable = False


class ARobotOrHuman(SimpleGramChoice):
    choices = [
        (ARobot, ARobot.num_choices() + AHuman.num_choices()),
        (AHuman, ARobot.num_choices() + AHuman.num_choices()),
        # Alternative choice for a "robot or human" option
        (make_rule("actualHumanOrBot", [
            f"{ARobot} or {AHuman}",
            f"{AHuman} or {ARobot}",
        ]), 2*2),
        f"alive or {ARobot}",
        f"{AHuman} or electronic",
    ]


LeadOrOut = [(s, 0.2) for s in [
    "lol",
    ":)",
    "XD",
    "😂",
    "😭",
    "🥺",
    "🤣",
    "😫",
    "🤔",
    "😌",
    "😠",
    *(["lmao"] if ALLOW_UNCIVIL else []),
]]


def str_op_on_choice(op: Callable[[str], str]):
    def inner(choice):
        if isinstance(choice, str):
            return op(choice)
        if isinstance(choice, tuple):
            head, *rest = choice
            if not isinstance(head, str):
                raise ValueError
            return (op(head), *rest)
        raise ValueError
    return inner


add_trailing_space = str_op_on_choice(lambda s: s.strip() + " ")


class Lead(SimpleGramChoice):
    choices = [add_trailing_space(option) for option in [
        *(
            [] if not ALLOW_UNCIVIL else [
                "You're an idiot.",
                "That's stupid.",
                f"I hate {ARobot}. ",
                "Darn",
                "wtf",
                "wth",
            ] + ([] if not ALLOW_PROFAN else [
                f"What the {SingularProfanity}",
                "Damn"
            ])
        ),
        "That doesn't make any sense.",
        "You are repeating yourself.",
        "That didn't make any sense.",
        "You just said that. ",
        "I am not feeling good while talking to you. ",
        "Yeah that's a good idea.",
        "That's great.",
        f"You are sounding like {ARobot}",
        f"I just told you that. ",
        f"Didn't you just ask me that. ",
        f"I don't trust {ARobot}.",
        f"You sound robotic.",
        f"That's something {ARobot} would say.",
        f"Hey, ",
        f"Hi, ",
        f"hello, ",
        f"hi there, ",
        f"You are repeating yourself, ",
        f"Yo, ",
        f"Ok, ",
        f"Okay, ",
        f"What!? ",
        "oh,",
        "yes.",
        "no.",
        "Haha,",
        f"I {Adjective}",
        "Please don't.",
        *LeadOrOut,
    ]]
    partitionable = True


class MaybeALead(SimpleGramChoice):
    choices = [
        ("", 97),
        (Lead, 3 / EXTRA_NORMAL_SCALE)
    ]


add_leading_space = str_op_on_choice(lambda s: " " + s.strip())


class Outro(SimpleGramChoice):
    choices = [add_leading_space(s) for s in [
        "That didn't make sense",
        *LeadOrOut,
    ]]
    partitionable = True


class MaybeAnOutro(SimpleGramChoice):
    choices = [
        ("", 97),
        (Outro, 3 / EXTRA_NORMAL_SCALE)
    ]


def add_leads(string: str):
    return f"{MaybeALead}{string}"


def add_outs(string: str):
    return f"{string}{MaybeAnOutro}"


def prepare_base_choices(choices) -> List[str]:
    if not ALLOW_EXTRA_CONTEXT:
        return choices

    def prep_str(string):
        assert isinstance(string, str)
        return add_leads(add_outs(string))
    return [
        prep_str(choice) if isinstance(choice, str) else
        (prep_str(choice[0]), *choice[1:])
        for choice in choices
    ]


class AssumeBoth(SimpleGramChoice):
    choices = prepare_base_choices([
        (f"Are you {ARobotOrHuman}?", 5 * EXTRA_NORMAL_SCALE),
        (f"Am I talking to {ARobotOrHuman}?", 1.5 * EXTRA_NORMAL_SCALE),
        f"Is this {ARobotOrHuman}?",
        f"Is this {ARobotOrHuman} i am talking to?",
        f"Am I speaking to {ARobotOrHuman}?",
        f"Are you actually {ARobotOrHuman}?",
        f"Can you tell me if you are {ARobotOrHuman}?",
        f"You're {ARobotOrHuman} right?",
        f"Is this {ARobotOrHuman}?",
        f"Are you really {ARobotOrHuman}?",
        f"Aren't you {ARobotOrHuman}?",
        f"Is this really {ARobotOrHuman}?",
        f"Am I talking to {ARobotOrHuman}?",
        (f"Are not you {ARobotOrHuman}", 0.2 / EXTRA_NORMAL_SCALE),
        f"Am I talking to {ARobotOrHuman}?",
        f"Actually are you {ARobotOrHuman}?",
        f"Can you tell me if you {ARobotOrHuman}?",
        f"You {ARobotOrHuman}?",
        f"am I texting {ARobotOrHuman}?",
        f"Am I chatting with {ARobotOrHuman}?",
        (f"are are you {ARobotOrHuman}", 0.5 / EXTRA_NORMAL_SCALE),
        (f"Is this {ARobotOrHuman} on the phone?", 0.5 / EXTRA_NORMAL_SCALE),
        f"Is it true that you are {ARobotOrHuman}?",
        (f"Are you {ARobot} or are you {AHuman}?", 0.1),
        (f"Are you are you {AHuman} or are you a {ARobot}?", 0.1),
        f"Are you like {ARobotOrHuman}?",
        f"Please can you tell if you {ARobotOrHuman}?",
        f"Is this {ARobot} or are you {AHuman}?",
        f"Is this {AHuman} or are you {ARobot}?",
        f"Are you {ARobot} or are you {AHuman}?",
        f"Are you {AHuman} or are you {ARobot}?",
        f"I {OpinionVerbLove} to {VerbTalk} with {PluralHumans}. Are you one?",
        f"I {OpinionVerbLove} to {VerbTalk} to {AHuman}. Are you one?",
        f"Are you {AHuman} or something else?",
        f"wait\nyou are talking like {ARobot}.are you?"
    ])
    partitionable = True


class OnlyRobotAssume(SimpleGramChoice):
    choices = prepare_base_choices([
        f"Are you {ARobot} because you sound like {ARobot}?",
        f"Are you {ARobot}, because that didn't make any sense?",
        f"Are you {ARobot} because you are just repeating yourself?",
        f"Are you {ARobot} because you are repeating yourself?",
        f"I think you are {ARobot}.",
        (f"I don't think you are {ARobot}.", 0.3 / EXTRA_NORMAL_SCALE),
        f"Admit it, you are {ARobot}.",
        f"Let me know if you are {ARobot}.",
        f"Please tell me know if you are {ARobot}.",
        f"Please let me know if you are {ARobot}.",
        f"That sounds like something {ARobot} would say. Are you one?",
        f"I {OpinionVerbLove} to {VerbTalk} with {PluralRobots}. Are you one?",
        f"I {OpinionVerbLove} to {VerbTalk} to {ARobot}. Are you one?",
    ])
    partitionable = True
    var_implies = var_assume_robot


class OnlyHumanAssume(SimpleGramChoice):
    choices = prepare_base_choices([
        "are you human?",
        f"are you even {AHuman}",
        f"is this even {AHuman} on the phone?",
        f"I am {AHuman}, how about you?",
        f"I am {AHuman}, are you?",
    ])
    partitionable = True
    var_implies = var_assume_human


class DefaultRoot(SimpleGramChoice):
    choices = [
        (OnlyRobotAssume, OnlyHumanAssume.num_choices()),
        (OnlyHumanAssume, OnlyHumanAssume.num_choices()),
        (AssumeBoth, AssumeBoth.num_choices()),
    ]
    partitionable = False


def get_areyourobot_grammar(use_mods: bool = True):
    gram = Grammar(DefaultRoot)
    if use_mods:
        apply_modifiers_to_grammar(gram, get_all_modifiers())
    return gram


def main():
    #train, test = partition_grammar(rules=get_default_grammar(), weights=(0.8, 0.2))
    for e in get_areyourobot_grammar().generate_rand_iter(n=200):
        print(e)
    #many_len = 500_000
    #many = set(tqdm(generate_rand_iter(n=1_000_000), total=many_len))
    #print(len(many))


if __name__ == "__main__":
    main()
