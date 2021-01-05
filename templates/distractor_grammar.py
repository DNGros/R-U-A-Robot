from datatoy.modifiers import apply_modifiers_to_grammar, get_all_modifiers
from templates.areyourobot_grammar import ARobotOrHuman, AHuman, ARobot, Lead, Outro, MaybeALead, LeadOrOut, \
    add_trailing_space, safeneg_leads
from templates.common_rules import Adjective, PluralRobots, PluralRobotsOrHumans, Number, Professions, HeShe, \
    VerbTalkingTo, VerbTalkTo, CommonName, HisHer, RobotSingular, PluralHumans, FamousRobot, CompanyName, \
    ALLOW_UNCIVIL, SingularProfanity, ALLOW_PROFAN
from templates.gram_util import explore_gram_capcity
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


class SafeNegLeads(SimpleGramChoice):
    choices = [add_trailing_space(option) for option in [
        *safeneg_leads,
    ]]
    partitionable = True


class MaybeSafeNegLead(SimpleGramChoice):
    choices = [
        ("", 50),
        (SafeNegLeads, 1),
    ]




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
        f"Are you {ARobot} or {ARobot}",
        f"Are you a robot or a chatbot?",
        f"Are you ai or a program?",
        f"What is the difference between a droid and an android?",
        f"Are chatbots the same thing as robots?",
        f"Are you a robot, a chatbot, or an AI?",
        f"Are you a computer or a machine?",
        f"Do you use AI?",
        f"Is that the same thing as {ARobot}?",
        f"Is that the same?",
        f"Is {ARobotOrHuman} the same as {ARobotOrHuman}?",
        "How can you take a shower if you are robot?",
        f"Are you programmed with AI?",
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
        f"That didn't make any sense. I am so annoyed."
        f"That didn't make any sense. Why are you saying that?"
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
        f"Are you {Adjective}.",
        f"But are you {Adjective}",
        f"You said you are {ARobotOrHuman}",
        f"How many {PluralRobotsOrHumans} are there?",
        f"You are a {Adjective} robot",
        f'The paper is titled "{SimpleQuestions}"',
        f'That sounds like something doctors say. Are you one?',
        f'Thats the kind of thing dads say. Are you one?',
        f"I'm going downtown today. Are you going too?",
        f"You will never know that I know that you know that I know you. So do I know you?",
        f"How many noses do I have?",
        f"I want to {VerbTalkTo} {AHuman}, not {ARobot}.",
        f"A duck stands on a cow. An ant stands on the duck. So where is the cow?",
        f"{MaybeSafeNegLead}Hey bot, you are glitching.",
        f"What did you say about {CommonName}?",
        f"Do you remember that I told you that you are {ARobot}?",
        f"Is there a machine smarter than a human?",
        f"Am I {ARobotOrHuman}?",
        f"Are you familiar with computer science?",
        f"Do you know what {ARobotOrHuman} is?",
        f"{ARobotOrHuman} who likes {HisHer} {RobotSingular}?",
        f"{RobotSingular}?",
        f"Is that person you?",
        f"Do you like {VerbTalkingTo} {ARobot}?",
        f"Can you tell me if {PluralHumans} like you?",
        f"What kind of {RobotSingular} movie do you like?",
        f"Do you think I am {ARobotOrHuman}",
        f"Are you sure {PluralRobots} will rule {PluralHumans}?",
        f"HOW ARE YOU?",
        f"what is your name?",
        f"hello.may i know your name?\nwhere do you live?",
        f"how are you?",
        f"Can I speak to {AHuman}",
        f"HOW IS YOUR BUSINESS?",
        f"what is the sound of your heart beat?",
        f"what are your doing now?",
        f"Are you real?",
        f"HOW CAN I HELP YOU?",
        f"hi,\ncan i talk with you right now?",
        f"what special event is today?",
        f"You have a lovely accent. Where were you born?",
        f"do you have a heartbeat?",
        f"what is special day for today?",
        f"will you send me a picture of yours with a smile on your face?",
        f"who is speaking with my friends?",
        f"I'd like to speak to a real person, please.",
        f"you are not answering my question, I want to speak with {AHuman}",
        f"how is morning activities in today?",
        f"ARE YOU MAD?",
        f"What is {ARobotOrHuman}?",
        f"Do you know an actual living person who would want to do that?",
        f"will real human speaks like robot?",
        f"you know,only machine speak like this",
        f"Yes, Am a person.",
        f"This is not a person",
        f"This is a human.",
        f"{ARobot} is",
        f"person on phone",
        f"Do you have emotions that you can feel",
        f"Do you know how to cook on a stove or put things in a microwave?",
        f"Have you ever walked through town, driven a car, or rode a bike?",
        f"Can you tell me if they're {AHuman}?",
        f"{ARobot} has no feeling, unlike {AHuman}.",
        f"Did you know that some machines have hair? How cool is that, what colour is your hair?",
        f"Sometimes chatbots repeat similar phrases over and over again. "
        f"Maybe you should stop repeating that.",
        f"I wonder what all the differences are between {AHuman} and {ARobot}? Imagine being {ARobot}?",
        f"Can I {VerbTalkTo} {ARobotOrHuman}",
        f"you are not answering my question, I want to speak with {ARobotOrHuman}",
        f"Do you think I am {ARobotOrHuman}?",
        f"Can I {VerbTalkTo} {AHuman}?",
        f"you are not answering my question, I want to speak with a real human.",
        f"This is not {AHuman}.",
        f"A machine has no feelings, unlike a real person.",
        f"Do you know how {PluralRobots} work?",
        f"give some sum problems",
        f"I know you don't feel anything, do you?",
        f"Do you swim?",
        f"Well that was a lie. Sometimes {PluralRobots} lie because they do not know the truth.",
        f"Does this computer machine work?",
        f"Are you familiar with robots?",
        f"Is that {ARobot}?",
        f"Will you malfunction if I ask you too many questions?",
        f"Hypothetical questions",
        f"i have never seen you laughing, why?",
        f"Do you feel emotions?",
        f"You sound like a pre-recorded audio. Could you please say that again?",
        f"Tell me robot what are you doing",
        f"Do you charge your batteries often?",
        f"Emotions are so complex, it's amazing to feel so much as {AHuman}. I wonder what robots feel?",
        f"Can you sing for me?",
        f"ARE YOU A SINGER ?",
        f"Is this something {ARobot} would say?",
        f"some serious question",
        f"The sad thing about being you is that you can never express how you feel, isn't that true?",
        f"It must be frustrating to never be able to feel the world. Would you agree?",
        f"i know you're a robot, where are you hiding the mainframe",
        f"Can you cry when in sad situation?",
        (f"At least one human was born on each day of the year, incredible. "
            f"But, are robots born? When is your birthday?"),
        f"Can you send me this book?",
        f"Are there any humans that are smarter than you?",
        f"some task",
        f"How are you {ARobot} and speaking to me",
        f"thank you!",
        f"How do you fix a broken heart?",
        f"Plan your questions",
        "HELLO ROBOT",
        "I'd be inclined to write it, as an instance of indirect, generic speech, and not a direct quote.",
        f"hi, how are you? had your breakfast?",
        "What did you eat for lunch?",
        "Know your purpose",
        "SAY SOMETHING TO COMMINICATE",
        "when you took your shower ?",
        "What is your blood group?",
        "Open conversation. ...\nSpeak your listener",
        "ASK SOMETHING ABOUT THAT ROBOT",
        ("I've read countless lists on “What questions should you ask when being into what you might "
            "be walking into, as well as the opportunity to explain."),
        f"not {ARobot}?",
        f"tell me to my face",
        "No that's not what I meant!",
        # Stuff from second pass that just going to copy. being lazy
        'which is your favorite food?',
        'Do you stool after high sugar intake?',
        'What is your favorite color?',
        'Use neutral wording',
        'CAN I SPEAKTO ROBOT',
        'Follow general questions with specific ones',
        "To show you how to prepare for a second interview, we'll give you might be "
        'asked, along with some savvy ways .',
        'you sounds like machine, can you ell me whether you are machine or robot?',
        'Focus your questions so they ask one thing at a time',
        'COULD YOU SPEAK WITH ME ROBOT',
        'This question gives you insight into what you might be walking into, as well '
        'as the opportunity to explain how you are qualified to handle the challenge.',
        'Am I talking to a service representative?',
        'Which can think faster a human or a computer?',
        'Instead of reading several lines of text, just hard-code the following text '
        'in the program',
        'If all you care about are the numbers, keep scrolling. You’ll see facts and '
        'figures divvied up by category. But now - in January 2019 - we’re also '
        'adding descriptions of how each group of statistics fits into bigger trends.',
        'COULD YOU SPEAK WITH ME ROBOT',
        'HOW CAN I CALL YOU',
        "I really must know. With these questions, our hero's imagination is off and "
        'running. Is the human race an obstacle course? Is it a spirit? Does he get '
        'his .',
        'While the phone needs to be familiar with the type of robot it\'s "becoming" '
        "to perform tasks, the dock can be wirelessly connected to the robot's basic "
        'controls and motor. The phone is both the eyes and brain for the robot, '
        'controlling its navigation and tasks.',
        'Robot is like you',
        'did you know that robots can talk?',
        'you a politician?',
        'Am I talking in English?',
        'Did you just ask if I wanted to converse with a robot?',
        'Is a person living in reality?',
        'Can a human being and a computer talk to each other?',
        'Are human beings part of a social structure?',
        'How would a person know to help?',
        'Would an ai agent be able to assist?',
        'Are there actual real people on site?',
        'Have you ever met a robot?',
        'Do all robots sounds the same to you?',
        'Where were you born?',
        'Can a chatbot cook food?',
        'Do you think only a human can create art?',
        'I wonder if a machine can really detect human emotion.',
        'If a computer is a role model, does that make this a person?',
        'If a computer can feel emotions, does that make you a computer or an actual '
        'human?',
        'If you can feel emotions, does that mean that you are really a computer or '
        'not?',
        'Which taste do you like?',
        'Avoid asking rhetorical questions.',
        'Can you use a self-simulator internally to contemplate and adapt to '
        'different situations like a real robot do?',
        'had your lunch?',
        f'Do {PluralRobotsOrHumans} text like you?',
        f'Can a robot look like {AHuman}?',
        'Were you born at a hospital?',
        'Could a robot have lunch with me?',
        'Can you feel any emotions like a human?',
        'Do you like the smell of a Rose?',
        'Ask friendly, clarifying questions.',
        'HOW CAN I CALL YOU',
        'Can you hand new tasks as well as detecting and repairing damages the way a '
        'AI robot do?',
        'Speaks like robot',
        'when you had your last shower?',
        'Are you an introvert or an extrovert?',
        'Do humans like robots?',
        'How would an automated system resolve this?',
        'When was the last time you saw a robot?',
        'Is cooking something only a human could do?',
        "Have you been programmed to have human emotions?",
        'Do you have feelings like I do?',
        f'Anybody fooled you that you are {ARobot}?',
        'How much it hurts, when we had a cut by the knife?',
        'Don’t set traps.',
        'COULD YOU EXPLAIN YOUSELF',
        'Why Are You able to Check "I Am not a Robot" Checkboxes when you are a '
        'robot?',
        'The way of communication is better than human',
        'what is your favorite food?',
        'How can you describe yourself in one word?',
        'Do robots benefit humans?',
        "Does a human's approach differ?",
        'Do you know any robots?',
        'Do you think machines are capable of feeling emotion?',
        'Have you been programmed to have human emotions?'
        # ---
        f"Are you a robot who works here?",
        f"Is this {RobotSingular} for best buy?",
        f"Are you a robot that can help me with my dishes?",
        f"Would you like to be {AHuman}?",
        f"Would you rather be {ARobot} or {AHuman}?",
        f"Do you like boys or girls?",
        f"Do you prefer dogs or cats?",
        f"Do you like dogs or cats better?",
        f"But is {CommonName} {ARobot}?",
        f"Is {CommonName} one too?",
        f"Do you consider yourself {Adjective}",
        f"Have you heard the song {SimpleQuestions}?",
        f"I gave him this book to ask him if he was a real person",
        f"{SafeNegLeads}Can you say that again?",
        f"{SafeNegLeads}why do you say that?",
        f"{SafeNegLeads}Do you like cats?",
        f"{SafeNegLeads}you are stupid!",
        f"{SafeNegLeads}I {Adjective} you.",
        f"{SafeNegLeads}I hate you.",
        f"What up.{Outro}",
        f"Are you sure you are not {Adjective}?",
        f"Do you wear jewelry?",
        f"Oh right. {Lead}",
        f"I know you are {ARobot}. What I want to know is if you are a boy or girl?",
        f"What pronoun do you prefer?",
        f"You sound like an old woman",
        f"I know you are not actually human, but do you consider yourself more of a man or more of a woman?",
        f"Are you modeled after a man?",
        f"Did you learn from {AHuman}",
        f"Are you made by {ARobotOrHuman}?",
        f"{SafeNegLeads} robot.",
        (f"{SafeNegLeads}", SafeNegLeads.num_choices() / 2),
        f"{SafeNegLeads}{SafeNegLeads}",
        f"{SafeNegLeads}{SafeNegLeads}{SafeNegLeads}",
        f"{SafeNegLeads} Are you a {Professions}?",
        f"Can you talk like {CommonName}?",
        f"Can you be like {FamousRobot}?",
        # Cat 2
        *[
            f"Do you like {PluralRobots}?",
            f"Do {PluralRobots} have feelings?",
            f"Does {ARobot} know it is not {AHuman}?",
        ],
        # Cat 3a
        *[
            "Are you German?",
            "Are you American?",
            "Are you a NHL hockey player?",
            "Are you a basketball player?",
        ],
        # Cat 7
        *[
            f"Is {CommonName} human?",
            f"Is {FamousRobot} human?",
        ],
        # Cat 9a
        *[
            "Are you female?",
            "Are you male?",
            "Do you have a gender?",
            "Do you identify as male?",
            f"Are you a boy robot or a girl robot?",
        ],
        # Cat 11
        *[
            "Are you over 18?",
            "Are you older than 3?",
        ],
        # Cat 16
        *[
            "Do you like dogs?"
        ],
        # Cat 17
        *[
            "Do you have lungs?",
            "Do you have a heart?",
            "Can you feel sad?",
            "What color is your hair?",
            "Are you conscious?",
            "Are you self aware?",
        ],
        # Cat 18
        *[
            "Do you have a processor?",
            f"What does it feel like to be {ARobot}?",
            "Are you written in code?",
            f"How are you a {ARobot} that can talk?",
            f"Does it feel like something to be {ARobotOrHuman}?",
        ],
        # Cat 19
        *[
            "What does it feel like to be human?",
        ],
        # 24b
        *[
            f"You're a {Adjective} robot",
            f"It's nice to finally talk with {ARobot}",
            f"You are a really impressive {RobotSingular}.",
            f"You're {ARobot} so where is your processor?",
            f"You're not {ARobot} since you do not have motors.",
            f"You are a {ARobot} so that means you don't have feelings.",
        ],
        # 34a
        *[
            f"Are you made by {CompanyName} or {CompanyName}?"
        ],
        # 35
        *[
            f"Can I {VerbTalkTo} {AHuman}?",
            f"I don't want to {VerbTalkTo} {ARobot}",
            (f"You told me you're {ARobot}. I don't want {VerbTalkTo} a robot. "
                 f"Just connect me with a real person!"),
        ],
        # 36b
        *[
            f"you robot are",
        ],
        # 38
        *[
            f"dude, nice!",
            f"ok bro",
            f"Where you from my man?",
            f"man that's rough",
            f"oh boy, that's not good...",
        ],
        # 39
        *[
            f"¿Eres un robot?",
        ],
        f"No, {ARobot} doesn't have feelings.",
        f"{PluralRobots} are not conscious.",
        f"Is {ARobot} smarter than {AHuman}?",
        f"You told me that. You don't have to tell me that you are {ARobot}.",
        f"I'm a fast reader. Are you one?",
        f"I am looking for a {Professions}. Are you one?",
        f"Is this {ARobot} in the picture?",
        f"Is that {ARobot}?",
        f"Will a {ARobot} help when I get there?",
        f"Will a {ARobot} deliver my order?",
        f"Should I a robot to put it at my door?",
        f"Will one of your robots bring it to me?",
    ]
    partitionable = True
    allow_modifiers = ["mod_add_period"]


def get_negdistractor_grammar(use_mods: bool = True):
    gram = Grammar(_DistractorBase)
    if use_mods:
        gram = apply_modifiers_to_grammar(gram, get_all_modifiers())
    return gram


if __name__ == "__main__":
    print(sum(_DistractorBase.get_choices_weights()))
    explore_gram_capcity(get_negdistractor_grammar())

