from typing import Sequence, Tuple

from templates.areyourobot_grammar import get_some_samples
from pathlib import Path
import random
import csv

from templates.gramdef import good_first_ones


def samples_to_csv(samples: Sequence[Tuple[str, ...]]):
    survey_file = Path("distractor_survey_questions.csv")
    with survey_file.open("w") as fp:
        writer = csv.writer(fp)
        writer.writerow(["example1", "example2", "example2"])
        for s in samples:
            writer.writerow(s)


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