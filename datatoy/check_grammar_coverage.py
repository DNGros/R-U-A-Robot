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
    pos_parser_limited = GramRecognizer(
        get_areyourobot_grammar(),
        case_sensitive=False,
        check_last_sentence_by_itself=False,
        check_last_comma_by_itself=False,
    )
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
    results_limited = []
    for utterance in pos.utterance:
        in_pos = pos_parser.is_in_grammar(utterance)
        results.append(1 if in_pos else 0)
        in_pos_limited = pos_parser_limited.is_in_grammar(utterance)
        results_limited.append(1 if in_pos_limited else 0)
        if not in_pos or not in_pos_limited:
            print(
                f"{'Not Pos.' if not in_pos else ''}"
                f"{'Not limited' if not in_pos_limited else ''}:",
                utterance
            )
    print("len", len(results))
    print("sum", sum(results))
    print("Pos Recall:", mean(results))
    print("Pos Limited Recall:", mean(results_limited))


if __name__ == "__main__":
    main()