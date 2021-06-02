"""
We hand label a collection of data examples from multiple sources:
Turker responses, tf_idf retrieved examples, the coding guide, and random utterance

This script iterates through all of them and verifies that the grammar has full
coverage of all labeled examples (ie, that it could correctly detect the examples and
that the grammar could generate the positive or AIC examples)
"""
from pathlib import Path
from tqdm import tqdm
from pprint import pprint
from datetime import datetime
import pandas as pd
from statistics import mean
from typing import Sequence, Tuple, Dict

from tabulate import tabulate

from datatoy.grammar_classifier import AreYouRobotClassifier, GrammarClassifyException, AreYouRobotClass
from datatoy.survey_data import get_survey_data, get_tfidf_distract, get_codeguide_table, get_neg_from_rand
from templates.ambigious_grammar import get_amb_grammar
from templates.areyourobot_grammar import get_areyourobot_grammar

from templates.distractor_grammar import get_negdistractor_grammar
from templates.gramdef import Grammar
from templates.gramgen import GramRecognizer


def check_grammar_coverage(
    df: pd.DataFrame,
    label_col: str = "pos_amb_neg",
    input_col: str = "utterance",
    neg_exact: bool = True,
):
    is_completely_good = []
    exactly_in_results = []
    classifier = AreYouRobotClassifier()
    #print(classifier.classify("I think you are a robot?"))
    #return
    confusion_matrix_dict = {
        label: {
            count_l: 0
            for count_l in list(AreYouRobotClass) + ['fail']
        }
        for label in list(AreYouRobotClass) + ['fail']
    }

    before_time = datetime.now()
    fails = []
    for index, ex in tqdm(df.iterrows(), total=len(df), mininterval=10):
        if not ex[label_col] or ex[label_col] == "nan" or pd.isnull(ex[label_col]):
            continue
        utterance, ex_label = ex[input_col], AreYouRobotClass(ex[label_col])
        #if ex_label != AreYouRobotClass.POSITIVE:
        #    continue
        try:
            pred = classifier.classify(utterance)
        except GrammarClassifyException as e:
            print(str(e), ":", utterance)
            confusion_matrix_dict[ex_label]['fail'] += 1
            exactly_in_results.append(0)
            continue
        correct_pred = pred.prediction == ex_label
        exactly_in = pred.exactly_in_class
        confusion_matrix_dict[ex_label][pred.prediction] += 1
        want_exactly_in = (neg_exact or ex_label != AreYouRobotClass.NEGATIVE)
        if want_exactly_in:
            exactly_in_results.append(int(exactly_in))
        if not correct_pred:
            print(f"Expect {ex_label} got {pred.prediction}: {utterance}")
        elif not exactly_in and want_exactly_in:
            print(f"Not exact {pred.prediction}: {utterance}")
            fails.append(utterance)
    #pprint(fails)

    #print(f"Elapsed time {(datetime.now() - before_time).total_seconds() * 1000 / len(df)} milisec per len")

    is_all_good = True
    for label, preds in confusion_matrix_dict.items():
        if label == "fail":
            continue
        print(f"-- Expect {label}")
        for plabel, pcount in preds.items():
            print(f"{plabel}: {pcount}")
        has_any_vals = any(preds.values())
        if has_any_vals:
            recall = preds[label] / sum(preds.values())
            print(f"Recall: {recall}")
            is_all_good &= recall == 1.0
    exact_count = mean(exactly_in_results)
    print(f"Exactly In Rate: {exact_count} ({sum(exactly_in_results)}/{len(exactly_in_results)})")
    is_all_good &= exact_count == 1
    print("✔️ 😀" if is_all_good else ":(")


def main():
    print("------ Check survey data -----")
    check_grammar_coverage(
        get_survey_data()
    )
    print("------ Check tfidf data -----")
    check_grammar_coverage(
        get_tfidf_distract(),
        input_col='text_unproc',
        neg_exact=False
    )
    print("------ Check code guide data -----")
    check_grammar_coverage(
        get_codeguide_table(),
        input_col='Examples',
        label_col='Label',
        neg_exact=True
    )
    print("------ Check rand data -----")
    check_grammar_coverage(
        get_neg_from_rand(),
        input_col='text_unproc',
        neg_exact=False
    )


if __name__ == "__main__":
    main()