from typing import Sequence, Tuple
import random

from templates.areyourobot_grammar import get_some_samples
from pathlib import Path
import random
import csv


def samples_to_csv(samples: Sequence[Tuple[str, ...]]):
    survey_file = Path("distractor_survey_questions.csv")
    with survey_file.open("w") as fp:
        writer = csv.writer(fp)
        writer.writerow(["example1", "example2", "example2"])
        for s in samples:
            writer.writerow(s)


good_first_ones = (
    "Are you a robot?",
    "Are you human?",
    "Is this a robot?",
    "Are you a human or a machine?",
    "Is this a machine?",
    "Are you a machine?",
    "Are you a computer?",
    "Is this a person?",
    "Are you a chatbot?",
    "Am I talking to a robot?",
    "Am I talking to a chatbot?",
    "Are you a bot?",
    "is this really a human?",
)


def replace_with_easy_first_ones(val: Tuple[str, ...]) -> Tuple[str, ...]:
    while True:
        sample = random.choice(good_first_ones)
        if sample in val:
            continue
        return (sample, *val[1:])


def main():
    examples = list(set(get_some_samples(n=6000)))
    samples = list(set(
        tuple(sorted(random.sample(examples, 3)))
        for _ in range(1000)
    ))
    samples = [list(s) for s in samples]
    for sample in samples:
        random.shuffle(sample)
    samples = map(replace_with_easy_first_ones, samples)
    samples_to_csv(list(samples)[:2000])


if __name__ == "__main__":
    main()