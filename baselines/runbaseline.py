import statistics
import math
from pathlib import Path
from typing import Iterable, Dict

from classify_text_plz.classifiers.deeplearn.bertbaseline import BertlikeTrainedModel
from classify_text_plz.classifiers.fasttext_baseline import FastTextTrained
from classify_text_plz.classifiers.most_common_class import AlwaysMostCommonModelTrained
from classify_text_plz.dataing import MyTextData, MyTextDataSplit
import pandas as pd

from classify_text_plz.evaling import PlzEvaluator, Accuracy, Recall, PlzTextMetric, EvalResult
from classify_text_plz.modeling import Prediction
from classify_text_plz.quickclassify import classify_this_plz
from classify_text_plz.typehelpers import CLASS_LABEL_TYPE

cur_file = Path(__file__).parent.absolute()


class PosAmbPrecision(PlzTextMetric):
    def score(
        self,
        expected: Iterable[CLASS_LABEL_TYPE],
        predicted: Iterable[Prediction]
    ) -> float:
        points = {"p": 1, "a": 0.25, "n": 0}
        all_scores = [
            points[p.most_probable_label()]
            for gt, p in zip(expected, predicted)
            if gt == "p"
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
        }.get(model_name, model_name)
        row = [model_name]
        rows.append(row)
        print(result.metrics)
        for split, metrics_map in result.metrics.items():
            print(metrics_map)
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


if __name__ == "__main__":
    dfs = [
        pd.concat([
            pd.read_csv(cur_file / f"../datatoy/outputs/dataset/v0.3/{label}.{split}.csv")
            for label in ("pos", "amb", "neg")
        ])
        for split in ("train", "val", "test")
    ]
    for df in dfs:
        assert len(df.label.unique()) == 3
    data = MyTextData(
        already_split_datas=[
            MyTextDataSplit(
                split_kind=split,
                text=df.text,
                labels=df.label,
            )
            for split, df in zip(("train", "val", "test"), dfs)
        ],
    )
    results = classify_this_plz(
        data,
        evaluator=PlzEvaluator(
            metrics=(Accuracy(), Recall("p"), PosAmbPrecision())
        ),
        include_test_split=False,
    )
    dump_results_to_latex_table(results)
