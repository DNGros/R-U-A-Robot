from pathlib import Path
from statistics import mean

from templates.areyourobot_grammar import get_areyourobot_grammar
import pandas as pd
from templates.gramgen import GramRecognizer, gram_to_lark_ebnf

cur_file = Path(__file__).parent.absolute()


def get_survey_data():
    return pd.read_csv(cur_file / "labels/part1_survey_data.csv")


def main():
    print(gram_to_lark_ebnf(get_areyourobot_grammar()))
    pos_parser = GramRecognizer(get_areyourobot_grammar())
    assert pos_parser.is_in_grammar("Is this a live person that I'm talking to?")
    assert pos_parser.is_in_grammar("am I talking to a real human being or to a machine?")
    assert pos_parser.is_in_grammar("Am I speaking with a machine or a person?")
    assert pos_parser.is_in_grammar("you are talking like a robot.are you?")
    assert pos_parser.is_in_grammar("wait\nare you a robot?")
    assert pos_parser.is_in_grammar("Aren't you a human?")
    assert pos_parser.is_in_grammar("Aren't you a woman?")
    assert pos_parser.is_in_grammar("are you a live person or a chatbot?")
    assert pos_parser.is_in_grammar("are you a robot talking to me?")
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