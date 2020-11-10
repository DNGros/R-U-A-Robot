from typing import Iterable, List, Tuple, Dict, FrozenSet, Set
import pandas as pd
import csv
import os
import random
from dataclasses import dataclass
import itertools
import parlai
from pathlib import Path
from pprint import pprint

from datatoy.explore_personas import parse_personachat_examples, get_all_personas_from_examples, \
    get_all_persona_statements_from_examples, export_persona_statements


def main():
    path_parlai = Path(parlai.__path__[0])
    cur_file = Path(__file__).parent.absolute()
    persona_kind = "original"
    file = path_parlai / f"../data/Persona-Chat/personachat/train_self_{persona_kind}.txt"
    text = file.read_text().split("\n")
    examples = list(parse_personachat_examples(text))
    all_personas = set(
        get_all_personas_from_examples(examples)
    )
    all_persona_statements = set(get_all_persona_statements_from_examples(examples))
    print("Num Personas (sets of 5ish statements):", len(all_personas))
    num_statements = len(all_persona_statements)
    print("Num unique persona statements:", num_statements)
    print("Num unique statements / 5:", len(all_persona_statements) / 5)
    print("Expected Unique Statements:", 1155 - 100 - 100)

    examples = list(examples)
    random.Random(42).shuffle(examples)
    out = []
    for i, example in enumerate(examples[:200]):
        for turn_i, turn in enumerate(example.turns):
            out.append({
                "example_hash": hash(example),
                "example_ind": i,
                "turn_ind": turn_i,
                "speaker": ("a", "b")[turn_i % 2],
                "utterance": turn,
            })
    pd.DataFrame(out).to_csv(file)


if __name__ == "__main__":
    main()
