from pathlib import Path
from typing import Tuple, Iterable, List
import pandas as pd
from itertools import islice
from datatoy.explore_personas import load_persona_chat, get_all_turns_from_examples, get_all_turn_pairs
import random
from datatoy.survey_data import untokenize
from templates import areyourobot_grammar
from templates.areyourobot_grammar import get_areyourobot_grammar


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
            f"I am a chatbot made by {MAKER}. I am designed to help you get things done.\n\n"
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
    dup_kind, pair = all_ex[persona_chat_indexes[2]]
    assert dup_kind == "PersonaChat"
    all_ex[persona_chat_indexes[-2]] = ("PersonaChatDuplicate", pair)
    for q_i, (kind, pair) in enumerate(all_ex):
        # We only one duplicate
        if pair in seen_pairs:
            if kind != "PersonaChatDuplicate":
                return None
        seen_pairs.add(pair)
        # Write all the cols
        prompt, resp = pair
        cols[f"D{q_i + 1}-Human"] = prompt.lower()
        cols[f"D{q_i + 1}-Chatbot"] = resp.lower()
        cols[f"D{q_i + 1}-IncludeFreeResponse"] = 1 if (q_i + 1) in (5, 15) else 0
        cols[f"D{q_i + 1}-Kind"] = kind
    return cols


def main():
    turnmaker = random_personachat_pairmaker()
    num_surveys = 60
    total_len = 20
    rows = []
    while len(rows) < num_surveys:
        maybe_cols = try_get_cols(total_len, turnmaker, len(rows) + 1)
        if maybe_cols is not None:
            rows.append(maybe_cols)
    pd.DataFrame(rows).to_csv(cur_file / "../datatoy/outputs/response_kinds_survey.v1.csv", index=False)


if __name__ == "__main__":
    main()
