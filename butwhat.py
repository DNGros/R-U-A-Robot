from pathlib import Path
import random
from pprint import pprint

import pandas as pd

cur_file = Path(__file__).parent.absolute()


if __name__ == "__main__":
    pos = pd.read_csv(cur_file / "datatoy/outputs/dataset/v0.1/neg.train.csv")
    pprint(random.sample(list(pos.text), 10))