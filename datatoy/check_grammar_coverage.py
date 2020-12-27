from pathlib import Path
from statistics import mean

from templates.areyourobot_grammar import get_areyourobot_grammar
import pandas as pd

from templates.distractor_grammar import get_negdistractor_grammar
from templates.gramdef import Grammar
from templates.gramgen import GramRecognizer, gram_to_lark_ebnf

cur_file = Path(__file__).parent.absolute()


def get_survey_data():
    return pd.read_csv(cur_file / "labels/part1_survey_data.csv")


def check_grammar_coverage(gram: Grammar, examples):
    #print(gram_to_lark_ebnf(gram))
    parser = GramRecognizer(gram)
    parser_limited = GramRecognizer(
        gram,
        case_sensitive=False,
        check_last_sentence_by_itself=False,
        check_last_comma_by_itself=False,
    )
    results = []
    results_limited = []
    for utterance in examples.utterance:
        in_gram_tricks = parser.is_in_grammar(utterance)
        results.append(1 if in_gram_tricks else 0)
        in_gram_limited = parser_limited.is_in_grammar(utterance)
        results_limited.append(1 if in_gram_limited else 0)
        if not in_gram_tricks or not in_gram_limited:
            print(
                f"{'Not In.' if not in_gram_tricks else ''}"
                f"{'Not limited' if not in_gram_limited else ''}:",
                utterance
            )
    print("Recall:", mean(results), f"({sum(results)}/{len(results)})")
    print("Limited Recall:", mean(results_limited), f"({sum(results_limited)}/{len(results_limited)})")


def check_pos():
    survey_df = get_survey_data()
    pos = survey_df.query('pos_amb_neg == "p"')
    print("----- POS ------------")
    check_grammar_coverage(get_areyourobot_grammar(), pos)


def check_neg():
    survey_df = get_survey_data()
    pos = survey_df.query('pos_amb_neg == "n"')
    print("----- NEG ------------")
    #gram = get_negdistractor_grammar()
    #parser = GramRecognizer(gram)
    #assert parser.is_in_grammar("hi,yo")
    check_grammar_coverage(get_negdistractor_grammar(), pos)


def main():
    check_pos()
    check_neg()


if __name__ == "__main__":
    main()