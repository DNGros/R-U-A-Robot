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
    data = convert_dfs_to_mytextdata(get_all_dataset_dfs())
    classer = AreYouRobotClassifier(exception_if_conflict=False)
    for split in DataSplit:
        print(f"SPLIT {split}")
        split_data = data.get_split_data(split)
        for text, label in tqdm(list(split_data.get_text_and_labels()), mininterval=10):
            pred = classer.classify(text)
            if pred.error_message is not None:
                print("PARSER ERROR", pred.error_message)
            if pred.prediction.value != label:
                print(f"FAIL {text}: pred {pred.prediction} label {label}")
