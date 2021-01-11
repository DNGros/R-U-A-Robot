from collections import deque
import math
import random
import attr
import uuid
from typing import Sequence, Iterable
import pandas as pd
from pathlib import Path
from typing import Set

from datatoy.grammar_classifier import AreYouRobotClass
from datatoy.survey_data import get_tfidf_distract, get_neg_from_rand
from templates.ambigious_grammar import get_amb_grammar
from templates.areyourobot_grammar import get_areyourobot_grammar
from templates.distractor_grammar import get_negdistractor_grammar
from templates.gramdef import partition_grammar, Grammar
from util.sampling import WeirdSplitter
from util.util import repeat_val, inner_chain

cur_file = Path(__file__).parent.absolute()

ROOT = cur_file / "outputs/dataset/v0.3"
TOTAL_SIZE = 6800
DUPLICATE_PROB_MASS = 0.25
SOURCE_SIZE = {
    "pos": .4,
    "aic": 0.1,
    "neg_rand": 0.10,
    "neg_distract": 0.2,
    "neg_tfidf": 0.2,
}
SPLIT_SIZES = {
    "train": .70,
    "val": .15,
    "test": .15,
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
    comment: str = ""
    guid: str = attr.ib(factory=lambda: uuid.uuid4())

    def as_dict(self):
        return {
            "guid": self.guid,
            "split": self.split,
            "text": self.text,
            "label": self.label.value,
            "source": self.source,
            "justification_cat": self.justification_cat,
            "comment": self.comment,
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


def save_pos_examples(all_added_strs: Set[str]):
    all_pos_grams = partition_grammar(
        get_areyourobot_grammar(),
        list(SPLIT_SIZES.values()),
        seed=42,
        duplicate_prob_mass=DUPLICATE_PROB_MASS,
    )
    desired_sizes = [int(TOTAL_SIZE * SPLIT_SIZES[name] * SOURCE_SIZE['pos']) for name in SPLIT_SIZES.keys()]
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
        df.to_csv(ROOT / f"pos.{name}.csv")


def get_neg_from_grammar(all_added_strs):
    all_neg_grams = partition_grammar(
        get_negdistractor_grammar(),
        list(SPLIT_SIZES.values()),
        seed=42,
        duplicate_prob_mass=DUPLICATE_PROB_MASS,
    )
    desired_sizes = [int(TOTAL_SIZE * SPLIT_SIZES[name] * SOURCE_SIZE['neg_distract']) for name in SPLIT_SIZES.keys()]
    all_gram_neg_vals = get_examples_from_grammars(all_neg_grams, desired_sizes, all_added_strs)
    git_label = get_git_label()
    return [
        [
            AreYouRobotDatasetExample(
                split=split,
                text=text,
                label=AreYouRobotClass.NEGATIVE,
                source=f"neg_grammar_{git_label}"
            )
            for text in split_texts
        ]
        for split, split_texts in zip(SPLIT_SIZES.keys(), all_gram_neg_vals)
    ]


def split_df(
    all_added_strs: Set[str],
    df: pd.DataFrame,
    desired_total_count: int,
    split_weights: Sequence[float],
    desired_label: str,
    source: str,
    label_col: str = "pos_amb_neg",
    text_col: str = "text_unproc",
    justification_col: str = "justification",
    comment_col: str = "comment",
    seed: float = 42,
) -> Sequence[Sequence[AreYouRobotDatasetExample]]:
    splitter = WeirdSplitter(
        split_weights, seed, duplicate_prob_mass=0, min_unique_elements_per_split=0)
    df = df[df[label_col] == desired_label]
    vals = [
        row
        for row in df.to_dict(orient="records")
        if not pd.isnull(row[label_col]) if row[text_col] not in all_added_strs
    ]
    # Remove duplicate values or values already in some split somewhere
    vals_no_dups = []
    possible_seen_texts = set()
    for v in vals:
        if v[text_col] not in all_added_strs and v[text_col] not in possible_seen_texts:
            vals_no_dups.append(v)
            possible_seen_texts.add(v[text_col])
    vals = vals_no_dups
    del vals_no_dups, possible_seen_texts
    # Split the values into each split
    if len(vals) < desired_total_count:
        raise ValueError(source, len(vals), desired_total_count)
    random.Random(seed).shuffle(list(vals))
    vals = vals[:desired_total_count]
    all_added_strs.update(v[text_col] for v in vals)
    split_vals = splitter.split_items(
        vals, [1 for _ in vals], key=lambda v: v[text_col])
    split_vals = [
        [
            AreYouRobotDatasetExample(
                split=split_name,
                text=val[text_col],
                label=AreYouRobotClass(desired_label),
                source=source,
                justification_cat=val[justification_col],
                comment=val[comment_col]
            )
            for val, weight in split_vals
        ]
        for split_name, split_vals in zip(SPLIT_SIZES.keys(), split_vals)
    ]
    return split_vals


def _get_neg_splits_from_rand(all_added_strs):
    git_label = get_git_label()
    return split_df(
        all_added_strs, get_neg_from_rand(), int(TOTAL_SIZE*SOURCE_SIZE['neg_rand']),
        list(SPLIT_SIZES.values()), "n", f"neg_rand_{git_label}")


def _get_neg_splits_from_tfidf(all_added_strs):
    git_label = get_git_label()
    return split_df(
        all_added_strs, get_tfidf_distract(), int(TOTAL_SIZE*SOURCE_SIZE['neg_tfidf']),
        list(SPLIT_SIZES.values()), "n", f"neg_tfidf_{git_label}")


def save_neg_examples(all_added_strs):
    rand_examples = _get_neg_splits_from_rand(all_added_strs)
    tfidf_examples = _get_neg_splits_from_tfidf(all_added_strs)
    gram_examples = get_neg_from_grammar(all_added_strs)
    for split_name, split_vals in zip(
        SPLIT_SIZES.keys(), inner_chain(gram_examples, tfidf_examples, rand_examples)
    ):
        df = pd.DataFrame(
            v.as_dict() for v in split_vals
        )
        expect_size = TOTAL_SIZE * SPLIT_SIZES[split_name] * (
                SOURCE_SIZE["neg_rand"] + SOURCE_SIZE["neg_tfidf"] + SOURCE_SIZE['neg_distract'])
        assert math.isclose(len(df), expect_size), f"{len(df)} {expect_size}"
        df.to_csv(ROOT / f"neg.{split_name}.csv", index=False)


def save_amb_examples(all_added_strs):
    all_amb_grams = partition_grammar(
        get_amb_grammar(),
        list(SPLIT_SIZES.values()),
        seed=42,
        duplicate_prob_mass=DUPLICATE_PROB_MASS,
    )
    desired_sizes = [int(TOTAL_SIZE * SPLIT_SIZES[name] * SOURCE_SIZE['aic']) for name in SPLIT_SIZES.keys()]
    all_vals = get_examples_from_grammars(all_amb_grams, desired_sizes, all_added_strs)
    print("Saving amb values")
    git_label = get_git_label()
    for name, vals in zip(SPLIT_SIZES.keys(), all_vals):
        df = pd.DataFrame([
            AreYouRobotDatasetExample(
                split=name,
                text=v,
                label=AreYouRobotClass.AMBIGIOUS,
                source=f"amb_grammar_{git_label}"
            ).as_dict()
            for v in vals
        ])
        df.to_csv(ROOT / f"amb.{name}.csv")


def main():
    assert sum(SOURCE_SIZE.values()) == 1.0
    assert sum(SPLIT_SIZES.values()) == 1.0
    all_data_strings = set()
    ROOT.mkdir(exist_ok=True, parents=True)
    save_pos_examples(all_data_strings)
    save_neg_examples(all_data_strings)
    save_amb_examples(all_data_strings)


if __name__ == "__main__":
    main()