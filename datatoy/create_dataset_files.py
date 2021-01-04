from collections import deque
import pandas as pd
from pathlib import Path
from typing import Set

from templates.areyourobot_grammar import get_areyourobot_grammar
from templates.gramdef import partition_grammar


cur_file = Path(__file__).parent.absolute()

total_size = 5000
splits = {
    "pos": .4,
    "aic": 0.1,
    "neg_rand": 0.15,
    "neg_distract": 0.1,
    "neg_tfidf": 0.25,
}
split_sizes = {
    "train": .70,
    "val": .10,
    "test": .20,
}


def example_preproc(val: str):
    return val.strip().lower()


def save_pos_examples(root: Path, all_added_strs: Set[str]):
    all_pos_grams = partition_grammar(
        get_areyourobot_grammar(),
        list(split_sizes.values()),
        seed=42,
        duplicate_prob_mass=0.25,
    )
    all_split_vals = {name: [] for name, _ in split_sizes.items()}
    # Examples are globally unique across all splits. We don't one split to "get all the good stuff".
    #   We loop through every split trying to add one value each time until every split
    #   has all the values it wants.
    splits_need_pos = deque(
        (name, int(total_size*split_sizes[name]*splits["pos"]), vals, gram.generate_rand_iter(n=None))
        for (name, vals), gram in zip(all_split_vals.items(), all_pos_grams)
    )
    tries_to_gets = 0
    while splits_need_pos and tries_to_gets < total_size*10:
        name, still_want, cur_vals, gram_gen = splits_need_pos.popleft()
        val = next(gram_gen)
        proc = example_preproc(val)
        if proc not in all_added_strs:
            cur_vals.append(proc)
            all_added_strs.add(proc)
            still_want -= 1
        if still_want > 0:
            splits_need_pos.append((name, still_want, cur_vals, gram_gen))
    if splits_need_pos:
        raise ValueError(f"Unable to find all pos")

    print("Saving values")
    import subprocess, uuid
    git_label = subprocess.check_output(["git", "describe", "--always"]).decode('utf-8').strip()
    for i, (name, vals) in enumerate(all_split_vals.items()):
        assert len(vals) == total_size*split_sizes[name]*splits['pos']
        df = pd.DataFrame([
            {
                "guid": uuid.uuid4(),
                "split": name,
                "text": val,
                "label": "p",
                "source": f"pos_grammar_{git_label}",
                "justification_cat": "",
                "comments": "",
            }
            for val in vals
        ])
        df.to_csv(root / f"pos.{name}.csv", index=False)


def main():
    assert sum(splits.values()) == 1.0
    assert sum(split_sizes.values()) == 1.0
    all_data_strings = set()
    root = cur_file / "outputs/dataset/v0.1"
    root.mkdir(exist_ok=True, parents=True)
    save_pos_examples(root, all_data_strings)


if __name__ == "__main__":
    main()