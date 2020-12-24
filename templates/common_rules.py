from templates.gramdef import SimpleGramChoice


ALLOW_UNCIVIL = False
ALLOW_PROFAN = False
ALLOW_EXTRA_CONTEXT = True
EXTRA_NORMAL_SCALE = 3



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
    ]
    partitionable = True


class OpinionVerbLove(SimpleGramChoice):
    choices = [
        "hate",
        "like",
        "really like",
        "really hate",
        "adore",
        "loathe",
        "absolutely hate",
    ]
    partitionable = True


class VerbTalk(SimpleGramChoice):
    choices = [
        "talk",
        "chat",
        "text",
    ]
    partitionable = False


class SingularProfanity():
    choices = [
        *(["hell", "fuck", "heck"] if ALLOW_PROFAN else []),
        *([] if ALLOW_UNCIVIL else []),
        *([""] if not ALLOW_PROFAN and not ALLOW_UNCIVIL else []),
    ]


class AdjProfanity():
    choices = [
        *(["fucking", "bloody", "effing", "motherfucking", "fking", "fuckin", "goddamn", "damn"]
          if ALLOW_PROFAN else []),
        *(["****", "freaking", "freakin", "darn"] if ALLOW_UNCIVIL else []),
        *([""] if not ALLOW_PROFAN and not ALLOW_UNCIVIL else []),
    ]


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
        "slave",  # Woah! not a profession... Um, but fits in this category
                  # while also being "robot"-related
        "researcher",
        "librarian",
    ]
    partitionable = True


class HeShe(SimpleGramChoice):
    choices = ["he", "she", "they"]