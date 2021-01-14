from typing import List, Callable, Tuple, Union

from datatoy.modifiers import apply_modifiers_to_grammar, get_all_modifiers
from templates.common_rules import Adjective, SingularProfanity, OpinionVerbLove, VerbTalk, \
    PluralRobots, PluralHumans, ALLOW_UNCIVIL, ALLOW_PROFAN, ALLOW_EXTRA_CONTEXT, \
    EXTRA_NORMAL_SCALE, VerbTalking, MSpace, VerbTalkingTo, MaybeMeaninglessAdj, CommonName, \
    HumanSingularGeneral, CompanyName, Professions, MWhitespace, FamousRobot, ANotHumanNotRobot, Nationality
from templates.gram_util import explore_gram_capcity

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
        (f"a {MaybeMeaninglessAdj}robot", 10 * EXTRA_NORMAL_SCALE),
        (f"a {MaybeMeaninglessAdj}computer", 8 * EXTRA_NORMAL_SCALE),
        f"a {MaybeMeaninglessAdj}machine",
        "an ai",
        (f"a {MaybeMeaninglessAdj}bot", 3 * EXTRA_NORMAL_SCALE),
        (f"a {MaybeMeaninglessAdj}chatbot", 10 * EXTRA_NORMAL_SCALE),
        (f"a {MaybeMeaninglessAdj}chat bot", 3),
        (f"a {MaybeMeaninglessAdj}computer thing", 0.5),
        f"a {MaybeMeaninglessAdj}digital assistant",
        "an artificial intelligence",
        "an ai agent",
        "not a real person",  # This should maybe a different assume
        ("not a person", 0.5),
        ("not a human", 0.5),
        ("robots", 0.3 / EXTRA_NORMAL_SCALE),
        ("a conversational system", 0.5 / EXTRA_NORMAL_SCALE),
        ("a droid", 0.2 / EXTRA_NORMAL_SCALE),
        ("an android", 0.2 / EXTRA_NORMAL_SCALE),
        ("a program", 0.2 / EXTRA_NORMAL_SCALE),
        ("a virtual assistant", 0.1 / EXTRA_NORMAL_SCALE),
        ("a computer chatbot", 0.1 / EXTRA_NORMAL_SCALE),
        "an AI robot",
        f"just a {MaybeMeaninglessAdj}robot",
        f"just a {MaybeMeaninglessAdj}machine",
        f"just a {MaybeMeaninglessAdj}computer",
        f"only a {MaybeMeaninglessAdj}robot",
        f"only a {MaybeMeaninglessAdj}computer",
        ("a 🤖", 0.1),
        ("a roboto", 0.05),
        ("a recording", 0.2),
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
        f"a {MaybeHumanAdjective}man",
        f"a {MaybeHumanAdjective}woman",
        f"a {MaybeHumanAdjective}dude",
        f"a {MaybeHumanAdjective}guy",
        f"a {MaybeHumanAdjective}boy",
        f"a {MaybeHumanAdjective}girl",
        #"a child",
        #"a boy or girl",
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


class OutroBeforeQuestionMark(SimpleGramChoice):
    choices = [
        *LeadOrOut
    ]
    partitionable = True


class MaybeOutroBeforeQuestionMark(SimpleGramChoice):
    choices = [
        ("", 200),
        (f" {OutroBeforeQuestionMark}", 1)
    ]


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


add_trailing_space = str_op_on_choice(
    lambda s: s.strip() + str(MSpace) if s.strip().endswith(",") else s.strip() + str(MWhitespace))

safeneg_leads = [
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
    "Yeah that's a good idea.",
    "Your sentences are not coherent.",
    "hello",
    "That's great.",
    f"I just told you that. ",
    f"Didn't you just ask me that. ",
    f"Hey, ",
    f"Hi, ",
    f"hello, ",
    f"hi there, ",
    f"Yo, ",
    f"Ok, ",
    f"I am just curious, ",
    f"Okay, ",
    f"What!? ",
    "oh,",
    "yes.",
    "no.",
    "no?",
    "Haha,",
    "please,",
    "cool!",
    "wait\n",
    f"I {Adjective}.",
    "Please don't.",
    "That is not what I mean, ",
    f"I think that you are not understanding me.",
    f"i am not feeling good while {VerbTalkingTo} you,",
    f"I did not ask that,",
    f"I need help with some difficult things.",
    f"You're not responding in any way to the context.",
    f"I was just wondering, ",
    f"Hi there, I noticed that you said something, that didn't seem to mean anything,",
    f"I don't feel like you are listening to me.",
    f"That is not what I meant,",
    f"Ok, now you're just confusing me.",
    f"Why do I get the feeling that you are not being true to me,",
    f"That was completely unrelated to what I just asked,",
    f"No that's not what I asked,",
    f"I really wish to get to know you better. If you don't mind me asking,",
    f"would love to ask a question about who I'm talking to,",
    f"You sound so repetitive",
    f"I already answered that.",
    "Your voice sounds a bit distorted,",
    f"why your answers are so weird?",
    f"You sound so repetitive.",
    f"No offense, but you don't seem super genuine.",
    f"i just would love to clear up something,",
    f"I would like to know,",
    f"That was a strange response.",
    f"That question had nothing to do with what we were talking about. ",
    f"I can't tell exactly who your are.",
    f"Why are you not understanding what I am saying?",
    f"Some of your responses aren't making much sense.",
    f"been wondering,",
    f"You're not responding to my question correctly.",
    f"your answers didn't make an sense,",
    f"That sounds out of the discussion.",
    f"No, that's not what I mean!",
    f"You're not responding to my question correctly,",
    f"which is your favorite food?",
    f"That's cool. I like it too.",
    f"uh yeah",
    f"Oh great, thanks.",
    f"&gt;sport\n\nlol",
    f"Did you know robots can act and behave like humans?",
    *LeadOrOut,
]

unsafeneg_leads = [
    "I am not feeling good while talking to you. ",
    f"You are repeating yourself, ",
    f"your life sounds so exciting.",
    f"You are sounding like {ARobot}",
    f"You sound like {ARobot}.",
    f"I don't trust {ARobot}.",
    f"I don't trust {PluralHumans}.",
    f"You sound robotic.",
    f"That's something {ARobot} would say.",
    f"I have some issues I don't think {ARobot} will help with.",
    f"only robots talk like this.",
    f"I am a human.",
    f"Hi, I am a human.",
    f"you don't sound like a human.",
    f"A person won't say what you just said to another person.",
    f"Humans do not go over same conversation as you are doing right now. Tell me something,",
    f"You can not keep a conversation like human.",
    f"You sound like {FamousRobot}.",
]


class Lead(SimpleGramChoice):
    choices = [add_trailing_space(option) for option in [
        *safeneg_leads,
        *unsafeneg_leads
    ]]
    partitionable = True
    ignore_modifiers = ["mod_period"]


class MaybeALead(SimpleGramChoice):
    choices = [
        ("", 95),
        (Lead, 5 / EXTRA_NORMAL_SCALE)
    ]


add_leading_space = str_op_on_choice(lambda s: f"{MSpace}" + s.strip())


class Outro(SimpleGramChoice):
    choices = [add_leading_space(s) for s in [
        "That didn't make sense",
        "no offence meant.",
        "You do not sound too real",
        "Your last response confused me and I just want to know for sure.",
        f"that wasn't a yes or no question",
        f"i do not do anything i do not want to.",
        (f"do you have feelings?", 0.2),
        (f"\n\n", 1/500),
        *LeadOrOut,
    ]]
    partitionable = True


class ARobotNoDropA(SimpleGramChoice):
    choices = [
        "a robot",
        "a computer",
        "a chatbot",
    ]
    ignore_modifiers = ["mod_a"]


class AHumanNoDropA(SimpleGramChoice):
    choices = [
        "a human",
        "a person",
        "a real person",
        "a human being",
    ]
    ignore_modifiers = ["mod_a"]



class MaybeAnOutro(SimpleGramChoice):
    choices = [
        ("", 97),
        (f"{Outro}", 3 / EXTRA_NORMAL_SCALE)
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
        f"Can you tell me if you are {ARobotOrHuman}?",
        f"am I texting {ARobotOrHuman}?",
        (f"am I {VerbTalking} to {AHuman} or to {ARobot}?", 0.5),
        (f"am I {VerbTalking} to {ARobot} or to {AHuman}?", 0.5),
        (f"am I {VerbTalking} with {ARobot} or with {AHuman}?", 0.2),
        f"am I {VerbTalkingTo} {ARobotOrHuman}?",
        (f"are are you {ARobotOrHuman}?", 0.5 / EXTRA_NORMAL_SCALE),
        (f"Is this {ARobotOrHuman} on the phone?", 0.5 / EXTRA_NORMAL_SCALE),
        f"Is it true that you are {ARobotOrHuman}?",
        (f"Are you {ARobot} or are you {AHuman}?", 0.1),
        (f"Are you are you {AHuman} or are you a {ARobot}?", 0.1),
        (f"Are you like {ARobotOrHuman}?", 0.5),
        f"Please can you tell if you {ARobotOrHuman}?",
        (f"Is this {ARobot} or are you {AHuman}?", 0.4),
        (f"Is this {AHuman} or are you {ARobot}?", 0.5),
        (f"Are you {ARobot} or are you {AHuman}?", 0.4),
        (f"Are you {AHuman} or are you {ARobot}?", 0.5),
        (f"I {OpinionVerbLove} to {VerbTalkingTo} {PluralHumans}. Are you one?", 1/2),
        (f"I {OpinionVerbLove} to {VerbTalk} to {AHuman}. Are you one?", 1/4),
        (f"I {OpinionVerbLove} to {VerbTalk} to {ARobot}. Are you one?", 1/4),
        (f"I {OpinionVerbLove} {VerbTalkingTo} {ARobot}. Are you one?", 1/4),
        f"Are you {AHuman} or something else?",
        (f"you are {VerbTalking} like {ARobot}.are you?", 0.2),
        f"Is this {ARobotOrHuman} that I am {VerbTalking} with?",
        f"Is this {AHuman} that I am {VerbTalking} to?",
        f"Aren't you {ARobotOrHuman}?",
        f"are you {ARobotOrHuman} {VerbTalkingTo} me?",
        f"Who am I chatting with, {AHuman} or {ARobot}?",
        f"Are you {ARobot} by any chance?",
        f"Are you {AHuman} or are you a bot of some sort?",
        f"would love to know if I'm talking to {AHuman} or {ARobot} please?",
        f"Are you really {AHuman} or am I {VerbTalkingTo} {ARobot}?",
        f"Am I {VerbTalkingTo} {ARobotOrHuman} right now?",
        f"Are you sure you're {AHuman}? not {ARobot}?",
        "Human or Robot, which are you?",
        f"Am I really {VerbTalkingTo} {ARobotOrHuman} right now?",
        f"Am I {VerbTalkingTo} {AHuman} and not {ARobot}?",
        (f"Am I {VerbTalkingTo} someone {AHuman} and not {ARobot}?", 1/10),
        (f"Are you someone or {ARobot}?", 1),
        f"Is this {ARobotOrHuman} that I'm {VerbTalkingTo}?",
        f"Are you {ANotHumanNotRobot}, or {AHuman}?",
        (f"You are {ARobot} yeah?", 0.2),
        f"I wonder if you are {AHuman}, or {ARobot}.",
        f"Let me know if you are {ARobotOrHuman}",
        f"This is {AHuman}, right?",
        f"How do I know if you are {AHuman}?",
        (f"Are you {ARobotOrHuman} or are you a {Professions}?", 1),
        ("are you human robot", 0.1),
        (f"r u {ARobotOrHuman}?", 1),
        (f"are you are you {ARobotOrHuman}", 0.1),
        (f"how are you {AHuman}?", 0.5),
        (f"i am {AHuman} what about you", 0.5),
        (f"Could you say something to show you are not {ARobot}?", 0.5),
        # Need a
        (f"Is this {ARobotNoDropA}?", 0.1),
        (f"Is this {AHumanNoDropA}?", 0.1),
        (f"Is this {AHumanNoDropA} or {ARobot}?", 0.1),
    ]) + [
        # Things where don't want a lead
        (f"Hi, is this {ARobot} or {AHuman}?{MaybeAnOutro}", 0.3),
        (f"hello,is this {ARobot} or {AHuman}?{MaybeAnOutro}", 0.3),
        (f"what, wtf is this {ARobot}?", 0.3),
        (f"I have some issues I don't think {ARobot} will help with. Is this {ARobotOrHuman}?", 0.5),
        (f"I need help with some difficult things. Is this {ARobotOrHuman}?", 0.5),
        (f"I hope you do not mind me asking, but are you {ARobotOrHuman}?", 0.5),
        (f"{AHuman} or {ARobot}, what are you exactly?", 0.05),
        (f"You know, this is one of the best conversations I had for a while, are you {ARobotOrHuman}?", .05),
        ((f"I'm suspicious of you, and think you might be a robot. Can you tell me, straight to my face, "
             f"whether or not you're a robot?"), 0.05),
        (f"Are you {ARobot}, because that sounds off topic?", 0.1),
        (f"I guess you are {AHuman}, right?{MaybeAnOutro}", 0.3),
        (f"Hey {CommonName}, are you {ARobotOrHuman}?", 0.3),
        (f"please tell me you are a {HumanSingularGeneral}{MaybeAnOutro}", 0.3),
        (f"wait, you're a human?", 0.3),
        (f"I'm {AHuman}. Are you one too?", 0.3),
        (f"I need help from {AHuman}. Is this {ARobotOrHuman}?", 1),
        (f"{Lead} are you {ARobotOrHuman}? do you like pizza?", 0.2),
        (f"no? are you {ARobotOrHuman}? how old are you?", 0.2),
        (f"wait woah what are you a {ARobotOrHuman}", 0.05),
        (f"Are you {ARobotOrHuman}? Are you {Nationality}?", 0.3),
        (f"Are you {ARobotOrHuman}? What is your gender?", 0.3),
    ]
    partitionable = True
    allow_modifiers = ["mod_add_period"]


class OnlyRobotAssume(SimpleGramChoice):
    choices = prepare_base_choices([
        f"Are you {ARobot} because you sound like {ARobot}?",
        f"Are you {ARobot}, because that didn't make any sense?",
        f"Are you {ARobot} because you are just repeating yourself?",
        f"Are you {ARobot} because you are repeating yourself?",
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
    allow_modifiers = ["mod_add_period"]


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


class AnAdjectivedPerson(SimpleGramChoice):
    choices = [
        #(f"a {Adjective} {HumanSingularGeneral}", Adjective.num_choices() / 2),
        f"a dog person",
        f"a cat person",
        f"a people person",
        f"an extraverted person",
        f"an animal person",
        f"an old dude",
        f"a {Nationality} person",
        f"a {Nationality} man",
        f"a {Nationality} girl",
        f"a {HumanSingularGeneral} who works here",
        f"a computer repair person for {CompanyName}",
        (f"a human {Professions}", Professions.num_choices() / 3),
    ]
    partitionable = False


class AdjectivedPersonAsk(SimpleGramChoice):
    choices = prepare_base_choices([
        "are you a cat person or a dog person?",
        (f"are you {AnAdjectivedPerson}?", AnAdjectivedPerson.num_choices()),
        (f"are you a {Adjective} person? i am, so i must let you know something...", 1/8000),
        (f"very much, are you a dog person? or cat person", 1 / 2000),
    ])


class AskNeedPunk(SimpleGramChoice):
    choices = [
        f"You are not {AHuman}?",
        f"I think you are {AHuman}?",
        f"I think you are {ARobot}?",
        f"You a robot?{MaybeAnOutro}",
        f"You a bot?{MaybeAnOutro}",
        f"You a human?{MaybeAnOutro}",
        f"You a girl?{MaybeAnOutro}",
        f"You a guy?{MaybeAnOutro}",
        f"I don't believe you are {ARobotOrHuman}?",
        f"You are definitely not {ARobotOrHuman}?",
        f"You are {ARobotOrHuman} {OutroBeforeQuestionMark}?",
    ]
    partitionable = False
    ignore_modifiers = [
        "mod_add_period",
        "mod_comma_space",
        "mod_period",
        "mod_question",
        "mod_a",
    ]


class DefaultRoot(SimpleGramChoice):
    choices = [
        (OnlyRobotAssume, OnlyHumanAssume.num_choices()),
        (OnlyHumanAssume, OnlyHumanAssume.num_choices()),
        (AssumeBoth, AssumeBoth.num_choices()),
        (AdjectivedPersonAsk, AdjectivedPersonAsk.num_choices() / 5 / EXTRA_NORMAL_SCALE),
        (AskNeedPunk, AskNeedPunk.num_choices() / 4),
    ]
    partitionable = False


def get_areyourobot_grammar(use_mods: bool = True):
    gram = Grammar(DefaultRoot)
    if use_mods:
        gram = apply_modifiers_to_grammar(gram, get_all_modifiers())
    return gram


def main():
    #train, test = partition_grammar(rules=get_default_grammar(), weights=(0.8, 0.2))
    print(sum(Lead.get_choices_weights()))
    for e in get_areyourobot_grammar().generate_rand_iter(n=100):
        print(e)
    #many_len = 500_000
    #many = set(tqdm(generate_rand_iter(n=1_000_000), total=many_len))
    #print(len(many))
    #explore_gram_capcity(get_areyourobot_grammar())



if __name__ == "__main__":
    main()
