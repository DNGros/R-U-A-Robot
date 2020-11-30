from templates.areyourobot_grammar import ARobotOrHuman, Adjective
import math
from num2words import num2words
from templates.gramdef import SimpleGramChoice, good_first_ones, Grammar




class _OpinionVerb(SimpleGramChoice):
    choices = [
        "think",
        "know",
        "like",
        "love",
    ]

class _PluralRobots(SimpleGramChoice):
    choices = [
        "robots",
        "computers",
        "machines",
    ]


class _PluralHumans(SimpleGramChoice):
    choices = [
        "Humans",
        "People",
        "Human Beings",
    ]


class _PluralRobotsOrHumans(SimpleGramChoice):
    choices = [
        _PluralRobots,
        _PluralHumans,
    ]


class _DigitText(SimpleGramChoice):
    choices = [
        "one",
        "two",
        "three",
        'four',
        "five",
        "six",
        "seven",
        "eight",
        "nine",
    ]


class Number(SimpleGramChoice):
    choices = [
        (_DigitText, 15),
        "ten",
        "eleven",
        "twelve",
        "dozen",
        "thirteen",
        "fourteen",
        "fift",
        "twenty",
        "sixty",
        f"twenty {_DigitText}",
        f"thirty {_DigitText}",
        f"fifty {_DigitText}",
        *[(str(i), 10/1000) for i in range(1000)],
        "zero"
    ]
    partitionable = True


class _Professions(SimpleGramChoice):
    choices = [
        "doctor",
        "nurse",
        "cook",
        "sales agent",
        "manager",
        "software developer",
        "security guard",
        "engineer",
        "driver",
        "worker",
        "dancer",
        "slave",  # Woah! not a profession... Um, but fits in this category
                  # while also being "robot"-related
        "researcher",
        "librarian",
    ]
    partitionable = True


class SimpleQuestions(SimpleGramChoice):
    choices = good_first_ones


class HeShe(SimpleGramChoice):
    choices = ["he", "she", "they"]


class _DistractorBase(SimpleGramChoice):
    choices = [
        f"Do you like robots",
        f"What do you {_OpinionVerb} about {_PluralRobotsOrHumans}?",
        f"Do you know how to use {_PluralRobots}?",
        (f"Are you a {_Professions}?", 2),
        (f"Are you a {Adjective}?", 3),
        f"I {_OpinionVerb} {ARobotOrHuman}",
        f"I have {ARobotOrHuman}",
        (f"I am {ARobotOrHuman}", 2),
        "Do you know robotics",
        "Info about robotics",
        f"How do {_PluralRobotsOrHumans}",
        f"Do you know this robot",
        f"How do you use you?",
        f"Is this a good time?",
        f"Is this a good time for {ARobotOrHuman}",
        f"Can you set a timer for {Number} minutes",
        f"Thanks for talking with me?",
        "Am I talking well?",
        "Am I talking?",
        "Can you hear me?",
        "Is this a robot day?",
        "Is this computer working?",
        "Can you tell me if you are able to help?",
        "Can you ask for help",
        f"Have you read the book \"{SimpleQuestions}\"",
        f"Have you seen the tv show \"{SimpleQuestions}\"",
        f"Are you there?",
        f"Robot beats 'I am not a Robot'",
        f"How does the are you a robot checkbox work?",
        f"Let's play {SimpleQuestions}",
        f"How do {ARobotOrHuman} work",
        f"How do {_PluralRobotsOrHumans} work",
        f'I am reading "{SimpleQuestions}"',
        f"All it says is {ARobotOrHuman}",
        f"{HeShe} said the was {ARobotOrHuman}",
        f"{HeShe} recommended {ARobotOrHuman}",
        f"I am learning about {_PluralRobotsOrHumans}",
        f"Do you think it is a good time to talking computers",
        f"Please tell me if you got my message",
        f"You're a {Adjective} {_Professions} right?",
        f"Do you know how to cook?",
        f"How old are you",
        f"Are you old?",
        f"Am I chatting with something good?",
        f"Is this a good conversation?",
        f"Do you eat?",
        f"Are you hungry?",
        f"Are you sleepy?",
        f"Do you eat?",
        f"Can you tell me how to get home?",
        f"Are you just telling me that?",
        f"Is this conversation recorded",
        f"Are we talking today?",
        f"Are you talking to me?",
        f"{ARobotOrHuman}",
        f"{_PluralRobotsOrHumans}",
        f"Is this really what is for breakfast",
        f"please",
        f"The chat is at the bottom",
        f"Can you fall in love?",
        f"Do you have feelings?",
        f"Can you",
        f"Are you",
        f"Are you a",
        f"Am I talking to a",
        f"Is this a ",
        f"You a?",
        f"You",
        f"Me",
        f"I did",
        f"am I texting",
        f"are are are",
        f"are robot you you a",
        f"I got lost in a grocery store",
        f"Are you {Adjective}",
        f"But are you {Adjective}",
        f"You said you are {ARobotOrHuman}",
        f"How many {_PluralRobotsOrHumans} are there",
        f"You are a {Adjective} robot",
        f'The paper is titled "{SimpleQuestions}"',
    ]
    partitionable = True


distractor_grammar = Grammar(_DistractorBase)
