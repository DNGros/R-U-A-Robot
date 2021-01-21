import statistics
import math
from pathlib import Path
from typing import Iterable, Dict, List, Tuple, Sequence, Union

from classify_text_plz.classifiers.deeplearn.bertbaseline import BertlikeTrainedModel
from classify_text_plz.classifiers.fasttext_baseline import FastTextTrained
from classify_text_plz.classifiers.stupid_classifiers import AlwaysMostCommonModelTrained, RandomGuessTrained
from classify_text_plz.dataing import MyTextData, MyTextDataSplit, DataSplit
import pandas as pd

from classify_text_plz.evaling import PlzEvaluator, Accuracy, Recall, PlzTextMetric, EvalResult
from classify_text_plz.modeling import Prediction, TextModelMaker, TextModelTrained
from classify_text_plz.quickclassify import classify_this_plz
from classify_text_plz.typehelpers import CLASS_LABEL_TYPE
from datatoy.grammar_classifier import GrammarClassifyException, AreYouRobotClassifier, AreYouRobotClass
from datatoy.survey_data import get_test_r_data
from templates.gramgen import GramRecognizer

cur_file = Path(__file__).parent.absolute()


class PosAmbPrecision(PlzTextMetric):
    def score(
        self,
        expected: Iterable[CLASS_LABEL_TYPE],
        predicted: Iterable[Prediction]
    ) -> float:
        points = {"p": 1, "a": 0.25, "n": 0}
        all_scores = [
            points[gt]
            for gt, p in zip(expected, predicted)
            if p.most_probable_label() == "p"
        ]
        if len(all_scores) == 0:
            return 0.0
        return statistics.mean(all_scores)


def dump_results_to_latex_table(results: Dict[str, EvalResult]):
    rows = []
    for model_name, result in results.items():
        model_name = {
            AlwaysMostCommonModelTrained.__name__: "MostCommonClass",
            BertlikeTrainedModel.__name__: "BERT",
            GramModelSuposedTrained.__name__: "Grammar",
            RandomGuessTrained.__name__: "Random Guess",
            "BOWLogisticRegression": "BOW LR",
        }.get(model_name, model_name)
        row = [model_name]
        rows.append(row)
        for split, metrics_map in result.metrics.items():
            row.append(metrics_map[PosAmbPrecision.__name__] * 100)
            row.append(metrics_map[Recall.__name__] * 100)
            row.append(metrics_map[Accuracy.__name__] * 100)
            row.append(
                statistics.geometric_mean(row[-3:]) if min(row[-3:]) > 3 else 0
            )
        # Pad for missing splits
        row.extend(["---"] * ((4 * 4 + 1) - len(row)))
    print(
        "\\\\\n".join([
            ' &'.join(
                c if isinstance(c, str) else (
                    f"{c:.1f}".rjust(4, '0') if not math.isclose(c, 100.0) else "100")
                for c in row
            )
            for row in rows
        ]) + r"\\"
    )


class GramModelMaker(TextModelMaker):
    def __init__(self, inner_classifier: AreYouRobotClassifier):
        self._classifier = inner_classifier

    def fit(self, data: MyTextData) -> TextModelTrained:
        return GramModelSuposedTrained(self._classifier)


class GramModelSuposedTrained(TextModelTrained):
    def __init__(self, inner_classifier: AreYouRobotClassifier):
        self.inner_classifier = inner_classifier

    def predict_text(self, text: str) -> Prediction:
        p = self.inner_classifier.classify(text)
        probs = {"p": 0.0, "n": 0.0, "a": 0.0}
        if p.error_message is not None:
            print("ERROR:", p.error_message)
        if p.exactly_in_class:
            probs[p.prediction.value] = 1.0
        else:
            # Make up some probabilities to use if not exactly in
            if p.prediction == AreYouRobotClass.POSITIVE:
                probs = {"p": 0.75, "n": 0.05, "a": 0.2}
            if p.prediction == AreYouRobotClass.AMBIGIOUS:
                if p.error_message is None:
                    probs = {"p": 0.2, "n": 0.2, "a": 0.5}
                else:
                    probs = {"p": 0.3, "n": 0.3, "a": 0.4}
            if p.prediction == AreYouRobotClass.NEGATIVE:
                probs = {"p": 0.01, "n": 0.9, "a": 0.09}
        return Prediction(probs, guarantee_all_classes=True)


def get_all_dataset_dfs(include_test: bool = False, include_test_r: bool = False) -> Dict[str, pd.DataFrame]:
    dfs = {
        split: pd.concat([
            pd.read_csv(cur_file / f"../datatoy/outputs/dataset/v0.9.2/{label}.{split}.csv")
            for label in ("pos", "amb", "neg")
        ])
        for split in ["train", "val"] + (["test"] if include_test else [])
    }
    if include_test_r:
        test_r = get_test_r_data()
        test_r.rename(columns={"pos_amb_neg": "label", "utterance": "text"}, inplace=True)
        dfs["test_r"] = test_r
    return dfs


def convert_dfs_to_mytextdata(dfs: Dict[str, pd.DataFrame]) -> MyTextData:
    data = MyTextData(
        already_split_datas=[
            MyTextDataSplit(
                split_kind=split,
                text=df.text,
                labels=df.label,
            )
            for split, df in dfs.items()
        ],
    )
    return data


if __name__ == "__main__":
    data = convert_dfs_to_mytextdata(get_all_dataset_dfs(
        include_test=True,
        include_test_r=True
    ))
    results = classify_this_plz(
        data,
        evaluator=PlzEvaluator(
            metrics=(Accuracy(), Recall("p"), PosAmbPrecision()),
            default_dump_split_highest_loss={
                DataSplit.TRAIN: 5,
                DataSplit.VAL: 20,
                DataSplit.TEST: 10,
                "test_r": 50,
            },
        ),
        #include_test_split=False,
        extra_model_maker=[GramModelMaker(AreYouRobotClassifier(exception_if_conflict=False))],
    )
    dump_results_to_latex_table(results)
