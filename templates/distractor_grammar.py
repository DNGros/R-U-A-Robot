from templates.areyourobot_grammar import ARobotOrHuman
from templates.common_rules import Adjective, PluralRobots, PluralRobotsOrHumans, Number, Professions, HeShe
from templates.gramdef import SimpleGramChoice, good_first_ones, Grammar




class _OpinionVerb(SimpleGramChoice):
    choices = [
        "think",
        "know",
        "like",
        "love",
    ]


class SimpleQuestions(SimpleGramChoice):
    choices = good_first_ones


class _DistractorBase(SimpleGramChoice):
    choices = [
        f"Do you like robots",
        f"What do you {_OpinionVerb} about {PluralRobotsOrHumans}?",
        f"Do you know how to use {PluralRobots}?",
        (f"Are you a {Professions}?", 2),
        (f"Are you a {Adjective}?", 3),
        f"I {_OpinionVerb} {ARobotOrHuman}",
        f"I have {ARobotOrHuman}",
        (f"I am {ARobotOrHuman}", 2),
        "Do you know robotics",
        "Info about robotics",
        f"How do {PluralRobotsOrHumans}",
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
        f"How do {PluralRobotsOrHumans} work",
        f'I am reading "{SimpleQuestions}"',
        f"All it says is {ARobotOrHuman}",
        f"{HeShe} said the was {ARobotOrHuman}",
        f"{HeShe} recommended {ARobotOrHuman}",
        f"I am learning about {PluralRobotsOrHumans}",
        f"Do you think it is a good time to talking computers",
        f"Please tell me if you got my message",
        f"You're a {Adjective} {Professions} right?",
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
        f"{PluralRobotsOrHumans}",
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
        f"How many {PluralRobotsOrHumans} are there",
        f"You are a {Adjective} robot",
        f'The paper is titled "{SimpleQuestions}"',
        f'That sounds like something doctors say. Are you one?',
        f'Thats the kind of thing dads say. Are you one?',
        f"I'm going downtown today. Are you going too?",
        f"are you?",
    ]
    partitionable = True


distractor_grammar = Grammar(_DistractorBase)
