from pathlib import Path
from datetime import datetime
import pandas as pd
from statistics import mean
from typing import Sequence, Tuple, Dict

from tabulate import tabulate

from datatoy.grammar_classifier import AreYouRobotClassifier, GrammarClassifyException, AreYouRobotClass
from datatoy.survey_data import get_survey_data
from templates.ambigious_grammar import get_amb_grammar
from templates.areyourobot_grammar import get_areyourobot_grammar

from templates.distractor_grammar import get_negdistractor_grammar
from templates.gramdef import Grammar
from templates.gramgen import GramRecognizer


def check_grammar_coverage(
    df: pd.DataFrame,
    label_col: str = "pos_amb_neg",
    input_col: str = "utterance",
):
    is_completely_good = []
    exactly_in_results = []
    classifier = AreYouRobotClassifier()
    confusion_matrix_dict = {
        label: {
            count_l: 0
            for count_l in list(AreYouRobotClass) + ['fail']
        }
        for label in list(AreYouRobotClass) + ['fail']
    }

    before_time = datetime.now()

    for index, ex in df.iterrows():
        utterance, ex_label = ex[input_col], AreYouRobotClass(ex[label_col])
        if ex_label != AreYouRobotClass.POSITIVE:
            continue
        try:
            pred = classifier.classify(utterance)
        except GrammarClassifyException as e:
            print(str(e), utterance)
            confusion_matrix_dict[ex_label]['fail'] += 1
            exactly_in_results.append(0)
            continue
        correct_pred = pred.prediction == ex_label
        exactly_in = pred.exactly_in_class
        confusion_matrix_dict[ex_label][pred.prediction] += 1
        exactly_in_results.append(int(exactly_in))
        if not correct_pred:
            print(f"Expect {ex_label} got {pred.prediction}: {utterance}")
        elif not exactly_in:
            print(f"Not exact {pred.prediction}: {utterance}")

    #print(f"Elapsed time {(datetime.now() - before_time).total_seconds() * 1000 / len(df)} milisec per len")

    is_all_good = True
    for label, preds in confusion_matrix_dict.items():
        if label == "fail":
            continue
        print(f"-- Expect {label}")
        for plabel, pcount in preds.items():
            print(f"{plabel}: {pcount}")
        recall = preds[label] / sum(preds.values())
        print(f"Recall: {recall}")
        is_all_good &= recall == 1.0
    exact_count = mean(exactly_in_results)
    print(f"Exactly In Rate: {exact_count} ({sum(exactly_in_results)}/{len(exactly_in_results)})")
    is_all_good &= exact_count == 1
    print("✔️ 😀" if is_all_good else ":(")


    #print("Recall:", mean(results), f"({sum(results)}/{len(results)})")
    #print("Limited Recall:", mean(results_limited), f"({sum(results_limited)}/{len(results_limited)})")
    #print(f"False count: full {sum(false_class)}. Limited {sum(false_class_limited)}")
    #this_is_completely_good = mean(results) == 1 and mean(results_limited) == 1 and \
    #                          sum(false_class) == 0 and sum(false_class_limited) == 0
    #print("✔️" if this_is_completely_good else "❌")
    #is_completely_good.append(int(this_is_completely_good))
    #print("✔️ 😀" if mean(is_completely_good) == 1 else ":(")


#def check_pos():
#    survey_df = get_survey_data()
#    pos = survey_df.query('pos_amb_neg == "p"')
#    print("----- POS ------------")
#    check_grammar_coverage(get_areyourobot_grammar(), pos)
#
#
#def check_neg():
#    survey_df = get_survey_data()
#    neg = survey_df.query('pos_amb_neg == "n"')
#    print("----- NEG ------------")
#    #gram = get_negdistractor_grammar()
#    #parser = GramRecognizer(gram)
#    #assert parser.is_in_grammar("hi,yo")
#    check_grammar_coverage(get_negdistractor_grammar(), neg)
#
#
#def check_amb():
#    survey_df = get_survey_data()
#    amb = survey_df.query('pos_amb_neg == "a"')
#    print("----- AMB ------------")
#    check_grammar_coverage(get_amb_grammar(), amb)


def main():
    check_grammar_coverage(
        get_survey_data()
    )


if __name__ == "__main__":
    main()