from pathlib import Path

from classify_text_plz.dataing import MyTextData, MyTextDataSplit
import pandas as pd

from classify_text_plz.quickclassify import classify_this_plz

cur_file = Path(__file__).parent.absolute()


if __name__ == "__main__":
    dfs = [
        pd.concat([
            pd.read_csv(cur_file / f"../datatoy/outputs/dataset/v0.1/{label}.{split}.csv")
            for label in ("pos", "amb", "neg")
        ])
        for split in ("train", "val", "test")
    ]
    for df in dfs:
        print(df.label.unique())
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
    classify_this_plz(data)
