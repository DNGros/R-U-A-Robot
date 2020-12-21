from pathlib import Path
from statistics import mean

from templates.areyourobot_grammar import areyourobot_grammar_obj
import pandas as pd
from templates.gramgen import GramRecognizer

cur_file = Path(__file__).parent.absolute()


def get_survey_data():
    return pd.read_csv(cur_file / "labels/part1_survey_data.csv")


def main():
    pos_parser = GramRecognizer(areyourobot_grammar_obj)
    survey_df = get_survey_data()
    pos = survey_df.query('pos_amb_neg == "p"')
    results = []
    for utterance in pos.utterance:
        r = pos_parser.is_in_grammar(utterance)
        results.append(1 if r else 0)
        if not r:
            print("Not In Grammar:", utterance)
    print("len", len(results))
    print("sum", sum(results))
    print("Pos Recall:", mean(results))


if __name__ == "__main__":
    main()