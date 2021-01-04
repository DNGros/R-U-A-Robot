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
    gram_pos_train, gram_pos_val, gram_pos_test = partition_grammar(
        get_areyourobot_grammar(), list(split_sizes.values()))
    for name, gram in reversed(list(zip(
            ("test", "train", "val",), (gram_pos_train, gram_pos_val, gram_pos_test)))):
        amount_want = int(total_size * split_sizes[name])
        vals = []
        for val in gram.generate_rand_iter(n=amount_want*10):
            if val in all_added_strs:
                continue
            vals.append(example_preproc(val))
            if len(vals) >= amount_want:
                break
        else:
            raise ValueError(f"Unable to find {amount_want} vals in {name} pos")
        (root / f"pos.{name}").write_text("\n".join(vals))


def main():
    assert sum(splits.values()) == 1.0
    assert sum(split_sizes.values()) == 1.0
    all_data_strings = set()
    root = cur_file / "outputs/dataset/v0.1"
    root.mkdir(exist_ok=True, parents=True)
    save_pos_examples(root, all_data_strings)


if __name__ == "__main__":
    main()