from typing import Iterable

import parlai
from pathlib import Path


def is_your_persona_line(line: str) -> bool:
    if "persona" not in line:
        return False
    return any(
        line.startswith(f"{i} your persona: ")
        for i in range(1, 11)
    )


def get_persona_from_line(line: str) -> str:
    if is_your_persona_line(line):
        return ":".join(line.split(":")[1:]).strip()
    raise ValueError()


def get_all_personas(lines: Iterable[str]):
    yield from (
        get_persona_from_line(line)
        for line in lines
        if is_your_persona_line(line)
    )


def main():
    path_parlai = Path(parlai.__path__[0])
    file = path_parlai / "../data/Persona-Chat/personachat/train_self_original.txt"
    text = file.read_text().split("\n")
    personas = set(get_all_personas(text))
    print(len(personas))
    # Sec 3 of paper says there should be 1155 personas.
    # Each persona has 5 components. However 100 personas are set asside for each of val and test
    expected = (1155 - 100 - 100) * 5
    print(expected)
    assert len(personas) == expected


if __name__ == "__main__":
    main()
