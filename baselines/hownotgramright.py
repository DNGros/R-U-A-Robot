import itertools

from spacy.tokens.span import defaultdict

from baselines.runbaseline import convert_dfs_to_mytextdata, get_all_dataset_dfs
from tqdm import tqdm
from classify_text_plz.dataing import MyTextData, DataSplit
import statistics
import math
from pathlib import Path
from typing import Iterable, Dict

from classify_text_plz.classifiers.deeplearn.bertbaseline import BertlikeTrainedModel
from classify_text_plz.classifiers.fasttext_baseline import FastTextTrained
from classify_text_plz.dataing import MyTextData, MyTextDataSplit
import pandas as pd

from classify_text_plz.evaling import PlzEvaluator, Accuracy, Recall, PlzTextMetric, EvalResult
from classify_text_plz.modeling import Prediction, TextModelMaker, TextModelTrained
from classify_text_plz.quickclassify import classify_this_plz
from classify_text_plz.typehelpers import CLASS_LABEL_TYPE
from datatoy.grammar_classifier import GrammarClassifyException, AreYouRobotClassifier, AreYouRobotClass
from templates.gramgen import GramRecognizer

cur_file = Path(__file__).parent.absolute()

if __name__ == "__main__":
    data = convert_dfs_to_mytextdata(get_all_dataset_dfs(
        include_test=True,
        include_test_r=False,
    ))
    classer = AreYouRobotClassifier(exception_if_conflict=False)
    for split_key, split_data in data.get_all_splits():
        print(f"SPLIT {split_key}")
        if split_key in (DataSplit.TRAIN, DataSplit.VAL):
            print("skip")
            continue
        all_fails = {"p": [], "a": [], "n": []}
        for text, label in tqdm(list(split_data.get_text_and_labels()), mininterval=10):
            pred = classer.classify(text)
            is_fail = False
            if pred.error_message is not None:
                is_fail = True
                print("PARSER ERROR", pred.error_message)
            if pred.prediction.value != label:
                is_fail = True
                if pred.prediction.value == "p":
                    print(f"FAIL {text}: pred {pred.prediction} label {label}")
            all_fails[label].append(int(not is_fail))
        for label, fails in all_fails.items():
            print(f"{label}: {statistics.mean(fails)} ({sum(fails)}/{len(fails)})")
        all_vs = list(itertools.chain(*all_fails.values()))
        print(f"Total: {statistics.mean(all_vs)} ({sum(all_vs)}/{len(all_vs)})")

