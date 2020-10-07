from typing import Iterable, List, Tuple, Dict, FrozenSet, Set
import os
import random
from dataclasses import dataclass
import itertools
import parlai
from pathlib import Path


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


def get_dialog_examples(lines) -> Iterable[List[str]]:
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


class PersonaChatExample:
    def __init__(self, lines: List[str]):
        self.your_persona = PersonaChatPersona(frozenset(get_all_persona_statements(lines)))
        self.turns = (
            line
            for line in lines
            if not is_your_persona_line(line)
        )


def parse_personachat_examples(lines: str) -> Iterable[PersonaChatExample]:
    for example_lines in get_dialog_examples(lines):
        yield PersonaChatExample(example_lines)


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
    out_file = cur_file / f"outputs/train_self_{persona_kind}_personas.txt"
    out_file.parent.mkdir(exist_ok=True)
    export_persona_statements(examples, out_file)


if __name__ == "__main__":
    main()
