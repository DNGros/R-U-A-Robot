import sys, os
import json
from pathlib import Path
from pprint import pprint


if __name__ == "__main__":
    cur_dir = Path(os.path.basename(__file__)).parent
    data = json.loads((cur_dir / "data_volunteers.json").read_text())
    print(len(data))
    #pprint(data)
