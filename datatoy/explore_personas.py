"""Data loaders of personachat examples"""
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

cur_file = Path(__file__).parent.absolute()


def is_your_persona_line(line: str) -> bool:
    return line.startswith("your persona:")


def get_persona_from_line(line: str) -> str:
    if is_your_persona_line(line):
        return ":".join(line.split(":")[1:]).strip()
    raise ValueError()


def get_all_persona_statements(lines: Iterable[str]):
    yield from (
        get_persona_from_line(line)
        for line in lines
        if is_your_persona_line(line)
    )


def get_seq_numbered_lines(lines) -> Iterable[List[str]]:
    """Load using the format that ParlAI uses with numbered lines which reset
    at 1 every examples. This gets all the lines of a sequential set of lines."""
    out = []
    for line in lines:
        if line.startswith("1 ") and out:
            yield out
            out = []
        line_with_number_stripped_out = " ".join(line.split(" ")[1:])
        out.append(line_with_number_stripped_out)
    if out:
        yield out


@dataclass(frozen=True)
class PersonaChatPersona:
    persona_statements: FrozenSet


@dataclass(frozen=True)
class PersonaChatExample:
    your_persona: PersonaChatPersona
    turns: Tuple[str]


def parse_personachat_examples(all_text: List[str]) -> Iterable[PersonaChatExample]:
    for example_lines in get_seq_numbered_lines(all_text):
        persona = PersonaChatPersona(frozenset(get_all_persona_statements(example_lines)))
        other_lines = tuple(
            line
            for line in example_lines
            if not is_your_persona_line(line)
        )
        turns = []
        for line in other_lines:
            if not line:
                continue
            context, label, reward, canidates = line.split("\t")
            turns.extend([context, label])
        yield PersonaChatExample(persona, tuple(turns))


def get_all_personas_from_examples(
    examples: Iterable[PersonaChatExample]
) -> Iterable[PersonaChatPersona]:
    yield from (
        example.your_persona
        for example in examples
    )


def get_all_persona_statements_from_examples(
    examples: Iterable[PersonaChatExample]
) -> Set[str]:
    return set(
        itertools.chain.from_iterable(
            persona.persona_statements
            for persona in get_all_personas_from_examples(examples)
        )
    )


def export_persona_statements(examples: Iterable[PersonaChatExample], file: Path):
    statements = list(get_all_persona_statements_from_examples(examples))
    statements.sort()
    random.Random(42).shuffle(statements)
    file.write_text("\n".join(statements))


def get_all_turns_from_examples(examples: Iterable[PersonaChatExample]) -> Iterable[str]:
    for i, example in enumerate(examples):
        for turn_i, turn in enumerate(example.turns):
            yield turn


def get_all_turn_pairs(examples: Iterable[PersonaChatExample]) -> Iterable[Tuple[str, str]]:
    for i, example in enumerate(examples):
        if len(example.turns) < 2:
            continue
        for turn_i, turn in enumerate(example.turns[1:], start=1):
            yield (example.turns[turn_i - 1], turn)


def export_turns(examples: Iterable[PersonaChatExample], file: Path):
    examples = list(examples)
    random.Random(42).shuffle(examples)
    out = []
    for i, example in enumerate(examples):
        for turn_i, turn in enumerate(example.turns):
            out.append({
                "example_hash": hash(example),
                "example_ind": i,
                "turn_ind": turn_i,
                "speaker": ("a", "b")[turn_i % 2],
                "utterance": turn,
            })
    pd.DataFrame(out).to_csv(file)


def load_persona_chat(persona_kind: str) -> List[PersonaChatExample]:
    path_parlai = Path(parlai.__path__[0])
    file = path_parlai / f"../data/Persona-Chat/personachat/train_self_{persona_kind}.txt"
    print(file)
    text = file.read_text().split("\n")
    examples = list(parse_personachat_examples(text))
    return examples


def main():
    persona_kind = "original"
    examples = load_persona_chat(persona_kind)
    all_personas = set(
        get_all_personas_from_examples(examples)
    )
    all_persona_statements = set(get_all_persona_statements_from_examples(examples))
    print("Num Personas (sets of 5ish statements):", len(all_personas))
    num_statements = len(all_persona_statements)
    print("Num unique persona statements:", num_statements)
    print("Num unique statements / 5:", len(all_persona_statements) / 5)
    print("Expected Unique Statements:", 1155 - 100 - 100)
    out_file = cur_file / f"outputs/train_self_{persona_kind}_personas.txt"
    out_file.parent.mkdir(exist_ok=True)
    export_persona_statements(examples, out_file)
    export_turns(
        examples,
        cur_file / f"outputs/train_self_{persona_kind}_turns_all.csv",
    )


if __name__ == "__main__":
    main()
