from collections import deque
import attr
import uuid
from typing import Sequence, Iterable
import pandas as pd
from pathlib import Path
from typing import Set

from datatoy.grammar_classifier import AreYouRobotClass
from templates.areyourobot_grammar import get_areyourobot_grammar
from templates.distractor_grammar import get_negdistractor_grammar
from templates.gramdef import partition_grammar, Grammar
cur_file = Path(__file__).parent.absolute()

ROOT = cur_file / "outputs/dataset/v0.1"
TOTAL_SIZE = 5000
DUPLICATE_PROB_MASS = 0.25
SPLITS = {
    "pos": .4,
    "aic": 0.1,
    "neg_rand": 0.15,
    "neg_distract": 0.1,
    "neg_tfidf": 0.25,
}
SPLIT_SIZES = {
    "train": .70,
    "val": .10,
    "test": .20,
}


def example_preproc(val: str):
    return val.strip().lower()


@attr.s(auto_attribs=True)
class AreYouRobotDatasetExample():
    split: str
    text: str
    label: AreYouRobotClass
    source: str
    justification_cat: str = ""
    comments: str = ""
    guid: str = attr.ib(factory=lambda: uuid.uuid4())

    def as_dict(self):
        return {
            "guid": self.guid,
            "split": self.split,
            "text": self.text,
            "label": self.label.value,
            "source": self.source,
            "justification_cat": self.justification_cat,
            "comments": self.comments,
        }


def get_examples_from_grammars(
        grams: Sequence[Grammar],
    desired_amounts: Sequence[int],
    all_added_strs: Set[str]
):
    assert len(grams) == len(desired_amounts)
    # Examples are globally unique across all splits. We don't one split to "get all the good stuff".
    #   We loop through every split trying to add one value each time until every split
    #   has all the values it wants.
    all_vals = [[] for _ in grams]
    splits_still_need = deque(
        (still_want, vals, gram.generate_rand_iter(n=None))
        for still_want, gram, vals in zip(desired_amounts, grams, all_vals)
    )
    tries_to_gets = 0
    while splits_still_need and tries_to_gets < sum(desired_amounts)*10:
        still_want, cur_vals, gram_gen = splits_still_need.popleft()
        val = next(gram_gen)
        proc = example_preproc(val)
        if proc not in all_added_strs:
            cur_vals.append(proc)
            all_added_strs.add(proc)
            still_want -= 1
        if still_want > 0:
            splits_still_need.append((still_want, cur_vals, gram_gen))
    if splits_still_need:
        raise ValueError(f"Unable to find all vals")
    return all_vals


def get_git_label() -> str:
    import subprocess, uuid
    git_label = subprocess.check_output(["git", "describe", "--always"]).decode('utf-8').strip()
    return git_label


#def write_vals(
#    path: Path,
#    vals: Sequence[str],
#):
#    df = pd.DataFrame([
#        {
#            "guid": uuid.uuid4(),
#            "split": name,
#            "text": val,
#            "label": label,
#            "source": source,
#            "justification_cat": justification_cat,
#            "comments": comment,
#        }
#        for val in vals
#    ])
#    df.to_csv(path, index=False)


def save_pos_examples(root: Path, all_added_strs: Set[str]):
    all_pos_grams = partition_grammar(
        get_areyourobot_grammar(),
        list(SPLIT_SIZES.values()),
        seed=42,
        duplicate_prob_mass=DUPLICATE_PROB_MASS,
    )
    desired_sizes = [int(TOTAL_SIZE * SPLIT_SIZES[name] * SPLITS['pos']) for name in SPLIT_SIZES.keys()]
    all_vals = get_examples_from_grammars(all_pos_grams, desired_sizes, all_added_strs)
    print("Saving values")
    git_label = get_git_label()
    for name, vals in zip(SPLIT_SIZES.keys(), all_vals):
        df = pd.DataFrame([
            AreYouRobotDatasetExample(
                split=name,
                text=v,
                label=AreYouRobotClass.POSITIVE,
                source=f"pos_grammar_{git_label}"
            ).as_dict()
            for v in vals
        ])
        df.to_csv(root / f"pos.{name}.csv")


def save_neg_examples(all_added_strs):
    all_neg_grams = partition_grammar(
        get_negdistractor_grammar(),
        list(SPLIT_SIZES.values()),
        seed=42,
        duplicate_prob_mass=DUPLICATE_PROB_MASS,
    )
    desired_sizes = [int(TOTAL_SIZE * SPLIT_SIZES[name] * SPLITS['pos']) for name in SPLIT_SIZES.keys()]
    all_vals = get_examples_from_grammars(all_neg_grams, desired_sizes, all_added_strs)


def main():
    assert sum(SPLITS.values()) == 1.0
    assert sum(SPLIT_SIZES.values()) == 1.0
    all_data_strings = set()
    ROOT.mkdir(exist_ok=True, parents=True)
    save_pos_examples(ROOT, all_data_strings)


if __name__ == "__main__":
    main()