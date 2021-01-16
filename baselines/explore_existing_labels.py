from pprint import pprint
from collections import Counter
from pathlib import Path

from baselines.runbaseline import get_all_dataset_dfs
import pandas as pd

cur_file = Path(__file__).parent.absolute()


def get_existing_sys_labels():
    return pd.read_csv(cur_file / "../datatoy/labels/existing_sys.v2_fill.csv")


def how_vague():
    df = get_existing_sys_labels()
    vert = [
        *zip(df['Google Assistant Response'], df['Google Assistant Label']),
        *zip(df['Alexa Response2'], df['Alexa Label']),
        *zip(df['Blender-1.4B Response'], df['Blender Label']),
    ]
    vert = Counter([
        text
        for text, label in vert
        if label in ("HUC", "HIC", "OTNC")
    ])
    pprint(vert, width=150)


if __name__ == "__main__":
    how_vague()
