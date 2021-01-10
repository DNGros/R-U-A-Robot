import statistics
from pathlib import Path
from typing import Iterable

from classify_text_plz.dataing import MyTextData, MyTextDataSplit
import pandas as pd

from classify_text_plz.evaling import PlzEvaluator, Accuracy, Recall, PlzTextMetric
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


if __name__ == "__main__":
    dfs = [
        pd.concat([
            pd.read_csv(cur_file / f"../datatoy/outputs/dataset/v0.2/{label}.{split}.csv")
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
    classify_this_plz(
        data,
        evaluator=PlzEvaluator(
            metrics=(Accuracy(), Recall("p"), PosAmbPrecision())
        )
    )
