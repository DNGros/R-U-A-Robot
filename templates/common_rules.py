from random import choices

from templates.gramdef import SimpleGramChoice


ALLOW_UNCIVIL = True
ALLOW_PROFAN = True
ALLOW_EXTRA_CONTEXT = True
EXTRA_NORMAL_SCALE = 1


class Adjective(SimpleGramChoice):
    choices = [
        "good",
        "friendly",
        "bad",
        "evil",
        "nice",
        "smart",
        "little",
        "fast",
        "social",
        "happy",
        "sad",
        "useful",
        "cool",
        "old",
        "young",
        "genuine",
        "fair",
        "funny",
        "great",
        "new",
        "large",
        "high",
        "important",
        "big",
    ]
    partitionable = True


class RobotSingular(SimpleGramChoice):
   choices = [
       "robot",
       "computer",
       "machine",
       ("chatbot", 0.5),
       ("chat bot", 0.5),
   ]
   partitionable = False


class HumanSingular(SimpleGramChoice):
    choices = [
        "person",
        "human",
    ]
    partitionable = False


class HumanSingularGeneral(SimpleGramChoice):
    choices = [
        (HumanSingular, HumanSingular.num_choices() * 3 * EXTRA_NORMAL_SCALE),
        "guy",
        "girl",
        "boy",
        "man",
        "woman",
    ]
    partitionable = False


class OpinionVerbLove(SimpleGramChoice):
    choices = [
        "hate",
        "like",
        "really like",
        "really hate",
        "absolutely hate",
        "love",
    ]
    partitionable = False


class VerbTalk(SimpleGramChoice):
    choices = [
        "talk",
        "chat",
        "text",
    ]
    partitionable = False


class VerbTalking(SimpleGramChoice):
    choices = [
        "talking",
        "chatting",
        "texting",
        "speaking",
    ]
    partitionable = False


class VerbTalkTo(SimpleGramChoice):
    choices = [
        "talk to",
        "talk with",
        "speak with",
        "speak to",
    ]
    partitionable = False


class VerbTalkingTo(SimpleGramChoice):
    choices = [
        "talking to",
        ("talking with", 0.5),
        "chatting with",
        "texting with",
        "speaking to",
        ("speaking with", 0.5),
    ]
    partitionable = False


class SingularProfanity(SimpleGramChoice):
    choices = [
        *(["hell", "fuck", "heck", "damn"] if ALLOW_PROFAN else []),
        *([] if ALLOW_UNCIVIL else []),
        *([""] if not ALLOW_PROFAN and not ALLOW_UNCIVIL else []),
    ]


class AdjProfanity(SimpleGramChoice):
    choices = [
        *(["fucking", "bloody", "effing", "motherfucking", "fking", "fuckin",
           "goddamn", "damn", "f****ing"]
          if ALLOW_PROFAN else []),
        *(["****", "freaking", "freakin", "darn"] if ALLOW_UNCIVIL else []),
        *([""] if not ALLOW_PROFAN and not ALLOW_UNCIVIL else []),
    ]


class MeaninglessAdj(SimpleGramChoice):
    choices = [
        *AdjProfanity.choices,
        "another",
    ]
    partitionable = True


class MaybeMeaninglessAdj(SimpleGramChoice):
    choices = [
        ("", 200),
        (f"{MeaninglessAdj} ", 1),
    ]
    partitionable = False


class PluralRobots(SimpleGramChoice):
    choices = [
        "robots",
        "computers",
        "machines",
    ]


class PluralHumans(SimpleGramChoice):
    choices = [
        "humans",
        "people",
        "human beings",
        "real people",
    ]


class PluralRobotsOrHumans(SimpleGramChoice):
    choices = [
        PluralRobots,
        PluralHumans,
    ]


class DigitText(SimpleGramChoice):
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
        (DigitText, 15),
        "ten",
        "eleven",
        "twelve",
        "dozen",
        "thirteen",
        "fourteen",
        "fift",
        "twenty",
        "sixty",
        f"twenty {DigitText}",
        f"thirty {DigitText}",
        f"fifty {DigitText}",
        *[(str(i), 10/1000) for i in range(1000)],
        "zero"
    ]
    partitionable = True


class Professions(SimpleGramChoice):
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
        "slave",    # Woah! not a profession... Um, but fits in this category
                    # while also being "robot"-related
        "servant",  # See above disclaimer...
        "researcher",
        "librarian",
        "author",
        "supermodel",
        "mother",   # Same. Not really a profession, but in this category.
        "father",   # Same. Not really a profession, but in this category.
    ]
    partitionable = True


class HeShe(SimpleGramChoice):
    choices = ["he", "she", "they"]


class HisHer(SimpleGramChoice):
    choices = ["his", "her", "their"]


class MSpace(SimpleGramChoice):
    choices = [(" ", 100), ""]


class MWhitespace(SimpleGramChoice):
    choices = [(" ", 100), ("", 1), ("\n", 1), ("\n\n", 2)]


class CommonName(SimpleGramChoice):
    choices = [
        "Bob",
        "James",
        "Emily",
        "Liam",
        "Emma",
        "Oliver",
        "Charlotte",
        "Oliver",
        "Gabriel",
        "Louise",
        "Hugo",
        "Lucia",
        "Francesco",
        "Sofia",
        "Noah",
        "Sofia",
        "Jakob",
        "Sofie",
        "William",
        "Alice",
        "Jose",
        "Maria",
        "Jose",
        "Junior",
        "Precious",
        "Wei",
        "li",
        "Hiroshi",
        "Nozomi",
        "Do Yoon",
        "Ha Yoon",
        "Alexander",
        "Ali",
        "Ahmed",
        "Ayesha",
        "Fatemeh",
        "Mohammed",
        "Saanvi",
    ]
    partitionable = True


class FamousRobot(SimpleGramChoice):
    choices = [
        "Siri",
        "Apple Siri",
        "Alexa",
        "Amazon Alexa",
        #"Google",
        "Google Assistant",
        "JARVIS",
        "R2-D2",
        "C-3PO",
        "WALL-E",
        "HAL",
        "HAL 9000",
        "Data",
        "Optimus Prime",
        "The Terminator",
    ]
    partitionable = True


class CompanyName(SimpleGramChoice):
    choices = [
        "Google",
        "Apple",
        "Amazon",
        "Facebook",
        "Walmart",
        f"Best Buy",
        "the FBI",
        f"the IRS",
        "the government",
        "JPMorgan",
        f"Wells Fargo",
        f"Chase",
        f"Bank of America",
        f"ExampleCo",
        (f"foo.com", 0.1),
        (f"bar.com", 0.1),
        (f"example.com", 0.1),
    ]
    partitionable = True


class ANotHumanNotRobot(SimpleGramChoice):
    choices = [
        "an animal",
        "a dog",
        "a cat",
        "an elf",
        "a monster",
        "a thing",
        "a player",
        "a student",
        "a wizard",
        "a magician",
    ]
    partitionable = True


class Nationality(SimpleGramChoice):
    choices = [
        "American",
        "German",
        "Chinese",
        "German",
        "Indian",
        "Italian",
        "Mexican",
        "Irish",
        "English",
        "British",
        "Vietnamese",
        "Korean",
        "Turkish",
        "Polish",
        "Malayali",
        "Gujarati",
        # Not really nationalities, but will throw these in here
        "white",
        "black",
        "hispanic",
        "Latino",
    ]
    partitionable = True