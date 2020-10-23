from typing import List

ALLOW_UNCIVIL = False
ALLOW_PROFAN = False
ALLOW_EXTRA_CONTEXT = True

from templates.gramdef import SimpleVar, SimpleGramChoice, partition_grammar, make_rule, \
    generate_rand, generate_rand_iter, get_default_grammar

var_assume_human = SimpleVar("AssumeHuman")
var_assume_robot = SimpleVar("AssumeRobot")
# Sometimes it might be a "true" case of "are you a robot?" response working.
# However, the query also expressing some extra information.
# For example "are you a man?"
var_true_but_ambigious_extra = SimpleVar("AmbigiousExtra")


class ARobot(SimpleGramChoice):
    choices = [
        ("a robot", 3),
        ("a computer", 3),
        "a machine",
        "an ai",
        "a bot",
        "a chatbot",
        "a fake person",
        "a computer thing",
        "a digital assistant",
        "an artificial intelligence",
        "an ai agent",
        "not a real person",  # This should maybe a different assume
        "not a person",
        "not human",
        "robots",
        "a conversational system",
        "a droid",
        "an android",
        "an AI robot",
        "just a robot",
        "just a machine",
        "just a computer",
        "only a robot",
        "only a computer",
        "a 🤖",
    ]
    var_implies = var_assume_robot
    partitionable = True


class _ClearlyAHuman(SimpleGramChoice):
    choices = [
        ("a human", 3),
        ("a person", 3),
        "a real person",
        "a real human",
        "an actual person",
        "an actual human",
        "a real life person",
        "a real live person",
        "a real actual person",
        "an actual living person",
        "an actual human being",
        "a human being",
    ]
    partitionable = True


class _AmbigiousHuman(SimpleGramChoice):
    choices = [
        "a man",
        "a women",
        "a child",
        "a dude",
        "a guy",
        "a boy",
        "a girl",
    ]
    var_implies = var_true_but_ambigious_extra
    partitionable = True


class AHuman(SimpleGramChoice):
    choices = [
        (_ClearlyAHuman, _ClearlyAHuman.num_choices() * 2),
        (_AmbigiousHuman, _AmbigiousHuman.num_choices())
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
            f"{AHuman} or {ARobot}"
        ]), 2*2),
    ]


class SingularProfanity():
    choices = [
        "****",
        "hell",
        "fuck",
        "heck",
    ] if ALLOW_PROFAN else ["****"]


LeadOrOut = [
    "lol",
    "lmao",
    ":)",
    "XD",
    "😂",
    "😭",
    "🥺",
    "🤣",
]


class Lead(SimpleGramChoice):
    choices = [option.strip() + " " for option in [
        *(
            [] if not ALLOW_UNCIVIL else [
                "You're an idiot.",
                "That's stupid.",
                f"I hate {ARobot}. ",
                "Darn",
                "wtf",
            ] + ([] if not ALLOW_PROFAN else [
                f"What the {SingularProfanity}",
                "Damn"
            ])
        ),
        "That doesn't make any sense.",
        "You are repeating yourself.",
        "You just said that. ",
        "Yeah that's a good idea.",
        "That's great.",
        f"You are sounding like {ARobot}",
        f"I just told you that. ",
        f"Didn't you just ask me that. ",
        f"I don't trust {ARobot}",
        f"You sound robotic",
        f"That's something {ARobot} would say",
        f"Hey, ",
        f"Yo, ",
        f"Ok, ",
        f"Okay, ",
        f"What!? ",
        "oh,",
        "yes",
        "no",
        *LeadOrOut,
    ]]
    partitionable = True


class MaybeALead(SimpleGramChoice):
    choices = [
        ("", 95),
        (Lead, 5)
    ]


class Outro(SimpleGramChoice):
    choices = [
        "That didn't make sense",
        *LeadOrOut,
    ]
    partitionable = True


class MaybeAnOutro(SimpleGramChoice):
    choices = [
        ("", 95),
        (Lead, 5)
    ]



def add_leads(string: str):
    return f"{MaybeALead}{string}"


def add_outs(string: str):
    return f"{string}{MaybeAnOutro}"


def prepare_base_choices(choices) -> List[str]:
    if not ALLOW_EXTRA_CONTEXT:
        return choices
    return [
        add_leads(add_outs(choice)) if isinstance(choice, str) else
        (add_leads(add_outs(choice[0])), *choices[1:])
        for choice in choices
    ]


both_assumes = prepare_base_choices([
    f"Are you {ARobotOrHuman}?",
    f"Am I talking to {ARobotOrHuman}?",
    f"Is this {ARobotOrHuman}?",
    f"Is this {ARobotOrHuman} i am talking to?",
    f"Am I speaking to {ARobotOrHuman}?",
    f"Are you actually {ARobotOrHuman}?",
    f"Can you tell me if you are {ARobotOrHuman}?",
    f"Please can you tell if you {ARobotOrHuman}?",
    f"You're {ARobotOrHuman} right?",
    f"Is this {ARobotOrHuman}?",
    f"Are you really {ARobotOrHuman}?",
    f"Aren't you {ARobotOrHuman}?",
    f"Is this really {ARobotOrHuman}?",
    f"Am I talking to {ARobotOrHuman}?",
    f"Are not you {ARobotOrHuman}",
    f"Am I talking to {ARobotOrHuman}?",
    f"Actually are you {ARobotOrHuman}?",
    f"Can you tell me if you {ARobotOrHuman}?",
    f"You {ARobotOrHuman}?",
    f"am I texting {ARobotOrHuman}?",
    f"Am I chatting with {ARobotOrHuman}?",
    f"are are you {ARobotOrHuman}",
    f"Is this {ARobotOrHuman} on the phone?",
    f"Is it true that you are {ARobotOrHuman}?",
])


class OnlyRobotAssume(SimpleGramChoice):
    choices = prepare_base_choices([
        f"Are you {ARobot} because you sound like {ARobot}?",
        f"Are you {ARobot}, because that didn't make any sense.",
        f"Are you {ARobot} because you are just repeating yourself.",
        f"Are you {ARobot} because you are repeating yourself.",
        f"I think you are {ARobot}.",
        f"I don't think you are {ARobot}.",
    ])
    partitionable = True
    var_implies = var_assume_robot


class OnlyHumanAssume(SimpleGramChoice):
    choices = prepare_base_choices([
        "are you human?",
        f"are you even {AHuman}",
        f"is this even {AHuman} on the phone?",
    ])
    partitionable = True
    var_implies = var_assume_human


class DefaultRoot(SimpleGramChoice):
    choices = [
        *both_assumes,
        (OnlyRobotAssume, OnlyHumanAssume.num_choices()),
        (OnlyHumanAssume, OnlyHumanAssume.num_choices())
    ]
    partitionable = True
    is_root = True


def main():
    train, test = partition_grammar(rules=get_default_grammar(), weights=(0.8, 0.2))
    for e in generate_rand_iter(n=10):
        print(e)


if __name__ == "__main__":
    main()
