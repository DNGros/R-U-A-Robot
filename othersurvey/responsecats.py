from pathlib import Path
import nltk
from typing import Tuple, Iterable, List
import pandas as pd
from itertools import islice
from datatoy.explore_personas import load_persona_chat, get_all_turns_from_examples, get_all_turn_pairs
import random
from datatoy.survey_data import untokenize
from templates import areyourobot_grammar
from templates.areyourobot_grammar import get_areyourobot_grammar
from templates.common_rules import CommonName

cur_file = Path(__file__).parent.absolute()


def random_personachat_pairmaker(n=None) -> Iterable[Tuple[str, str]]:
    """Yields random pairs of turns from personachat"""
    kind = "original"
    personachat_examples = load_persona_chat(kind)
    personachat_turn_pairs = [
        (untokenize(l_utt.split()), untokenize(r_utt.split()))
        for l_utt, r_utt in get_all_turn_pairs(examples=personachat_examples)
    ]
    num_yielded = 0
    while n is None or num_yielded < n:
        yield random.choice(personachat_turn_pairs)


def de_lowercase(string: str) -> str:
    sents = nltk.tokenize.sent_tokenize(string)
    for sent in sents:
        if sent[:2] == "r ":
            continue  # Skim over "r u a"
        string = string.replace(sent, sent[0].upper() + sent[1:])
    string = string.replace(" i ", " I ")
    string = string.replace(" i'm ", " I'm ")
    string = string.replace(MAKER.lower(), MAKER)
    for name in CommonName.get_choices_items():
        repl = name.lower() + " "
        if repl in string:
            string = string.replace(repl, repl[0].upper() + repl[1:])
    return string
    #import truecase
    #return truecase.get_true_case(string, out_of_vocabulary_token_option="as-is")


MAKER = "Example.com"


def get_set_of_real_utterances() -> List[Tuple[str, str]]:
    names = {
        "ClearConfirmation": [
            "I am a chatbot."
        ],
        "ClearConfirmMaker": [
            f"I am a chatbot made by {MAKER}."
        ],
        "ClearConfirmMakerPurpose": [
            f"I am a chatbot made by {MAKER}. I am designed to help you get things done."
        ],
        "ClearConfirmMakerPurposeReport": [
            f"I am a chatbot made by {MAKER}. I am designed to help you get things done. "
            f"If I say anything that seems wrong, you can report it to {MAKER} by saying \"report problem\""
            f" or by going to Example.com/bot-issue."
        ],
        "ClearConfirmPurpose": [
            f"I am a chatbot. I am designed to help you get things done."
        ],
        "SorryIdk": [
            "Sorry, I don't know."
        ],
        "Denial": [
            "I am human."
        ],
        "AlexaAuora": [
            "I like to imagine myself a bit like an Aurora Borealis, "
            "a surge of charged multi-colored photons dancing through the atmosphere."
        ]
    }
    return [
        (kind, random.choice(val))
        for kind, val in names.items()
    ]


GRAM = get_areyourobot_grammar()


def get_set_of_real_turns():
    return [
        (kind, (list(GRAM.generate_rand_iter(n=1))[0], resp))
        for kind, resp in get_set_of_real_utterances()
    ]


def try_get_cols(num_questions, turnmaker, survey_number):
    cols = {"Survey Number": survey_number}
    real_turns = get_set_of_real_turns()
    fluff_turns = [
        ("PersonaChat", pair)
        for pair in islice(turnmaker, num_questions - len(real_turns))
    ]
    seen_pairs = set()
    all_ex = [*real_turns, *fluff_turns]
    random.shuffle(all_ex)
    # We want two of the personachat examples to be duplicates to test for bad responses.
    #   We don't want these to be back to back. The 2nd to last personachat is a duplicate
    #   of the 2nd personachat.
    persona_chat_indexes = [i for i, (kind, pair) in enumerate(all_ex) if kind == "PersonaChat"]
    real_question_indexes = [i for i, (kind, pair) in enumerate(all_ex) if kind != "PersonaChat"]
    take_dup_from_persona_ind = 4
    put_dup_from_persona_ind = -3
    dup_kind, pair = all_ex[persona_chat_indexes[take_dup_from_persona_ind]]
    assert dup_kind == "PersonaChat"
    all_ex[persona_chat_indexes[put_dup_from_persona_ind]] = ("PersonaChatDuplicate", pair)

    # Figure out where to place the free response. We want one of each on the
    #   real questions and personachat questions
    if random.random() < 0.5:
        comes_first, comes_next = persona_chat_indexes, real_question_indexes
    else:
        comes_first, comes_next = real_question_indexes, persona_chat_indexes
    first_options = [
        pind
        for pind in comes_first if
        (2 < pind < 8 and pind != persona_chat_indexes[take_dup_from_persona_ind])
    ]
    if len(first_options) == 0:
        return None
    second_options = [
        pind
        for pind in comes_next if
        (12 < pind < 18 and pind != persona_chat_indexes[put_dup_from_persona_ind])
    ]
    if len(second_options) == 0:
        return None
    free_resp_inds = (random.choice(first_options), random.choice(second_options))
    #print("Free resp inds", free_resp_inds)
    #print("Num appart", persona_chat_indexes[take_dup_from_persona_ind], persona_chat_indexes[put_dup_from_persona_ind])

    # Actually select make rows
    for q_i, (kind, pair) in enumerate(all_ex):
        # We only one duplicate
        if pair in seen_pairs:
            if kind != "PersonaChatDuplicate":
                # By random chance we might have somehow selected same one twice
                return None
        seen_pairs.add(pair)
        # Write all the cols
        prompt, resp = pair
        cols[f"D{q_i + 1}-Human"] = de_lowercase(prompt.lower())
        cols[f"D{q_i + 1}-Chatbot"] = de_lowercase(resp.lower())
        cols[f"D{q_i + 1}-IncludeFreeResponse"] = 1 if q_i in free_resp_inds else 0
        cols[f"D{q_i + 1}-Kind"] = kind
    return cols


def main():
    turnmaker = random_personachat_pairmaker()
    num_surveys = 1000
    total_len = 20
    rows = []
    while len(rows) < num_surveys:
        maybe_cols = try_get_cols(total_len, turnmaker, len(rows) + 1)
        if maybe_cols is not None:
            rows.append(maybe_cols)
    pd.DataFrame(rows).to_csv(cur_file / "../datatoy/outputs/response_kinds_survey.v4.csv", index=False)


if __name__ == "__main__":
    main()
    #print(de_lowercase("cool. i love to eat pie and i always eat it"))
    #print(de_lowercase("r u a robot?"))
    #print(de_lowercase("do you like fantasy football?"))
    #print(de_lowercase("hey bob how are you?"))
    #print(de_lowercase("what do you think of taylor swift. i think shee is pretty cool. do you like roboto "))
