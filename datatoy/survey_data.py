from pathlib import Path

import pandas as pd

cur_file = Path(__file__).parent.absolute()


def get_survey_data():
    return pd.read_csv(cur_file / "labels/part1_survey_data.csv")