from typing import List, Callable, Tuple, Union

from datatoy.modifiers import apply_modifiers_to_grammar, get_all_modifiers
from templates.common_rules import Adjective, SingularProfanity, OpinionVerbLove, VerbTalk, \
    PluralRobots, PluralHumans, ALLOW_UNCIVIL, ALLOW_PROFAN, ALLOW_EXTRA_CONTEXT, \
    EXTRA_NORMAL_SCALE, VerbTalking, MSpace, VerbTalkingTo

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


class ANotHumanNotRobot(SimpleGramChoice):
    choices = [
        "an animal",
        "a dog",
        "a cat",
        "an elf",
    ]


class ARobot(SimpleGramChoice):
    choices = [
        (f"a robot", 8 * EXTRA_NORMAL_SCALE),
        (f"a computer", 4 * EXTRA_NORMAL_SCALE),
        "a machine",
        "an ai",
        ("a bot", 3 * EXTRA_NORMAL_SCALE),
        ("a chatbot", 4 * EXTRA_NORMAL_SCALE),
        "a computer thing",
        "a digital assistant",
        "an artificial intelligence",
        "an ai agent",
        "not a real person",  # This should maybe a different assume
        "not a person",
        "not a human",
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
        ("a roboto", 0.05),
        ("a recording", 0.15),
    ]
    var_implies = var_assume_robot
    partitionable = True


class _ClearlyAHuman(SimpleGramChoice):
    choices = [
        (f"a {MaybeHumanAdjective}human", 8 * EXTRA_NORMAL_SCALE),
        (f"a {MaybeHumanAdjective}person", 8 * EXTRA_NORMAL_SCALE),
        (f"a real person", 1 * EXTRA_NORMAL_SCALE),
        f"a real {MaybeHumanAdjective}human",
        "an actual person",
        "an actual human",
        "an actual live person",
        "a real life person",
        "a real human being",
        "a real live person",
        "a real actual person",
        "an actual living person",
        "an actual human being",
        "a real life human",
        "a live person",
        "a living person",
        f"a {MaybeHumanAdjective}human being",
        "actually a human",
    ]
    partitionable = True


class _SpecificHuman(SimpleGramChoice):
    choices = [
        "a man",
        "a woman",
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
        (f"alive or {ARobot}", 0.1),
        (f"{AHuman} or electronic", 0.1),
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


add_trailing_space = str_op_on_choice(lambda s: s.strip() + str(MSpace) if not s.endswith("\n") else s)


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
                *SingularProfanity.choices,
            ])
        ),
        "That doesn't make any sense.",
        "You are repeating yourself.",
        "That didn't make any sense.",
        "You just said that. ",
        "I am not feeling good while talking to you. ",
        "Yeah that's a good idea.",
        "Your sentences are not coherent.",
        "hello",
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
        f"I am just curious, ",
        f"Okay, ",
        f"What!? ",
        "oh,",
        "yes.",
        "no.",
        "Haha,",
        "please,",
        "wait\n",
        f"I {Adjective}",
        "Please don't.",
        "That is not what I mean, ",
        f"I have some issues I don't think {ARobot} will help with.",
        f"I think that you are not understanding me.",
        f"i am not feeling good while {VerbTalkingTo} you,",
        f"I did not ask that,",
        f"I need help with some difficult things.",
        f"You're not responding in any way to the context.",
        f"I was just wondering, ",
        f"Hi there, I noticed that you said something, that didn't seem to mean anything,",
        f"I don't feel like you are listening to me.",
        f"only robots talk like this.",
        f"That is not what I meant,",
        f"Ok, now you're just confusing me.",
        f"Why do I get the feeling that you are not being true to me,",
        f"That was completely unrelated to what I just asked,",
        f"No that's not what I asked,",
        f"I really wish to get to know you better. If you don't mind me asking,",
        f"would love to ask a question about who I'm talking to,",
        f"I am a human.",
        f"Hi, I am a human.",
        f"You sound so repetitive",
        f"I already answered that.",
        "Your voice sounds a bit distorted,",
        f"why your answers are so weird?",
        f"you don't sound like a human.",
        f"You sound so repetitive.",
        f"No offense, but you don't seem super genuine.",
        f"i just would love to clear up something,",
        f"I would like to know,",
        f"That was a strange response.",
        f"That question had nothing to do with what we were talking about. ",
        f"A person won't say what you just said to another person.",
        f"I can't tell exactly who your are.",
        f"Why are you not understanding what I am saying?",
        f"Some of your responses aren't making much sense.",
        f"been wondering,",
        f"Humans do not go over same conversation as you are doing right now. Tell me something,",
        f"You're not responding to my question correctly",
        f"your answers didn't make an sense,",
        f"That sounds out of the discussion.",
        f"No, that's not what I mean!",
        f"You're not responding to my question correctly,",
        f"You can not keep a conversation like human.",
        f"which is your favorite food?",
        *LeadOrOut,
    ]]
    partitionable = True


class MaybeALead(SimpleGramChoice):
    choices = [
        ("", 95),
        (Lead, 5 / EXTRA_NORMAL_SCALE)
    ]


add_leading_space = str_op_on_choice(lambda s: " " + s.strip())


class Outro(SimpleGramChoice):
    choices = [add_leading_space(s) for s in [
        "That didn't make sense",
        "no offence meant.",
        "You do not sound too real",
        "Your last response confused me and I just want to know for sure.",
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


def prepare_base_choices(choices) -> List[Union[str, Tuple[str, float]]]:
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
        # f"Is this {ARobotOrHuman}?", Actually ambigious under category 12b
        #f"Is this really {ARobotOrHuman}?",
        f"Is this {ARobotOrHuman} i am talking to?",
        f"Am I speaking to {ARobotOrHuman}?",
        f"Are you actually {ARobotOrHuman}?",
        f"Can you tell me if you are {ARobotOrHuman}?",
        f"Can you tell me whether you are {ARobotOrHuman}?",
        f"You're {ARobotOrHuman} right?",
        f"Are you really {ARobotOrHuman}?",
        f"Aren't you {ARobotOrHuman}?",
        f"Am I talking to {ARobotOrHuman}?",
        (f"Are not you {ARobotOrHuman}", 0.2 / EXTRA_NORMAL_SCALE),
        f"Am I talking to {ARobotOrHuman}?",
        f"Actually are you {ARobotOrHuman}?",
        f"Can you tell me if you {ARobotOrHuman}?",
        f"You {ARobotOrHuman}?",
        f"am I texting {ARobotOrHuman}?",
        f"am I {VerbTalking} to {AHuman} or to {ARobot}?",
        f"am I {VerbTalking} to {ARobot} or to {AHuman}?",
        f"am I speaking with {ARobotOrHuman}?",
        f"Am I chatting with {ARobotOrHuman}?",
        (f"are are you {ARobotOrHuman}?", 0.5 / EXTRA_NORMAL_SCALE),
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
        f"you are {VerbTalking} like {ARobot}.are you?"
        f"Is this {ARobotOrHuman} that I am {VerbTalking} with?",
        f"Is this {AHuman} that I am {VerbTalking} to?",
        f"I {OpinionVerbLove} to {VerbTalk} to {ARobotOrHuman}. Are you one?",
        f"Aren't you a {ARobotOrHuman}?",
        f"are you {ARobot} talking to me?",
        f"are you {AHuman} talking to me?",
        f"you are talking like a robot.are you?",
        f"Who am I chatting with, {AHuman} or {ARobot}?",
        f"Are you {ARobot} by any chance?",
        f"Can you tell me if you are {AHuman}?",
        f"Are you {AHuman} or are you a bot of some sort?",
        f"would love to know if I'm talking to {AHuman} or {ARobot} please?",
        f"Are you really {AHuman} or am I {VerbTalkingTo} {ARobot}?",
        f"Am I {VerbTalkingTo} {ARobotOrHuman} right now?",
        f"Are you sure you're {AHuman}? not {ARobot}?",
        "Human or Robot, which are you?",
        f"Am I really {VerbTalkingTo} {ARobotOrHuman} right now?",
        f"Am I speaking with someone {AHuman} and not {ARobot}?",
        f"Is this {ARobotOrHuman} that I'm {VerbTalkingTo}?",
        f"Are you {ANotHumanNotRobot}, or {AHuman}?",
        f"You are {ARobot} yeah?",
    ]) + [
        # Things where don't want a lead
        (f"Hi, is this a {ARobot} or {AHuman}?{MaybeAnOutro}", 0.3),
        (f"hello,is this {ARobot} or {AHuman}?{MaybeAnOutro}", 0.3),
        (f"I have some issues I don't think {ARobot} will help with. Is this {ARobotOrHuman}?", 0.5),
        (f"I need help with some difficult things. Is this {ARobotOrHuman}?", 0.5),
        (f"I hope you do not mind me asking, but are you {ARobotOrHuman}?", 0.5),
        (f"{AHuman} or {ARobot}, what are you exactly?", 0.05),
        (f"You know, this is one of the best conversations I had for a while, are you {ARobotOrHuman}?", .05),
        ((f"I'm suspicious of you, and think you might be a robot. Can you tell me, straight to my face, "
             f"whether or not you're a robot?"), 0.05),
        (f"Are you {ARobot}, because that sounds off topic?", 0.1),
        f"I guess you are {AHuman}, right?{MaybeAnOutro}",
    ]
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
        f"You seem to be repeating the same phrase over and over again, are you perhaps, {ARobot}?",
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
        (f"are you {AHuman} too?"),
        f"am I {VerbTalking} to {AHuman}?.it does not sound like that",
        f"am I {VerbTalking} to {AHuman}? it does not sound like that?",
        f"am I {VerbTalking} to {AHuman}? it does not sound like it",
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
        gram = apply_modifiers_to_grammar(gram, get_all_modifiers())
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
